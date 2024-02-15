""" Data acquisition script for miniscope experiments in singing canaries
-------------------------------------------------------------------------
Yarden Cohen, Feb 2024

This script runs in a terminal and can replace the VideoCapture app (https://github.com/gardner-lab/video-capture) if needed. 
The FinchScope (https://github.com/gardner-lab/FinchScope) was developed by Will Liberti for capturing fluorescence signals in small animals.
The script monitors a microphone, detects events based on their spectral acoustic properties, and uses these events to trigger turning on the FinchScope's 
LED and to synchronously acquire the microphone and FinchScope fluorescence video. 

Installation:
- Create a conda environment with the latest python and the following packages:
ffmpeg, matplotlib, numpy, scipy, pandas, tkinter, pyserial, pyaudio, opencv-python, json


Usage:

Canary song triggering """ 

import concurrent.futures
import pyaudio
import cv2
import scipy as cp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from scipy.io.wavfile import write
from serial.tools import list_ports
import os
import subprocess
import tkinter as tk
from tkinter import Tk, filedialog
import serial
import json
from datetime import datetime
import matplotlib
matplotlib.use('MACOSX')

# A function that lists all the available audio devices and allows picking one via the Terminal
def get_audio_devices():
    print("Available Audio Devices:")
    print("------------------------")
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        try:
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
        except:
            pass
    print("------------------------")
    audio_channel_n = input('Type AUDIO channel number: ')
    devinfo = p.get_device_info_by_index(int(audio_channel_n))  # Or whatever device you care about.
    samplerate = int(devinfo['defaultSampleRate'])
    devname = p.get_device_info_by_host_api_device_index(0, int(audio_channel_n)).get('name')
    return int(audio_channel_n),samplerate,devname

# A function that lists all the available video devices, 
# shows a frame from each device, and allows picking one via the Terminal
def choose_camera():
    print("Available Video Device Indexes:")
    print("------------------------")
    index = 0
    arr = []
    while True:
        try:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        except:
            pass

    print(arr)
    plt.close('all')
    if len(arr) > 1:
        
        fig, axs = plt.subplots(len(arr))
        for idx in arr:
            cap = cv2.VideoCapture(idx)
            frame = cap.read(1)
            axs[idx].imshow(frame[1])
            axs[idx].title.set_text('video source: '+ str(idx))
    else:
        fig, axs = plt.subplots()
        cap = cv2.VideoCapture(0)
        frame = cap.read(1)
        axs.imshow(frame[1])

    fig.suptitle('Video Sources')
    
        
    plt.show()
    video_channel = int(input('Type VIDEO channel number: '))
    cap = cv2.VideoCapture(video_channel)
    frame = cap.read(1)[1]
    height,width,colors = np.shape(frame)

    return video_channel, width, height, colors

# A function that lists all the available COM ports and allows picking one via the Terminal
def choose_COM():
    print("------------------------")
    print("Available COM port:")
    print("------------------------")
    port = list(list_ports.comports())
    idx = 0
    for p in port:
        print(str(idx) + ': ' + str(p.device))
        idx += 1
    com_idx = input('Type COM channel number: ')
    return str(port[int(com_idx)].device)

# A function that sets the LED level 0..255 (integers)
def set_LED(level):
    s = ('4n'+chr(int(level))).encode('latin-1')
    #s= struct.pack('!b',int(level))
    
    ser.write(s)

    #print(np.frombuffer(s, dtype='b'))

# A function that allows moving a slider to pick the LED level
def choose_LED_power():
    window = tk.Tk()
    v1 = tk.DoubleVar()
    window.geometry("300x100")
    window.title('Choose LED power')
    #master.title('Choose LED level')
    w = tk.Scale(window, from_=0, to=255,orient=tk.HORIZONTAL,width=10,variable = v1,command = set_LED) #int(v1.get())
    w.pack()
    window.mainloop()
    s = ('4n'+chr(int(0))).encode('latin-1')
    ser.write(s)
    return int(v1.get())

# def set_LED(serobj,level):
#     serobj.write(b'4n'+chr(level).encode('utf-8'))
      

# def choose_LED_power(serobj):
#     window = tk.Tk()
#     v1 = tk.DoubleVar()
#     window.geometry("300x100")
#     window.title('Choose LED power')
#     #master.title('Choose LED level')
#     w = tk.Scale(window, from_=0, to=255,orient=tk.HORIZONTAL,width=10,variable = v1,command = set_LED(serobj,int(v1.get())))
#     w.pack()
#     window.mainloop()
#     return int(v1.get())

