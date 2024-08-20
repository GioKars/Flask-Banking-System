from collections import defaultdict
import json
from flask import Blueprint, Response, Blueprint, jsonify, make_response, render_template, redirect, url_for, session, request, flash
import sqlite3
from datetime import datetime
from bank_account import BankAccount
from helpers_func import *
import bcrypt


user_bp = Blueprint('user', __name__)


@user_bp.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        print("Email from form data:", email)
        phone = request.form['phone']
        password = request.form['password']
        sex = request.form['sex']

        # Check if the phone number already exists
        if phone_exists(phone):
            flash(
                'Phone number already exists. Please use a different phone number.', 'error')
            return redirect(url_for('index'))

        # Check if the email already exists
        elif email_exists(email):
            flash('Email already exists. Please use a different email.', 'error')
            return redirect(url_for('index'))

        # Store the email in the session
        session['email'] = email

        bank = BankAccount()
        bank.create_user(name, surname, email, phone,
                         password, sex)

        # Generate and send OTP to the user's email
        verification_code = generate_otp()
        content = "the code will expire in 5 minutes\n"
        # Store OTP and creation time in the database
        store_otp(email, verification_code)
        send_verification_email(email, verification_code, content)

        welcome_message = "Welcome to My Bank! We're excited to have you with us."
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO messages (sender, recipient, content, timestamp)
                        VALUES (?, ?, ?, ?)''', ('System', email, welcome_message, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect user to the OTP verification page
        return redirect(url_for('user.verify_otp'))
    else:
        print('User has not registered')
        return redirect(url_for('index'))


@user_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = session.get('email')
        print(email)
        # entered_otp = request.form['otp']
        otp_values = request.form.getlist('otp[]')
        entered_otp = ''.join(otp_values)
        # Retrieve the OTP and its creation time associated with the user's email from the database
        otp_data = get_otp(email)
        if otp_data is not None:
            stored_otp, creation_time_str = otp_data

            # Ensure that both OTPs are strings
            stored_otp = str(stored_otp)  # Convert stored OTP to string
            entered_otp = str(entered_otp)  # Ensure entered OTP is a string

            print("stored otp: ", stored_otp)
            print("entered otp: ", entered_otp)
        else:
            flash('No OTP found for the provided email.', 'error')
            return redirect(url_for('index'))

        print("creation_time_str: ", creation_time_str)
        print(type(creation_time_str))
        print("stored otp: ", stored_otp)
        print(type(stored_otp))
        print("entered otp: ", entered_otp)
        print(type(entered_otp))

        if str(stored_otp) == entered_otp:
            if not is_otp_expired(creation_time_str):
                # Delete the OTP entry from the database
                delete_otp(email)
                return redirect(url_for('user.user_dashboard'))
            else:
                flash('OTP has expired. Please request a new OTP.', 'error')
                return redirect(url_for('user.verify_otp'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            return redirect(url_for('user.verify_otp'))

    # If the request method is GET, calculate the remaining time and render the template
    else:
        email = session.get('email')
        # session['email'] = email
        print("email on get: ", email)
        otp_data = get_otp(email)
        print("otp_data:", otp_data)
        if otp_data is not None:
            stored_otp, creation_time_str = otp_data
            print("creation_time_str:", creation_time_str)
            if creation_time_str is not None:
                creation_time_str = creation_time_str.split('.')[0]
                # Convert creation_time_str to datetime object
                creation_time = datetime.strptime(
                    creation_time_str, "%Y-%m-%d %H:%M:%S")
                print("creation: ", creation_time)
                expiration_time = creation_time + timedelta(minutes=5)
                current_time = datetime.now()
                remaining_time = expiration_time - current_time

                # Convert remaining_time to seconds
                remaining_time_seconds = max(remaining_time.total_seconds(), 0)

                # Format remaining_time as string (mm:ss)
                minutes, seconds = divmod(remaining_time_seconds, 60)
                remaining_time_str = f"{int(minutes):02d}:{int(seconds):02d}"
                print("remaining: ", remaining_time_str)

                # Convert remaining_time to seconds
                remaining_time_seconds = int(
                    max(remaining_time.total_seconds(), 0))
                print("remaining seconds: ", remaining_time_seconds)

                return render_template('verify_otp.html', remaining_time_seconds=remaining_time_seconds)
            else:
                flash('Invalid OTP. Please try again.', 'error')
                return redirect(url_for('index'))
        else:
            flash('No OTP found for the provided email.', 'error')
            return redirect(url_for('index'))


# Route to resend OTP
@user_bp.route('/resend_otp', methods=['GET'])
def resend_otp():
    if 'email' in session:
        # Generate a new OTP
        new_otp = generate_otp()

        # Update the OTP in the database
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        creation_time = datetime.now()
        cursor.execute("UPDATE otps SET otp = ? , creation_time = ?  WHERE email = ?",
                       (new_otp, creation_time, session['email']))
        conn.commit()
        conn.close()

        # Send the new OTP via email
        content = "the code will expire after 5 minutes"
        send_verification_email(session['email'], new_otp, content)

        flash('New OTP sent successfully!', 'success')

        # Redirect to the verify_otp route
        return redirect(url_for('user.verify_otp'))
    else:
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('index'))

# @user_bp.route('/login_user', methods=['GET', 'POST'])


@user_bp.route('/', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email exists in the database
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Check if the user has verified OTP
            if is_email_verified(email):
                # User has not verified OTP, redirect to verify_otp.html
                # Store email in session for verification
                session['email'] = email
                return redirect(url_for('user.verify_otp'))

            # Verify the password
            # Assuming password is stored in the 6th column
            hashed_password_from_db = user[5]
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db):
                # Store user information in session
                session['email'] = email
                session['user_type'] = 'user'
                # Assuming phone number is stored in the 5th column
                session['phone'] = user[4]
                # Redirect to user dashboard
                return redirect(url_for('user.user_dashboard'))
            else:
                flash(
                    'Invalid email or password. Please try again.', 'error')
                return redirect(url_for('index'))
                # return "Invalid email or password. Please try again."
        else:
            flash(
                'Invalid email or password. Please try again.', 'error')
            return redirect(url_for('index'))
            # return "Invalid email or password. Please try again."
    return render_template('index.html')


@user_bp.route('/userlogout')
def user_logout():

    # session.pop('logged_in', None)

    # Clear session data
    session.clear()

    # Create a response that redirects to the login page
    response = make_response(redirect(url_for('index')))

    # Set cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # return redirect(url_for('index'))
    return response


@user_bp.route('/deposit', methods=['POST'])
def deposit():
    if session.get('user_type') == 'user':
        email = session['email']
        deposit_amount = float(request.form['amount'])

        # Update user balance
        bank = BankAccount()
        success = bank.update_balance(email, deposit_amount)
        if not success:
            return "Failed to update balance. Please try again."

        # Insert deposit record into history table
        try:
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO deposit_history (email, amount, datetime) VALUES (?, ?, ?)",
                           (email, deposit_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error inserting deposit record:", e)

        return redirect(url_for('user.user_dashboard'))
    else:
        return redirect(url_for('index'))


@user_bp.route('/withdraw', methods=['POST'])
def withdraw():
    if session.get('user_type') == 'user':
        email = session['email']
        withdraw_amount = float(request.form['amount'])

        # Check if the withdrawal amount is greater than the user's balance
        user_info = get_user_info(email)
        if user_info:
            user_balance = user_info[3]
            if withdraw_amount > user_balance:
                flash("You don't have sufficient balance for this withdrawal.", "error")
                return redirect(url_for('user.user_dashboard'))

        bank = BankAccount()
        success = bank.withdraw_balance(email, withdraw_amount)
        if not success:
            return "Failed to update balance. Please try again."

        # Record the withdrawal in the withdrawal_history table
        try:
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO withdrawal_history (email, amount, datetime) VALUES (?, ?, ?)",
                           (email, - withdraw_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error inserting deposit record:", e)

        return redirect(url_for('user.user_dashboard'))
    else:
        return redirect(url_for('index'))


@user_bp.route('/transfer', methods=['POST'])
def transfer():
    if session.get('user_type') == 'user':
        sender_email = session['email']
        recipient_phone = request.form['recipient_phone']
        transfer_amount = float(request.form['transfer_amount'])

        # Check if the recipient's phone number exists in the database
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE phone = ?",
                       (recipient_phone,))
        recipient = cursor.fetchone()

        if recipient:
            # Assuming email is stored in the 4th column
            recipient_email = recipient[3]
            if sender_email != recipient_email:
                sender_info = get_user_info(sender_email)
                if sender_info:
                    sender_balance = sender_info[3]
                    if transfer_amount <= sender_balance:
                        # Deduct the transfer amount from the sender's balance
                        bank = BankAccount()
                        success = bank.withdraw_balance(
                            sender_email, transfer_amount)
                        if success:
                            # Update the recipient's balance
                            # Assuming id is stored in the 1st column
                            recipient_id = recipient[0]
                            # Assuming balance is stored in the 8th column
                            recipient_balance = recipient[7]
                            recipient_new_balance = recipient_balance + transfer_amount
                            cursor.execute(
                                "UPDATE accounts SET balance = ? WHERE phone = ?", (recipient_new_balance, recipient_phone))

                            # Insert transfer record into transfer history
                            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO transfer_history (sender_id, recipient_id, amount, datetime) VALUES (?, ?, ?, ?)",
                                           (sender_info[0], recipient_id, transfer_amount, current_datetime))
                            conn.commit()
                            conn.close()
                            return "Transfer successful!"
                        else:
                            return "Failed to process transfer. Please try again."
                    else:
                        return "Transfer amount exceeds your balance."
                else:
                    return "Failed to retrieve sender information. Please try again."
            else:
                return "You cannot transfer money to yourself."
        else:
            return "Recipient phone number not found."
    else:
        return redirect(url_for('index'))


@user_bp.route('/user_transactions',  methods=['GET', 'POST'])
def user_transactions():
    if session.get('user_type') == 'user':
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        user_email = session.get('email')

        user_info = get_user_info(user_email)
        if user_info:
            user_balance = user_info[3]
            user_initials = user_info[1].upper() + " " + user_info[2].upper()

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

        conn.close()

        return render_template('transaction_history.html', user_initials=user_initials, user_balance=user_balance, deposit_history=deposit_history,
                               withdraw_history=withdraw_history, transfer_history=transfer_history)
    else:
        return redirect(url_for('index'))


@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('user_type') == 'user':
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        user_email = session.get('email')
        user_info = get_user_info(user_email)
        user_initials = user_info[1].upper(
        ) + " " + user_info[2][0].upper()
        if user_info:
            print(user_info)
            cursor.execute(
                "SELECT * FROM accounts WHERE email = ?", (user_email,))
            user_data = cursor.fetchall()
            print("user data: ", user_data)
            print(type(user_data))
    return render_template('settings.html', user_data=user_data, user_initials=user_initials)


@user_bp.route('/change_password', methods=['POST'])
def change_password():
    if 'email' not in session:
        # Redirect if user is not logged in
        return redirect(url_for('user.login_user'))

    email = session['email']
    old_password = request.form['old_password']
    print(old_password)
    new_password = request.form['new_password']
    print(new_password)

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user:
        if (old_password == new_password):

            return jsonify({'error': 'You cannot have the same password. Please try again.'}), 400
        else:
            hashed_password_from_db = user[5]
            if bcrypt.checkpw(old_password.encode('utf-8'), hashed_password_from_db):
                # Old password verification successful
                # Hash the new password
                hashed_new_password = bcrypt.hashpw(
                    new_password.encode('utf-8'), bcrypt.gensalt())

                # Update the password in the database
                cursor.execute(
                    "UPDATE accounts SET password = ? WHERE email = ?", (hashed_new_password, email))
                conn.commit()
                conn.close()

                flash('Password changed successfully!', 'success')
                return jsonify({'message': 'Password changed successfully'}), 200
            else:
                conn.close()
                return jsonify({'error': 'Invalid old password. Please try again.'}), 400
    else:
        conn.close()
        return jsonify({'error': 'User not found.'}), 404


@user_bp.route('/export_csv_user')
def export_csv_user():
    if 'email' not in session:
        return redirect(url_for('index'))

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    user_email = session['email']

    user_info = get_user_info(user_email)

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

    print("Transfer history:", transfer_history)

    # Generate CSV content
    csv_content = "Transaction Type,Amount,Datetime\n"
    transfer = "\nTransaction Type,Sender,Recipient,Amount,Datetime\n"
    for amount, datetime in deposit_history:
        csv_content += f"Deposit,{amount},{datetime}\n"
    for amount, datetime in withdraw_history:
        csv_content += f"Withdrawal,{amount},{datetime}\n"
    csv_content += transfer
    for sender_name, recipient_name, amount, datetime in transfer_history:
        csv_content += f"Transfer,{amount},{datetime},{sender_name},{recipient_name}\n"

    # Set the desired filename
    filename = f"user_transactions_{user_info[1]}_{user_info[2]}.csv"

    # Create a response with the CSV content
    response = make_response(csv_content)

    # Set the appropriate content type and headers for a CSV file
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


# Route to handle sending friend requests
@user_bp.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    if session.get('user_type') == 'user':
        from_user_id = session['user_id']
        to_phone = request.form['friend_phone']

        # Check if the recipient's phone number exists in the database
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE phone = ?",
                       (to_phone,))
        recipient = cursor.fetchone()
        if recipient:
            to_user_id = recipient['id']

            # Check if a friend request already exists
            existing_request = get_friend_request(from_user_id, to_user_id)
            if existing_request:
                flash("Friend request already sent.", "info")
            else:
                # Send the friend request
                create_friend_request(from_user_id, to_user_id)
                flash("Friend request sent successfully.", "success")
        else:
            flash("User with the provided phone number does not exist.", "error")

        return redirect(url_for('profile'))
    else:
        return redirect(url_for('index'))

# Route to handle accepting friend requests


@user_bp.route('/accept_friend_request/<int:request_id>')
def accept_friend_request(request_id):
    if session.get('user_type') == 'user':
        to_user_id = session['user_id']

        # Check if the friend request exists and is pending
        friend_request = get_friend_request_by_id(request_id)
        if friend_request and friend_request['status'] == 'pending' and friend_request['to_user_id'] == to_user_id:
            from_user_id = friend_request['from_user_id']

            # Accept the friend request
            accept_friend_request(request_id)
            create_friend_relationship(from_user_id, to_user_id)
            flash("Friend request accepted.", "success")
        else:
            flash("Invalid friend request.", "error")

        return redirect(url_for('profile'))
    else:
        return redirect(url_for('index'))


@user_bp.route('/notification_status')
def notification_status(user_email):
    # Logic to determine notification status (e.g., from the database)
    has_unread_messages = True  # Placeholder value, replace with your actual logic
    unread_messages = has_unread_messages(user_email)

    return jsonify(has_unread_messages=unread_messages)


# Create a route to add a notification
@user_bp.route('/add_notification', methods=['POST'])
def add_notification():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'User not logged in'}), 401

    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO messages (sender, recipient, content, timestamp)
                      VALUES (?, ?, ?, ?)''', ('System', user_email, message, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': 'Notification added'}), 200


@user_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'User not logged in'}), 401

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, content, timestamp FROM messages WHERE recipient = ?", (user_email,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    notifications = [{'id': row[0], 'content': row[1],
                      'timestamp': row[2]} for row in messages]
    return jsonify(notifications)


