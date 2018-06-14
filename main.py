import picamera
import cups
import os
from time import sleep
import RPi.GPIO as GPIO, time, os, subprocess
from subprocess import Popen
import time
from Tkinter import *
import sys
from PIL import Image, ImageTk

class Booth(object):
    def __init__(self):
        print "init"
        self.pins = [40, 38, 36, 32, 22, 18, 16, 11, 12, 07 ]
        self.images = []
        self.create_images()
        self.camera_setup()
        self.pin_setup()
        self.printer_setup()
        self.led_low()

    def camera_setup(self):
        self.camera = picamera.PiCamera(resolution = (900, 1100), framerate= 30 )
        self.camera.rotation = 90
        self.camera.brightness = 55
        self.camera.shutter_speed = 7000
        self.camera.iso = 800
        self.camera.saturation = 30
        self.taking_photo=False
        self.camera.preview_fullscreen=False
        self.camera.preview_window=(160, 0, 480, 525)
        #camera.image_effect="washedout"

    def printer_setup(self):
        self.conn = cups.Connection()
        self.printers = self.conn.getPrinters()
        self.printer_name = self.printers.keys()[0]
        self.paper_count = 18
        self.paper_left = self.paper_count

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(37, GPIO.IN)
        GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(31, GPIO.OUT)
        GPIO.output(31,GPIO.LOW)
        for pin in self.pins:
            print pin
            GPIO.setup(pin, GPIO.OUT)
        return

    def create_images(self):
        for number in range(1,9):
            print number
            image = Image.open('countdown/' + str(number) + '.png')
            photo = ImageTk.PhotoImage(image)
            label = Label(image=photo)
            label.image = photo # keep a reference!
            self.images.append(label)

    def led_high(self):
        for pin in self.pins:
            GPIO.output(pin,GPIO.HIGH)
        return

    def led_low(self):
        for pin in self.pins:
            GPIO.output(pin,GPIO.LOW)
        return

    def count_down(self, photo_count):
            
        i=1
        image_number = 4
        for pin in reversed(self.pins):
            if i % 2 == 0:
                self.images[image_number].pack()
                if( image_number == 4 ):
                    if photo_count == 1 :
                        self.images[6].pack_forget()
                    self.images[0].pack_forget()
                else:
                    self.images[image_number+1].pack_forget()   	        
                image_number -= 1
            time.sleep(0.6)
            GPIO.output(pin,GPIO.LOW)
            i += 1
        return

    def display_images(self):
        for image_number in range(1, 4):
            image = Image.open('photobooth_images_turned/image'+ str(image_number) + '.jpg' )
            image = image.resize((800,480), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            new_label = Label(image=photo)
            new_label.image = photo # keep a reference!
            new_label.pack(fill=BOTH, expand=1)
            if image_number == 1:
                self.images[5].pack_forget()
            else:
                active_label.pack_forget()
            active_label = new_label
            sleep(10)
        active_label.pack_forget()

    def start_process(self):
        self.camera.stop_preview()
        self.camera.rotation = 0
        self.camera.resolution = (900, 1100)
        sleep(2)
        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g

    def stop_process(self):
        self.images[6].pack()
        self.camera.rotation = 90
        self.camera.start_preview()
        self.camera.exposure_mode = 'auto'
        self.camera.awb_mode = 'auto'

    def reset_paper_count(self):
        print "reset"
        if self.paper_left != self.paper_count:
            print "in"
            self.stop_process()
            self.images[7].pack_forget()
            GPIO.output(31,GPIO.LOW)
            self.taking_photo = False

    def printer_busy(self):
        printerqueuelength = len(self.conn.getJobs())
        if printerqueuelength >= 1:
            self.images[7].pack()
            self.conn.enablePrinter(self.printer_name)
            return True
        else:
            self.images[7].pack_forget()
            return False

def interrupt_event(pin):
    global booth
    print "interupt"
    print GPIO.input(37)
    print GPIO.input(29)
    input_state = GPIO.input(37)
    input_state2 = GPIO.input(29) == False
    if ( input_state or input_state2 ) and booth.paper_left > 0:
        if booth.taking_photo:
            return
        else:
            booth.taking_photo = True
        if booth.printer_busy():
            booth.taking_photo = False
            return
        else:
            booth.led_high()
            booth.start_process()
            for image_number in range(1,4):
                booth.led_high()
                sleep(1)
                booth.count_down(1)
                booth.camera.capture('photobooth_images/image'+ str(image_number) + '.jpg' )

            booth.images[0].pack_forget()
            booth.images[5].pack()
            subprocess.call("sudo ./assemble_and_print&", shell=True)
            subprocess.call("sudo ./turn_images", shell=True)
            booth.display_images()
            booth.paper_left -= 1
            if booth.paper_left == 0:
                booth.images[7].pack()
            else:
                booth.stop_process()
        booth.taking_photo = False

master = Tk()
master.wm_attributes('-fullscreen', 'true')

global booth
booth = Booth()

master.bind("<Return>", lambda e: (
  GPIO.cleanup(),
  booth.camera.stop_preview(),
  booth.camera.close(),
  master.destroy()))

GPIO.add_event_detect(37, GPIO.FALLING, callback=interrupt_event)
GPIO.add_event_detect(29, GPIO.FALLING, callback=interrupt_event)
GPIO.add_event_detect(33, GPIO.FALLING, callback=booth.reset_paper_count)
booth.images[6].pack()
booth.camera.start_preview()

master.mainloop()
