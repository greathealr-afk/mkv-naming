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
        print("Usage: python3 extract_snippet.py <mkv_file> [timestamps...]")
        print("Example: python3 extract_snippet.py video.mkv 00:10:00 00:20:00 00:30:00")
        sys.exit(1)

    mkv_file = sys.argv[1]
    timestamps = sys.argv[2:] if len(sys.argv) > 2 else ["00:10:00"]
    duration = "00:02:00"
    
    # Use a persistent venv
    venv_dir = os.path.expanduser("~/.cache/gemini-cli/pgs_to_srt_venv")
    pip_bin = os.path.join(venv_dir, "bin", "pip")
    pgsrip_bin = os.path.join(venv_dir, "bin", "pgsrip")

    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        os.makedirs(os.path.dirname(venv_dir), exist_ok=True)
        venv.create(venv_dir, with_pip=True)
        print("Installing pgsrip...")
        run_cmd([pip_bin, "install", "pgsrip"])

    for ts in timestamps:
        with tempfile.TemporaryDirectory() as temp_dir:
            snippet_mkv = os.path.join(temp_dir, f"snippet_{ts.replace(':', '')}.mkv")
            
            print(f"\n--- Snippet at {ts} (duration {duration}) ---")
            # Extract the subtitle stream (PGS) into a temporary MKV
            run_cmd([
                "ffmpeg", "-ss", ts, "-i", mkv_file, 
                "-map", "0:s:0", "-t", duration, 
                "-c", "copy", snippet_mkv
            ])
            
            # pgsrip the snippet
            # Note: pgsrip outputs to the same dir as the input
            run_cmd([pgsrip_bin, snippet_mkv])
            
            import glob
            srt_files = glob.glob(snippet_mkv.replace(".mkv", "*.srt"))
            if srt_files:
                for srt_file in srt_files:
                    with open(srt_file, 'r') as f:
                        print(f"\n--- SRT Content from {os.path.basename(srt_file)} ---")
                        print(f.read())
            else:
                print(f"Failed to generate SRT snippet for {ts}.")

if __name__ == "__main__":
    main()
