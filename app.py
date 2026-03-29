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
import sys  # لتشغيل نفس بيئة البايثون

app = Flask(__name__)

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
# تسجيل طالب (رفع صورة أو كاميرا)
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

        # حالة الكاميرا
        if (file is None or file.filename == "") and os.path.exists("temp_capture.jpg"):
            image = cv2.imread("temp_capture.jpg")

        # حالة رفع صورة
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
        # حفظ البيانات (نخزن المسار)
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
# تسجيل حضور (تشغيل الكاميرا بدون كتم)
# ===================================================
@app.route("/attendance")
def attendance():

    # حذف أي نتيجة قديمة
    if os.path.exists("attendance_result.txt"):
        os.remove("attendance_result.txt")

    # تشغيل الكاميرا
    subprocess.Popen(
        [sys.executable, "attendance_mqtt.py"]
    )

    # عرض صفحة انتظار
    return render_template("attendance_wait.html")


# ===================================================
# فحص نتيجة الحضور
# ===================================================
@app.route("/check_result")
def check_result():

    if not os.path.exists("attendance_result.txt"):
        return jsonify({"status": "waiting"})

    with open("attendance_result.txt", "r") as f:
        data = f.read()

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
# تشغيل التطبيق
# ===================================================
if __name__ == "__main__":
    app.run(debug=True)