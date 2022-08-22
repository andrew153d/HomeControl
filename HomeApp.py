import paho.mqtt.client as mqtt
import time

import RPi.GPIO as GPIO

from flask import Flask, render_template, request


MQTT_ADDRESS = '192.168.12.218'
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = 'home/office/test'


app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define actuators GPIOs
ledYlw = 26
currentMode = 'A'


#initialize GPIO status variables
ledYlwSts = 0

redValu = '0'
grnValu = '0'
bluValu = '0'

connSts = "Disconnected"
powerSts = "OFF"

# Define led pins as output

GPIO.setup(ledYlw, GPIO.OUT) 


# turn leds OFF 
GPIO.output(ledYlw, GPIO.HIGH)
time.sleep(1);
GPIO.output(ledYlw, GPIO.LOW);

mqtt_client = mqtt.Client()
form_data = {
'field' : 'field_value',
'mode'      : currentMode,
}


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))

def sendColors():
	mqtt_client.connect(MQTT_ADDRESS, 1883)
	mqtt_client.loop_start()
	mqtt_client.subscribe(MQTT_TOPIC)
	
	def getStr(input):
		msg = ''
		if int(input) < 10:
			msg+='0'
		if int(input) < 100:
			msg+='0'
		msg+=input
		return msg

	global redValu
	global grnValu
	global bluValu
	global currentMode
	msg = currentMode
	msg+=getStr(redValu)
	msg+=getStr(grnValu)
	msg+=getStr(bluValu)
	mqtt_client.publish(MQTT_TOPIC, msg)
	mqtt_client.loop_stop()

@app.route('/data/<color>', methods = ['POST', 'GET'])
def data(color):
	global form_data
	global powerSts
	global connStatus
	global redValu
	global grnValu
	global bluValu
	msg = currentMode
	if request.method == 'GET':
		return f"The URL /data is accessed directly. Try going to '/form' to submit form"
	if request.method == 'POST':
		form_data = request.form
		if color == 'red':
			redValu = form_data['field']
		if color == 'grn':
			grnValu = form_data['field']
		if color == 'blu':
			bluValu = form_data['field']

		sendColors()
	templateData = {
		'mode':currentMode,
		'redValu':redValu,
		'grnValu':grnValu,
		'bluValu':bluValu,
		'powerSts':powerSts,
		'connSts':connSts,
		
	}
	return render_template('index.html',**templateData)

@app.route("/")
def index():
	# Read Sensors Status
	ledYlwSts = GPIO.input(ledYlw)
	templateData = {
              'ledYlw'  : ledYlwSts,
              'mode'    : currentMode,
        }
	return render_template('index.html', **templateData)
	
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	global redValu
	global grnValu
	global bluValu
	global currentMode
	global powerSts
	global connSts
	if deviceName == 'connSts':
		if action == 'conn':
			if connSts == "Disconnected":
				connSts = "Connected"
				mqtt_client.connect(MQTT_ADDRESS, 1883)
				GPIO.output(ledYlw, GPIO.HIGH)
			elif connSts == "Connected":
				connSts = "Disconnected"
				GPIO.output(ledYlw, GPIO.LOW)
			print(connSts == "Disconnected")
	if deviceName == 'powerSts':
		if action == 'toggle':
			if powerSts == "ON":
				powerSts = "OFF"
				redValu = '0'
				grnValu = '0'
				bluValu = '0'
				sendColors()
			elif powerSts == "OFF":
				powerSts = "ON"
	if deviceName == 'switchMode':
		currentMode = chr(ord(currentMode)+1)
		if currentMode == 'G':
			currentMode = 'A'
		sendColors()

	ledYlwSts = GPIO.input(ledYlw)
	templateData = {
              'ledYlw'  : ledYlwSts,
              'mode'    : currentMode,
              'redValu' : redValu,
              'grnValu' : grnValu,
              'bluValu' : bluValu,
              'connSts' : connSts,
              'powerSts': powerSts,
	}
	return render_template('index.html', **templateData)

def main():
    
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    print("Running")

if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)
