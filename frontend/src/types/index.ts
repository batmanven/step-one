export interface Session {
  session_id: string;
  status: string;
  message: string;
  dataset_path: string;
}

export interface Output {
  session_id: string;
  status: string;
  progress: number;
  stage: string;
  outputs: {
    linkedin_collage?: string;
    linkedin_caption?: string;
    instagram_caption?: string;
    stories?: string[];
    case_study?: string;
  };
  error?: string;
}

export interface ProcessResponse {
  session_id: string;
  status: string;
  message: string;
  dataset_path: string;
}
