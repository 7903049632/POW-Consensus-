void setup() {
  Serial.begin(9600);
  Serial.println("NANO_READY");
}

void loop() {

  if (Serial.available()) {

    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.startsWith("MINED")) {
      Serial.println("VALIDATED|TRUE");
    } else {
      Serial.println("VALIDATED|FALSE");
    }
  }
}