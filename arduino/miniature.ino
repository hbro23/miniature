
#define print(prefix, title, msg) Serial.print(prefix); Serial.print(title); Serial.println(msg);
#define debug(title, msg) print("[LOG] ", title, msg);
#define notify(cmd) print("[CMD] ", "", cmd);
#define log(title) debug(title, "");

const byte LOOP = 0;

volatile byte currentButton = LOOP;
volatile byte previousButton = currentButton;

byte lastChange = 250;

const byte BUTTON_1 = 1;
const byte BUTTON_2 = 2;
const byte BUTTON_3 = 3;
const byte BUTTON_4 = 4;


const byte BUTTON_1_PIN = 20;
const byte BUTTON_2_PIN = 19;


const byte LIGTH_1_PIN = 53;
const byte LIGTH_2_PIN = 52;
const byte LIGTH_3_PIN = 51;
const byte LIGTH_4_PIN = 50;

String chapter;
byte data;
int value;

void setup() {
  Serial.begin(9600);

  //Buttons
  attachInterrupt(digitalPinToInterrupt(BUTTON_1_PIN), pressButton20, HIGH);
  attachInterrupt(digitalPinToInterrupt(BUTTON_2_PIN), pressButton19, HIGH);

  //Stations ligths
  pinMode(LIGTH_1_PIN, OUTPUT);
  pinMode(LIGTH_2_PIN, OUTPUT);

  log("start");
}


void loop() {

  //Comunications
  if (Serial.available()) {
    chapter = Serial.readStringUntil('.');

    debug("chapter recived: ", chapter);
    
    if (chapter == "LOOP") {
      log("setting loop");
      setNewChapter(LOOP);
    }

    if (chapter.startsWith("button")) {
      data = (byte)chapter.substring(7).toInt();
      debug("setting chapter recived: ", data);
      setNewChapter(data);
    }

    chapter = "";
  }

  //Task
  turnOnLigth();

  //Notification
  if (lastChange != previousButton
      && currentButton != previousButton) {
    
    switch (currentButton) {
      case BUTTON_1:
        chapter = "button_1";
        break;

      case BUTTON_2:
        chapter = "button_2";
        break;
    }

    lastChange = previousButton;
    
    if (chapter != ""){
      debug("sending: ", chapter);
      notify(chapter);
    }
    
  }

  delay(100);
}

// void checkButton17() {
//   value = digitalRead(BUTTON_1);

//   if (value == HIGH) {
//     previousButton = currentButton;
//     currentButton = BUTTON_1;
//   }

//   delay(300);
// }

void setNewChapter(byte button) {
  if (button == currentButton) {
    debug("button equal to previous one: ", currentButton)
    return;
  }

  previousButton = currentButton;
  currentButton = button;
  debug("new chapter setted: ", currentButton)
  debug("previous: ", previousButton)
}

void pressButton20() {
  setNewChapter(BUTTON_1);
}
void pressButton19() {
  setNewChapter(BUTTON_2);
}

void turnOnLigth() {
  byte pin = 0;
  switch (currentButton) {
    case BUTTON_1:
      pin = LIGTH_1_PIN;
      break;

    case BUTTON_2:
      pin = LIGTH_2_PIN;
      break;

    case LOOP:
      pin = LIGTH_3_PIN;
      break;
  }

  digitalWrite(pin, HIGH);
  delay(1000);
  digitalWrite(pin, LOW);
  delay(500);
}




//void loop(){

//}
