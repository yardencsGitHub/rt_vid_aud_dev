## Data acquisition script for miniscope experiments in singing canaries
-------------------------------------------------------------------------
Yarden Cohen, Feb 2024

This script runs in a terminal and can replace the [VideoCapture App](https://github.com/gardner-lab/video-capture) if needed. 
The [FinchScope](https://github.com/gardner-lab/FinchScope) was developed by Will Liberti for capturing fluorescence signals in small animals.
The script monitors a microphone, detects events based on their spectral acoustic properties, and uses these events to trigger turning on the FinchScope's 
LED and to synchronously acquire the microphone and FinchScope fluorescence video. 

### Installation and setting up:
- Create a conda environment with the latest python and the following packages:
ffmpeg, matplotlib, numpy, scipy, pandas, tkinter, pyserial, pyaudio, opencv-python, json, keyboard
- Copy the script files
- Use the **configure_param_files** script (type *python configure_param_files.py* in the terminal) to create a configuration file (or start with one of the files in the *parameter_files* folder).
- Use the 

### Usage:

Canary song triggering
