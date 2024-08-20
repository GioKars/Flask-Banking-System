from flask import session
import string
import sqlite3
import smtplib
import random
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL = os.getenv('EMAIL_USER')
PASSW = os.getenv('EMAIL_PASSWORD')


def get_current_user_email():
    # Example implementation for session-based authentication
    if 'user_email' in session:
        return session['user_email']
    return None


def generate_otp():
    length = 6
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(length))


def store_otp(email, otp):
    """Store the OTP associated with the user's email in the database."""
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    creation_time = datetime.now()
    cursor.execute('''CREATE TABLE IF NOT EXISTS otps (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT,
                                otp INTEGER,
                                creation_time TEXT
                            );''')
    cursor.execute("INSERT INTO otps (email, otp, creation_time) VALUES (?, ?, ?)",
                   (email, otp, creation_time))
    conn.commit()
    conn.close()


def get_otp(email):
    """Retrieve the OTP and its creation time associated with the user's email from the database."""
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp, creation_time FROM otps WHERE email = ?", (email,))
    otp_data = cursor.fetchone()
    conn.close()
    return otp_data if otp_data else (None, None)


def delete_otp(email):
    """Delete the OTP entry associated with the user's email from the database."""
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
    conn.commit()
    conn.close()


def send_verification_email(email, verification_code, content):
    s = smtplib.SMTP(host="smtp.office365.com", port=587)
    s.starttls()
    s.login(EMAIL, PASSW)

    # Create the email message
    msg = EmailMessage()
    msg.set_content(f"OTP code: {verification_code}\n{content}")

    msg['Subject'] = 'OTP CODE'
    msg['From'] = EMAIL
    msg['To'] = email
    # msg.set_content('This is a test email sent using Elastic Email SMTP.')

    # Send the email
    s.send_message(msg)
    s.quit()
    return "Sent email"


def is_email_verified(email):
    # Check if the email is in the otps.db database
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM otps WHERE email = ?", (email,))
    otp_record = cursor.fetchone()
    conn.close()
    return otp_record is not None


def get_user_info(email):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, surname, balance,phone FROM accounts WHERE email = ?", (email,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info


def phone_exists(phone):
    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE phone = ?", (phone,))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except sqlite3.OperationalError as e:
        print("Table 'accounts' does not exist yet:", e)
        return False  # Return False to indicate that the phone number does not exist


def email_exists(email):
    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except sqlite3.OperationalError as e:
        print("Table 'accounts' does not exist yet:", e)
        return False  # Return False to indicate that the phone number does not exist


def is_otp_expired(creation_time_str):
    """Check if the OTP has expired."""
    # Remove the fraction of seconds from the input string
    creation_time_str = creation_time_str.split('.')[0]
    # Convert creation_time_str to a datetime object
    creation_time = datetime.strptime(creation_time_str, "%Y-%m-%d %H:%M:%S")
    # Calculate expiration time by adding 5 minutes
    expiration_time = creation_time + timedelta(minutes=5)
    # Check if the current time is past the expiration time
    return datetime.now() > expiration_time


''' PART FOR SEND FRIEND REQUESTS TO OTHER USERS '''


def create_friend_table():
    # Create friends table
    conn_friends = sqlite3.connect('bank.db')
    cursor_friends = conn_friends.cursor()
    cursor_friends.execute(
        '''CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            friend_id INTEGER,
            status TEXT 
        );''')

    # Close the cursor and connection
    cursor_friends.close()
    conn_friends.close()


def create_friend_request_table():
    # Create friend_requests table
    conn_requests = sqlite3.connect('bank.db')
    cursor_requests = conn_requests.cursor()
    cursor_requests.execute(
        '''CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY,
            from_user_id INTEGER,
            to_user_id INTEGER,
            status TEXT -- 'pending', 'accepted', 'rejected'
        );''')

    # Close the cursor and connection
    cursor_requests.close()
    conn_requests.close()


def get_friend_request(from_user_id, to_user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM friend_requests WHERE from_user_id = ? AND to_user_id = ? AND status = 'pending'", (from_user_id, to_user_id))
    request = cursor.fetchone()
    conn.close()
    return request


def create_friend_request(from_user_id, to_user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO friend_requests (from_user_id, to_user_id, status) VALUES (?, ?, 'pending')", (from_user_id, to_user_id))
    conn.commit()
    conn.close()


def get_friend_request_by_id(request_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM friend_requests WHERE id = ?", (request_id,))
    request = cursor.fetchone()
    conn.close()
    return request


def create_friend_relationship(user1_email, user2_email):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Check if the friendship already exists
    cursor.execute("SELECT * FROM friendships WHERE (user1_email = ? AND user2_email = ?) OR (user1_email = ? AND user2_email = ?)",
                   (user1_email, user2_email, user2_email, user1_email))
    existing_friendship = cursor.fetchone()

    if existing_friendship:
        return False  # Friendship already exists

    # Insert friendship into the database
    cursor.execute(
        "INSERT INTO friendships (user1_email, user2_email) VALUES (?, ?)", (user1_email, user2_email))
    conn.commit()
    conn.close()
    return True


def messages_db():
    # Create messages table
    conn_messages = sqlite3.connect('bank.db')
    cursor_messages = conn_messages.cursor()
    cursor_messages.execute(
        ''' CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        );''')

    # Close the cursor and connection
    cursor_messages.close()
    conn_messages.close()


def has_unread_messages(user_email):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Query to check if the user has any unread messages
    cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE recipient = ? AND is_read = 0", (user_email,))
    unread_count = cursor.fetchone()[0]

    conn.close()

    return unread_count > 0


# Function to fetch messages from the database
def fetch_messages(recipient_email):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT sender, content, timestamp FROM messages WHERE recipient = ? ORDER BY timestamp DESC''', (recipient_email,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    for message in messages:
        print("Sender:", message[0])
        print("Content:", message[1])
        timestamp = datetime.strptime(message[2], '%Y-%m-%d %H:%M:%S.%f')
        # Format the timestamp without milliseconds
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        print("Timestamp:", formatted_timestamp)
        print("---")

    return [{'sender': msg[0], 'content': msg[1], 'timestamp': formatted_timestamp} for msg in messages]
