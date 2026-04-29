# MKV Naming & OCR Tools

A collection of AI-powered workflows for identifying, OCRing, and renaming MKV files (typically from Blu-ray or DVD backups) based on their image-based PGS subtitles.

## 🚀 Primary Usage

While these tools are optimized for the Gemini CLI and its `mkv-subtitle-ocr` skill, they are designed to work well with any AI-driven development tool that can execute scripts and interpret file content.

### Gemini CLI (Recommended)
The AI agent understands the complex workflows of subtitle extraction, OCR, and episode identification. Use a prompt like:

> "Use the `mkv-subtitle-ocr` skill to identify and rename all MKV files in the current folder. Group episodes into season folders and ensure SRT files are generated for each."

## Requirements

The following system packages must be installed to support the AI's operations:

- **mkvtoolnix**: For track identification and extraction.
- **tesseract-ocr**: The OCR engine (ensure language packs like `tesseract-ocr-eng` are installed).
- **ffmpeg**: For extracting subtitle snippets.
- **python3**: With the `venv` module.

## How it Works

The Gemini CLI uses the following underlying scripts to perform its tasks. **Manual execution of these scripts is discouraged**, as the AI handles environment setup, error recovery, and context-aware renaming:

- `scripts/pgs_to_srt.py`: Automates the conversion of PGS subtitles to SRT.
- `scripts/extract_snippet.py`: Extracts short snippets of dialogue for episode identification.

## Key Features

- **Automated Venv Management**: The AI manages a Python virtual environment in `~/.cache/gemini-cli/` to handle dependencies.
- **Snippet-Based Identification**: The AI quickly identifies episodes by reading a few minutes of dialogue from the middle of the file.
- **Media Server Ready**: The AI ensures naming conventions for Plex and Jellyfin (e.g., `Show Name - S01E01 - Title.mkv`).
