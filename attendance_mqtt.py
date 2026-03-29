"""
===================================================
كود Python - التعرف على الوجوه + إرسال MQTT (DeepFace)
===================================================
تثبيت المكتبات:
    pip install opencv-python deepface numpy paho-mqtt

كيفية التشغيل:
    1. شغّل هذا الكود على جهازك
    2. افتح Wokwi وشغّل كود ESP32
    3. الكاميرا ستبدأ التعرف وترسل النتيجة لـ Wokwi تلقائياً
"""

import cv2
import numpy as np
import pickle
import os
import sqlite3
from datetime import datetime
import time
import paho.mqtt.client as mqtt
from deepface import DeepFace

# ===================================================
# إعدادات MQTT
# ===================================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "smartattendance/result"

# ===================================================
# إعدادات النظام
# ===================================================
STUDENTS_DATA_FILE = "students_data.pkl"
DATABASE_FILE      = "attendance.db"
MIN_SECONDS_BETWEEN_RECORDS = 60

# ===================================================
# اتصال MQTT
# ===================================================
mqtt_client = mqtt.Client()
mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("MQTT Connected")
    else:
        print(f"MQTT Connection Failed: {rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print("MQTT Disconnected")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

def connect_mqtt():
    try:
        print(f"Connecting to {MQTT_BROKER}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()

        timeout = 0
        while not mqtt_connected and timeout < 5:
            time.sleep(1)
            timeout += 1

    except Exception as e:
        print(f"MQTT Error: {e}")

# ===================================================
# MQTT (منع التكرار الحقيقي)
# ===================================================
last_sent_message = ""
last_send_time = 0
MIN_SECONDS_BETWEEN_SENDS = 2

def send_mqtt_message(message):
    global last_sent_message, last_send_time

    current_time = time.time()

    # منع التكرار خلال ثانيتين
    if message == last_sent_message and (current_time - last_send_time) < MIN_SECONDS_BETWEEN_SENDS:
        return

    if mqtt_connected:

        print(f"Sending: {message}")

        # إرسال مرة واحدة فقط (مهم جداً)
        mqtt_client.publish(
            MQTT_TOPIC,
            message,
            qos=1,
            retain=True   # مهم جداً (لا تغيّره)
        )
        time.sleep(1)

        # تأخير بسيط لضمان وصول الرسالة
        time.sleep(0.3)

        last_sent_message = message
        last_send_time = current_time

    else:
        print("MQTT not connected")

# ===================================================
# قاعدة البيانات
# ===================================================
def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            date TEXT,
            time TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def record_attendance(student_id, student_name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM attendance WHERE student_id=? AND date=?", (student_id, date_str))

    if cursor.fetchone():
        conn.close()
        return False, "Already recorded"

    cursor.execute("INSERT INTO attendance VALUES (NULL, ?, ?, ?, ?, ?)",
                   (student_id, student_name, date_str, time_str, "Present"))

    conn.commit()
    conn.close()
    return True, time_str

# ===================================================
# تحميل بيانات الطلاب
# ===================================================
def load_students_data():
    if not os.path.exists(STUDENTS_DATA_FILE):
        print("No students data found")
        return None
    with open(STUDENTS_DATA_FILE, "rb") as f:
        return pickle.load(f)

# ===================================================
# التعرف باستخدام DeepFace
# ===================================================
def recognize_face(frame, known_images):
    try:
        for i, known_img in enumerate(known_images):

            # لو الصورة path
            if isinstance(known_img, str):
                known_img = cv2.imread(known_img)

            result = DeepFace.verify(frame, known_img, enforce_detection=False)

            if result["verified"]:
                return i

        return -1

    except:
        return -1

# ===================================================
# النظام الرئيسي
# ===================================================
def run_system():
    print("=" * 55)
    print(" Smart Attendance System (DeepFace + MQTT)")
    print("=" * 55)

    init_database()

    data = load_students_data()
    if data is None:
        return

    known_images = data["images"]
    known_names  = data["names"]
    known_ids    = data["ids"]

    if len(known_images) == 0:
        print("No students registered")
        return

    print(f"Loaded {len(known_images)} students")

    connect_mqtt()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found")
        return

    last_recorded = {}
    frame_count = 0
    done = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ===================================================
        # عرض حالة البحث دائماً
        # ===================================================
        cv2.putText(frame, "Searching...", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        frame_count += 1

        if frame_count % 3 == 0:

            match_index = recognize_face(frame, known_images)

            if match_index != -1:
                name = known_names[match_index]
                student_id = known_ids[match_index]

                cv2.putText(frame, f"Recognized: {name}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                current_time = time.time()
                last_time = last_recorded.get(student_id, 0)

                if current_time - last_time > MIN_SECONDS_BETWEEN_RECORDS:

                    success, msg = record_attendance(student_id, name)
                    last_recorded[student_id] = current_time

                    if success:
                        send_mqtt_message(f"PRESENT:{name}:{student_id}")
                        print(f"{name} marked present")

                        # إرسال النتيجة للويب
                        with open("attendance_result.txt", "w") as f:
                            f.write(f"PRESENT:{name}")

                        done = True

                    else:
                        send_mqtt_message(f"ALREADY:{name}:{student_id}")
                        print(f"{name} already marked")

                        # إرسال النتيجة للويب
                        with open("attendance_result.txt", "w") as f:
                            f.write(f"ALREADY:{name}")

                        done = True

            else:
                cv2.putText(frame, "Unknown Face", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Smart Attendance", frame)

        # يقفل فقط بعد التعرف
        if done:
            print("Auto Stop: Attendance completed")

            # مهم جداً لضمان وصول MQTT
            time.sleep(2)

            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# ===================================================
# تشغيل البرنامج
# ===================================================
if __name__ == "__main__":
    run_system()
    exit()