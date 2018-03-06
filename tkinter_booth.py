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


def camera_setup():
    global camera
    camera = picamera.PiCamera(resolution = (480, 525), framerate= 30 )
    camera.rotation = 90
    camera.brightness = 55
    camera.shutter_speed = 7000
    camera.iso = 800
    camera.saturation = 30
    #camera.image_effect="washedout"

def printer_setup():
    global conn
    global printer_name
    conn = cups.Connection()
    printers = conn.getPrinters()
    printer_name = printers.keys()[0]

def pin_setup(pins):
    GPIO.setup(37, GPIO.IN)
    GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(31, GPIO.OUT)  
    GPIO.output(31,GPIO.LOW)
    for pin in pins:   
        GPIO.setup(pin, GPIO.OUT)  
    return

def setup(pins):
    camera_setup()
    pin_setup(pins)

def led_high(pins):
    for pin in pins:   
        GPIO.output(pin,GPIO.HIGH)  
    return

def led_low(pins):
    for pin in pins:   
        GPIO.output(pin,GPIO.LOW)  
    return

def count_down(pins):
    global images
    i=1
    image_number = 4
    for pin in reversed(pins): 
        print i       
        if i % 2 == 0:
          images[image_number].pack()
          if( image_number == 4 ):
	    images[0].pack_forget()
          else:
	    images[image_number+1].pack_forget()
          image_number -= 1
        time.sleep(0.6)
        GPIO.output(pin,GPIO.LOW)
    	i += 1
    return

def display_images():
  for image_number in range(1, 4): 
    image = Image.open('/home/pi/Desktop/photobooth_images/image'+ str(image_number) + '.jpg' )
    photo = ImageTk.PhotoImage(image)
    label = Label(image=photo)
    label.image = photo # keep a reference!
    label.pack()
    sleep(10) 
    label.pack_forget()

def start_process():
    global camera
    global images;
    camera.stop_preview()
    camera.rotation = 0
    camera.resolution = (480, 525)
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    images[6].pack_forget()
    return camera

def stop_process():
    global images;
    global camera
    images[6].pack()
    camera.rotation = 90
    camera.start_preview()
    camera.exposure_mode = 'auto'
    camera.awb_mode = 'auto'
    return camera

def single_nightrider(pins):
	for item_counter in range(len(pins) + 4): 
   	 	input_state = GPIO.input(37)
    		if input_state == True:
			return
		start_value = item_counter - 4
                for item_number in range(start_value ,start_value + 4):
        		if item_number >= 0 and item_number < len(pins):
				GPIO.output(pins[item_number],GPIO.HIGH)
        	sleep(0.15)	
		led_low(pins)

def nightrider(pins):
    for _ in range(5):
    	single_nightrider(pins)
	input_state = GPIO.input(37)
    	if input_state == True:
		return
	sleep(0.4)
	single_nightrider(pins[::-1])
	input_state = GPIO.input(37)
	if input_state == True:
		return
	sleep(0.4)
    return   

def Reset_paper_count(pin):
    print "reset"
    global paper_count
    global images
    global paper_left
    if paper_left != paper_count:
      print "in"
      global taking_photo
      paper_left=paper_count
      stop_process()
      images[7].pack_forget()
      start = time.time()
      GPIO.output(31,GPIO.LOW)
      taking_photo = False

#GPIO.cleanup()   
pins = [40, 38, 36, 32, 22, 18, 16, 11, 12, 07 ]   
printer_setup()
taking_photo=False
GPIO.setmode(GPIO.BOARD)
setup(pins)
led_low(pins)
camera.preview_fullscreen=False
camera.preview_window=(160, 0, 480, 525)
camera.start_preview()

start = time.time()

pad=3
master = Tk()
paper_count=18
paper_left=paper_count
master.wm_attributes('-fullscreen', 'true')
images = []
for number in range(1,9): 
  print number
  image = Image.open('countdown/' + str(number) + '.png')
  photo = ImageTk.PhotoImage(image)
  label = Label(image=photo)
  label.image = photo # keep a reference!
  images.append(label)
images[6].pack()
#Reset_paper_count(31)

def printer_busy():
    global printer_name
    global conn
    global images
    printerqueuelength = len(conn.getJobs())
    print conn
    print printer_name
    print printerqueuelength
    if  printerqueuelength >= 1:
        images[7].pack()
        conn.enablePrinter(printer_name)
        return True
    else:
        images[7].pack_forget()
        return False

def Interrupt_event(pin):
    print "interupt"
    global taking_photo
    global camera
    global paper_left
    global images

    input_state = GPIO.input(37)
    input_state2 = GPIO.input(29) == False
    if ( input_state or input_state2 ) and paper_left > 0:
        print taking_photo
        if taking_photo:
          return
        else:
          taking_photo = True
	if printer_busy():
	  taking_photo = False
          return
        led_high(pins)
        #Popen("omxplayer -r /home/pi/Desktop/CountdownTimer.mp4", shell=True)
        camera = start_process()
        for image_number in range(1,4):
	    led_high(pins)
            sleep(1)
            count_down(pins)
            camera.capture('/home/pi/Desktop/photobooth_images/image'+ str(image_number) + '.jpg' )
        images[0].pack_forget()
	images[5].pack()
        subprocess.call("sudo assemble_and_print", shell=True)
        #os.system("rm /home/pi/Desktop/temp*")
        images[5].pack_forget()
        display_images()
        paper_left -= 1
        if paper_left == 0:
		images[7].pack()
                #GPIO.output(31,GPIO.HIGH)
	else:        
        	stop_process()
		start = time.time()
	taking_photo = False

GPIO.add_event_detect(37, GPIO.BOTH, callback=Interrupt_event)
GPIO.add_event_detect(29, GPIO.FALLING, callback=Interrupt_event)
GPIO.add_event_detect(33, GPIO.FALLING, callback=Reset_paper_count)


master.bind("<Return>", lambda e: (
  GPIO.cleanup(),
  camera.stop_preview(),
  camera.close(),
  master.destroy()))



master.mainloop()
