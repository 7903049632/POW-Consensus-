void setup() {
  Serial.begin(9600);
}

void loop() {
  int state = random(0, 2);

  if (state == 0)
    Serial.println("Nano Node Status : IDLE");
  else
    Serial.println("Nano Node Status : BUSY");

  delay(2000);
}
