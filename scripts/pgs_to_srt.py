import subprocess
import sys
import os
import venv
import shutil
import tempfile

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(result.returncode)
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pgs_to_srt.py <mkv_file> [track_id]")
        sys.exit(1)

    mkv_file = sys.argv[1]
    
    # Use a persistent venv in the user's home directory to avoid issues with 
    # colons (':') in workspace paths, which break Python's venv module.
    venv_dir = os.path.expanduser("~/.cache/gemini-cli/pgs_to_srt_venv")
    
    pip_bin = os.path.join(venv_dir, "bin", "pip")
    pgsrip_bin = os.path.join(venv_dir, "bin", "pgsrip")

    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        os.makedirs(os.path.dirname(venv_dir), exist_ok=True)
        try:
            venv.create(venv_dir, with_pip=True)
        except ValueError as e:
            # Fallback if home directory also contains colons or other issues
            print(f"Warning: Failed to create venv in {venv_dir}. Falling back to /tmp.")
            venv_dir = os.path.join(tempfile.gettempdir(), "pgs_to_srt_venv")
            if not os.path.exists(venv_dir):
                venv.create(venv_dir, with_pip=True)
            pip_bin = os.path.join(venv_dir, "bin", "pip")
            pgsrip_bin = os.path.join(venv_dir, "bin", "pgsrip")
        
        print("Installing pgsrip...")
        run_cmd([pip_bin, "install", "pgsrip"])

    print(f"Converting subtitles from {mkv_file}...")
    # pgsrip handles track detection; passing track_id is optional and omitted for simplicity
    run_cmd([pgsrip_bin, mkv_file])
    print("Done! Check for the .srt file in the same directory.")

if __name__ == "__main__":
    main()
