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

from flask import Flask, render_template, request, send_file
import os
import pickle
import cv2
import subprocess

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
# تسجيل طالب (رفع صورة أو بعد الكاميرا)
# ===================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        student_id = request.form.get("student_id")

        file = request.files.get("image")

        image = None

        # ===================================================
        # تحديد مصدر الصورة (كاميرا أو رفع)
        # ===================================================

        # 🟢 حالة الكاميرا
        if (file is None or file.filename == "") and os.path.exists("temp_capture.jpg"):
            image = cv2.imread("temp_capture.jpg")

        # 🟣 حالة رفع صورة
        elif file and file.filename != "":
            filepath = "temp.jpg"
            file.save(filepath)
            image = cv2.imread(filepath)
            os.remove(filepath)

        # 🔴 لا يوجد صورة
        else:
            return "Please upload image or use camera"

        # ===================================================
        # حفظ الصورة كملف حقيقي داخل images/
        # ===================================================
        if not os.path.exists("images"):
            os.makedirs("images")

        # تنظيف الاسم (منع مشاكل في اسم الملف)
        safe_name = name.replace(" ", "_")

        image_filename = f"images/{safe_name}.jpg"

        # منع التكرار
        counter = 1
        original_filename = image_filename

        while os.path.exists(image_filename):
            image_filename = f"images/{safe_name}_{counter}.jpg"
            counter += 1

        # حفظ الصورة
        cv2.imwrite(image_filename, image)

        # ===================================================
        # حفظ البيانات (نخزن المسار بدل الصورة)
        # ===================================================
        data = load_data()

        data["images"].append(image_filename)
        data["names"].append(name)
        data["ids"].append(student_id)

        save_data(data)

        # حذف الصورة المؤقتة
        if os.path.exists("temp_capture.jpg"):
            os.remove("temp_capture.jpg")

        # ===================================================
        # عرض صفحة النجاح مع الصورة
        # ===================================================
        return render_template("success.html",
                               name=name,
                               student_id=student_id,
                               image_path=image_filename)

    return render_template("register.html")

# ===================================================
# تشغيل الكاميرا + الرجوع تلقائي
# ===================================================
@app.route("/register_camera", methods=["POST"])
def register_camera():

    name = request.form.get("name")
    student_id = request.form.get("student_id")

    subprocess.run([
        "python",
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
# تسجيل حضور
# ===================================================
@app.route("/attendance")
def attendance():
    subprocess.Popen(["python", "attendance_mqtt.py"])
    return "Attendance system started"

# ===================================================
if __name__ == "__main__":
    app.run(debug=True)