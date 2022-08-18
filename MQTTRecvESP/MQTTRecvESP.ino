#include "PubSubClient.h"
#include "ESP8266WiFi.h"
#define UPDATES_PER_SECOND 100

//#define DEBUG //uncomment to print out debug statements
const char* ssid = "GrowWifi";
const char* wifi_password = "T4*15KpHi1bj";

// MQTT
const char* mqtt_server = "192.168.12.218";  // IP of the MQTT broker
const char* test_topic = "home/office/test";
const char* mqtt_username = "cdavid"; // MQTT username
const char* mqtt_password = "cdavid"; // MQTT password
const char* clientID = "client_test"; // MQTT client ID
bool state = 0;

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
  digitalWrite(LED_BUILTIN, state);
  state = !state;
  }

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
PubSubClient client(mqtt_server, 1883, callback, wifiClient); 

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
  connect_MQTT();
  Serial.setTimeout(500);
  if(!client.subscribe(test_topic)){
    #ifdef DEBUG
    Serial.println("ERR: subscription Failed");
    #endif
  }
   //for( int i = 0; i < NUM_LEDS; i++) {
   //     leds[i] = CRGB(100, 10, 10);
   //}
  // FastLED.show();
   //FastLED.delay(1000 / UPDATES_PER_SECOND);

  
  client.loop();
  delay(100);
}
