"""
Unified Application Launcher for Multimodal Attendance & Engagement Agent.
Usage:
  python run.py             # Launches FastAPI Core Server (http://localhost:8000)
  python run.py --server    # Launches FastAPI Core Server
  python run.py --streamlit # Launches Optional Streamlit Dashboard (http://localhost:8501)
  python run.py --test      # Runs validation test suite
"""

import sys
import os
import argparse
import uvicorn
import subprocess

def run_fastapi_server(host="127.0.0.1", port=8000):
    print("=" * 70)
    print("[EduSense AI] Launching Multimodal Attendance & Engagement Agent")
    print(f"[Server URL] http://{host}:{port}")
    print(f"[API Docs]   http://{host}:{port}/docs")
    print("=" * 70)
    uvicorn.run("backend.main:app", host=host, port=port, reload=False, log_level="info")

def run_streamlit_app(port=8501):
    print("=" * 70)
    print("[Streamlit] Launching Interactive Analytics Dashboard")
    print(f"[Dashboard URL] http://localhost:{port}")
    print("=" * 70)
    subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", str(port)])

def run_tests():
    print("=" * 70)
    print("[Test Suite] Running Validation and Edge-Case Test Suite")
    print("=" * 70)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multimodal Attendance & Engagement Agent Launcher")
    parser.add_argument("--server", action="store_true", help="Launch FastAPI web server (default)")
    parser.add_argument("--streamlit", action="store_true", help="Launch Streamlit dashboard")
    parser.add_argument("--test", action="store_true", help="Execute test suite")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")

    args = parser.parse_args()

    if args.streamlit:
        run_streamlit_app()
    elif args.test:
        run_tests()
    else:
        run_fastapi_server(host=args.host, port=args.port)
