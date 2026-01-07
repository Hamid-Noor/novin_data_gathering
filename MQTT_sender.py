# import paho.mqtt.client as mqtt
# import time
# import os

# # 📁 خواندن فایل با هندل خطا


# def readFile(filename):
#     try:
#         if os.path.isfile(filename):
#             with open(filename, 'r', encoding="utf-8") as f:
#                 return f.read().strip()
#         else:
#             return None
#     except Exception as e:
#         print(f"[File Error] {e}")
#         return None


# # ⚙️ تنظیمات MQTT
# broker = "10.56.202.36"
# port = 11883
# topic_produced = "factory/novin/lines/live"
# client_id = "raspberry-sender"
# mqtt_user = "user_azinmqtt"
# mqtt_pass = "Yasd@456+"

# connected = False
# client = mqtt.Client(client_id=client_id)
# client.username_pw_set(mqtt_user, mqtt_pass)

# # 📡 هندل اتصال


# def on_connect(client, userdata, flags, rc):
#     global connected
#     if rc == 0:
#         connected = True
#         print("[MQTT] Connected successfully.")
#     else:
#         print(f"[MQTT] Connection failed with code {rc}")

# # 🔌 هندل قطع اتصال


# def on_disconnect(client, userdata, rc):
#     global connected
#     connected = False
#     print(f"[MQTT] Disconnected. Will retry...")


# client.on_connect = on_connect
# client.on_disconnect = on_disconnect

# # 🚀 شروع loop
# client.loop_start()

# # 🗂 آخرین مقادیر معتبر
# lastPackedCount = None
# lastWebDashboard = None

# # 🔁 حلقه اصلی
# while True:
#     try:
#         if not connected:
#             try:
#                 client.connect(broker, port, keepalive=30)
#                 print("[MQTT] Trying to connect...")
#             except Exception as e:
#                 print(f"[MQTT Error] Connect failed: {e}")
#         else:
#             print(123)
#             temppackedcount = readFile("test.txt")
#             # اگر مقدار جدید معتبر بود، جایگزین کن
#             if temppackedcount and temppackedcount.strip() != "":
#                 lastPackedCount = temppackedcount
#             print(f'lastPackedCount :',end=' ')
#             print(*(lastPackedCount.split("}")), sep='\n')
#             # فقط آخرین مقدار معتبر رو منتشر کن
#             if lastPackedCount is not None:
#                 resultpackedcount = client.publish(
#                     topic_produced, payload=str(lastPackedCount), qos=1, retain=True)
#             else:
#                 resultpackedcount = client.publish(
#                     topic_produced, payload=str('[]'), qos=1, retain=True)

#     except Exception as e:
#         print(f"[Loop Error] {e}")
#     time.sleep(2)



import json
import os
import random
import time
import paho.mqtt.client as mqtt

# =========================
# Settings
# =========================
BROKER = "10.56.202.36"
PORT = 11883

CLIENT_ID = "raspberry-sender"
MQTT_USER = "user_azinmqtt"
MQTT_PASS = "Yasd@456+"

PAYLOAD_FILE = "mqtt_payloads.json"  # خروجی result_maker
PUBLISH_QOS = 1
RETAIN = True

PUBLISH_INTERVAL_SEC = 2

# Retry/backoff
BACKOFF_MIN = 1.0
BACKOFF_MAX = 60.0
JITTER = 0.25

connected = False


def read_file(path: str) -> str | None:
    try:
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            s = f.read().strip()
        return s or None
    except Exception as e:
        print(f"[File Error] {e}")
        return None


def _backoff_sleep(attempt: int) -> None:
    base = min(BACKOFF_MAX, BACKOFF_MIN * (2 ** max(0, attempt)))
    factor = 1.0 + random.uniform(-JITTER, JITTER)
    delay = max(BACKOFF_MIN, min(BACKOFF_MAX, base * factor))
    print(f"[MQTT] Reconnect in {delay:.1f}s (attempt={attempt})")
    time.sleep(delay)


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        connected = True
        print("[MQTT] Connected ✅")
    else:
        connected = False
        print(f"[MQTT] Connect failed (rc={rc})")


def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print(f"[MQTT] Disconnected (rc={rc})")


def build_client() -> mqtt.Client:
    c = mqtt.Client(client_id=CLIENT_ID)
    c.username_pw_set(MQTT_USER, MQTT_PASS)
    c.on_connect = on_connect
    c.on_disconnect = on_disconnect
    return c


def ensure_connected(client: mqtt.Client) -> None:
    attempt = 0
    while True:
        if connected and client.is_connected():
            return
        try:
            print(f"[MQTT] Connecting to {BROKER}:{PORT} ...")
            client.connect_async(BROKER, PORT, keepalive=60)
            client.loop_start()

            t0 = time.time()
            while time.time() - t0 < 5.0:
                if connected and client.is_connected():
                    attempt = 0
                    return
                time.sleep(0.1)

            try:
                client.loop_stop()
            except Exception:
                pass

            attempt += 1
            _backoff_sleep(attempt)

        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            try:
                client.loop_stop()
            except Exception:
                pass
            attempt += 1
            _backoff_sleep(attempt)


def publish_loop():
    client = build_client()

    last_sent_by_topic = {}  # topic -> payload_str

    while True:
        try:
            ensure_connected(client)

            raw = read_file(PAYLOAD_FILE)
            if raw is None:
                time.sleep(PUBLISH_INTERVAL_SEC)
                continue

            try:
                payloads = json.loads(raw)
            except Exception as e:
                print(f"[JSON Error] {e}")
                time.sleep(PUBLISH_INTERVAL_SEC)
                continue

            # payloads: {topic: object}
            for topic, obj in payloads.items():
                try:
                    payload_str = json.dumps(obj, ensure_ascii=False)
                except Exception:
                    payload_str = str(obj)

                # فقط اگر تغییر کرد publish کن
                if last_sent_by_topic.get(topic) == payload_str:
                    continue

                info = client.publish(topic, payload=payload_str, qos=PUBLISH_QOS, retain=RETAIN)
                info.wait_for_publish(timeout=2.0)
                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    last_sent_by_topic[topic] = payload_str
                    print(f"[MQTT] Published {topic}")
                else:
                    print(f"[MQTT] Publish failed {topic} (rc={info.rc})")
                    try:
                        client.disconnect()
                    except Exception:
                        pass
                    break

            time.sleep(PUBLISH_INTERVAL_SEC)

        except Exception as e:
            print(f"[Loop Error] {e}")
            try:
                client.disconnect()
            except Exception:
                pass
            time.sleep(1)


if __name__ == "__main__":
    publish_loop()
