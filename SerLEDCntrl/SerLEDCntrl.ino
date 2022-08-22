#include <FastLED.h>

#define LED_PIN     2
#define NUM_LEDS    89
#define BRIGHTNESS  255
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];
#define UPDATES_PER_SECOND 100

class RGBcolor{
  public:
  int R;
  int G;
  int B;
  RGBcolor(){
    R = 0;
    G = 30;
    B = 0;
  }
};

class HSVcolor{
  public:
  int H;
  int S;
  int V;
  HSVcolor(){
    H = 100;
    S = 0;
    V = 0;
  }
};

const unsigned int MAX_INPUT = 50;

RGBcolor rgb;
HSVcolor hsv;

char currentMode = 'B';
int counter = 0;
 char data[14];
int LEDindex = 0;
CHSV color[NUM_LEDS];
int widthIndex = 20;

int Lindex;
int Rindex;


double max_element(RGBcolor in){
  double a = (double)max(in.R, in.G);
  return (double)max(a, in.B);
}

double min_element(RGBcolor in){
  double a = (double)min(in.R, in.G);
  return (double)min(a, in.B);
}

HSVcolor getHSV(RGBcolor in){
    double hue, sat;
  
    double maxval, minval;
    
    maxval=max_element(in);
    
    minval=min_element(in);
    //Serial.print("max: ");
    //Serial.println(maxval);
    //Serial.print("min: ");
    //Serial.println(minval);
    double difference=maxval-minval;
    
    double red, green, blue;
    red=   (double)in.R;
    green= (double)in.G;
    blue=  (double)in.B; 
    
    HSVcolor out;
    
    if(difference==0)
    hue=0;
    else if(red==maxval)
    hue= fmod(((60*((green-blue)/difference))+360), 360.0);
    else if(green=maxval)
    hue= fmod(((60*((blue-red)/difference))+120), 360.0);
    else if(blue=maxval)
    hue= fmod(((60*((red-green)/difference))+240), 360.0);
    
    out.H = (int)(hue);
    
    
    if(maxval==0)
    sat=0;
    else
    sat=100*(difference/maxval);

    
    out.S = (int)(sat);
    
    out.V = (int)(maxval);

    //Serial.print (" H: ");
    //Serial.print(out.H);
    //Serial.print(" S: ");
    //Serial.print(out.S);
    //Serial.print(" V: ");
    //Serial.println(out.V);
    return out;
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin (9600);
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(  BRIGHTNESS );
  Serial.println("starting");
  randomSeed(10);
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
      //Serial.println(counter);
      if(counter == 10){
        currentMode = data[0];
        rgb.R = (data[1]-'0')*100+(data[2]-'0')*10+(data[3]-'0');
        rgb.G = (data[4]-'0')*100+(data[5]-'0')*10+(data[6]-'0');
        rgb.B = (data[7]-'0')*100+(data[8]-'0')*10+(data[9]-'0');
       // Serial.println(data);
       Serial.print("mode: ");
       Serial.println(currentMode);
       //Serial.print (" R: ");
       //Serial.print(rgb.R);
       //Serial.print(" G: ");
      // Serial.print(rgb.G);
       //Serial.print(" B: ");
       //Serial.println(rgb.B);
       hsv = getHSV(rgb);
       switch(currentMode){
        case 'D':
          Lindex = 60;
          Rindex = 61;
        break;
       }
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
        //for( int i = 0; i < NUM_LEDS; i++) {
        //  leds[i] = CRGB(rgb.R, rgb.G, rgb.B);
        //}
        fill_solid(leds, NUM_LEDS, CRGB(rgb.R, rgb.G, rgb.B));
      break;
      case 'B':
          for(int i = 0; i<=9; i++){
           leds[(LEDindex + i)%NUM_LEDS] = CRGB(0, 0, 0);
          }
          //leds[LEDindex] = CRGB(0, 0, 0);
          LEDindex++;
          LEDindex%=NUM_LEDS;
          for(int i = 0; i<=9; i++){
            leds[(LEDindex + i)%NUM_LEDS] = CRGB(rgb.R, rgb.G, rgb.B);
          }
          //leds[LEDindex] = CRGB(rgb.R, rgb.G, rgb.B);
          delay(40);
      break;
      
      case 'C':
        fill_rainbow(leds, NUM_LEDS, LEDindex, 1);
        LEDindex++;
        LEDindex%=255;
        delay(100);
      break;  
      case 'D':
      //LEDindex = 2;
      //index = random(0, NUM_LEDS);  
      hsv.H = 125;
      Lindex--;
      if(Lindex<0){
        Lindex = NUM_LEDS-1;
      }
      if(Lindex == Rindex){
        Serial.println(" ---------equals---------");
        hsv.H+=40;
        hsv.H = hsv.H%255;
      }
      Rindex++;
      Rindex%=NUM_LEDS;
      if(Lindex == Rindex){
        Serial.println(" ---------equals---------");
        hsv.H+=20;
        hsv.H = hsv.H%255;
      }
      leds[Lindex] = CHSV(hsv.H, 255, 255);
      leds[Rindex] = CHSV(hsv.H, 255, 255);
      
      
      
      
     
      
      //widthIndex++;
      //if(widthIndex>=NUM_LEDS/2){
      //  widthIndex = 0;
      //  //index = random(0, NUM_LEDS);
      ////  hsv.H = random(0, 255);
      //  Serial.println("resetting counter");
      //}
      delay(100);
      break;    
    }
    FastLED.show();
  }

  
}
