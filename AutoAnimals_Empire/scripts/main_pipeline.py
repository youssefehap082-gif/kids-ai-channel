
import os
import sys

def check_keys():
    print("🔍 Checking System Fuel (API Keys)...")
    
    required_keys = [
        "OPENAI_API_KEY", 
        "ELEVENLABS_API_KEY", 
        "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN"
    ]
    
    missing = []
    for key in required_keys:
        if not os.environ.get(key):
            missing.append(key)
            
    if missing:
        print(f"❌ CRITICAL ERROR: Missing Keys: {missing}")
        print("⚠️  Please check GitHub Secrets mapping.")
        # We don't exit yet to allow partial runs in future
    else:
        print("✅ All Core Keys Detected. Systems Online.")

def run_pipeline():
    print("🎬 Starting Daily Auto-Tube Pipeline...")
    check_keys()
    
    # Placeholder for Phase 2 Logic
    print("ℹ️  Pipeline is ready for Phase 2 (Content Generation).")
    print("✅ Execution finished.")

if __name__ == "__main__":
    run_pipeline()
