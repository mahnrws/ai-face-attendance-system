# AI Face Attendance System

An AI-driven **Facial Recognition Attendance System** built with Python, OpenCV, and MySQL.
The system automates attendance tracking by detecting and recognizing faces in real time, then securely storing logs in a relational database.

---

## Features

* **Real-Time Face Recognition**
  Detects and recognizes faces using Haar Cascade classifiers.

* **User Registration**
  Register new users by capturing face images (`register.py`).

* **Attendance Logging**
  Recognized users are automatically logged into a **MySQL database** with timestamps (`mark-attendance.py`).

* **Admin Dashboard**
  Admin authentication (`admin-auth.py`) and operations (`admin-operations.py`) to manage users and review attendance records.

* **Database Integration**
  Attendance records are stored in a **MySQL table**, enabling structured queries and analytics.

---

## Repository Structure

```
ai-face-attendance-system/
├── README.md                     # Project overview and usage
├── app.py                        # Core app logic
├── main.py                       # Entry point for running the system
├── register.py                   # Register new users
├── mark-attendance.py            # Logs attendance into MySQL
├── admin-auth.py                 # Admin authentication
├── admin-operations.py           # Admin functions
├── haarcascade_frontalface_default.xml  # Pretrained model for face detection
├── requirements.txt              # Python dependencies
└── database_setup.sql            # SQL script to create tables
```

---

## Tech Stack

* **Python 3.7+**
* **OpenCV** – face detection and recognition
* **NumPy, Pandas** – data handling
* **MySQL** – database for attendance logs
* **Haar Cascades** – face detection model

---

## Prerequisites

1. Install Python 3.7+
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Install and configure **MySQL**.

   Example setup:

   ```sql
   CREATE DATABASE attendance_system;

   USE attendance_system;

   CREATE TABLE attendance (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(100) NOT NULL,
       date DATE NOT NULL,
       time TIME NOT NULL
   );
   ```

   Update your database credentials in the Python scripts where `mysql.connector` or `pymysql` is used.

---

## Usage

1. **Clone the repository**

   ```bash
   git clone https://github.com/mahnrws/ai-face-attendance-system.git
   cd ai-face-attendance-system
   ```

2. **Register Users**
   Run:

   ```bash
   python register.py
   ```

   This captures and stores face data for new users.

3. **Run the System**
   Start the main application:

   ```bash
   python main.py
   ```

4. **Mark Attendance**
   Recognized users will be logged into the **MySQL attendance table** with timestamps.

5. **Admin Functions**

   * Authenticate: `python admin-auth.py`
   * Perform operations: `python admin-operations.py`

---

## Attendance Storage

All logs are stored in **MySQL** with the following fields:

* `id` (Primary Key)
* `username`
* `date`
* `time`

This enables robust reporting and querying compared to CSV files.

---

## Contributing

Contributions are welcome.

1. Fork this repo
2. Create your feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Added feature"`)
4. Push to the branch (`git push origin feature-name`)
5. Open a pull request

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

* OpenCV for real-time computer vision
* Haar Cascades for efficient face detection
* MySQL for reliable data storage
* Developed by **Mahnoor Waqas**

---
