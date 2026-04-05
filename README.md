# GradProject-Face-ID-Attendance
Face ID Attendance Graduation Project 

# AttendAI - Smart Attendance System using AI

## Overview
AttendAI is an intelligent attendance system that uses face recognition and MQTT communication to automate student attendance tracking.

The system integrates:
- Face Recognition (DeepFace)
- Real-time camera processing (OpenCV)
- Web interface (Flask)
- IoT communication (MQTT with ESP32 / Wokwi)
- Automated email reporting

---

## Features
- Register students with face images
- Real-time face recognition using camera
- Automatic attendance recording
- Prevent duplicate attendance
- Dashboard for attendance records
- Daily email reports (HTML format)
- MQTT integration with ESP32

---

## Technologies Used
- Python
- Flask
- OpenCV
- DeepFace
- SQLite
- MQTT (paho-mqtt)
- HTML / CSS

---


---

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd FACE-IO-main
```


## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the System

### Start Flask App:
```bash
python app.py
```

Then open in your browser:
```
http://127.0.0.1:5000
```

---

## Usage

### 📝 Register Student
- Upload image or use camera
- Save student data

### ✅ Attendance
- Click "Attendance"
- Camera starts automatically
- System detects and records attendance

### 📊 Dashboard
- View attendance records grouped by date

---

## MQTT Setup

| Property | Value |
|----------|-------|
| **Broker** | `broker.hivemq.com` |
| **Topic** | `smartattendance/result` |
| **Usage** | Communication with ESP32 (Wokwi simulation supported) |

---

## Email Configuration

### a. Create a `.env` file:
```env
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
RECEIVER=doctor_email@gmail.com
```

### ⚠️ Important Note:
Use **App Password** instead of your real Gmail password for enhanced security.

---

## Technical Notes

| File | Description |
|------|-------------|
| `students_data.pkl` | Stores registered students data |
| `attendance.db` | Stores attendance records |

> **To reset data:** Delete these files

---

## Future Improvements

- ✨ Live camera streaming in browser
- 📱 Mobile app integration
- 📈 Advanced analytics dashboard




# Author:
- Mosab Osama
- Amro Maher
