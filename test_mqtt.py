
# VERSION 1
# ____________________________________________________________________________________
# import paho.mqtt.client as mqtt
# import time

# # ===================================================
# # إعدادات MQTT
# # ===================================================
# BROKER = "broker.hivemq.com"
# # BROKER = "test.mosquitto.org" # More faster server 
# PORT = 1883
# TOPIC = "smartattendance/result"

# connected = False

# # ===================================================
# def on_connect(client, userdata, flags, rc):
#     global connected
#     if rc == 0:
#         print("Connected to MQTT ✅")
#         connected = True

# # ===================================================
# client = mqtt.Client()
# client.on_connect = on_connect

# client.connect(BROKER, PORT, 60)

# client.loop_start()

# # ننتظر الاتصال
# while not connected:
#     time.sleep(0.1)

# #  مهم: ندي وقت لـ ESP32 يشترك
# time.sleep(3)

# # ===================================================
# # إرسال الرسالة (مع QoS + تكرار)
# # ===================================================
# for i in range(3):
#     client.publish(TOPIC, "UNKNOWN", qos=1)
#     time.sleep(1)

# print("Message sent!")

# time.sleep(2)

# client.loop_stop()





# VERSION 2
# __________________________________________________________________________________
# import paho.mqtt.client as mqtt
# import time

# BROKER = "broker.hivemq.com"
# # BROKER = "test.mosquitto.org" # More faster server 
# PORT = 1883
# TOPIC = "smartattendance/result"

# client = mqtt.Client()

# client.connect(BROKER, PORT, 60)

# client.loop_start()

# print("Waiting before sending...")
# time.sleep(5)   #  أهم سطر

# print("Sending message...")

# for i in range(5):   #  نرسل 5 مرات
#     client.publish(TOPIC, "UNKNOWN")
#     print("Sent", i+1)
#     time.sleep(1)

# client.loop_stop()




# VERSION 3
# ______________________________________________________________________________
import paho.mqtt.client as mqtt
import time
import random

# ===================================================
# إعدادات MQTT
# ===================================================
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smartattendance/result2"

client = mqtt.Client()

client.connect(BROKER, PORT, 60)
client.loop_start()

# ندي وقت للاتصال
time.sleep(3)

#  رسالة فيها ID عشان ما تتكرر
message_id = random.randint(1000, 9999)
message = f"UNKNOWN:{message_id}"

print("Sending:", message)

# إرسال احترافي
client.publish(
    TOPIC,
    message,
    qos=1,        #  ضمان التوصيل
    retain=True   #  تخزين الرسالة
)

print("Message sent!")

time.sleep(2)
client.loop_stop()
