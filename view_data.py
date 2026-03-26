import pickle
import cv2

# تحميل البيانات
with open("students_data.pkl", "rb") as f:
    data = pickle.load(f)

names = data["names"]
ids = data["ids"]
images = data["images"]

print(f"Total students: {len(names)}")

# عرض كل الطلاب
for i in range(len(names)):
    print("=" * 40)
    print(f"Name: {names[i]}")
    print(f"ID: {ids[i]}")

    img = images[i]

    # عرض الصورة
    # img = img.astype('uint8')
    cv2.imshow(f"Student {i+1}", img)

    print("Press any key to show next student...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

print("✅ Done viewing all students")