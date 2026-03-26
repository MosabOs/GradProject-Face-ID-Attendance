"""
===================================================
الملف الأول: تسجيل وجوه الطلاب (DeepFace)
===================================================
قبل التشغيل، ثبّت المكتبات:
    pip install opencv-python deepface numpy

كيفية الاستخدام:
    python register_student.py

سيطلب منك إدخال اسم الطالب ورقمه،
ثم يفتح الكاميرا لالتقاط صورة وجهه.
"""

import cv2
import numpy as np
import os
import pickle
from deepface import DeepFace

# مجلد حفظ بيانات الطلاب
STUDENTS_DATA_FILE = "students_data.pkl"

def load_students_data():
    """Load previously saved student data"""
    if os.path.exists(STUDENTS_DATA_FILE):
        with open(STUDENTS_DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {"names": [], "ids": [], "images": []}

def save_students_data(data):
    """Save student data"""
    with open(STUDENTS_DATA_FILE, "wb") as f:
        pickle.dump(data, f)
    print("The student's data has been successfully saved ✅")

def register_student():
    """Register a new student"""
    print("=" * 50)
    print(" Student registration system - Smart Attendance (DeepFace)")
    print("=" * 50)

    # إدخال بيانات الطالب
    student_name = input("\nEnter student name: ").strip()
    student_id = input("Enter student ID: ").strip()

    if not student_name or not student_id:
        print("❌ Name and ID are required")
        return

    # فتح الكاميرا
    print("\n📷 Opening camera... Look at the camera and press SPACE to capture the image")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera not found")
        return

    captured_image = None

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("❌ Failed to read from camera")
            continue

        display_frame = frame.copy()

        cv2.putText(display_frame, "Press SPACE to capture | Q to quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Student: {student_name}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Register Student", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("❌ Operation cancelled")
            break

        elif key == ord(' '):  # SPACE
            try:
                # 🔥 DeepFace face detection
                result = DeepFace.extract_faces(frame, enforce_detection=True)

                if len(result) == 0:
                    print("⚠️ No face detected. Try again.")
                    continue
                elif len(result) > 1:
                    print("⚠️ Multiple faces detected. Only one allowed.")
                    continue
                else:
                    captured_image = frame
                    print(f"✅ Face of {student_name} captured successfully")
                    break

            except:
                print("⚠️ No face detected. Try again.")
                continue

    cap.release()
    cv2.destroyAllWindows()

    # حفظ البيانات
    if captured_image is not None:
        data = load_students_data()

        if student_id in data["ids"]:
            print(f"⚠️ Student ID {student_id} is already registered")
            return

        data["names"].append(student_name)
        data["ids"].append(student_id)
        data["images"].append(captured_image)

        save_students_data(data)

        print(f"\n✅ Student registered: {student_name} | ID: {student_id}")
        print(f"📊 Total registered students: {len(data['names'])}")

if __name__ == "__main__":
    register_student()