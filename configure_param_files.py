import tkinter as tk
from tkinter import filedialog
import matplotlib
matplotlib.use('MACOSX')
import json
import numpy as np

def save_button():
    print(e1.get(),e2.get())
    curr_dict_to_save = {'THR_SONG_NOSONG':float(e1.get()),
                 'THR_SONG_BG':float(e2.get()),
                 'THR_ENTROPY':float(e3.get()),
                 'SONG_BAND':[int(e4.get()),int(e5.get())],
                 'NOSONG_BAND':[int(e6.get()),int(e7.get())],
                 'EXP_SONG':float(e8.get()),
                 'EXP_BG':float(e9.get()),
                 'SEC_AFTER_TRIGGER':float(e10.get())
                 }
    tl1 = tk.Toplevel(master)
    tl1.withdraw()
    tl1.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    
    json_object = json.dumps(curr_dict_to_save, indent=4)
    # Writing to sample.json
    with filedialog.asksaveasfile(title="Please select a parameters file:") as params_file:
        params_file.write(json_object)

def load_button():
    tl1 = tk.Toplevel(master)
    tl1.withdraw()
    tl1.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    path_to_params = filedialog.askopenfilename(title="Please select a parameters file:")
    with open(path_to_params, 'r') as openfile:
    # Reading from json file
        json_object = json.load(openfile)
        
    e1.delete(0, tk.END) #deletes the current value
    e1.insert(0, json_object['THR_SONG_NOSONG'])
    e2.delete(0, tk.END) #deletes the current value
    e2.insert(0, json_object['THR_SONG_BG'])
    e3.delete(0, tk.END) #deletes the current value
    e3.insert(0, json_object['THR_ENTROPY'])
    e4.delete(0, tk.END) #deletes the current value
    e4.insert(0, json_object['SONG_BAND'][0])
    e5.delete(0, tk.END) #deletes the current value
    e5.insert(0, json_object['SONG_BAND'][1])
    e6.delete(0, tk.END) #deletes the current value
    e6.insert(0, json_object['NOSONG_BAND'][0])
    e7.delete(0, tk.END) #deletes the current value
    e7.insert(0, json_object['NOSONG_BAND'][1])
    e8.delete(0, tk.END) #deletes the current value
    e8.insert(0, json_object['EXP_SONG'])
    e9.delete(0, tk.END) #deletes the current value
    e9.insert(0, json_object['EXP_BG'])
    e10.delete(0, tk.END) #deletes the current value
    e10.insert(0, json_object['SEC_AFTER_TRIGGER'])


if __name__ == '__main__':
    import tkinter as tk

    master = tk.Tk()
    master.title('Parameter File Editor')
    master.geometry("600x400")
    curr_dict = {'THR_SONG_NOSONG':1.4,'THR_SONG_BG':21,'THR_ENTROPY':7.5,'SONG_BAND':[3000,8700],'NOSONG_BAND':[500,1500],'EXP_SONG':0.0002,'EXP_BG':600,'SEC_AFTER_TRIGGER':5.0}
    def_values = [1.4,21,7.5,3000,8700,500,1500,0.0002,600,5.0]

    tk.Label(master, text='THR_SONG_NOSONG').grid(row=0,column=0)
    tk.Label(master, text='THR_SONG_BG').grid(row=1,column=0)
    tk.Label(master, text='THR_ENTROPY').grid(row=2,column=0)
    tk.Label(master, text='SONG_BAND_MIN').grid(row=3,column=0)
    tk.Label(master, text='SONG_BAND_MAX').grid(row=3,column=2)
    tk.Label(master, text='NOSONG_BAND_MIN').grid(row=4,column=0)
    tk.Label(master, text='NOSONG_BAND_MAX').grid(row=4,column=2)
    tk.Label(master, text='EXP_SONG').grid(row=5,column=0)
    tk.Label(master, text='EXP_BG').grid(row=6,column=0)
    tk.Label(master, text='SEC_AFTER_TRIGGER').grid(row=7,column=0)
    

    e1 = tk.Entry(master)
    e2 = tk.Entry(master)
    e3 = tk.Entry(master)
    e4 = tk.Entry(master)
    e5 = tk.Entry(master)
    e6 = tk.Entry(master)
    e7 = tk.Entry(master)
    e8 = tk.Entry(master)
    e9 = tk.Entry(master)
    e10 = tk.Entry(master)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    e4.grid(row=3, column=1)
    e5.grid(row=3, column=3)
    e6.grid(row=4, column=1)
    e7.grid(row=4, column=3)
    e8.grid(row=5, column=1)
    e9.grid(row=6, column=1)
    e10.grid(row=7, column=1)
    
    
    b1=tk.Button(master, text='Save', command=save_button).grid(row=8,column=1)
    b2=tk.Button(master, text='Load', command=load_button).grid(row=8,column=0)

    entries = [e1,e2,e3,e4,e5,e6,e7,e8,e9,e10]
    for entry,val in zip(entries,def_values):
         entry.insert(0,val)
    #     idx += 1

    master.mainloop()