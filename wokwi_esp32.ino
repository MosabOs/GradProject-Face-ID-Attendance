/*
===================================================
  كود ESP32 - داخل Wokwi
===================================================
  الخطوات:
  1. افتح wokwi.com
  2. New Project → ESP32
  3. انسخ الكود في main.ino
  4. أضف:
     - LCD I2C
     - LED أخضر (25)
     - LED أحمر (26)
     - Buzzer (27)
===================================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>

// ===================================================
// WiFi
// ===================================================
const char* WIFI_SSID     = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ===================================================
// MQTT
// ===================================================
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "smartattendance/result";

// ===================================================
// Pins
// ===================================================
const int GREEN_LED = 25;
const int RED_LED   = 26;
const int BUZZER    = 27;

// ===================================================
// LCD
// ===================================================
LiquidCrystal_I2C lcd(0x27, 16, 2);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ===================================================
// متغيرات
// ===================================================
bool mqttShown = false;
bool isProcessing = false;

// ===================================================
// Scroll للنص الطويل
// ===================================================
void scrollText(String text, int row, int delayTime = 300) {

  if (text.length() <= 16) {
    lcd.setCursor(0, row);
    lcd.print(text);
    return;
  }

  for (int i = 0; i <= text.length() - 16; i++) {
    lcd.setCursor(0, row);
    lcd.print(text.substring(i, i + 16));
    delay(delayTime);
  }
}

// ===================================================
// استقبال الرسائل
// ===================================================
void onMessageReceived(char* topic, byte* payload, unsigned int length) {

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("New Message: " + message);

  // تجاهل الرسائل الفارغة
  if (message.length() == 0) return;

  // منع التداخل فقط (مهم)
  if (isProcessing) return;

  isProcessing = true;

  lcd.clear();

  // ===================================================
  // ===== PRESENT =====
  // ===================================================
  if (message.startsWith("PRESENT:")) {

    String data = message.substring(8);

    int sep = data.indexOf(":");
    String name = (sep != -1) ? data.substring(0, sep) : data;

    lcd.setCursor(0, 0);
    lcd.print("Attendance OK!");

    scrollText(name, 1);

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    tone(BUZZER, 1000, 300);

    delay(5000);

    digitalWrite(GREEN_LED, LOW);
  }

  // ===================================================
  // ===== ALREADY =====
  // ===================================================
  else if (message.startsWith("ALREADY:")) {

    String data = message.substring(8);

    int sep = data.indexOf(":");
    String name = (sep != -1) ? data.substring(0, sep) : data;

    lcd.setCursor(0, 0);
    lcd.print("Already Marked!");

    scrollText(name, 1);

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, HIGH);
    tone(BUZZER, 500, 200);

    delay(5000);

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, LOW);
  }

  // ===================================================
  // ===== UNKNOWN =====
  // ===================================================
  else if (message.startsWith("UNKNOWN")) {

    lcd.setCursor(0, 0);
    lcd.print("Unknown Face!");
    lcd.setCursor(0, 1);
    lcd.print("Access Denied");

    digitalWrite(RED_LED, HIGH);
    tone(BUZZER, 300, 500);

    delay(5000);

    digitalWrite(RED_LED, LOW);
  }

  // ===================================================
  // رجوع للوضع الطبيعي
  // ===================================================
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready...");

  isProcessing = false;
}

// ===================================================
// WiFi
// ===================================================
void connectWiFi() {

  lcd.clear();
  lcd.print("Connecting WiFi");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  lcd.clear();
  lcd.print("WiFi OK");
  delay(1000);
}

// ===================================================
// MQTT
// ===================================================
void connectMQTT() {

  while (!mqttClient.connected()) {

    String clientId = "ESP32-" + String(random(1000, 9999));

    if (mqttClient.connect(clientId.c_str())) {

      Serial.println("MQTT Connected");

      mqttClient.subscribe(MQTT_TOPIC);

      if (!mqttShown) {
        lcd.clear();
        lcd.print("MQTT OK");
        delay(1000);
        mqttShown = true;
      }

    } else {
      delay(1000);
    }
  }
}

// ===================================================
// setup
// ===================================================
void setup() {

  Serial.begin(115200);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Smart Attendance");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");
  delay(1500);

  connectWiFi();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMessageReceived);

  connectMQTT();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready...");
}

// ===================================================
// loop
// ===================================================
void loop() {

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  mqttClient.loop();
}