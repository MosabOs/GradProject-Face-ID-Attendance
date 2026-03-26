import paho.mqtt.client as mqtt
import time

connected = False

def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        print("Connected to MQTT ✅")
        connected = True

client = mqtt.Client()
client.on_connect = on_connect

client.connect("broker.hivemq.com", 1883, 60)

client.loop_start()

while not connected:
    time.sleep(0.1)

client.publish("smartattendance/result", "UNKNOWN")

print("Message sent!")

time.sleep(3)

client.loop_stop()