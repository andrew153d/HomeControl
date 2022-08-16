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
redValu = 0
grnValu = 0
bluValu = 0

# Define led pins as output

GPIO.setup(ledYlw, GPIO.OUT) 


# turn leds OFF 
GPIO.output(ledYlw, GPIO.LOW)

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

def getstr(input):
	msg = ''
	if int(input) < 10:
		msg+='0'
	if int(input) < 100:
		msg+='0'
	msg+=input
	return msg


@app.route('/data', methods = ['POST', 'GET'])
def data():
	global form_data
	msg = currentMode
	if request.method == 'GET':
		return f"The URL /data is accessed directly. Try going to '/form' to submit form"
	if request.method == 'POST':
		form_data = request.form
		red = form_data['red_field']
		msg += getstr(red)
		grn = form_data['grn_field']
		msg += getstr(grn)
		blu = form_data['blu_field']
		msg+= getstr(blu)
		mqtt_client.publish(MQTT_TOPIC, msg)




	templateData = {
		'mode':currentMode,
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
	global currentMode
	if deviceName == 'ledYlw':
		if action == 'on':
			GPIO.output(ledYlw, GPIO.HIGH)
		if action == 'off':
			GPIO.output(ledYlw, GPIO.LOW)
		mqtt_client.connect(MQTT_ADDRESS, 1883)
	if deviceName == 'switchMode':
		if currentMode == 'A':
			currentMode = 'B'
			mqtt_client.publish(MQTT_TOPIC, "B100000000")
		elif currentMode == 'B':
			currentMode = 'A'
			mqtt_client.publish(MQTT_TOPIC, "A000050100")
		else:
			currentMode = 'A'
	else:
		currentMode = 'A'

	ledYlwSts = GPIO.input(ledYlw)
	templateData = {
              'ledYlw'  : ledYlwSts,
              'mode'    : currentMode,
	}
	return render_template('index.html', **templateData)

def main():
    
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    #publish(mqtt_client)
    mqtt_client.loop()

if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)
