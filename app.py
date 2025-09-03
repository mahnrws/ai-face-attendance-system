import cv2
import pickle
import mysql.connector

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def register_student(name, roll_number, department):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" Could not open webcam")
        return

    print(f" {name} from {department}, please look at the camera... Press 'q' to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Failed to capture frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            face_blob = pickle.dumps(face_crop)

            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='face_attendance'
                )
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO students (name, roll_number, department, face_image) VALUES (%s, %s, %s, %s)",
                    (name, roll_number, department, face_blob)
                )
                conn.commit()
                cursor.close()
                conn.close()

                print(f" {name} from {department} registered successfully!")
            except mysql.connector.Error as err:
                print(f" Database error: {err}")
            finally:
                cap.release()
                cv2.destroyAllWindows()
                return

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow('Register Face', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(" Cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(" Face not registered.")

def start_registration():
    print("\n Face Registration Started\n")
    while True:
        name = input("Enter student name (or type 'exit' to quit): ")
        if name.lower() == 'exit':
            print(" Exiting registration.")
            break
        roll_number = input("Enter roll number: ")
        department = input("Enter department: ")
        register_student(name, roll_number, department)

start_registration()