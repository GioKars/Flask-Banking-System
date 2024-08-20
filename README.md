# Bank Database Management System

## Overview

This is a Flask-based web application for managing bank accounts and transactions. The application allows users to create accounts, manage their transactions, and view their transaction history. Additionally, it includes an admin panel for managing users and their accounts.

## Features

- **User Registration and Login**: Secure user authentication.
- **Account Management**: Create, view, and manage bank accounts.
- **Transaction History**: View and filter past transactions.
- **Admin Panel**: Admin-specific features to manage users and monitor transactions.

## Project Structure

- `app.py`: Main application file.
- `admin_routes.py`: Routes related to admin functionalities.
- `user_routes.py`: Routes related to user functionalities.
- `bank_account.py`: Bank account-related logic.
- `helpers_func.py`: Helper functions used across the application.
- `static/`: Contains static files like CSS, JavaScript, and images.
- `templates/`: Contains HTML templates for rendering views.

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use .venv\\Scripts\\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables by creating a `.env` file in the project root with the following contents:

   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

5. Initialize the database:

   ```bash
   python init_db.py
   ```

6. Run the application:
   ```bash
   flask run
   ```

## License

This project is licensed under the MIT License.