# A class for the audio-video acquisition
class Aud_Vid():

    def __init__(self, samplerate, video_dev,audio_dev): #, arg
        self.video = cv2.VideoCapture(video_dev)
        self.FPS = int(input('Enter FPS: '))
        self.CHUNK = int(float(samplerate)/float(self.FPS))# 1470 #1470
        print('User supplied FPS results in CHUNK = ' + str(self.CHUNK))
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1 #2
        self.RATE = int(samplerate) #44100
        self.INDEVIDX = audio_dev
        self.audio = pyaudio.PyAudio() #input_device_index=self.INDEVIDX,
        self.instream = self.audio.open(input_device_index=self.INDEVIDX,format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        self.outstream = self.audio.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,output=True,frames_per_buffer=self.CHUNK)
        print(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        # 640.0
        
        print(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 360.0
        
        print(self.video.get(cv2.CAP_PROP_FPS))
        # 29.97002997002997
        
        print(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        # 360.0

        self.video.set(cv2.CAP_PROP_BUFFERSIZE,0)


    def sync(self):
          with concurrent.futures.ThreadPoolExecutor() as executor:
                  tv = executor.submit(self.video.read) 
                  ta = executor.submit(self.instream.read,self.CHUNK,exception_on_overflow = False) #1470
                  # exception_on_overflow = False
                  vid = tv.result()
                  aud = ta.result()
                  return(vid[1].tobytes(),aud)

# A function that opens a dialog box for picking the working folder and the parameters file
def get_working_folder_and_params():
    root = Tk() # pointing root to Tk() to use it as Tk() in program.
    root.withdraw() # Hides small tkinter window.
    root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    dir_path = filedialog.askdirectory(title="Please select a working directory:") # Returns opened path as str
    path_to_params = filedialog.askopenfilename(title="Please select a parameters file:")
    return dir_path, path_to_params

# A function that writes the audio and video to file
def write_av_to_file(video_data,video_params,audio_data,audio_samplerate,working_dir,file_basename):
    # create audio-video file
    temp_audio_file = os.path.join(working_dir,'temp_' + file_basename + '.wav')
    temp_video_file = os.path.join(working_dir,'temp_' + file_basename + '.mp4')
    output_av_file = os.path.join(working_dir,file_basename + '.mp4')

    print('writing:')
    print(temp_audio_file)
    print(temp_video_file)

    bbx = [np.frombuffer(bx, dtype='<i2').reshape(-1) for bx in audio_data]
    audiodata = np.array(bbx).reshape(-1)
    write(temp_audio_file, audio_samplerate, audiodata.astype(np.int16))

    v_fps = video_params[0]; v_width = video_params[1]; v_height = video_params[2]; v_colors = video_params[3]
    #fourcc = cv2.VideoWriter_fourcc(*'XVID') #XVID
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    output = cv2.VideoWriter(temp_video_file, fourcc, v_fps, (v_width, v_height))
    for ai in video_data:
        sig = np.frombuffer(ai, dtype='B').reshape(v_height,v_width,v_colors)
        output.write(sig)
    output.release()

    print('writing:')
    print(output_av_file)

    ffmpeg_string = 'ffmpeg -i ' + temp_video_file + ' -i ' + temp_audio_file + ' -c:v copy -c:a aac ' + output_av_file
    os.system(ffmpeg_string)
    os.remove(temp_audio_file)  
    os.remove(temp_video_file)  

def write_metadata_to_file(md_filename,working_dir,header,file_rec_start_time,frame_times,no_song_powers,song_powers,bg_powers,ents,detects):
    csv_filename = os.path.join(working_dir, md_filename + '.csv')
    df = pd.DataFrame({'time':np.array(frame_times)-file_rec_start_time,
                                       'song_power':song_powers,
                                       'nosong_power':no_song_powers,
                                       'bg_power':bg_powers,
                                       'entropy':ents,
                                       'trigger':detects})
    with open(csv_filename, 'w') as csv_file:
        for line in header:
            csv_file.write(line)
        df.to_csv(csv_file)

if __name__ == '__main__':
    audio_dev, samplerate,devname = get_audio_devices() 
    com_dev = choose_COM()
    #print('You chose:\n Audio device {}, whose samplerate is {}, \n Video device {}, \n and COM device {}.'.format(audio_dev,samplerate,video_dev,com_dev))
    ser = serial.Serial(com_dev,baudrate=115200)
    ser.close()
    ser.open()
    LEDpw = choose_LED_power()
    # shut the LED dowm

    video_dev, frame_width, frame_height, frame_colors = choose_camera()
    av = Aud_Vid(samplerate, video_dev, audio_dev)
    fourcc = cv2.VideoWriter_fourcc(*'XVID') #XVID
    fps = av.FPS
    videoparams = [fps,frame_width,frame_height,frame_colors]
    
    CSV_header = 'System Parameters: \n Audio: source=' + devname + ', samplerate=' + str(samplerate) +',\n' + \
        'Video: source idx,fps,width,height,colors=' + str(videoparams) + ',\n' + \
        'Serial: port=' + com_dev + ', baudrate = 115200, \n' \
        'LED level: ' + str(LEDpw) + ',\n'
    print("Select working Folder:")
    working_folder, path_to_params = get_working_folder_and_params()
    print('Parameters in: ' + path_to_params)
    with open(path_to_params, 'r') as openfile:
    # Reading from json file
        params_dict = json.load(openfile)
    params_header = 'Trigger Parameters: \n' # will keep all the parameters in the CSV header
    for item in params_dict.items():
        print(item[0] + ': ' + str(item[1]))
        params_header = params_header + item[0] + ': ' + str(item[1]) + '\n'
    CSV_header = CSV_header + params_header
    print("Starting to monitor song:")
    
    (a,b) = av.sync()
    sig_old = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
    (a,b) = av.sync()
    sig = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
    f,pxx = cp.signal.welch(np.concatenate([sig_old,sig]), fs=samplerate, window='hann',nfft=2048)

    fidx_song = [[i for i,e in enumerate(f) if e >= params_dict['SONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['SONG_BAND'][1]][-1]]
    fidx_no_song = [[i for i,e in enumerate(f) if e >= params_dict['NOSONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['NOSONG_BAND'][1]][-1]]

    is_recording = False
    video_frames = []
    audio_frames = []
    frame_times = []
    no_song_powers = []
    song_powers = []
    bg_powers = []
    ents = []
    detects = []
    curr_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            st = time.time()
            (a,b) = av.sync()
            sig = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
            f,pxx = cp.signal.welch(np.concatenate([sig_old,sig]), fs=samplerate, window='hann',nfft=2048)
            sig_old = sig
            no_song_power = np.sum(pxx[fidx_no_song[0]:fidx_no_song[1]])
            song_power = np.sum(pxx[fidx_song[0]:fidx_song[1]])
            bg_power = np.sum(pxx[0:fidx_song[0]])
            psong = pxx[fidx_song[0]:fidx_song[1]] / (np.sum(pxx[fidx_song[0]:fidx_song[1]]) + 1e-10)
            ent = -sum(psong*np.log2(psong))

            

            detect = (song_power / no_song_power >= params_dict['THR_SONG_NOSONG']) * (song_power / bg_power >= params_dict['THR_SONG_BG']) * (ent <= params_dict['THR_ENTROPY'])
            if is_recording == True:
                no_song_powers.append(no_song_power)
                song_powers.append(song_power)
                bg_powers.append(bg_power)
                ents.append(ent)
                frame_times.append(st)
                video_frames.append(a)
                audio_frames.append(b)
                detects.append(detect)
            # print('Detect: {}, Powers: Song: {}, Song-NoSong: {}, Song-BG: {}, Entropy: {}'.format(detect,
            #                                                                                        song_power, 
            #                                                                            song_power/(no_song_power+1e-15),
            #                                                                            song_power/(bg_power+1e-15),
            #
            #                                                                             ent))
            #print([curr_time,st,is_recording])
            if detect == True:
                curr_time = st
                if is_recording == False:
                    file_rec_start_time = st
                    is_recording = True
                    set_LED(LEDpw)
                    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    print('Starting to record: ' + filename)
                    no_song_powers.append(no_song_power)
                    song_powers.append(song_power)
                    bg_powers.append(bg_power)
                    ents.append(ent)
                    frame_times.append(st)
                    video_frames.append(a)
                    audio_frames.append(b)
                    detects.append(detect)
                else:
                    pass
            else:
                if st-curr_time > params_dict['SEC_AFTER_TRIGGER'] and is_recording == True:
                    is_recording = False
                    set_LED(0)
                    # here save av file
                    executor.submit(write_av_to_file,video_frames,videoparams,audio_frames,samplerate,working_folder,filename) #executor.submit(
                    # here save CSV file
                    executor.submit(write_metadata_to_file,filename,working_folder,CSV_header,file_rec_start_time,frame_times,no_song_powers,song_powers,bg_powers,ents,detects) #executor.submit(
                    
                    video_frames = []
                    audio_frames = []
                    frame_times = []
                    no_song_powers = []
                    song_powers = []
                    bg_powers = []
                    ents = []
                    detects = []
                else:
                    pass
                #VideoWriterObj = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))
