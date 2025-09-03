import cv2
import pickle
import mysql.connector
import numpy as np
from datetime import datetime

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='face_attendance'
    )

def load_faces_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_number, department, face_image FROM students")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    faces = []
    labels = []
    label_map = {}
    roll_to_id = {}

    for row in rows:
        student_id, name, roll, dept, face_blob = row
        if face_blob is None:
            print(f" Skipping student '{name}' (Roll: {roll}) - no face image found.")
            continue
        face = pickle.loads(face_blob)
        faces.append(face)
        labels.append(student_id)
        label_map[student_id] = (name, roll, dept)
        roll_to_id[roll] = student_id

    return faces, labels, label_map, roll_to_id

marked_ids = set()

def mark_attendance(student_id, label_map):
    if student_id in marked_ids:
        return

    name, roll, dept = label_map[student_id]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance_log (roll_number, name, department) VALUES (%s, %s, %s)",
        (roll, name, dept)
    )
    conn.commit()
    cursor.close()
    conn.close()

    marked_ids.add(student_id)
    print(f" Attendance marked: {name} ({roll}) - {dept} at {datetime.now().strftime('%H:%M:%S')}")

def mark_single_student(user_id, label_map, recognizer):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" Webcam not found")
        return False

    print(" Camera is on. Look at the camera. Press 'q' to stop this session.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Failed to read from webcam")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rects = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        found_user = False

        for (x, y, w, h) in faces_rects:
            face_crop = gray[y:y + h, x:x + w]

            try:
                student_id, confidence = recognizer.predict(face_crop)

                if student_id == user_id and confidence < 70:
                    name, roll, dept = label_map[student_id]
                    mark_attendance(student_id, label_map)
                    label_text = f"{name}  ({int(confidence)})"
                    color = (0, 255, 0)  # Green
                    found_user = True
                else:
                    label_text = "Unknown"
                    color = (0, 0, 255)  # Red

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label_text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            except Exception as e:
                cv2.putText(frame, "Recognition Error", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                print(f" Recognition error: {e}")

        cv2.imshow('Attendance', frame)
        key = cv2.waitKey(1) & 0xFF

        if found_user:
            print(" Face recognized and attendance marked.")
            break

        if key == ord('q'):
            print("\n Stopping this attendance session.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return found_user

def start_attendance():
    print("\n Starting Attendance System\n")

    faces, labels, label_map, roll_to_id = load_faces_from_db()
    if not faces:
        print(" No registered faces found. Please register students with face images first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    while True:
        user_roll = input("\nEnter roll number to mark attendance or type 'exit' to quit: ").strip()

        if user_roll.lower() == 'exit':
            print(" Exiting Attendance System.")
            break

        if user_roll not in roll_to_id:
            print(f" Roll number '{user_roll}' not found in database. Try again.")
            continue

        user_id = roll_to_id[user_roll]

        print(f"\nPlease look at the camera, {label_map[user_id][0]} (Roll: {user_roll})")

        marked = mark_single_student(user_id, label_map, recognizer)

        if not marked:
            print(" Attendance could not be marked for this student. Try again.")

start_attendance()