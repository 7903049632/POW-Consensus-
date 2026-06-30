void setup() {
  Serial.begin(9600);
}

void loop() {
  int load = random(0, 100);

  if (load > 60)
    Serial.println("Mega Node Status : BUSY");
  else
    Serial.println("Mega Node Status : IDLE");

  delay(1500);
}
