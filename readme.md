# RPA Exercise - Drawing and Counting Squares

A Robotic Process Automation (RPA) exercise using PyAutoGUI and computer vision to draw and count squares in a painting application (Paintbrush).

> **Note:** This project is specifically designed for MacOS and relies on MacOS-specific features (scaling screen coordinates to Retina display and Spotlight for opening the application).

## Description

This program demonstrates basic RPA capabilities by:
1. Opening a painting application
2. Drawing 2-5 random squares
3. Using computer vision to count the squares
4. Saving the artwork and closing upon user command

## Prerequisites

- MacOS
- Python 3.x
- PyAutoGUI
- OpenCV (cv2)
- numpy

## Installation

```bash
pip install pyautogui
pip install opencv-python
pip install numpy
```

## Usage

Run the program using:

```bash
python main.py
```

Press /exit once the program has finished drawing to close the program and save the painting.

## How It Works

1. The program launches a painting application
2. Automatically draws squares using mouse movements
3. Takes a screenshot for image processing
4. Uses computer vision to detect and count squares
5. Saves the work and closes when user requests

The user also has an option to add their drawings or to draw over the program drawn squares before exiting to test the CV capabilities.

## Notes

- Ensure the painting application (Paintbrush) is installed
- Results may vary
- Only compatible with MacOS due to system-specific implementations