import sqlite3
import bcrypt


class BankAccount:
    def __init__(self):
        # Initialize database connection
        self.conn = sqlite3.connect('bank.db')
        self.conn.row_factory = sqlite3.Row  # Access row columns by name
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                surname TEXT,
                                email TEXT UNIQUE,
                                phone VARCHAR(10) UNIQUE,
                                password TEXT,
                                sex TEXT,
                                balance FLOAT,
                                approved INTEGER
                              )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS deposit_history (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT,
                                amount REAL,
                                datetime TEXT,
                                FOREIGN KEY (email) REFERENCES accounts(email)
                            );''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS withdrawal_history (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT,
                                amount REAL,
                                datetime TEXT,
                                FOREIGN KEY (email) REFERENCES accounts(email)
                            );''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transfer_history (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                sender_id INTEGER,
                                recipient_id INTEGER,
                                amount REAL,
                                datetime TEXT,
                                FOREIGN KEY (sender_id) REFERENCES accounts (id),
                                FOREIGN KEY (recipient_id) REFERENCES accounts (id)
                            );''')
        self.conn.commit()

    def create_user(self, name, surname, email, phone, password, sex, balance=0, approved=False):
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        self.cursor.execute('''INSERT INTO accounts (name, surname, email, phone, password, sex, balance, approved) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (name, surname, email, phone, hashed_password, sex.upper(), balance, approved))
        self.conn.commit()

    def get_all_accounts(self):
        self.cursor.execute("SELECT * FROM accounts")
        return self.cursor.fetchall()

    def update_balance(self, email, deposit_amount):
        try:
            self.cursor.execute(
                "UPDATE accounts SET balance = balance + ? WHERE email = ?", (deposit_amount, email))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error updating balance:", e)
            return False

    def withdraw_balance(self, email, withdraw_amount):
        try:
            self.cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE email = ?", (withdraw_amount, email))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error updating balance:", e)
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()
