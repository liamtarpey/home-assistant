# Logic Pro recording signal -> Home Assistant.
# Logic's "Recording Light" control surface sends MIDI to the IAC Driver Bus 1 virtual port; this script forwards each message to a webhook.
# Setup used: python3 -m venv ~/logic-midi ; ~/logic-midi/bin/pip install mido python-rtmidi
# Run:        ~/logic-midi/bin/python ~/logic-midi/listener.py
# Home Assistant is at 192.168.1.124 on port 80 (not 8123). Use the IP address, not homeassistant.local,
# because the work VPN breaks .local names outside Safari.
import json
import time
import urllib.request
import mido

HA = "http://192.168.1.124/api/webhook/REPLACE_WITH_THE_SAME_WEBHOOK_ID"


def post(data):
    req = urllib.request.Request(HA, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=3).status


print("Home Assistant says:", post({"type": "startup"}))

names = [n for n in mido.get_input_names() if "IAC" in n]
if not names:
    raise SystemExit("No IAC Driver port found. Check it is online in Audio MIDI Setup.")
print("Listening on", names[0])

start = time.time()
last_key, last_time = None, 0
with mido.open_input(names[0]) as port:
    for msg in port:
        now = time.time()
        data = {"type": msg.type}
        for key in ("note", "velocity", "control", "value", "channel"):
            if hasattr(msg, key):
                data[key] = getattr(msg, key)
        sig = json.dumps(data, sort_keys=True)
        if sig == last_key and now - last_time < 0.2:
            continue
        last_key, last_time = sig, now
        print(f"{now - start:8.2f}s  {data}")
        try:
            post(data)
        except Exception as e:
            print("post failed:", e)
