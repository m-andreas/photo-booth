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

class Booth
    def __init__(self):
        self.pins = [40, 38, 36, 32, 22, 18, 16, 11, 12, 07 ]
        self.images = []
        camera_setup()
        pin_setup()
        printer_setup()
        create_images()
        led_low()

    def camera_setup(self):
        self.camera = picamera.PiCamera(resolution = (480, 525), framerate= 30 )
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
        self.printers = conn.getPrinters()
        self.printer_name = printers.keys()[0]
        self.paper_count=18
        self.paper_left=paper_count

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(37, GPIO.IN)
        GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(31, GPIO.OUT)
        GPIO.output(31,GPIO.LOW)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        return

    def create_images
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

    def count_down(self):
        i=1
        image_number = 4
        for pin in reversed(self.pins):
            print i
            if i % 2 == 0:
                self.images[image_number].pack()
                if( image_number == 4 ):
                    self.images[0].pack_forget()
            else:
    	        self.images[image_number+1].pack_forget()
            image_number -= 1
            time.sleep(0.6)
            GPIO.output(pin,GPIO.LOW)
        	i += 1
        return

    def display_images():
        for image_number in range(1, 4):
            image = Image.open('photobooth_images/image'+ str(image_number) + '.jpg' )
            photo = ImageTk.PhotoImage(image)
            new_label = Label(image=photo)
            new_label.image = photo # keep a reference!
            new_label.pack()
            try:
                active_label.pack_forget()
            active_label = new_label
            sleep(10)
        active_label.pack_forget()

    def start_process():
        self.camera.stop_preview()
        self.camera.rotation = 0
        self.camera.resolution = (480, 525)
        sleep(2)
        self.camera.shutter_speed = camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        self.images[6].pack_forget()

    def stop_process():
        self.images[6].pack()
        self.camera.rotation = 90
        self.camera.start_preview()
        self.camera.exposure_mode = 'auto'
        self.camera.awb_mode = 'auto'

    def Reset_paper_count(pin):
        print "reset"
        if self.paper_left != self.paper_count:
            print "in"
            stop_process()
            self.images[7].pack_forget()
            GPIO.output(31,GPIO.LOW)
            self.taking_photo = False

    def printer_busy():
        printerqueuelength = len(self.conn.getJobs())
        if printerqueuelength >= 1:
            self.images[7].pack()
            self.conn.enablePrinter(self.printer_name)
            return True
        else:
            self.images[7].pack_forget()
            return False

    def Interrupt_event(pin):
        print "interupt"

        input_state = GPIO.input(37)
        input_state2 = GPIO.input(29) == False
        if ( input_state or input_state2 ) and self.paper_left > 0:
            if taking_photo:
                return
            else:
                self.taking_photo = True
        if printer_busy():
            self.taking_photo = False
                return
            led_high()
            start_process()
            for image_number in range(1,4):
                led_high()
                sleep(1)
                count_down()
                self.camera.capture('photobooth_images/image'+ str(image_number) + '.jpg' )
            self.images[0].pack_forget()
            self.images[5].pack()
            subprocess.call("sudo ./assemble_and_print", shell=True)
            self.images[5].pack_forget()
            display_images()
            self.paper_left -= 1
            if self.paper_left == 0:
                self.images[7].pack()
        else:
            stop_process()
            start = time.time()
        self.taking_photo = False

booth = Booth.new()
GPIO.add_event_detect(37, GPIO.BOTH, callback=booth.Interrupt_event)
GPIO.add_event_detect(29, GPIO.FALLING, callback=booth.Interrupt_event)
GPIO.add_event_detect(33, GPIO.FALLING, callback=booth.Reset_paper_count)

self.images[6].pack()
camera.start_preview()

master = Tk()
master.wm_attributes('-fullscreen', 'true')
master.bind("<Return>", lambda e: (
  GPIO.cleanup(),
  camera.stop_preview(),
  camera.close(),
  master.destroy()))

master.mainloop()
