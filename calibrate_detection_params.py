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
import keyboard


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
    samplerate = devinfo['defaultSampleRate']
    return int(audio_channel_n),samplerate

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
    video_channel = input('Type VIDEO channel number: ')
    return(int(video_channel))

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
    
def choose_LED_power():
    window = tk.Tk()
    v1 = tk.DoubleVar()
    window.geometry("300x100")
    window.title('Choose LED power')
    #master.title('Choose LED level')
    w = tk.Scale(window, from_=0, to=255,orient=tk.HORIZONTAL,width=10,variable = v1)
    w.pack()
    window.mainloop()
    return int(v1.get())
    
def print_value(val):
    print(val)

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

def get_working_folder_and_params():
    root = Tk() # pointing root to Tk() to use it as Tk() in program.
    root.withdraw() # Hides small tkinter window.
    root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    path_to_params = filedialog.askopenfilename(title="Please select a parameters file:")
    return path_to_params
          
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('MACOSX')
    audio_dev, samplerate = get_audio_devices() 
    #com_dev = choose_COM()
    #print('You chose:\n Audio device {}, whose samplerate is {}, \n Video device {}, \n and COM device {}.'.format(audio_dev,samplerate,video_dev,com_dev))
    LEDpw = choose_LED_power()
    video_dev = choose_camera()
    av = Aud_Vid(samplerate, video_dev, audio_dev)
    #ser = serial.Serial(com_dev,baudrate=115200)
    #ser.close()
    #ser.open()

    #print("Select working Folder:")
    path_to_params = get_working_folder_and_params()
    print('Parameters in: ' + path_to_params)
    with open(path_to_params, 'r') as openfile:
    # Reading from json file
        params_dict = json.load(openfile)
    for item in params_dict.items():
        print(item[0] + ': ' + str(item[1]))

    print("Starting to monitor song:")
    
    (a,b) = av.sync()
    sig_old = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
    (a,b) = av.sync()
    sig = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
    f,pxx = cp.signal.welch(np.concatenate([sig_old,sig]), fs=samplerate, window='hann',nfft=2048)

    fidx_song = [[i for i,e in enumerate(f) if e >= params_dict['SONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['SONG_BAND'][1]][-1]]
    fidx_no_song = [[i for i,e in enumerate(f) if e >= params_dict['NOSONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['NOSONG_BAND'][1]][-1]]

    while True:
        if keyboard.is_pressed("a"):
            os.system('python configure_param_files.py')
            path_to_params = get_working_folder_and_params()
            print('Parameters in: ' + path_to_params)
            with open(path_to_params, 'r') as openfile:
            # Reading from json file
                params_dict = json.load(openfile)
            for item in params_dict.items():
                print(item[0] + ': ' + str(item[1]))
            
            (a,b) = av.sync()
            sig_old = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
            (a,b) = av.sync()
            sig = np.frombuffer(b, dtype='<i2').reshape(-1).astype('float')/32000.0
            f,pxx = cp.signal.welch(np.concatenate([sig_old,sig]), fs=samplerate, window='hann',nfft=2048)
            fidx_song = [[i for i,e in enumerate(f) if e >= params_dict['SONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['SONG_BAND'][1]][-1]]
            fidx_no_song = [[i for i,e in enumerate(f) if e >= params_dict['NOSONG_BAND'][0]][0], [i for i,e in enumerate(f) if e <= params_dict['NOSONG_BAND'][1]][-1]]

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

        print('Detect: {}, Powers: Song: {}, Song-NoSong: {}, Song-BG: {}, Entropy: {}'.format(detect,
                                                                                               song_power, 
                                                                                   song_power/(no_song_power+1e-15),
                                                                                   song_power/(bg_power+1e-15),
                                                                                   ent))