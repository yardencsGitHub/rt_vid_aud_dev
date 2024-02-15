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

The configuration file defines parameters used to trigger acquisition based on spectral acoustic properties:
* The acoustic power in the 'song' band - defined as a frequency range.
* The acoustic power in the non-song band - defined as a frequency range. Lower than the 'song' band.
* The acoustic power in the background band - defined as the frequency range from 0Hz to the beginning of the no-song band.
* The acoustic Entropy - calculated as the Wiener entropy the power in the frequency bins of the song band.

The configuration file also defines the time duration (in seconds) from the last song detection to continue acquisition.

### Usage:
The script acquires video frames and audio frames synchronously and uses the audio to triggering recording based on three quantities:
-- The ratio 
- Run the **calibrate_detection_params** script as administrator (type *sudo python calibrate_detection_params.py* in the terminal) to tune the parameters used for song detection

