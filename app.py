import sqlite3
from flask import Flask, render_template, redirect, url_for, request
from flask_mail import Mail, Message
from user_routes import user_bp
from admin_routes import admin_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

mail = Mail(app)


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/test')
# def test():
#     conn = sqlite3.connect('bank.db')
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT accounts.email FROM accounts INNER JOIN otps ON accounts.email = otps.email;")
#     # Fetch all rows from the result
#     rows = cursor.fetchall()
#     conn.close()
#     # Pass the fetched data to the template
#     return render_template('test.html', data=rows)


# @app.route('/delete', methods=['POST'])
# def delete_record():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         conn = sqlite3.connect('bank.db')
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM accounts WHERE email = ?", (email,))
#         cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
#         # cursor.execute("DELETE FROM otps")
#         conn.commit()
#         conn.close()
#         return redirect(url_for('test'))


if __name__ == '__main__':
    app.run(debug=True)
