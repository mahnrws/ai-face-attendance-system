from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import cv2
import pickle
import mysql.connector
import numpy as np
from datetime import datetime
import bcrypt
import base64
import os
import urllib.request

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here'

camera = None
recognizer = None
face_cascade = None

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'face_attendance'
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def download_haar_cascade():
    cascade_path = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(cascade_path):
        print("Downloading Haar cascade file...")
        url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
        urllib.request.urlretrieve(url, cascade_path)
        print("Haar cascade file downloaded.")
    return cascade_path


def initialize_face_detection():
    global face_cascade
    try:
        cascade_path = download_haar_cascade()
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            raise Exception("Cascade classifier not loaded")
        print("Face detection initialized.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def load_faces_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, roll_number, department, face_image FROM students WHERE face_image IS NOT NULL")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        faces, labels, label_map = [], [], {}
        for row in rows:
            student_id, name, roll, dept, face_blob = row
            try:
                face = pickle.loads(face_blob)
                faces.append(face)
                labels.append(student_id)
                label_map[student_id] = {'name': name, 'roll': roll, 'dept': dept}
            except:
                continue

        return faces, labels, label_map
    except Exception as e:
        print(f"Error loading faces: {e}")
        return [], [], {}


def train_recognizer():
    global recognizer
    try:
        faces, labels, label_map = load_faces_from_db()
        if faces:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, np.array(labels))
            print(f"Trained on {len(faces)} face(s).")
            return True, label_map
        else:
            return False, {}
    except Exception as e:
        print(f"Recognizer error: {e}")
        return False, {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/register', methods=['POST'])
def register_student():
    try:
        data = request.json
        name = data.get('name')
        roll = data.get('roll')
        dept = data.get('department')

        if not all([name, roll, dept]):
            return jsonify({'success': False, 'message': 'All fields are required'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE roll_number = %s", (roll,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Roll number already exists'})

        cursor.execute(
            "INSERT INTO students (name, roll_number, department) VALUES (%s, %s, %s)",
            (name, roll, dept)
        )
        student_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'student_id': student_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/capture_face', methods=['POST'])
def capture_face():
    try:
        data = request.json
        student_id = data.get('student_id')
        image_data = data.get('image_data')

        if not student_id or not image_data:
            return jsonify({'success': False, 'message': 'Missing data'})

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if not len(faces):
            return jsonify({'success': False, 'message': 'No face detected'})

        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_crop = gray[y:y + h, x:x + w]
        face_resized = cv2.resize(face_crop, (200, 200))

        face_blob = pickle.dumps(face_resized)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET face_image = %s WHERE id = %s", (face_blob, student_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Face captured'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.json
        roll_number = data.get('roll_number')
        image_data = data.get('image_data')

        if not roll_number or not image_data:
            return jsonify({'success': False, 'message': 'Missing data'})

        success, label_map = train_recognizer()
        if not success:
            return jsonify({'success': False, 'message': 'No registered faces'})

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if not len(faces):
            return jsonify({'success': False, 'message': 'No face detected'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, department FROM students WHERE roll_number = %s", (roll_number,))
        student_data = cursor.fetchone()

        if not student_data:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Student not found'})

        student_id, name, dept = student_data

        cursor.execute(
            "SELECT id FROM attendance_log WHERE roll_number = %s AND DATE(timestamp) = CURDATE()",
            (roll_number,)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Attendance already marked'})

        for (x, y, w, h) in faces:
            face_crop = gray[y:y + h, x:x + w]
            face_resized = cv2.resize(face_crop, (200, 200))

            predicted_id, confidence = recognizer.predict(face_resized)

            if predicted_id == student_id and confidence < 70:
                cursor.execute(
                    "INSERT INTO attendance_log (roll_number, name, department) VALUES (%s, %s, %s)",
                    (roll_number, name, dept)
                )
                conn.commit()
                cursor.close()
                conn.close()

                return jsonify({'success': True, 'message': f'Attendance marked for {name}', 'confidence': float(confidence)})

        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Face not recognized'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/admin_login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM admins WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/students')
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, roll_number, department FROM students ORDER BY name")
        students = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'students': [
                {'id': row[0], 'name': row[1], 'roll': row[2], 'department': row[3]} for row in students
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/attendance_log')
def get_attendance_log():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT roll_number, name, department, timestamp FROM attendance_log "
            "WHERE DATE(timestamp) = CURDATE() ORDER BY timestamp DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'attendance': [
                {'roll': r[0], 'name': r[1], 'department': r[2], 'time': r[3].strftime('%H:%M:%S')}
                for r in rows
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance_log WHERE DATE(timestamp) = CURDATE()")
        today_attendance = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
        total_departments = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_students': total_students,
                'today_attendance': today_attendance,
                'total_departments': total_departments
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    if initialize_face_detection():
        print("Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Face detection initialization failed.")
