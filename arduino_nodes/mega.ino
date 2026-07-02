String input = "";

long hashFunc(String data, long nonce) {
  long h = 7;
  String text = data + String(nonce);

  for (int i = 0; i < text.length(); i++) {
    h = (h * 31 + text[i]) % 100000;
  }
  return h;
}

void setup() {
  Serial.begin(9600);
  Serial.println("MEGA_READY");
}

void loop() {

  if (Serial.available()) {

    input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("MINE")) {

      String data = input.substring(5);

      Serial.println("MEGA_MINING");

      for (long nonce = 0; nonce < 20000; nonce++) {

        long h = hashFunc(data, nonce);

        if (h % 2000 == 0) {

          Serial.print("MINED|MEGA|");
          Serial.print(nonce);
          Serial.print("|");
          Serial.println(h);

          break;
        }
      }
    }
  }
}