---
name: makemkv-subtitle-ocr
description: Extract and OCR image-based PGS subtitles from MakeMKV (MKV) backups to text-based SRT format. Includes a workflow for identifying and renaming episodes based on subtitle content. Suitable for Blu-ray and DVD backups.
---

# MakeMKV Subtitle OCR

This skill provides a workflow for extracting and converting image-based PGS (HDMV) subtitles from MKV files to text-based SRT format using OCR (Optical Character Recognition), and identifying episodes for proper renaming.

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

- **Avoid the First 5 Minutes:** Recaps and "Previously on..." sections are common in the first few minutes and often contain dialogue from *previous* episodes.
- **Search for Unique Dialogue:** Instead of common character names, search for specific, rare nouns or plot points (e.g., "ZPM", "Wraith hive ship", "Ancient chair").
- **Multiple Snippets:** If the 10-minute mark doesn't give you enough information, take another snippet from the 25-minute mark.
- **Sequential Validation:** If you are processing a batch from a single disc (e.g., title_01.mkv to title_05.mkv), the episodes are almost always sequential. If title_01 is S01E01 and title_03 is S01E03, then title_02 is almost certainly S01E02. Flag any "out of order" identifications for manual review.
- **Duration Check:** Compare the duration with an episode guide. Some tracks are "Extended Versions" or "Director's Cuts" which have different durations.
- **Opening Title Card:** Most shows display the episode title on screen a few minutes into the episode. Look for text that appears alone on a line shortly after the intro theme.

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

To ensure your media server correctly identifies and groups your episodes, follow these structural guidelines.

### 1. Naming Convention
Rename verified files to the standard format for automatic metadata matching:
Show Name - SXXEXX - Episode Title.mkv

### 2. Folder Structure
Media servers require episodes to be placed in specific subfolders. Move your renamed files into a Season XX folder within the show's root directory.

```bash
# Recommended structure
Show Name/
├── Season 01/
│   ├── Show Name - S01E01 - Pilot.mkv
│   └── Show Name - S01E01 - Pilot.en.srt
└── Season 02/
    ├── Show Name - S02E01 - New Beginnings.mkv
    └── Show Name - S02E01 - New Beginnings.en.srt
```

### 3. External Subtitles
Always keep the generated .srt files alongside the .mkv files with matching base names. Jellyfin and Plex will automatically load them.

## Troubleshooting

- No languages found: Ensure tesseract-ocr-eng (or other language packs) are installed.
- Venv issues: Python's venv module refuses to create environments in paths containing a colon (:). The bundled script attempts to use ~/.cache/gemini-cli/pgs_to_srt_venv or /tmp to avoid this.
- Duplicates: TV discs often contain a "Play All" track which is a large MKV containing all episodes. Verify if one file's duration matches the sum of the others.
