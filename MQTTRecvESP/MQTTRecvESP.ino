#include "PubSubClient.h"
#include "ESP8266WiFi.h"
#define UPDATES_PER_SECOND 100

//#define DEBUG //uncomment to print out debug statements
const char* ssid = "GrowWifi";
const char* wifi_password = "T4*15KpHi1bj";

// MQTT
const char* mqtt_server = "192.168.12.217";  // IP of the MQTT broker
const char* test_topic = "home/office/test";
const char* mqtt_username = "cdavid"; // MQTT username
const char* mqtt_password = "cdavid"; // MQTT password
const char* clientID = "ESPclient"; // MQTT client ID
bool state = 0;
int nowTime;
int lastMsgTime;

void callback(char* topic, byte* payload, unsigned int length) {
  for(int i = 0; i<length; i++){
    Serial.print((char)payload[i]);
  }
  Serial.print('\n');
  #ifdef DEBUG
  Serial.println("");
  Serial.print("recvd Data: ");
 
  for(int i = 0; i<length; i++){
    Serial.print((char)payload[i]);
  }
  
  Serial.print(" length: ");
  Serial.println(length);
  #endif
  digitalWrite(LED_BUILTIN, LOW);
  //state = !state;
  lastMsgTime = nowTime;
  }
  
// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
PubSubClient client(mqtt_server, 1883, callback, wifiClient); 


void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    // Attempt to connect
    if (client.connect(clientID, mqtt_username, mqtt_password)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe(test_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 5 seconds before retrying
      delay(2000);
    }
  }
}





void WifiConnect(){
  #ifdef DEBUG
  Serial.print("Connecting to ");
  Serial.println(ssid);
  #endif

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    #ifdef DEBUG
    Serial.print(".");
    #endif
  }

  #ifdef DEBUG
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  #endif
}

// Custom function to connet to the MQTT broker via WiFi
void connect_MQTT(){
  if(client.connected()){
    return;
  }

  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  // If the connection is failing, make sure you are using the correct MQTT Username and Password (Setup Earlier in the Instructable)
  if (client.connect(clientID, mqtt_username, mqtt_password)) {
    #ifdef DEBUG
    Serial.println("Connected to MQTT Broker!");
    #endif
  }
  else {
    #ifdef DEBUG
    Serial.println("Connection to MQTT Broker failed...");
    #endif
  }
}


void setup() {
  Serial.begin(9600);
  WifiConnect();
  //FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  // FastLED.setBrightness(  BRIGHTNESS );
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  nowTime = millis();

  if(nowTime>lastMsgTime+100){
    digitalWrite(LED_BUILTIN, HIGH);
  }
  
  //connect_MQTT();
  if (!client.connected()) {
    reconnect();
  }
  if(!client.subscribe(test_topic)){
    #ifdef DEBUG
    Serial.println("ERR: subscription Failed");
    #endif
  }
  client.loop();
}
