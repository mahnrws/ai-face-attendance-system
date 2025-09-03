# AI Face Attendance System

An AI-driven Facial Recognition Attendance System using Python and OpenCV, designed to automate attendance tracking by detecting and recognizing faces in real time.

---

## Key Features

* **Real-Time Face Recognition**
  Detects and recognizes faces via webcam using Haar Cascade classifiers.

* **User Registration Module**
  Capture face images and register new users using `register.py`.

* **Attendance Marking**
  Marks attendance automatically when recognized, storing entries with timestamps (`mark-attendance.py`).

* **Administrative Workflow**
  Includes scripts for admin authentication and operations to manage users and attendance.

---

## Repository Structure

```
ai-face-attendance-system/
├── README.md                     # Project overview and usage
├── app.py                        # Main application logic
├── main.py                       # Entry point for launching the app
├── register.py                   # Tool for registering new users
├── mark-attendance.py            # Attendance logging module
├── admin-auth.py                 # Admin authentication handler
├── admin-operations.py           # Admin management & operations
├── haarcascade_frontalface_default.xml  # Face detection model
├── attendance.csv                # Logs of attendance records
└── …                             # Additional configuration or auxiliary files
```

---

## Prerequisites

Ensure you have the following installed:

* Python 3.7 or higher
* Required Python packages (install via pip):

  ```bash
  pip install opencv-python numpy pandas
  ```

---

## Usage

1. **Clone the repository**:

   ```bash
   git clone https://github.com/mahnrws/ai-face-attendance-system.git
   cd ai-face-attendance-system
   ```

2. **Register Users**
   Run `register.py` to capture face images and save them for each user.

3. **Launch the Application**
   Execute the main script to start attendance tracking:

   ```bash
   python main.py
   ```

4. **Mark Attendance**
   Recognized users will have their names logged into `attendance.csv` with timestamp.

5. **Admin Features**

   * Use `admin-auth.py` to authenticate.
   * `admin-operations.py` offers administrative functions like user management and attendance review.

---

## Attendance Log

Attendance is recorded in `attendance.csv` and includes:

* Username
* Date and Time (e.g., when the face was recognized)

---

## How It Works

1. **Face Detection**: Uses Haar Cascades to locate faces in video frames.
2. **Recognition**: Matches detected faces against known user face data.
3. **Attendance Logging**: Automatically logs presence with timestamps into `attendance.csv`.

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests with enhancements—new features, improved accuracy, optimized workflow, etc.

To contribute:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Add feature"`)
4. Push to your branch (`git push origin feature-name`)
5. Submit a pull request

---

## License

This project is available under the terms of the \[insert-your-license-here]—please specify or replace with the appropriate license.

---

## Acknowledgments

* **OpenCV** for its robust support of real-time computer vision
* **Haar Cascades** for effective yet efficient face detection
* **Built by mahnrws**

---
