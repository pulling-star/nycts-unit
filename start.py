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
import json_log_formatter
import socket
import urllib2
from base import base


##### CLIENT CONFIGURATION #####
client = '29'
b = base(client)

### LOGGING ###
formatter = json_log_formatter.JSONFormatter()

json_handler = logging.FileHandler(filename='./device_logs/logs.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger('log')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)
logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})

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


##### HANDLERS #####
def signal_handler(signal, frame):
    b.matrix.Clear()
    sys.exit(0)

def clearOnExit():
    b.matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    b.matrix.SetImage(image, 0, 0)

def displayError(e):
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), e, font=font, fill=orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.matrix.CreateFrameCanvas()


weather_offline_data = {'weather': 75, 'conditions': 'SUNNY'}

while True:

    ##### NODE API #####
    config = json.loads('{}')
    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
        logger.info(extra={'status': 1, 'job': 'api_config'})
    except urllib2.URLError as e:
        logger.info(extra={'status': 0, 'job': 'api_config'})
    else:
        config = json.loads(result.read())

    ##### DEV MODE #####
    dev = config["dev"]

    if config["reboot"] == "1":
        baseurl = "http://127.0.0.1:3000/setConfig/reboot/0"
        try:
            result = urllib2.urlopen(baseurl)
            logger.info(extra={'status': 1, 'job': 'api_reboot'})
        except urllib2.URLError as e:
            error_message = e.reason
            logger.info(extra={'status': 0, 'job': 'api_reboot'})
        else:
            config = json.loads(result.read())
            os.system('reboot now')


    transition_time = int(config["transition_time"])
    b.matrix.brightness = int(config["brightness"])

    ##### BOOT SCREEN #####
    try:
        swap.Clear()
        swapImage = Image.new('RGB', (width, height))
        swapDraw  = ImageDraw.Draw(swapImage)
        if dev == True:
            ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
            swapDraw.text((2, 0), 'IP: ' + ip , font=font, fill=red)
        else:
            swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=font, fill=red)
            swapDraw.text((68, 0), ' legit. realtime.'  , font=font, fill=green)
            swapDraw.text((2, 16), '@' , font=font, fill=green)
            swapDraw.text((12, 16), 'n y c t r a i n s i g n' , font=font, fill=orange)
        swap.SetImage(swapImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)


        swap.Clear()
        textImage = Image.new('RGB', (width, height))
        textDraw  = ImageDraw.Draw(textImage)
        textDraw.text((2, 0), config["text_line_1"] , font=font, fill=red)
        textDraw.text((2, 16), config["text_line_2"] , font=font, fill=blue)
        swap.SetImage(textImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)


    ##### WEATHER SCREEN #####
        swap.Clear()

        logger.info('Loading weather screen', extra={'screen': 'weather_screen'})

        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text='"+ str(config["weather_zip"]) + "')"
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        try:
            result = urllib2.urlopen(yql_url)

        except urllib2.URLError as e:
            error_message = e.reason
            logger.info(extra={'status': 0, 'job': 'weather_screen'})
            weather = weather_offline_data['weather']
            conditions = weather_offline_data['conditions']
        else:
            data = json.loads(result.read())
            weather = data['query']['results']['channel']['item']['condition']['temp']
            conditions = data['query']['results']['channel']['item']['condition']['text'].upper()

            weather_offline_data['weather'] = weather
            weather_offline_data['conditions'] = conditions

        weatherImage = Image.new('RGB', (width, height))
        weatherDraw  = ImageDraw.Draw(weatherImage)

        weatherDraw.text((2, 0), 'IT IS ' + weather + ' FUCKING DEGREES' , font=font, fill=red)
        weatherDraw.text((2, 16), '& ' + conditions + ' OUTSIDE', font=font, fill=green)

        swap.SetImage(weatherImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

    ##### TRAIN SCREEN #####
        swap.Clear()

        count = not count

        if count == True:
            frame = 'ln'
        else :
            frame ='ls'

        if frame == 'ln':
            dirLabel = '    MANHATTAN '
            dirOffset = 22
        if frame == 'ls':
            dirLabel = '   ROCKAWAY PKWY'
            dirOffset = 12

        try:
            connection = urllib.urlopen('http://riotpros.com/mta/v1/?client=' + client)
            logger.info(extra={'status': 1, 'job': 'train_screen'})

        except urllib2.URLError as e:
            error_message = e.reason
            logger.info(extra={'status': 0, 'job': 'train_screen'})
        else:
            raw = connection.read()
            times = raw.split()
            connection.close()

        if len(times) > 3:
            try:
                val = int(times[0])
            except ValueError:
                min1 = '*'
                min2 = '*'

            if frame == 'ln':
                min1 = times[0]
                min2 = times[1]

            if frame == 'ls':
                min1 = times[2]
                min2 = times[3]
        else:
            min1 = '*'
            min2 = '*'

        if len(min1) < 2:
            min1 = min1.rjust(3)
        time1Offset = minOffset - font.getsize(min1)[0]

        if len(min2) < 2:
            min2 = min2.rjust(3)
        time2Offset = minOffset - font.getsize(min2)[0]

        dirLabelw = font.getsize(dirLabel)[0]
        draw.rectangle((0, 0, width, height), fill=black)
        draw.text((lOffset, 0 + topOffset), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 0 + topOffset), dirLabel, font=font, fill=green)
        draw.text((time1Offset, 0 + topOffset), min1, font=font, fill=orange)
        draw.text((minOffset, 0 + topOffset), minLabel, font=font, fill=green)

        draw.text((lOffset, 16), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 16), dirLabel, font=font, fill=green)
        draw.text((time2Offset, 16), min2, font=font, fill=orange)
        draw.text((minOffset, 16), minLabel, font=font, fill=green)

        draw.point((width - 12, 7), fill=black)
        draw.point((width - 12, 20), fill=black)

        swap.SetImage(image, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

        swap.Clear()
        swap.SetImage(pic.convert('RGB'), 0, 0)

        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

##### EXCEPTION SCREEN #####
    except Exception as e:
        logging.exception("message")
        error_message = e.reason
        logger.info(extra={'status': 0, 'job': 'boot_screen'})
        displayError()
        pass
