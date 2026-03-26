/*
===================================================
  كود ESP32 - داخل Wokwi
===================================================
  الخطوات:
  1. افتح موقع wokwi.com
  2. اختر New Project ثم ESP32
  3. انسخ هذا الكود في ملف main.ino
  4. أضف المكونات في Wokwi:
       - LCD 16x2 (I2C)
       - LED أخضر على Pin 25
       - LED أحمر على Pin 26
       - Buzzer على Pin 27
  5. اضغط Start Simulation
===================================================
  مكتبات مطلوبة في Wokwi (أضفها من Library Manager):
       - PubSubClient  (للـ MQTT)
       - LiquidCrystal_I2C (للشاشة)
===================================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>

// ===================================================
// إعدادات الواي فاي - في Wokwi استخدم هذه القيم كما هي
// ===================================================
const char* WIFI_SSID     = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ===================================================
// إعدادات MQTT - نفس القيم في Python
// ===================================================
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "smartattendance/result";

// ===================================================
// أرقام الأطراف (Pins)
// ===================================================
const int GREEN_LED = 25;
const int RED_LED   = 26;
const int BUZZER    = 27;

// ===================================================
// تهيئة الشاشة LCD (عنوان I2C: 0x27، 16 عمود، 2 سطر)
// ===================================================
LiquidCrystal_I2C lcd(0x27, 16, 2);

WiFiClient   espClient;
PubSubClient mqttClient(espClient);

// 🔥 متغير لمنع تكرار MQTT OK
bool mqttConnectedOnce = false;

// ===================================================
// دالة استقبال رسائل MQTT
// ===================================================
void onMessageReceived(char* topic, byte* payload, unsigned int length) {

  // تحويل الرسالة إلى نص
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  lcd.clear();

  // ===== حضور مسجل =====
  if (message.startsWith("PRESENT:")) {

    String parts = message.substring(8);
    int colonIndex = parts.indexOf(':');
    String studentName = (colonIndex > 0) ? parts.substring(0, colonIndex) : parts;

    lcd.setCursor(0, 0);
    lcd.print("Attendance OK!");
    lcd.setCursor(0, 1);
    lcd.print(studentName.substring(0, 16));

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    tone(BUZZER, 1000, 300);
    delay(2000);
    digitalWrite(GREEN_LED, LOW);
  }

  // ===== مسجل مسبقاً =====
  else if (message.startsWith("ALREADY:")) {

    String parts = message.substring(8);

    lcd.setCursor(0, 0);
    lcd.print("Already Marked!");
    lcd.setCursor(0, 1);
    lcd.print(parts.substring(0, 16));

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, HIGH);
    tone(BUZZER, 500, 200);
    delay(2000);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, LOW);
  }

  // ===== وجه غير معروف =====
  else if (message == "UNKNOWN") {

    lcd.setCursor(0, 0);
    lcd.print("Unknown Face!");
    lcd.setCursor(0, 1);
    lcd.print("Access Denied");

    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    tone(BUZZER, 300, 500);
    delay(2000);
    digitalWrite(RED_LED, LOW);
  }

  // ❌ تم تعطيل الرجوع التلقائي للوضع الطبيعي
  /*
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready...");
  */
}

// ===================================================
// الاتصال بالواي فاي
// ===================================================
void connectWiFi() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    attempts++;
  }

  lcd.clear();

  if (WiFi.status() == WL_CONNECTED) {
    lcd.print("WiFi OK");
  } else {
    lcd.print("WiFi Failed");
  }

  delay(1000);
}

// ===================================================
// الاتصال بـ MQTT
// ===================================================
void connectMQTT() {

  if (mqttClient.connected()) return;

  if (mqttClient.connect("ESP32Client")) {

    mqttClient.subscribe(MQTT_TOPIC);

    // 🔥 يظهر مرة واحدة فقط
    if (!mqttConnectedOnce) {
      lcd.clear();
      lcd.print("MQTT OK");
      mqttConnectedOnce = true;
    }

  } else {

    lcd.clear();
    lcd.print("MQTT Failed");
  }

  delay(1000);
}

// ===================================================
// الإعداد الأولي
// ===================================================
void setup() {

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

  // اتصال
  connectWiFi();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMessageReceived);

  connectMQTT();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready...");
}

// ===================================================
// الحلقة الرئيسية
// ===================================================
void loop() {

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  mqttClient.loop();
  delay(100);
}