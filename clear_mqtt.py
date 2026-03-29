import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)

# مسح الرسالة القديمة
client.publish("smartattendance/result", "", retain=True)

client.disconnect()

print("MQTT cleared")