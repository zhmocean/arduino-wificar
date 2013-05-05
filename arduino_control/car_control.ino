#include <Servo.h>

#define LEFT_SPEED 6
#define LEFT_0 7
#define LEFT_1 8
#define RIGHT_SPEED 5
#define RIGHT_0 2
#define RIGHT_1 4

#define SERVO_H 9
#define SERVO_V 10
#define SERVO_H_MAX_AL 170
#define SERVO_H_MIN_AL 30
#define SERVO_V_MAX_AL 160
#define SERVO_V_MIN_AL 30

#define CMD_SPLITER '#'
#define CMD_LENTH 2

Servo servoH;
Servo servoV;

int allSpeed =180;
byte buffer = 0;
String g_cmd = "";
int pointer = 0;
int servoH_al = 90;
int servoV_al = 90;
byte readFlag = 0;

void setup(){
  servoH.attach(SERVO_H);
  servoV.attach(SERVO_V);
  servoH.write(servoH_al);
  servoV.write(servoV_al);
  
  pinMode(LEFT_SPEED, OUTPUT);
  pinMode(LEFT_0, OUTPUT);
  pinMode(LEFT_1, OUTPUT);
  pinMode(RIGHT_SPEED, OUTPUT);
  pinMode(RIGHT_0, OUTPUT);
  pinMode(RIGHT_1, OUTPUT);
  
  Serial.begin(9600);
}

void loop(){
  
  if (Serial.available() >0){
    buffer = Serial.read();
    //Serial.println(buffer);
    //debug("read", buffer);
    //servoV.write(buffer);
    //Serial.println(servoV.read());
    
    if (char(buffer) == CMD_SPLITER){
      readFlag = 1;
      delay(20);
      buffer = Serial.read();
    }    
    
    if (readFlag ==1){
      //read command
      if((buffer != 255) && (buffer != 0) && (buffer != -1)&&(char(buffer) != CMD_SPLITER)){
        g_cmd += char(buffer);
        pointer ++;
      }       
      
     if (pointer >=CMD_LENTH){
        dispatchCmd(g_cmd);
        
        //release command
        g_cmd="";   
        buffer = 0;
        pointer = 0;  
        readFlag = 0;
      }
    }
  }
}

void dispatchCmd(String cmd){
  debug("",cmd);
//  if(cmd.startsWith("EU") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
//    eyeUp((cmd[CMD_LENTH-1]-'A')*2);
//  }
//  if(cmd.startsWith("ED") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
//    eyeDown((cmd[CMD_LENTH-1]-'A')*2);
//  }
//  if(cmd.startsWith("EL") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
//    eyeLeft((cmd[CMD_LENTH-1]-'A')*2);
//  }
//  if(cmd.startsWith("ER") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
//    eyeRight((cmd[CMD_LENTH-1]-'A')*2);
//  }
  if(cmd.startsWith("U") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
    eyeUp((cmd[CMD_LENTH-1]-'A')*2);
  }
  if(cmd.startsWith("D") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
    eyeDown((cmd[CMD_LENTH-1]-'A')*2);
  }
  if(cmd.startsWith("W") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
    eyeLeft((cmd[CMD_LENTH-1]-'A')*2);
  }
  if(cmd.startsWith("E") && cmd[CMD_LENTH-1]>'A' and cmd[CMD_LENTH-1]<'M'){
    eyeRight((cmd[CMD_LENTH-1]-'A')*2);
  }  
  
  if(cmd.startsWith("F") ){
    forward();
  }
  if(cmd.startsWith("B")){
    back();
  }
  if(cmd.startsWith("L")){
    left();
  }
  if(cmd.startsWith("R")){
    right();
  }  
  if(cmd.startsWith("S")){
    stopIt();
  }    
}

void debug(String type, String m){
  Serial.println(m);
}

void eyeLeft(byte al){
  servoH_al += al;
  if(servoH_al  >SERVO_H_MAX_AL){
    servoH_al = SERVO_H_MAX_AL;
  }
  servoH.write(servoH_al);
}
void eyeRight(byte al){
  servoH_al -= al;
  if(servoH_al < SERVO_H_MIN_AL){
    servoH_al = SERVO_H_MIN_AL;
  }
  servoH.write(servoH_al);
}

void eyeUp(byte al){
  servoV_al += al;
  if(servoV_al >SERVO_V_MAX_AL){
    servoV_al = SERVO_V_MAX_AL;
  }
  servoV.write(servoV_al);
}
void eyeDown(byte al){
  servoV_al -= al;
  if(servoV_al <SERVO_V_MIN_AL){
    servoV_al = SERVO_V_MIN_AL;
  }
  servoV.write(servoV_al);
}

void forward(){
  leftForward();
  rightForward();
}

void back(){
  leftBack();
  rightBack();
}

void left(){
  leftBack();
  rightForward();
}

void right(){
  leftForward();
  rightBack();
}

void stopIt(){
  analogWrite(LEFT_SPEED, 0);
  analogWrite(RIGHT_SPEED, 0);  
}

void leftForward(){
  digitalWrite(LEFT_0, LOW);
  digitalWrite(LEFT_1, HIGH);
  analogWrite(LEFT_SPEED, allSpeed);
}

void leftBack(){
  digitalWrite(LEFT_0, HIGH);
  digitalWrite(LEFT_1, LOW);
  analogWrite(LEFT_SPEED, allSpeed);
}

void rightForward(){
  digitalWrite(RIGHT_0, LOW);
  digitalWrite(RIGHT_1, HIGH);
  analogWrite(RIGHT_SPEED, allSpeed);
}

void rightBack(){
  digitalWrite(RIGHT_0, HIGH);
  digitalWrite(RIGHT_1, LOW);
  analogWrite(RIGHT_SPEED, allSpeed);
}

