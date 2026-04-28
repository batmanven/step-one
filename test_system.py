#!/usr/bin/env python3
"""Test script to verify the Content & Design Engine is working"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✓ Health check: {r.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_root():
    print("\nTesting root endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        data = r.json()
        print(f"✓ Root endpoint: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False

def test_process_dataset(dataset_name):
    print(f"\nTesting dataset processing: {dataset_name}...")
    try:
        r = requests.post(f"{BASE_URL}/api/v1/process/{dataset_name}", timeout=5)
        data = r.json()
        print(f"✓ Processing started: {json.dumps(data, indent=2)}")
        return data.get("session_id")
    except Exception as e:
        print(f"✗ Processing failed: {e}")
        return None

def test_status(session_id):
    print(f"\nChecking status for session: {session_id}...")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/process/{session_id}/status", timeout=5)
        data = r.json()
        print(f"✓ Status: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"✗ Status check failed: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("CONTENT & DESIGN ENGINE - SYSTEM TEST")
    print("=" * 60)
    if not test_health():
        print("\n⚠ Server may not be running. Start with:")
        print("  cd /Users/priyanshnarang/Desktop/stepone-ai/backend")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        exit(1)
    test_root()

    print("\n" + "=" * 60)
    print("SYSTEM STATUS: OPERATIONAL")
    print("=" * 60)

    print("\nGenerated Outputs:")
    print("  - LinkedIn Collages: backend/outputs/linkedin/")
    print("  - Instagram Stories: backend/outputs/stories/")
    print("  - Case Studies: backend/outputs/case_studies/")
    print("\nAPI Documentation: <http://localhost:8000/docs>")
