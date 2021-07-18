const int analogOutPin = 4; // Analog output pin

byte outputValue = 100;        // valor del PWM

String command;

void setup() {
  Serial.begin(9600);
}

void loop() {

  if (Serial.available() > 0 ) {
    command = Serial.readString(); // read the incoming data as string

    Serial.println(command);
    
    if (command == "+\r\n" ) {
      Serial.println("Aumenta");
      outputValue = outputValue + 5;
    }

    if (command == "-\r\n" ) {
      Serial.println("Disminuye");
      outputValue = outputValue + 5;
    }

    if (command == "0\r\n" ) {
      Serial.println("Reinicia");
      outputValue = 100;
    }

    Serial.print("Valor: ");
    Serial.print(outputValue);
  }

  
  analogWrite(analogOutPin, outputValue);
}
