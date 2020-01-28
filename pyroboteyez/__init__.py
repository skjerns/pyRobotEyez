# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 18:27:19 2019

@author: Simon
"""
import numpy as np
import time
import PIL
import cv2
import argparse
from PIL import ImageTk
import tkinter as tk
from PIL import Image
import stimer

def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()



class App():
    def __init__(self, window_title, video_source=0, no_flip=False,
                 focus=0, width=800, height=600, wait=5, file='capture.jpg'):
        self.wait=wait
        self.file=file
        self.height=height
        self.width=width
        self.focus=focus
        self.window = tk.Tk()
        self.window.title(window_title)
        self.video_source = video_source
        self.no_flip = no_flip
        self.d_w = 640
        self.d_h = int(height*(self.d_w/width))
        self.vid = Capture(self.video_source, focus=focus, width=width,
                           height=height)
        self.canvas = tk.Canvas(self.window, width = self.d_w, height = self.d_h)
        self.canvas.pack()
        self.start = time.time()
        self.update()
        center(self.window)
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.mainloop()
        
    def update(self):
        elapsed = time.time() - self.start
        
        if elapsed > self.wait:
            self.save()
            time.sleep(2.5)
            self.vid.__del__()
            self.window.destroy()
            return
        elapsed = str(int(self.wait - elapsed))
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        stimer.toggle(1)
        ret, img = self.vid.get_frame()
        stimer.toggle(1)
        img = np.array(img)
        if not self.no_flip: img = np.fliplr(img)
        self.img = img
        if ret:
            frame = cv2.resize(img, (self.d_w, self.d_h), interpolation=cv2.INTER_NEAREST)
            textsize = cv2.getTextSize(elapsed, font, 5, 5)[0]
            textX = (self.d_w - textsize[0]-50) // 2
            textY = (self.d_h + textsize[1]+65) // 2
            frame=cv2.putText(frame, elapsed,(textY,textX), 
                            font, 5,(255,255,255),5,cv2.LINE_AA)
            cv2.waitKey(1)
            self.frame = ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.frame, anchor = tk.NW)

        self.window.after(15, self.update)

    def save(self):
        img = self.img[:,::-1]
        img = img[:,::-1,:]
        img = Image.fromarray(img)
        img.save(self.file)



class Capture():
    def __init__(self, video_source=0, focus=5, width=800, height=600):
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
        self.vid.set(cv2.CAP_PROP_AUTOFOCUS, focus<0)
        if focus>=0:
            self.vid.set(cv2.CAP_PROP_FOCUS, focus)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
        
        if not self.vid.isOpened():
           raise ValueError("Unable to open video source", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
        

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            
            
            
if __name__=='__main__':           
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-w',"--width", help="width of the image", type=int, default=1920)
    parser.add_argument('-h',"--height", help="height of the image", type=int, default=1080)
    parser.add_argument('-f',"--file", help="height of the image", type=str, default='capture.jpg')
    parser.add_argument('--help', action='help', help='show this help message and exit')
    parser.add_argument('--wait', help='how many seconds to wait', default=5, type=int)
    parser.add_argument('--focus', help='focus set point to set, -1 is autofocus',
                        choices=list(range(0,260,5))+[-1], type=int, default=5)
    parser.add_argument('--no-flip', help='do not flip display image', type=bool,
                        default=False)
    args = parser.parse_args()
    
    width = args.width
    height = args.height
    file = args.file
    wait = args.wait
    focus = args.focus
    no_flip = args.no_flip
    
    self=App("Video Capture", focus=focus, width=width, height=height,
        wait=wait, file=file, no_flip=no_flip)