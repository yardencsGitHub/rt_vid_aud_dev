# Data acquisition script for miniscope experiments in singing canaries
-------------------------------------------------------------------------
Yarden Cohen, Feb 2024

This script runs in a terminal and can replace the [VideoCapture App](https://github.com/gardner-lab/video-capture) if needed. 
The [FinchScope](https://github.com/gardner-lab/FinchScope) was developed by Will Liberti for capturing fluorescence signals in small animals.
The script monitors a microphone, detects events based on their spectral acoustic properties, and uses these events to trigger turning on the FinchScope's 
LED and to synchronously acquire the microphone and FinchScope fluorescence video. 

---
## Installation and setting up:
- Create a conda environment with the latest python and the following packages:
ffmpeg, matplotlib, numpy, scipy, pandas, tkinter, pyserial, pyaudio, opencv-python, json, keyboard
- Copy the script files
- Use the **configure_param_files** script (type *python configure_param_files.py* in the terminal) to create a configuration file (or start with one of the files in the *parameter_files* folder).

- The configuration file defines parameters used to trigger acquisition based on spectral acoustic properties:
  -  The acoustic power in the 'song' band - defined as a frequency range.
  -  The acoustic power in the non-song band - defined as a frequency range. Lower than the 'song' band.
  -  The acoustic power in the background band - defined as the frequency range from 0Hz to the beginning of the no-song band.
  -  The acoustic Entropy - calculated as the Wiener entropy the power in the frequency bins of the song band.

- The configuration file also defines the time duration (in seconds) from the last song detection to continue acquisition.
---
## Usage:
- The script acquires video frames and audio frames synchronously and uses the audio to triggering recording based on three quantities:
  - The power ratio between the song and no-song frequency bands.
  - The power ration between the song and the background bands.
  - The entropy of the song band.

### Parameter calibration for optimal detection:
- Run the **calibrate_detection_params** script as administrator (type *sudo python calibrate_detection_params.py* in the terminal) to tune the parameters used for song detection.
  - The script prompts choosing an initial configuration file.
  - The script prompts choosing an audio source (via the terminal)
  - The script prompts choosing a video source: It first shows frames acquired from the available sources. Then, after the window showing the images is closed the script allows picking the video source in the terminal and asks that the source's frame rate (FPS) will be entered (since this rate is not reliably given by all frame grabing hardwares).
  - The script shows a continuous read of the power rations, the entropy, and the detection.
  - Press the 'a' key on the keyboard ('a' for 'adjust') to change the parameters used for detection. The script will call *python configure_param_files.py* to allow making changes to parameter files and then will prompt for selecting a new parameters file.

### Running the script:
Type *python av_capture.py* in the terminal. The script will go through several steps that allow
- Picking an audio source
- Picking the right COM port to communicate with the ARDUINO Mega card responsible for the LED power level.
- When the COM port is chosen (in the terminal) a slider window appear. Using a slider allows changing the LED power (the resulting video can be observed via *Photo Booth* for example).
- When the slider window is closed, the script allows picking a video source as above (this time remember to close all pop up windows before selecting the video source in the terminal)
- The script asks for a folder in which data will be saved.
- The script asks for a parameters file.
- Then monitoring starts and the terminal will show when recording starts and when file writing is executed.

### Data files:
The script saves audio and video in .mp4 files and all metadata in .csv files.
The .csv files (one for each video with the same name) include the parameters of the parameters file, all choice made while running the script (e.g. the LED power), and the timing and detection parameters for each video frame. 


