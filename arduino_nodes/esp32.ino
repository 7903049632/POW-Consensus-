void setup() {
  Serial.begin(9600);
  Serial.println("ESP32_READY");
}

void loop() {

  if (Serial.available()) {

    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.startsWith("MINE")) {

      long nonce = random(1000, 9999);
      long hash = random(50000, 99999);

      Serial.print("MINED|ESP32|");
      Serial.print(nonce);
      Serial.print("|");
      Serial.println(hash);
    }
  }
}