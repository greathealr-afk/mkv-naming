---
name: makemkv-subtitle-ocr
description: Extract and OCR image-based PGS subtitles from MakeMKV (MKV) backups to text-based SRT format. Includes a workflow for identifying and renaming episodes based on subtitle content. Suitable for Blu-ray and DVD backups.
---

# MakeMKV Subtitle OCR

This skill provides a workflow for extracting and converting image-based PGS (HDMV) subtitles from MKV files to text-based SRT format using OCR (Optical Character Recognition), and identifying episodes for proper renaming.

## Safety Mandates (CRITICAL)

- **NO DELETION:** Never use `rm`, `unlink`, or `shutil.rmtree` on any media files or folders.
- **Atomic Renaming:** Use `mv` for renaming. Never copy and then delete the source.
- **NO OVERWRITE:** ALWAYS check if the destination file exists before renaming. Never overwrite an existing file unless it has been explicitly verified as a duplicate or inferior version. In shell, use `mv -n` (no-clobber). In Python, use `os.path.exists()` before `os.rename()`.
- **Folder Cleanup:** Do NOT attempt to delete "empty" source folders. Leave them for the user to verify and remove manually.
- **Preserve Source:** If a move operation is complex, prefer keeping the source until the destination is verified.

## Requirements

The following tools must be installed on the system:
- mkvtoolnix (contains mkvmerge and mkvextract)
- tesseract-ocr
- python3 (with venv module)
- ffmpeg (for snippet extraction)

## Workflow

### 1. Identify Subtitle Tracks
Use mkvmerge to list the tracks in the MKV file and find the Track ID for the PGS subtitles.

```bash
mkvmerge -i "your_video.mkv"
```
Look for lines like: Track ID <N>: subtitles (HDMV PGS).

### 2. Extract and OCR Subtitles
Use the bundled Python script to automate the process. This script handles the virtual environment and pgsrip tool.

```bash
python3 scripts/pgs_to_srt.py "your_video.mkv"
```

## Identification & Renaming Workflow

If your MKV files have generic names (e.g., title_01.mkv), use the subtitles to identify the correct episode number and title.

### 1. Extract a Subtitle Snippet (Robust)
To identify the episode without OCRing the entire file, use the `extract_snippet.py` script. By default, it extracts a 2-minute snippet from the 10-minute mark to avoid recaps and intros.

```bash
# Basic usage (10-minute mark, 2-minute duration)
python3 scripts/extract_snippet.py "input.mkv"

# Custom mark (e.g., 20 minutes in)
python3 scripts/extract_snippet.py "input.mkv" 00:20:00 00:02:00
```

### 2. Identify the Episode (Robust Strategy)

To avoid false positives (misidentifying an episode because of recaps or common dialogue), use these techniques:

- **The Pilot Trap (CRITICAL):** The very first episode of a series (S01E01) **NEVER** starts with a recap. Before identifying a file as the Pilot, **ALWAYS** extract a snippet at `00:00:00`. If it contains "Previously on..." or "Previously...", it is **NOT** the Pilot.
- **The Triangulation Strategy (Recommended):** To maximize reliability and avoid being misled by recaps or generic dialogue, always check at least three points:
    1.  **00:00:00**: Check for "Previously on" to avoid the Pilot Trap.
    2.  **00:10:00**: Identify unique nouns, plot points, and character dynamics.
    3.  **00:20:00**: Look for title cards or deeper plot details that confirm the specific episode.
- **Search for Unique Dialogue:** Instead of common character names, search for specific, rare nouns or plot points (e.g., "ZPM", "Wraith hive ship", "Ancient chair").
- **Check for the Title Card:** Most shows display the episode title on screen between the 2-minute and 8-minute marks. Look for a standalone line of text that doesn't sound like dialogue.
- **Sequential Validation:** Episodes on a disc are almost always sequential. If `title_01` is E01 and `title_03` is E03, then `title_02` is almost certainly E02. If your identification breaks this sequence, re-check the "Previously on" sections.
- **Duration Check:** Compare durations with an episode guide. Some tracks might be extras or "Extended Versions".

### 3. Verify and Rename
Cross-reference your findings with an online episode guide (e.g., IMDb, Fandom).
Rename the file using the standard format:
Show Name - SXXEXX - Episode Title.mkv

## Advanced Usage: Batch Operations

### 1. Parallel Processing
OCR is CPU-intensive. For entire seasons, run jobs in parallel to save time:
```bash
# Process all MKVs in a directory in parallel groups
for f in *.mkv; do python3 scripts/pgs_to_srt.py "$f" & done; wait
```

### 2. Pre-Filtering by Duration
Use ffprobe to identify which files are actual episodes vs. extras before starting the OCR:
```bash
# List durations for all MKVs to identify episodes (usually 20-50 mins)
for f in *.mkv; do echo "$f: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")"; done
```

## Media Server Optimization (Jellyfin/Plex)

To ensure your media server correctly identifies and groups your episodes and movies, follow these structural guidelines.

### 1. Naming Convention
Rename verified files to the standard format for automatic metadata matching:
- **TV Episodes:** Show Name - SXXEXX - Episode Title.mkv
- **Movies:** Movie Title (Year).mkv

### 2. Folder Structure
Media servers require content to be organized in specific folder structures.

**TV Shows:**
Move your renamed files into a Season XX folder within the show's root directory.

```bash
# Recommended TV structure
Show Name/
├── Season 01/
│   ├── Show Name - S01E01 - Pilot.mkv
│   └── Show Name - S01E01 - Pilot.en.srt
└── Season 02/
    ├── Show Name - S02E01 - New Beginnings.mkv
    └── Show Name - S02E01 - New Beginnings.en.srt
```

**Movies:**
Each movie should ideally be in its own folder. The folder name **MUST** include the release year in parentheses.

```bash
# Recommended Movie structure
Movie Title (Year)/
└── Movie Title (Year).mkv
```

### 3. External Subtitles
Always keep the generated .srt files alongside the .mkv files with matching base names. Jellyfin and Plex will automatically load them.

## Troubleshooting

- No languages found: Ensure tesseract-ocr-eng (or other language packs) are installed.
- Venv issues: Python's venv module refuses to create environments in paths containing a colon (:). The bundled script attempts to use ~/.cache/gemini-cli/pgs_to_srt_venv or /tmp to avoid this.
- Duplicates: TV discs often contain a "Play All" track which is a large MKV containing all episodes. Verify if one file's duration matches the sum of the others.
