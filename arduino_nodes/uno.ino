#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

int epoch = 0;

void setup() {
  Serial.begin(9600);
  dht.begin();

  Serial.println("UNO_SENSOR_NODE_READY");
}

void loop() {

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // sensor safety check
  if (isnan(temp) || isnan(hum)) {
    Serial.println("SENSOR_ERROR");
    delay(2000);
    return;
  }

  int tx_count = random(5, 20);
  int difficulty = 1;

  // IMPORTANT FORMAT (Python expects this)
  Serial.print("SENSOR,");
  Serial.print(epoch);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.print(hum);
  Serial.print(",");
  Serial.print(tx_count);
  Serial.print(",");
  Serial.println(difficulty);

  epoch++;

  delay(2000);
}