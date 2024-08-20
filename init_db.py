import sqlite3


def create_database():
    # Create admin credentials database
    conn_admin = sqlite3.connect('admin.db')
    cursor_admin = conn_admin.cursor()

    # Create a table to store admin credentials
    cursor_admin.execute('''
    CREATE TABLE IF NOT EXISTS admin_credentials (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Insert admin credentials (you can replace these with your actual admin credentials)
    cursor_admin.execute(
        "INSERT INTO admin_credentials (username, password) VALUES (?, ?)", ('admin', 'password'))

    conn_admin.commit()
    conn_admin.close()
    print("Admin credentials table created successfully.")


if __name__ == '__main__':
    create_database()
