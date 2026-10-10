#include <DHT.h>

#define PIN_WATER A0
#define PIN_DHT 2
#define PIN_BUZZER 9
#define PIN_LED 13
#define DHTTYPE DHT11

DHT dht(PIN_DHT, DHTTYPE);

const float WARN_M = 4.5;
const float DANGER_M = 5.5;
const float HYST_M = 0.3;

unsigned long lastSampleTime = 0;
const unsigned long SAMPLE_INTERVAL_MS = 1000;
int alertLevel = 0; // 0 normal, 1 warning, 2 danger

int computeLevel(float m) {
  if (m >= DANGER_M) return 2;
  if (alertLevel == 2 && m >= DANGER_M - HYST_M) return 2;
  if (m >= WARN_M) return 1;
  if (alertLevel >= 1 && m >= WARN_M - HYST_M) return 1;
  return 0;
}

void driveLocalAlarm(unsigned long now) {
  bool on = false;
  if (alertLevel == 2) on = (now / 200) % 2;
  else if (alertLevel == 1) on = (now / 800) % 2;
  digitalWrite(PIN_BUZZER, on);
  digitalWrite(PIN_LED, on);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(PIN_WATER, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  delay(1000);
}

void loop() {
  unsigned long now = millis();
  driveLocalAlarm(now);

  if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = now;

    int rawWater = analogRead(PIN_WATER);

    float waterCm = (rawWater / 700.0) * 45.0;
    if (waterCm > 45.0) waterCm = 45.0;
    if (waterCm < 0.0) waterCm = 0.0;

    float riverLevelM = (rawWater / 700.0) * 6.5;
    if (riverLevelM > 6.5) riverLevelM = 6.5;

    float humidity = dht.readHumidity();
    float tempC = dht.readTemperature();
    if (isnan(humidity)) humidity = 0.0;
    if (isnan(tempC)) tempC = 0.0;

    alertLevel = computeLevel(riverLevelM);

    Serial.print(F("{\"node_id\":\"EDGE-UNO-01\""));
    Serial.print(F(",\"water_raw\":"));
    Serial.print(rawWater);
    Serial.print(F(",\"water_level_cm\":"));
    Serial.print(waterCm, 1);
    Serial.print(F(",\"simulated_river_m\":"));
    Serial.print(riverLevelM, 2);
    Serial.print(F(",\"temperature_c\":"));
    Serial.print(tempC, 1);
    Serial.print(F(",\"humidity_percent\":"));
    Serial.print(humidity, 1);
    Serial.print(F(",\"alert_level\":"));
    Serial.print(alertLevel);
    Serial.println(F("}"));
  }
}
