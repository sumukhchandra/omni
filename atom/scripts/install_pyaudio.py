import sys
import json
import urllib.request
import subprocess
import os
import platform


import ssl

def install_pyaudio():
    print("🔍 Searching for PyAudio wheel on PyPI...")
    
    url = "https://pypi.org/pypi/PyAudio/json"
    context = ssl._create_unverified_context()
    
    try:
        with urllib.request.urlopen(url, context=context) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Failed to fetch PyPI data: {e}")
        return

    # Target: 0.2.14 for cp312-win_amd64
    target_version = "0.2.14"
    if target_version not in data["releases"]:
        print(f"❌ Version {target_version} not found on PyPI.")
        return

    files = data["releases"][target_version]
    wheel_url = None
    wheel_filename = None

    # We need cp312 and win_amd64
    # The tag might be cp312-cp312-win_amd64.whl
    
    print(f"   Python Version: {sys.version}")
    print(f"   Platform: {platform.system()} {platform.machine()}")
    
    expected_tag = "cp312-cp312-win_amd64"
    
    for f in files:
        if f["filename"].endswith(".whl") and expected_tag in f["filename"]:
            wheel_url = f["url"]
            wheel_filename = f["filename"]
            break
    
    if not wheel_url:
        print(f"❌ Could not find wheel with tag '{expected_tag}' in PyAudio {target_version} files.")
        print("Available files:")
        for f in files:
            print(f" - {f['filename']}")
        return

    print(f"✅ Found wheel: {wheel_filename}")
    print(f"⬇️  Downloading from {wheel_url}...")
    

    print(f"⬇️  Downloading from {wheel_url}...")
    
    try:
        with urllib.request.urlopen(wheel_url, context=context) as response, open(wheel_filename, 'wb') as out_file:
            out_file.write(response.read())
        print("✅ Download complete.")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return


    print("📦 Installing...")
    try:
        # Use --user and --break-system-packages as before
        cmd = [sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", wheel_filename]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation Successful!")
            if os.path.exists(wheel_filename):
                os.remove(wheel_filename)
        else:
            print(f"❌ Installation failed with code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            # Keep file for inspection
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    install_pyaudio()
