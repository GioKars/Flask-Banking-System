from flask import Blueprint, make_response, render_template, redirect, url_for, session, request, flash
import sqlite3
from datetime import datetime
from bank_account import BankAccount
from helpers_func import get_user_info

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/adminlogin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_credentials WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            # session['logged_in'] = True -----NOT CORRECT-----
            session['user_type'] = 'admin'
            return redirect(url_for('admin.admin'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('adminlogin.html')


@admin_bp.route('/adminlogout')
def admin_logout():
    # session.pop('logged_in', None)
    # Clear session data
    session.clear()

    # Create a response that redirects to the login page
    response = make_response(redirect(url_for('admin.login_admin')))

    # Set cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # return redirect(url_for('index'))
    return response


@admin_bp.route('/admin')
def admin():
    # if 'logged_in' in session and session['logged_in']:
    if session.get('user_type') == 'admin':
        bank = BankAccount()
        accounts = bank.get_all_accounts()
        return render_template('admin.html', accounts=accounts)
    else:
        return redirect(url_for('admin.login_admin'))


@admin_bp.route('/approve/<int:account_id>')
def approve(account_id):
    if session.get('user_type') == 'admin':
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET approved = 1 WHERE id = ?", (account_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin'))
    else:
        return redirect(url_for('admin.adminlogin'))


@admin_bp.route('/toggle_freeze/<int:account_id>/<action>')
def toggle_freeze(account_id, action):
    if session.get('user_type') == 'admin':
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        if action == 'freeze':
            cursor.execute(
                "UPDATE accounts SET frozen = 1 WHERE id = ?", (account_id,))
        elif action == 'unfreeze':
            cursor.execute(
                "UPDATE accounts SET frozen = 0 WHERE id = ?", (account_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin'))
    else:
        return redirect(url_for('admin.adminlogin'))


@admin_bp.route('/transactions/<int:account_id>', methods=['GET', 'POST'])
def view_transactions(account_id):

    if session.get('user_type') == 'admin':

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email FROM accounts WHERE id = ?", (account_id,))
        user_email = cursor.fetchone()[0]

        user_info = get_user_info(user_email)
        if user_info:
            user_balance = user_info[3]
            user_initials = user_info[1].upper(
            ) + " " + user_info[2].upper()

        # Fetch deposit history
        cursor.execute(
            "SELECT amount, datetime FROM deposit_history WHERE email = ?", (user_email,))
        deposit_history = cursor.fetchall()

        # Fetch withdrawal history
        cursor.execute(
            "SELECT amount, datetime FROM withdrawal_history WHERE email = ?", (user_email,))
        withdraw_history = cursor.fetchall()

        # Fetch transfer history including sender's name
        cursor.execute("""
                SELECT th.amount, th.datetime, sender.name || ' ' || sender.surname AS sender_name,
                    recipient.name || ' ' || recipient.surname AS recipient_name
                FROM transfer_history th
                INNER JOIN accounts sender ON th.sender_id = sender.id
                INNER JOIN accounts recipient ON th.recipient_id = recipient.id
                WHERE th.sender_id = ? OR th.recipient_id = ?
            """, (user_info[0], user_info[0]))
        transfer_history = cursor.fetchall()

        print("Transfer history view transactions:", transfer_history)

        return render_template('transaction_history.html', user_initials=user_initials, user_balance=user_balance, deposit_history=deposit_history,
                               withdraw_history=withdraw_history, account_id=account_id,
                               transfer_history=transfer_history)
    else:
        return redirect(url_for('admin.login_admin'))


@admin_bp.route('/export_csv/<int:account_id>')
def export_csv(account_id):
    if session.get('user_type') == 'admin':
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email FROM accounts WHERE id = ?", (account_id,))
        user_email = cursor.fetchone()[0]

        user_info = get_user_info(user_email)

        # Fetch deposit history
        cursor.execute(
            "SELECT amount, datetime FROM deposit_history WHERE email = ?", (user_email,))
        deposit_history = cursor.fetchall()

        # Fetch withdrawal history
        cursor.execute(
            "SELECT amount, datetime FROM withdrawal_history WHERE email = ?", (user_email,))
        withdraw_history = cursor.fetchall()

        # Fetch transfer history
        cursor.execute(
            "SELECT sender_id, recipient_id, amount, datetime FROM transfer_history WHERE sender_id = ? OR recipient_id = ?", (user_info[0], user_info[0]))
        transfer_history = cursor.fetchall()
        conn.close()

        # Generate CSV content
        csv_content = "Transaction Type,Amount,Datetime\n"
        transfer = "\nTransaction Type,Sender,Recipient,Amount,Datetime\n"
        for amount, datetime in deposit_history:
            csv_content += f"Deposit,{amount},{datetime}\n"
        for amount, datetime in withdraw_history:
            csv_content += f"Withdrawal,{amount},{datetime}\n"
        csv_content += transfer
        for sender_email, recipient_email, amount, datetime in transfer_history:
            csv_content += f"Transfer,{sender_email},{recipient_email},{amount},{datetime}\n"

        # Set the desired filename
        filename = f"user_transactions_id_{account_id}_{user_info[1]}_{user_info[2]}.csv"

        # Create a response with the CSV content
        response = make_response(csv_content)

        # Set the appropriate content type and headers for a CSV file
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    else:
        return redirect(url_for('admin.login_admin'))
