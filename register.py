import cv2
import pickle
import mysql.connector
import sys
import os

if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'face_attendance',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}


def get_cascade_path():
    possible_paths = [
        'haarcascade_frontalface_default.xml',
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            print(f" Found cascade file at: {path}")
            return path
    print(" Could not find haarcascade_frontalface_default.xml")
    print(" Download from:")
    print("   https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml")
    return None


def init_database():
    try:
        config = DB_CONFIG.copy()
        config.pop('database', None)

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS face_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(" Database created or verified")

        cursor.execute("USE face_attendance")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                roll_number VARCHAR(50) NOT NULL UNIQUE,
                face_image LONGBLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
        print(" Students table created or verified")

        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(" MySQL Error:", err)
        return False


def test_database_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        print(" Database connection successful")
        return True
    except mysql.connector.Error as err:
        print(" Failed to connect to database:")
        print("    Error Code:", err.errno)
        print("    SQLSTATE:", err.sqlstate)
        print("    Message:", err.msg)
        return False


def register_student(name, roll_number, face_cascade):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" Could not open webcam")
        return False

    print(f" {name}, please look at the camera...")
    print("   - Press SPACE to capture when ready")
    print("   - Press 'q' to cancel")

    face_captured = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Failed to read frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Face Detected - Press SPACE', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if len(faces) == 0:
            cv2.putText(frame, 'No face detected', (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif len(faces) > 1:
            cv2.putText(frame, 'Multiple faces - Show only one', (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Register Face - SPACE to capture, Q to quit', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print(" Registration cancelled")
            break
        elif key == ord(' ') and len(faces) == 1:
            try:
                x, y, w, h = faces[0]
                face_crop = gray[y:y+h, x:x+w]
                face_blob = pickle.dumps(face_crop)

                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM students WHERE roll_number = %s", (roll_number,))
                if cursor.fetchone():
                    print(f" Roll number {roll_number} already exists")
                    break

                cursor.execute(
                    "INSERT INTO students (name, roll_number, face_image) VALUES (%s, %s, %s)",
                    (name, roll_number, face_blob)
                )
                conn.commit()
                cursor.close()
                conn.close()

                print(f" {name} registered successfully!")
                face_captured = True
                break
            except Exception as e:
                print(f" Error during registration: {e}")
                break

    cap.release()
    cv2.destroyAllWindows()
    return face_captured


def start_registration():
    print(" Face Registration System")
    print("=" * 40)

    if not init_database():
        return
    if not test_database_connection():
        return

    cascade_path = get_cascade_path()
    if not cascade_path:
        return

    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(" Failed to load face detection model")
        return

    while True:
        name = input("\nEnter student name (or type 'exit' to quit): ").strip()
        if name.lower() in ['exit', 'quit', '']:
            print(" Exiting registration system")
            break
        if len(name) < 2:
            print(" Name too short")
            continue

        roll_number = input("Enter roll number: ").strip()
        if not roll_number:
            print(" Invalid roll number")
            continue

        success = register_student(name, roll_number, face_cascade)

        if success:
            print(" Registration completed")
        else:
            print(" Registration failed")

        cont = input("Register another student? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            break

    print("\n Registration session complete!")


if __name__ == "__main__":
    try:
        start_registration()
    except KeyboardInterrupt:
        print("\n Interrupted by user")
    except Exception as e:
        print(f"\n Unexpected error: {e}")

