from flask import Flask, render_template
from user_routes import user_bp
from admin_routes import admin_bp
from bank_account import BankAccount 
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)


@app.before_request
def initialize_database():
    if not getattr(app, '_db_initialized', False):
        BankAccount()
        app._db_initialized = True
        print("bank.db created")


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
