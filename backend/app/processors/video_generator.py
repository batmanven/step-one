"""
Video Generator: Processes raw event videos, detects high-action segments,
and automatically edits them into a highlight reel using FFmpeg.
"""
from pathlib import Path
import cv2
import numpy as np
import ffmpeg
import os
from typing import List, Tuple
import shutil

class VideoGenerator:
    def __init__(self, dataset_path: Path):
        self.videos_dir = dataset_path / "videos"
        self.temp_dir = Path("outputs/temp_videos")
        
    def create_highlight_reel(self, session_id: str, target_duration: int = 30) -> Path:
        """Create a highlight reel of target duration (seconds)"""
        if not self.videos_dir.exists():
            print("No videos directory found.")
            return None
            
        video_files = list(self.videos_dir.glob("*.mp4")) + list(self.videos_dir.glob("*.mov"))
        if not video_files:
            print("No video files found in dataset.")
            return None
            
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # We want clips of 3 seconds each
        clip_duration = 3
        target_clips = max(target_duration // clip_duration, 1)
        
        # Distribute clips evenly across available videos
        clips_per_video = max(target_clips // len(video_files), 1)
        if clips_per_video == 0 and video_files:
             clips_per_video = 1
             
        extracted_clips = []
        clip_counter = 0
        
        for video_path in video_files:
            try:
                # Find best timestamps using motion analysis
                best_timestamps = self._find_action_highlights(video_path, clip_duration, clips_per_video)
                
                # Extract the clips
                for start_time in best_timestamps:
                    out_path = self.temp_dir / f"clip_{clip_counter}.mp4"
                    self._extract_clip(video_path, start_time, clip_duration, out_path)
                    if out_path.exists():
                        extracted_clips.append(out_path)
                        clip_counter += 1
                        
                    if len(extracted_clips) >= target_clips:
                        break
                        
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")
                
            if len(extracted_clips) >= target_clips:
                break
                
        if not extracted_clips:
            print("Failed to extract any usable clips.")
            return None
            
        # Concatenate all clips into final reel
        output_dir = Path("outputs/reels")
        output_dir.mkdir(parents=True, exist_ok=True)
        final_reel = output_dir / f"{session_id}_reel.mp4"
        
        try:
            self._concatenate_clips(extracted_clips, final_reel)
        except Exception as e:
            print(f"Error concatenating reel: {e}")
            return None
            
        # Cleanup
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
            
        return final_reel if final_reel.exists() else None

    def _find_action_highlights(self, video_path: Path, clip_duration: int, count: int) -> List[float]:
        """Use frame differencing to find segments with the most motion/action"""
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # If video is shorter than the requested clip, just take from start
        if duration <= clip_duration:
            cap.release()
            return [0.0]
            
        frames_per_window = int(clip_duration * fps)
        
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return [0.0]
            
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.resize(prev_gray, (320, 240)) # Downscale for speed
        
        motion_scores = []
        current_score = 0
        
        frame_idx = 1
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Sample every 5th frame for speed
            if frame_idx % 5 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (320, 240))
                
                # Calculate absolute difference
                diff = cv2.absdiff(prev_gray, gray)
                score = np.sum(diff)
                
                motion_scores.append(score)
                prev_gray = gray
                
            frame_idx += 1
            
        cap.release()
        
        if not motion_scores:
            return [0.0]
            
        # Calculate moving average for windows
        # Note: scores array represents samples at (fps/5) rate
        samples_per_window = max(int((clip_duration * fps) / 5), 1)
        
        window_scores = []
        for i in range(len(motion_scores) - samples_per_window):
            window_score = sum(motion_scores[i:i+samples_per_window])
            # Store timestamp (i * 5 / fps) and score
            window_scores.append((i * 5 / fps, window_score))
            
        if not window_scores:
            return [0.0]
            
        # Sort by score descending
        window_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top 'count' windows, ensuring they don't overlap heavily
        selected_timestamps = []
        for timestamp, score in window_scores:
            if not selected_timestamps:
                selected_timestamps.append(timestamp)
            else:
                # Check overlap (keep them at least 1 clip duration apart)
                conflict = False
                for t in selected_timestamps:
                    if abs(t - timestamp) < clip_duration:
                        conflict = True
                        break
                if not conflict:
                    selected_timestamps.append(timestamp)
                    
            if len(selected_timestamps) >= count:
                break
                
        return selected_timestamps
        
    def _extract_clip(self, video_path: Path, start_time: float, duration: int, out_path: Path):
        """Use FFmpeg to quickly extract a clip without re-encoding video"""
        try:
            (
                ffmpeg
                .input(str(video_path), ss=start_time, t=duration)
                .output(str(out_path), c='copy', loglevel="error")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")

    def _concatenate_clips(self, clips: List[Path], out_path: Path):
        """Use FFmpeg to concatenate the extracted clips"""
        # Create a concat demuxer file
        list_file = self.temp_dir / "concat_list.txt"
        with open(list_file, "w") as f:
            for clip in clips:
                # ffmpeg requires full paths in the list file
                f.write(f"file '{clip.absolute()}'\n")
                
        try:
            (
                ffmpeg
                .input(str(list_file), format='concat', safe=0)
                .output(str(out_path), c='copy', loglevel="error")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print(f"FFmpeg concat error: {e.stderr.decode()}")
