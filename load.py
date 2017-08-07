# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import urllib
import signal
import logging
import json
import socket
import urllib2
from rgbmatrix import RGBMatrix


client = '29'
b = RGBMatrix(32,4)
b.brightness = 50

dev = True

##### MATRIX #####
width          = 128
height         = 32


##### IMAGE / COLORS / FONTS / OFFSET #####
image     = Image.new('RGB', (width, height))
draw      = ImageDraw.Draw(image)

orange    = (255, 100, 0)
green     = (0,   255, 0)
black     = (0,     0, 0)
red       = (255,   0, 0)
blue      = (0,     200, 255)

font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0
topOffset   = 3

lLabel = 'L '

lOffset = 4
minLabel = 'MIn'
minOffset = width - 6 - font.getsize(minLabel)[0]

count = True

slideLength = 10

pic = Image.open("emoji.gif")
pic = pic.convert('RGB')
pic.thumbnail((128,32), Image.ANTIALIAS)

weather = '74'
conditions = 'Mostly Sunny'
transition_time = 4

##### HANDLERS #####
def signal_handler(signal, frame):
    b.Clear()
    sys.exit(0)

def clearOnExit():
    b.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    b.SetImage(image, 0, 0)

def displayError():
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=font, fill=orange)
    b.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.CreateFrameCanvas()

while True:
    try:

        swap.Clear()
        swapImage = Image.new('RGB', (width, height))
        swapDraw  = ImageDraw.Draw(swapImage)
        swapDraw.text((2, 0), 'Fucking Loading...', font=font, fill=red)
        swap.SetImage(swapImage, 0, 0)
        time.sleep(transition_time)
        swap = b.SwapOnVSync(swap)

    except Exception as e:
        logging.exception("message")
        displayError()
        pass