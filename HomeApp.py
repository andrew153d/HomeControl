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
MQTT_CLIENTS = '$SYS/broker/clients/total'


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
num_connected_devices = 1


mqtt_client = mqtt.Client("pi")
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Define a message callback function
def on_message(client, userdata, message):
	global num_connected_devices
	topic = message.topic
	payload = message.payload.decode()
	print("Received message on topic '{}': {}".format(topic, payload))
	if (topic == MQTT_CLIENTS):
		num_connected_devices = payload



mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_ADDRESS, 1883)

mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.subscribe(MQTT_CLIENTS)

mqtt_client.loop_start()

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



def sendColors():
	global powerSts
	
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

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = float(f.read()) / 1000
    return temp

def get_template():
	global currentMode
	global redValu
	global grnValu
	global bluValu
	global powerSts
	global connSts
	global num_connected_devices
	cpu_temp = get_cpu_temp()
	cpu_load = psutil.cpu_percent()
	templateData = {

		'mode':currentMode,
		'redValu':redValu,
		'grnValu':grnValu,
		'bluValu':bluValu,
		'powerSts':powerSts,
		'connSts':connSts,
		'cpu_load':str(cpu_load)+'%',
		'cpu_temp':str(round(cpu_temp))+chr(176)+'C',
		'num_conn_dev': num_connected_devices,
		
	}
	return templateData

def extractName(form_data):

	try:
		output =  next(iter(form_data))
	except(StopIteration):
		output = ''
	return output

def handleColor(form_data):
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

def handlePresets(form_data):
	global redValu
	global grnValu
	global bluValu
	preset = form_data['light']
	print(preset)
	if(preset == 'optionA'):
		redValu = '100'
		grnValu = '100'
		bluValu = '100'
	elif(preset == 'optionB'):
		redValu = '0'
		grnValu = '255'
		bluValu = '255'
	elif(preset == 'optionC'):
		redValu = '30'
		grnValu = '255'
		bluValu = '30'
	elif(preset == 'optionD'):
		redValu = '255'
		grnValu = '0'
		bluValu = '255'
	sendColors()


@app.route("/", methods = ['POST', 'GET'])
def index():
	name = extractName(request.form)
	print(name)
	if (name == 'rfield' or name == 'gfield' or name == 'bfield'):
		handleColor(request.form)
	elif(name == 'light'):
		handlePresets(request.form)	
	
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
   pass 

if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)
