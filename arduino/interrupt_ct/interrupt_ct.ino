const int inputPin = 21;
const byte buttonNumber = 1;

volatile byte lastButton = 0;
volatile long timing = 0;


void setup() {
  Serial.begin(9600);

  pinMode(inputPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(inputPin), buttonPress, HIGH);

  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  switch (lastButton) {
    case 1:
      task();
      if ((millis() - timing) >= 5000) {
        Serial.println("Reinicia");
        lastButton = 0;
      }
      break;
    default:
      Serial.println("Ninguno");
      break;
  }

  

  Serial.println("Espera");
  delay(500);
}

void task() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(500);
}

void buttonPress() {
  lastButton = 1;
  timing = millis();
}
