#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // Simple workload logic
  if (isnan(temp) || temp > 35) {
    Serial.println("Node Status : BUSY");
  } else {
    Serial.println("Node Status : IDLE");
  }

  Serial.print("TEMP: ");
  Serial.print(temp);
  Serial.print(" HUM: ");
  Serial.println(hum);

  delay(2000);
}
