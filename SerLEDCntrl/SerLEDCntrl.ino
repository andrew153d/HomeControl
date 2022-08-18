#include <FastLED.h>

#define LED_PIN     2
#define NUM_LEDS    125
#define BRIGHTNESS  255
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];
#define UPDATES_PER_SECOND 100


const unsigned int MAX_INPUT = 50;
int R = 0, G = 10, B = 0;
char currentMode = 'A';
int counter = 0;
 char data[14];
int LEDindex = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin (9600);
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(  BRIGHTNESS );
}

int readTime = 0;

void loop() {
  // put your main code here, to run repeatedly:
 int nowTime = millis();
  
  if(Serial.available()){
    char in = Serial.read();
    data[counter] = in;
    if(in == '\n'){
      Serial.print(data);
      Serial.println(counter);
      if(counter == 10){
        currentMode = data[0];
        R = (data[1]-'0')*100+(data[2]-'0')*10+(data[3]-'0');
        G = (data[4]-'0')*100+(data[5]-'0')*10+(data[6]-'0');
        B = (data[7]-'0')*100+(data[8]-'0')*10+(data[9]-'0');
       // Serial.println(data);
       Serial.print (" R: ");
       Serial.print(R);
       Serial.print(" G: ");
       Serial.print(G);
       Serial.print(" B: ");
       Serial.println(B);
      }
      counter = 0;
      
    
    }else{
      counter++;
    }
    readTime = nowTime;
  }

  if(nowTime>readTime+400){
    switch(currentMode){
      case 'A':
        for( int i = 0; i < NUM_LEDS; i++) {
          leds[i] = CRGB(R, G, B);
        }
      break;
      case 'B':
        leds[LEDindex] = CRGB(0, 0, 0);
        LEDindex++;
        LEDindex%=NUM_LEDS;
        leds[LEDindex] = CRGB(R, G, B);
        delay(100);
      break;
    }
    FastLED.show();
  }

  
}
