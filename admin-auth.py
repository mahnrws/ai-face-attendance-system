import mysql.connector
import bcrypt

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='face_attendance'
    )

def register_admin(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        print(" Admin registered successfully.")
    except mysql.connector.IntegrityError:
        print(" Username already exists.")
    finally:
        cursor.close()
        conn.close()

def login_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        print(f" Welcome, {username}!")
        return True
    else:
        print(" Invalid username or password.")
        return False

def logout_admin():
    print("👋 Logged out successfully.")

if __name__ == "__main__":
    session_active = False

    while True:
        print("\n=== Admin Menu ===")
        print("1. Register Admin")
        print("2. Login")
        print("3. Logout")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            uname = input("Enter new username: ")
            pw = input("Enter new password: ")
            register_admin(uname, pw)

        elif choice == '2':
            if session_active:
                print("️ Already logged in.")
                continue
            uname = input("Username: ")
            pw = input("Password: ")
            session_active = login_admin(uname, pw)

        elif choice == '3':
            if session_active:
                logout_admin()
                session_active = False
            else:
                print(" Not logged in.")

        elif choice == '4':
            print(" Goodbye!")
            break
        else:
            print(" Invalid option.")


