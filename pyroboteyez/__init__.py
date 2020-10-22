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
from tqdm import tqdm
from threading import Thread

#%%
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
                 focus=0, width=800, height=600, wait=3, file='capture.jpg',
                 flash='auto'):
        self.tqdm_loop = tqdm(unit=' fp')
        self.wait = wait
        self.file = file
        self.height = height
        self.width = width
        self.focus = focus
        self.flash = flash
        self.no_flip = no_flip
        self.video_source = video_source
        self.flash_screen = None
        self.flash_len = 1500

        self.window = tk.Tk()
        self.window.title(window_title)
        self.d_w = 640
        self.d_h = int(height*(self.d_w/width))
        self.camera = CaptureCamera(self.video_source, focus=focus, width=width,
                                 height=height)
        self.canvas = tk.Canvas(self.window, width = self.d_w, height = self.d_h)
        self.canvas.pack()
        self.last = time.time()
        self.start = time.time()
        self.update()
        center(self.window)
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.mainloop()


    def flash_if_needed(self, timeout=1000):
        """
        shows a maximized white window in the background that dissappears
        after n seconds
        """
        if self.flash_screen is not None:
            return # this means flash window is already opened
        if self.flash=='auto':
            if np.median(self.img)>90:
                self.flash_screen = 'too bright'
                return
        elif self.flash==False:
            return

        def destroy():
            self.flash_screen.destroy()
            self.flash_screen.update_ideltasks()
        self.flash_screen = tk.Tk()
        self.flash_screen["bg"] = "#ffe2a1"
        self.flash_screen.deiconify()
        self.flash_screen.state('zoomed')
        self.flash_screen.lift()
        self.flash_screen.attributes('-topmost', True)
        self.flash_screen.attributes('-topmost', False)
        self.flash_screen.update_idletasks()


    def capture(self):
        self.save()
        img = np.ones([self.d_h, self.d_w])*200
        flash_frame = ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
        if not (self.flash_screen is None) and \
           not isinstance(self.flash_screen, str):
            self.flash_screen.destroy()

        self.canvas.create_image(0, 0, image = flash_frame, anchor = tk.NW)
        self.canvas.update_idletasks()
        self.window.update_idletasks()
        time.sleep(0.04)
        img = cv2.resize(self.img, (self.d_w, self.d_h), interpolation=cv2.INTER_NEAREST)
        frame = ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
        self.canvas.create_image(0, 0, image = frame, anchor = tk.NW)
        self.canvas.update_idletasks()
        self.window.update_idletasks()

        time.sleep(1.5)
        self.camera.__del__()
        self.window.destroy()
        return

    def update(self):

        elapsed = time.time() - self.start
        self.tqdm_loop.update()

        # 500ms before taking a picture, we flash
        if (elapsed > self.wait-self.flash_len/1000) and \
            self.flash_screen is None:
                self.flash_if_needed()

        if elapsed > self.wait:
            self.capture()
            return

        elapsed = str(int(self.wait - elapsed))

        font = cv2.FONT_HERSHEY_SIMPLEX
        success, img = self.camera.get_frame()
        img = np.array(img)
        if not self.no_flip: img = np.fliplr(img)
        self.img = img
        if success:
            frame = cv2.resize(img, (self.d_w, self.d_h),
                               interpolation = cv2.INTER_NEAREST)
            textsize = cv2.getTextSize(elapsed, font, 5, 5)[0]
            textX = (self.d_w - textsize[0]-50) // 2
            textY = (self.d_h + textsize[1]+65) // 2
            frame = cv2.putText(frame, elapsed,(textY,textX), 
                            font, 5,(255,255,255), 5, cv2.LINE_AA)
            cv2.waitKey(1)
            self.frame = ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.frame, anchor = tk.NW)

        self.window.after(30, self.update)

    def save(self):
        img = self.img[:,::-1]
        img = img[:,::-1,:]
        img = Image.fromarray(img)
        img.save(self.file)



class CaptureCamera():

    def __init__(self, video_source=0, focus=5, width=800, height=600):
        self.stream = cv2.VideoCapture(video_source, cv2.CAP_DSHOW,)
        self.stream.set(cv2.CAP_PROP_AUTOFOCUS, focus<0)
        if focus>=0:
            self.stream.set(cv2.CAP_PROP_FOCUS, focus)

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,height)

        if not self.stream.isOpened():
           raise ValueError("Unable to open video source", video_source)
        self.width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.read()
        self.stopped = False
        self.start()

    def get_frame(self):
        return self.success, self.frame

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def read(self):
        success, frame = self.stream.read()
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.success = success

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            self.read()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()
            
            
            
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