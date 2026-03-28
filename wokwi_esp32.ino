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
  مكتبات مطلوبة:
       - PubSubClient
       - LiquidCrystal_I2C
===================================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>

// ===================================================
// إعدادات الواي فاي - في Wokwi استخدم هذه القيم
// ===================================================
const char* WIFI_SSID     = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ===================================================
// إعدادات MQTT (السيرفر القديم)
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
// تهيئة الشاشة
// ===================================================
LiquidCrystal_I2C lcd(0x27, 16, 2);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ===================================================
// متغيرات احترافية 
// ===================================================
bool mqttConnectedOnce = false;
String lastMessage = "";   // لمنع التكرار

// ===================================================
// دالة تحريك النص اذا كان الاسم طويل (Scroll)
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
// استقبال الرسائل (نسخة احترافية)
// ===================================================
void onMessageReceived(char* topic, byte* payload, unsigned int length) {

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("New Message: " + message);

  //  تجاهل الرسائل المكررة
  if (message == lastMessage) return;
  lastMessage = message;

  lcd.clear();

  // ===== حضور مسجل =====
  if (message.startsWith("PRESENT:")) {

    String data = message.substring(8);

    // فصل الاسم عن الـ ID
    int separatorIndex = data.indexOf(":");
    String name;

    if (separatorIndex != -1) {
      name = data.substring(0, separatorIndex);
    } else {
      name = data;
    }

    lcd.setCursor(0, 0);
    lcd.print("Attendance OK!");
    
    //  عرض الاسم مع Scroll
    scrollText(name, 1);

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    tone(BUZZER, 1000, 300);
    delay(2000);
    digitalWrite(GREEN_LED, LOW);
  }

  // ===== مسجل مسبقاً =====
  else if (message.startsWith("ALREADY:")) {

    String data = message.substring(8);

    int separatorIndex = data.indexOf(":");
    String name;

    if (separatorIndex != -1) {
      name = data.substring(0, separatorIndex);
    } else {
      name = data;
    }

    lcd.setCursor(0, 0);
    lcd.print("Already Marked!");

    // عرض الاسم مع Scroll
    scrollText(name, 1);

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, HIGH);
    tone(BUZZER, 500, 200);
    delay(2000);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, LOW);
  }

  // ===== وجه غير معروف =====
  else if (message.startsWith("UNKNOWN")) {

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
// الاتصال بـ MQTT (نسخة احترافية)
// ===================================================
void connectMQTT() {

  if (mqttClient.connected()) return;

  int retries = 0;

  while (!mqttClient.connected() && retries < 5) {

    if (mqttClient.connect("ESP32Client")) {

      mqttClient.subscribe(MQTT_TOPIC);

      if (!mqttConnectedOnce) {
        lcd.clear();
        lcd.print("MQTT OK");
        mqttConnectedOnce = true;
        delay(1000);
      }

    } else {
      retries++;
      delay(1000);
    }
  }
}

// ===================================================
// الإعداد الأولي
// ===================================================
void setup() {

  Serial.begin(115200); // Debug

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

  // الاتصال
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
