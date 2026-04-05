"""
===================================================
Flask Web App - Smart Attendance System
===================================================
تشغيل:
    pip install flask
    python app.py

ثم افتح:
    http://127.0.0.1:5000
===================================================
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import pickle
import cv2
import subprocess
import sys
import schedule
import time
import threading

# Automatic send smail to lecture doctor PART
##################
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
RECEIVER = os.getenv("RECEIVER")

##################

app = Flask(__name__)

# ===================================================
# متغير عالمي للتحكم في الكاميرا
# ===================================================
attendance_process = None

# ===================================================
# ملف البيانات
# ===================================================
DATA_FILE = "students_data.pkl"

# ===================================================
# تحميل البيانات
# ===================================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"images": [], "names": [], "ids": []}

    with open(DATA_FILE, "rb") as f:
        return pickle.load(f)

# ===================================================
# حفظ البيانات
# ===================================================
def save_data(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

# ===================================================
# الصفحة الرئيسية
# ===================================================
@app.route("/")
def index():
    return render_template("index.html")

# ===================================================
# تسجيل طالب
# ===================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        student_id = request.form.get("student_id")

        file = request.files.get("image")
        image = None

        # ===================================================
        # تحديد مصدر الصورة
        # ===================================================
        if (file is None or file.filename == "") and os.path.exists("temp_capture.jpg"):
            image = cv2.imread("temp_capture.jpg")

        elif file and file.filename != "":
            filepath = "temp.jpg"
            file.save(filepath)
            image = cv2.imread(filepath)
            os.remove(filepath)

        else:
            return "Please upload image or use camera"

        # ===================================================
        # حفظ الصورة داخل images/
        # ===================================================
        if not os.path.exists("images"):
            os.makedirs("images")

        safe_name = name.replace(" ", "_")
        image_filename = f"images/{safe_name}.jpg"

        counter = 1
        while os.path.exists(image_filename):
            image_filename = f"images/{safe_name}_{counter}.jpg"
            counter += 1

        cv2.imwrite(image_filename, image)

        # ===================================================
        # حفظ البيانات
        # ===================================================
        data = load_data()

        data["images"].append(image_filename)
        data["names"].append(name)
        data["ids"].append(student_id)

        save_data(data)

        # حذف المؤقت
        if os.path.exists("temp_capture.jpg"):
            os.remove("temp_capture.jpg")

        # ===================================================
        # صفحة النجاح
        # ===================================================
        return render_template("success.html",
                               name=name,
                               student_id=student_id,
                               image_path=image_filename)

    return render_template("register.html")

# ===================================================
# تشغيل الكاميرا للتسجيل
# ===================================================
@app.route("/register_camera", methods=["POST"])
def register_camera():

    name = request.form.get("name")
    student_id = request.form.get("student_id")

    subprocess.run([
        sys.executable,
        "registration/register_student_using_camera.py",
        name,
        student_id
    ])

    return render_template("register.html",
                           name=name,
                           student_id=student_id,
                           captured=True)

# ===================================================
# عرض الصور
# ===================================================
@app.route('/image/<path:filename>')
def get_uploaded_image(filename):
    return send_file(filename, mimetype='image/jpeg')

# ===================================================
# تشغيل الحضور (فتح الكاميرا)
# ===================================================
@app.route("/attendance")
def attendance():

    global attendance_process

    # حذف أي نتيجة قديمة
    if os.path.exists("attendance_result.txt"):
        os.remove("attendance_result.txt")

    # حذف أي stop قديم
    if os.path.exists("stop_signal.txt"):
        os.remove("stop_signal.txt")

    # تشغيل الكاميرا في process منفصل
    attendance_process = subprocess.Popen(
        [sys.executable, "attendance_mqtt.py"]
    )

    return render_template("attendance_wait.html")

# ===================================================
# إيقاف الكاميرا (عند الضغط Back)
# ===================================================
@app.route("/stop_camera")
def stop_camera():

    global attendance_process

    #  إرسال إشارة إيقاف للبرنامج
    open("stop_signal.txt", "w").close()

    if attendance_process is not None:
        try:
            attendance_process.terminate()   # إيقاف الكاميرا
            print("Camera process terminated")
        except:
            pass

        attendance_process = None

    # حذف النتيجة حتى لا يتم التحويل
    if os.path.exists("attendance_result.txt"):
        os.remove("attendance_result.txt")

    return jsonify({"status": "stopped"})

# ===================================================
# فحص النتيجة (Polling)
# ===================================================
@app.route("/check_result")
def check_result():

    if not os.path.exists("attendance_result.txt"):
        return jsonify({"status": "waiting"})

    with open("attendance_result.txt", "r") as f:
        data = f.read()

    # حذف بعد القراءة
    os.remove("attendance_result.txt")

    status, name = data.split(":")

    return jsonify({"status": status, "name": name})

# ===================================================
# عرض النتيجة
# ===================================================
@app.route("/result/<status>/<name>")
def result(status, name):
    return render_template("attendance_result.html",
                           status=status,
                           name=name)



# ===================================================
# Dashboard - عرض سجل الحضور
# ===================================================
@app.route("/dashboard")
def dashboard():

    import sqlite3

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT student_name, student_id, date, time, status FROM attendance ORDER BY date DESC, time DESC")

    records = cursor.fetchall()

    conn.close()

    # إرسال الإيميل (مرة واحدة لكل فتح)
    # send_email_report(records)

    return render_template("dashboard.html", records=records)



# ===================================================
# إرسال تقرير الحضور لليوم فقط (HTML)
# ===================================================
def send_today_report():

    import sqlite3
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_name, student_id, date, time, status
        FROM attendance
        WHERE date = ?
        ORDER BY time ASC
    """, (today,))

    records = cursor.fetchall()
    conn.close()

    if not records:
        print("No attendance today")
        return

    # ===================================================
    # تجهيز HTML للإيميل
    # ===================================================
    logo1 = "https://i.imgur.com/6OpSVtr.png"   # IUA Logo
    logo2 = "https://i.imgur.com/qoSuHBm.png"   # IUA Engineer faculty logo

    html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">

        <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px; box-shadow:0px 0px 10px rgba(0,0,0,0.1);">

            <!-- ===================================================
                 اللوقوهات
            =================================================== -->
            <table style="width:100%; margin-bottom:10px;">
                <tr>
                    <td style="text-align:left;">
                        <img src="{logo1}" width="90">
                    </td>
                    <td style="text-align:right;">
                        <img src="{logo2}" width="90">
                    </td>
                </tr>
            </table>

            <h2 style="color:#181f69; text-align:center;">
                IUA Smart AI Attendance System Report
            </h2>
            <h3 style="color:#181f69; text-align:center;">
                IUA Faculty Of Engineer
            </h3>

            <p style="text-align:center; color:#555;">
                Date: {today}
            </p>

            <table style="width:100%; border-collapse:collapse; margin-top:20px;">

                <tr style="background:#181f69; color:white;">
                    <th style="padding:10px;">Name</th>
                    <th style="padding:10px;">ID</th>
                    <th style="padding:10px;">Time</th>
                    <th style="padding:10px;">Status</th>
                </tr>
    """

    for r in records:
        name, student_id, date, time_, status = r

        html += f"""
        <tr style="text-align:center;">
            <td style="padding:10px; border-bottom:1px solid #ddd;">{name}</td>
            <td style="padding:10px; border-bottom:1px solid #ddd;">{student_id}</td>
            <td style="padding:10px; border-bottom:1px solid #ddd;">{time_}</td>
            <td style="padding:10px; border-bottom:1px solid #ddd; color:green; font-weight:bold;">
                {status}
            </td>
        </tr>
        """

    html += """
            </table>

            <p style="margin-top:20px; text-align:center; color:#888; font-size:12px;">
                This is an automated report from IUA Smart AI Attendance System
            </p>

        </div>

    </body>
    </html>
    """

    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Attendance Report - {today}"
        msg["From"] = EMAIL
        msg["To"] = RECEIVER

        # نضيف HTML بدل النص
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        server.send_message(msg)
        server.quit()

        print("Daily HTML email sent successfully")

    except Exception as e:
        print("Email error:", e)

# ===================================================
# تشغيل الإرسال اليومي تلقائياً
# ===================================================
def run_scheduler():

    #
    schedule.every().day.at("16:00").do(send_today_report)

    while True:
        schedule.run_pending()
        time.sleep(30)

# ===================================================
# تشغيل التطبيق
# ===================================================
if __name__ == "__main__":

    # تشغيل scheduler في background
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=True)