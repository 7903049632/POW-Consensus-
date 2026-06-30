void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));
}

void loop() {
  // Simulated temperature (you can replace with real sensor later)
  int temperature = random(20, 50);
  int humidity = random(30, 80);

  // Node load simulation
  int load = random(0, 100);

  // BUSY / IDLE logic
  if (load > 60) {
    Serial.println("ESP32 Node Status : BUSY");
  } else {
    Serial.println("ESP32 Node Status : IDLE");
  }

  // Sensor-like output
  Serial.print("ESP32 TEMP: ");
  Serial.print(temperature);
  Serial.print(" | HUM: ");
  Serial.println(humidity);

  delay(2000);
}