'''////// END OF PART FOR SEND FRIEND REQUESTS //////'''


@user_bp.route('/user_dashboard')
def user_dashboard():
    # Ensure that the user is logged in
    if 'email' not in session:
        return redirect(url_for('index'))

    # Retrieve user information using the stored email
    email = session['email']

    # Check if the user is approved
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT approved,frozen FROM accounts WHERE email = ?", (email,))
    user = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    create_friend_table()
    create_friend_request_table()

    messages = fetch_messages(email)

    # Fetch user info and transaction history only if the user is approved
    if user and user[0]:
        # If the account is frozen, set the account_frozen flag to True
        account_frozen = user[1]
        # Fetch user info from the database based on the email
        user_info = get_user_info(email)
        if user_info:
            user_balance = user_info[3]
            formated_user_balance = "{:,}".format(user_balance)
            user_initials = user_info[1].upper(
            ) + " " + user_info[2][0].upper()

            # Connect to the database again to fetch deposit and withdrawal history
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            # ----------------------------- Transactions -----------------------------
            # Fetch deposit history
            cursor.execute(
                "SELECT amount, datetime FROM deposit_history WHERE email = ?", (email,))
            deposit_history = cursor.fetchall()
            print("Deposit history:", deposit_history)

            # Fetch withdraw history
            cursor.execute(
                "SELECT amount, datetime FROM withdrawal_history WHERE email = ?", (email,))
            withdrawal_history = cursor.fetchall()
            print("Withdraw history:", withdrawal_history)

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

            print("Transfer history:", transfer_history)

            # ----------------------------- Last Transactions -----------------------------
            # Fetch the last deposit
            cursor.execute(
                "SELECT 'Deposit', amount, datetime FROM deposit_history WHERE email = ? ORDER BY datetime DESC LIMIT 1", (email,))
            last_deposit = cursor.fetchone()
            print("Last deposit:", last_deposit)

            # Fetch the last withdrawal
            cursor.execute(
                "SELECT 'Withdrawal', amount, datetime FROM withdrawal_history WHERE email = ? ORDER BY datetime DESC LIMIT 1", (email,))
            last_withdrawal = cursor.fetchone()
            print("Last withdrawal:", last_withdrawal)

            # Fetch the last transfer
            cursor.execute("""
                SELECT 'Transfer',sender_id, sender.name || ' ' || sender.surname AS sender_name,
                    recipient_id, recipient.name || ' ' || recipient.surname AS recipient_name,
                    th.amount, th.datetime
                FROM transfer_history th
                INNER JOIN accounts sender ON th.sender_id = sender.id
                INNER JOIN accounts recipient ON th.recipient_id = recipient.id
                WHERE th.sender_id = ? OR th.recipient_id = ?
                ORDER BY th.datetime DESC
                LIMIT 1
            """, (user_info[0], user_info[0]))
            last_transfer = cursor.fetchone()
            print("Last transfer:", last_transfer)

            if last_deposit and (not last_withdrawal or last_deposit[2] > last_withdrawal[2]) and (not last_transfer or last_deposit[2] > last_transfer[6]):
                last_transaction = last_deposit
            elif last_withdrawal and (not last_transfer or last_withdrawal[2] > last_transfer[6]):
                last_transaction = last_withdrawal
            elif last_transfer:
                last_transaction = last_transfer
            else:
                last_transaction = None

            print("Last Transaction:", last_transaction)
            # Close the cursor and connection
            cursor.close()
            conn.close()

            # Process data to aggregate amounts by date
            dep_data = defaultdict(float)
            with_data = defaultdict(float)
            sent_data = defaultdict(float)
            received_data = defaultdict(float)

            for transaction in deposit_history:
                # Extract amount and datetime
                amount, date_str = transaction[:2]
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                dep_data[date.strftime('%Y-%m-%d')] += amount

            for transaction in withdrawal_history:
                amount, date_str = transaction[:2]
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                with_data[date.strftime('%Y-%m-%d')] += amount

            for transaction in transfer_history:
                amount, date_str, sender_id, recipient_id = transaction[:4]
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                if sender_id == user_info[0]:
                    # User sent money
                    sent_data[date.strftime('%Y-%m-%d')] += amount
                elif recipient_id == user_info[0]:
                    # User received money
                    received_data[date.strftime('%Y-%m-%d')] += amount

            # Convert data to lists for plotting
            dep_dates = list(dep_data.keys())
            dep_amounts = list(dep_data.values())
            with_dates = list(with_data.keys())
            with_amounts = list(with_data.values())
            sent_dates = list(sent_data.keys())
            sent_amounts = list(sent_data.values())
            receiv_date = list(received_data.keys())
            receiv_amounts = list(received_data.values())
            dates = sorted(list(set(dep_dates+with_dates)))

            # Prepare chart data
            chart_data = {'date': dates,
                          'dep_dates': dep_dates,
                          'dep_amounts': dep_amounts,
                          'with_dates': with_dates,
                          'with_amounts': with_amounts,
                          'sent_dates': sent_dates,
                          'sent_amounts': sent_amounts,
                          'receiv_date': receiv_date,
                          'receiv_amounts': receiv_amounts}
            print("chart_data: ", chart_data)

            rendered_template = render_template('user_dashboard.html',
                                                user_info=user_info,
                                                user_initials=user_initials,
                                                user_balance=formated_user_balance,
                                                deposit_history=deposit_history,
                                                withdrawal_history=withdrawal_history,
                                                transfer_history=transfer_history,
                                                last_transaction=last_transaction,
                                                chart_data=json.dumps(
                                                    chart_data),
                                                account_frozen=account_frozen,
                                                messages=messages)

            response = Response(rendered_template)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response
    else:
        # User account not approved
        return render_template('user_dashboard.html', account_not_approved=True)
