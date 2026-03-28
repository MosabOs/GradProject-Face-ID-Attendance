"""
===================================================
الملف الأول: تسجيل وجوه الطلاب باستخدام الكاميرا (DeepFace)
===================================================
قبل التشغيل، ثبّت المكتبات:
    pip install opencv-python deepface numpy

كيفية الاستخدام:
    python register_student.py

سيطلب منك إدخال اسم الطالب ورقمه،
ثم يفتح الكاميرا لالتقاط صورة وجهه.
"""

"""
===================================================
تسجيل طالب باستخدام الكاميرا (بدون إدخال متكرر)
===================================================
"""

"""
===================================================
تسجيل طالب باستخدام الكاميرا (مرحلة الالتقاط فقط)
===================================================
"""

import cv2
import sys

# استقبال الاسم و ID
if len(sys.argv) < 3:
    print("Name and ID required")
    exit()

name = sys.argv[1]
student_id = sys.argv[2]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # تعليمات داخل الكاميرا
    cv2.putText(frame, "Press SPACE to capture", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)

    if key == 32:
        cv2.imwrite("temp_capture.jpg", frame)
        break

    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
