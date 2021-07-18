const int inputPin = 52;
 
void setup() {
  Serial.begin(9600);
  pinMode(inputPin, OUTPUT);
}

void loop() {

 task();

  Serial.println("Espera");
  delay(2000);
}

void task() {
  Serial.println("comenzo");
  digitalWrite(inputPin, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(inputPin, LOW);    // turn the LED off by making the voltage LOW
  delay(500);
  Serial.println("termino");
}
