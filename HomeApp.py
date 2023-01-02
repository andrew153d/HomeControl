import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
from flask import Flask, render_template, request
from werkzeug.exceptions import BadRequestKeyError
import psutil

MQTT_ADDRESS = '192.168.12.217'
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = 'home/office/deskLights'
MQTT_IF_TOPIC = 'home/internet_fan'


app = Flask(__name__)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


currentMode = 'A'
cpu_load = '0'
redValu = '0'
grnValu = '0'
bluValu = '0'

connSts = "Disconnected"
powerSts = "OFF"



mqtt_client = mqtt.Client()

form_data = {
'field' : 'field_value',
'mode'      : currentMode,
}

templateData = {

		'mode':currentMode,
		'redValu':redValu,
		'grnValu':grnValu,
		'bluValu':bluValu,
		'powerSts':powerSts,
		'connSts':connSts,
		'cpu_load':cpu_load,
		
	}

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe(MQTT_IF_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))

def sendColors():
	global powerSts
	
		
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

	msg = currentMode
	msg+=getStr(redValu)
	msg+=getStr(grnValu)
	msg+=getStr(bluValu)
	print(powerSts)
	if(powerSts == "OFF"):
		mqtt_client.publish(MQTT_TOPIC, 'A000000000')
	else:
		mqtt_client.publish(MQTT_TOPIC, msg)
	
	mqtt_client.loop_stop()

@app.route('/data/<color>', methods = ['POST'])
def handleColorInput(color):
	return('', 200)

@app.route('/data/<color>', methods = ['GET'])
def data(color):
	global form_data
	global templateData
	global redValu
	global grnValu
	global bluValu
	global connSts
	global powerSts
	global currentMode
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
	return render_template('index.html',**templateData)

def get_template():
	global currentMode
	global redValu
	global grnValu
	global bluValu
	global powerSts
	global connSts
	global cpu_load
	templateData = {

		'mode':currentMode,
		'redValu':redValu,
		'grnValu':grnValu,
		'bluValu':bluValu,
		'powerSts':powerSts,
		'connSts':connSts,
		'cpu_load':cpu_load,
		
	}
	return templateData

def extractColor(form_data):
	global redValu
	global grnValu
	global bluValu
	# for key in form_data.keys():
	#	print(key)
	# first = next(iter(form_data))
	# Get the first key-value pair from the dictionary
	try:
		first_pair = next(iter(form_data))
		if   first_pair == 'rfield':
			redValu = form_data['rfield']
		elif first_pair == 'gfield':
			grnValu = form_data['gfield']
		elif first_pair == 'bfield':
			bluValu = form_data['bfield']
		sendColors()
	except(StopIteration):
		pass


@app.route("/", methods = ['POST', 'GET'])
def index():
	extractColor(request.form)
	
	template_data = get_template()
	return render_template('index.html', **template_data)
	
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	global form_data
	global templateData
	global redValu
	global grnValu
	global bluValu
	global connSts
	global powerSts
	global currentMode

	if deviceName == 'connSts':
		if action == 'conn':
			if connSts == "Disconnected":
				connSts = "Connected"
				mqtt_client.connect(MQTT_ADDRESS, 1883)
			elif connSts == "Connected":
				connSts = "Disconnected"
	if deviceName == 'powerSts':
		if action == 'toggle':
			if powerSts == "ON":
				powerSts = "OFF"
			elif powerSts == "OFF":
				powerSts = "ON"
			sendColors()
	if deviceName == 'switchMode':
		currentMode = chr(ord(currentMode)+1)
		if currentMode == 'G':
			currentMode = 'A'
		sendColors()
	template_data = get_template()
	return render_template('index.html', **template_data)

def main():
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)
