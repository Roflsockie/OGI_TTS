# OGI TTS - Portable Text-to-Speech Application

A portable desktop application for converting text to speech using Microsoft Edge TTS engine. Supports multiple languages and voices with a modern dark-themed GUI.

## Features

- **Multi-language Support**: Russian, English, Ukrainian, Japanese
- **Voice Options**: Male and Female voices for each language
- **File Import**: Support for .txt and .docx files
- **Auto Language Detection**: Automatically detects text language
- **Progress Tracking**: Real-time progress bar with detailed status updates
- **Portable Design**: Single executable file, no installation required
- **Audio Output**: Saves generated speech as WAV files
- **Modern UI**: Dark-themed interface with intuitive controls

## Requirements

- Windows 10/11
- No additional dependencies (all included in the executable)

## Development Setup

If you want to run the application from source code:

1. Install Python 3.11
2. Install dependencies: `pip install -r requirements.txt`
3. Download FFMPEG binaries and place them in `ffmpeg/bin/` folder
4. Run `main.py`

## Installation

1. Download the `OGI_TTS.exe` file
2. Place it in any folder on your computer
3. Run the executable

## Usage

1. **Import Text**: Click "Import Text" to select a .txt or .docx file
2. **Choose Model**: Select "Edge TTS" (currently the only available option)
3. **Select Voice**: Choose between Male or Female voice
4. **Play Example**: Enter text in the input field and click "Play example" to preview
5. **Generate Speech**: Click "Text to Speech" to convert the full imported text
6. **Open Results**: Use "Open Result Folder" to access generated audio files

The application will create a `tts_audio` folder in the same directory as the executable to store output files.

## Supported Languages and Voices

- **Russian**: Dmitry (Male), Svetlana (Female)
- **English**: Zira (Male), Aria (Female)
- **Ukrainian**: Ostap (Male), Polina (Female)
- **Japanese**: Keita (Male), Nanami (Female)

## Technical Details

- Built with Python 3.11 and PyQt5
- Uses Microsoft Edge TTS for high-quality speech synthesis
- Portable executable created with PyInstaller
- File size: ~52MB

## License

This project is open source. Feel free to use and modify.

## Author

Created with ❤️ for easy text-to-speech conversion
