# ═══════════════════════════════════════════════════
#  tkinter_app.py  —  Tkinter Publisher UI
#  Run AFTER:  python app.py
# ═══════════════════════════════════════════════════

import tkinter as tk
from tkinter import scrolledtext
import paho.mqtt.client as mqtt
import json, time
from datetime import datetime

BROKER = "broker.emqx.io"
PORT   = 1883
TOPIC  = "test/tkinter"

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,
    client_id=f"tkinter-{int(time.time())}",
    clean_session=True
)

is_connected = False

# ───────────────────────────────────────────
#  MQTT CALLBACKS
# ───────────────────────────────────────────
def on_connect(c, u, f, rc):
    global is_connected
    if rc == 0:
        is_connected = True
        log(" Connected to MQTT Broker!")
        log(f"   Broker : {BROKER}")
        log(f"   Topic  : {TOPIC}")
        win.after(0, lambda: [
            btn_con.config(state="disabled",
                           text=" Connected",
                           bg="#94a3b8"),
            btn_pub.config(state="normal"),
            btn_dis.config(state="normal"),
            # dot.config(fg="#4ade80")
        ])
    else:
        log(f" Connection failed (rc={rc})")

def on_disconnect(c, u, rc):
    global is_connected
    is_connected = False
    log(" Disconnected")
    win.after(0, lambda: [
        btn_con.config(state="normal",
                       text=" CONNECT",
                       bg="#4ade80"),
        btn_pub.config(state="disabled"),
        btn_dis.config(state="disabled"),
        # dot.config(fg="#ef4444")
    ])
    if rc != 0:
        log(" Reconnecting in 3s...")
        win.after(3000, auto_connect)

def on_publish(c, u, mid):
    log(f" Delivered to broker!")
    log(f" MQTTController → MessageController → Model → MongoDB")
    log(f" http://localhost:5000/messages")

client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_publish    = on_publish

# ───────────────────────────────────────────
#  ACTIONS
# ───────────────────────────────────────────
def auto_connect():
    if is_connected:
        return
    log(f" Connecting to {BROKER}:{PORT}...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        log(f" Error: {e}")
        win.after(3000, auto_connect)

def connect():
    auto_connect()

def publish():
    if not is_connected:
        log("  Not connected!")
        return
    name = e_name.get().strip()
    msg  = e_msg.get().strip()
    if not name:
        log("  Name is empty!")
        return
    if not msg:
        log("  Message is empty!")
        return

    payload = json.dumps({
        "name"      : name,
        "msg"       : msg,
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    log("─" * 40)
    log(f" Publishing...")
    log(f"   topic   : {TOPIC}")
    log(f"   payload : {payload}")
    client.publish(TOPIC, payload, qos=1)

def disconnect():
    try:
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        log(f" {e}")

def log(text):
    box.config(state="normal")
    box.insert("end", text + "\n")
    box.see("end")
    box.config(state="disabled")

def clear_log():
    box.config(state="normal")
    box.delete("1.0", "end")
    box.config(state="disabled")

# ───────────────────────────────────────────
#  WINDOW CONTROLS
# ───────────────────────────────────────────
def do_minimize(): win.iconify()

def do_close():
    try:
        client.loop_stop()
        client.disconnect()
    except: pass
    win.destroy()

def drag_start(e):
    win._x = e.x; win._y = e.y

def drag_move(e):
    if win.state() == "normal":
        win.geometry(
            f"+{win.winfo_x()+e.x-win._x}"
            f"+{win.winfo_y()+e.y-win._y}"
        )

# ───────────────────────────────────────────
#  BUILD WINDOW
# ───────────────────────────────────────────
win = tk.Tk()
win.title("MQTT Publisher")
win.geometry("500x540")
win.resizable(True, True)
win.configure(bg="#0f172a")

# ── TITLE BAR ────────────────────────────────
tbar = tk.Frame(win, bg="#0d2137", height=40)
tbar.pack(fill="x", side="top")
tbar.pack_propagate(False)
tbar.bind("<ButtonPress-1>", drag_start)
tbar.bind("<B1-Motion>",     drag_move)

# ── INFO ─────────────────────────────────────
tk.Label(win,
         bg="#0f172a", fg="#1e3a5f",
         font=("Segoe UI", 9, "bold")).pack(pady=(10, 0))
tk.Label(win, text=f"Broker: {BROKER}  |  Topic: {TOPIC}",
         bg="#0f172a", fg="#334155",
         font=("Segoe UI", 8)).pack()

# ── FORM ─────────────────────────────────────
frm = tk.Frame(win, bg="#0f172a")
frm.pack(padx=26, pady=12, fill="x")

def make_field(label, row, default):
    tk.Label(frm, text=label, bg="#0f172a", fg="#94a3b8",
             font=("Segoe UI", 10), width=12,
             anchor="w").grid(row=row, column=0, pady=7, sticky="w")
    e = tk.Entry(frm, bg="#1e293b", fg="#f8fafc",
                 insertbackground="#38bdf8",
                 font=("Segoe UI", 11), relief="flat", width=28)
    e.insert(0, default)
    e.grid(row=row, column=1, padx=8, ipady=6, sticky="ew")
    return e

e_name = make_field("Name :",    0, "Alice")
e_msg  = make_field("Message :", 1, "Hello from Tkinter!")
frm.columnconfigure(1, weight=1)

tk.Label(win, text='JSON → {"name":"...","msg":"...","timestamp":"..."}',
         bg="#0f172a", fg="#92400e", font=("Segoe UI", 8)).pack()

# ── BUTTONS ──────────────────────────────────
brow = tk.Frame(win, bg="#0f172a")
brow.pack(pady=10)

btn_con = tk.Button(brow, text=" CONNECT", command=connect,
                    bg="#4ade80", fg="#000",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat", padx=14, pady=6,
                    cursor="hand2", activebackground="#22c55e")
btn_con.pack(side="left", padx=5)

btn_pub = tk.Button(brow, text=" PUBLISH", command=publish,
                    bg="#facc15", fg="#000",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat", padx=14, pady=6,
                    cursor="hand2", activebackground="#eab308",
                    state="disabled")
btn_pub.pack(side="left", padx=5)

btn_dis = tk.Button(brow, text=" DISCONNECT", command=disconnect,
                    bg="#f87171", fg="#000",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat", padx=14, pady=6,
                    cursor="hand2", activebackground="#ef4444",
                    state="disabled")
btn_dis.pack(side="left", padx=5)

# ── LOG BOX ──────────────────────────────────
lrow = tk.Frame(win, bg="#0f172a")
lrow.pack(fill="x", padx=18, pady=(8, 2))
tk.Label(lrow, text="📋 Activity Log",
         bg="#0f172a", fg="#475569",
         font=("Segoe UI", 9, "bold")).pack(side="left")
tk.Button(lrow, text="Clear", command=clear_log,
          bg="#1e293b", fg="#64748b",
          font=("Segoe UI", 8), relief="flat",
          padx=8, cursor="hand2").pack(side="right")

box = scrolledtext.ScrolledText(win, bg="#020c18", fg="#4ade80",
                                 font=("Courier New", 9),
                                 relief="flat", state="disabled")
box.pack(padx=18, pady=(0, 4), fill="both", expand=True)

tk.Label(win,
         text="  ● Run: python app.py first  "
              "● GET http://localhost:5000/messages",
         bg="#0d2137", fg="#1e3a5f",
         font=("Segoe UI", 7), anchor="w"
         ).pack(fill="x", side="bottom", ipady=3)

win.after(700, auto_connect)
win.mainloop()