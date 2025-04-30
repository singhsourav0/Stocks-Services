# --- app.py ---
from flask import Flask, render_template, request
import psycopg2
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
app = Flask(__name__)

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=5432
    )

# Create table if not exists
def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL,
            name VARCHAR(100),
            email VARCHAR(100) PRIMARY KEY,
            phoneno VARCHAR(100),
            Stocks VARCHAR(100)
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Home route – static landing page
@app.route('/', endpoint='index')
def index():
    return render_template('index.html')


@app.route('/prorequest', endpoint='prorequest')
def index():
    return render_template('prorequest.html')


@app.route('/request', methods=['GET', 'POST'], endpoint='request')
def request_page():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phoneno']
            category = request.form['category']
            item = request.form['Item']

            stocks = f"{category} - {item}"

            conn = get_db_connection()
            cur = conn.cursor()

            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cur.fetchone()

            if existing_user:
                # Update existing record
                cur.execute(
                    "UPDATE users SET stocks = %s WHERE email = %s",
                    (stocks, email)
                )
                conn.commit()
                message = f"Account exists. Updated your preferences to {stocks}, Now you will get updated Weakly for {stocks}."
                send_email(name, email, stocks, is_new_user=False)
            else:
                # Insert new user
                cur.execute(
                    "INSERT INTO users (name, email, phoneno, stocks) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, stocks)
                )
                conn.commit()
                message = f"Thank you {name}! You subscribed for {stocks}, your info is saved and working for you."
                send_email(name, email, stocks, is_new_user=True)

            cur.close()
            conn.close()

            return render_template('request.html', message=message)

        except Exception as e:
            print("Error:", e)
            return render_template('request.html', message="An error occurred. Please try again.")

    return render_template('request.html')


# Email sender
# def send_email(name, email):
#     try:
#         msg = EmailMessage()
#         msg['Subject'] = "Stock Subscription Confirmation"
#         msg['From'] = os.getenv('EMAIL')
#         msg['To'] = email
#         msg.set_content(f"Hi {name},\n\nThanks for subscribing! We'll keep you updated weekly.\n\nRegards,\nTeam")

#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#             smtp.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASS'))
#             smtp.send_message(msg)
#     except Exception as e:
#         print("Email error:", e)

def send_email(name, email, stocks, is_new_user=True):
    msg = EmailMessage()
    msg['Subject'] = "Stock Subscription Confirmation"
    msg['From'] = os.getenv('EMAIL')
    msg['To'] = email

    if is_new_user:
        html_content = f"""
        <html>
        <body style="margin:0;padding:0;background-color:#f9f9f9;font-family:Arial,sans-serif;">
            <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 0 10px rgba(0,0,0,0.1);">
                <div style="background:#25a85b;color:#fff;padding:20px 25px;font-size:20px;font-weight:600;">
                    Thanks for Subscribing!
                </div>
                <div style="padding:30px 25px;color:#333;line-height:1.6;">
                    <p>Hi {name},</p>
                    <p>Welcome aboard! You’ve successfully subscribed to <strong>{stocks}</strong>.</p>
                    <p>Starting this Sunday, you’ll receive weekly updates packed with market insights, stock performance, and expert commentary.</p>
                    <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:15px;margin:20px 0;">
                        Get more out of AutoStock—<a href="#" style="color:#22c55e;text-decoration:none;font-weight:bold;">Upgrade your plan</a> for real-time alerts and advanced insights.
                    </div>
                    <p>We’re excited to have you with us!</p>
                    <hr style="border:none;border-top:1px solid #eee;margin:30px 0;">
                    <p style="font-size:14px;color:#999;">
                        Questions? Just reply to this email for any Unsubscribe <a href="mailto:souravkumar8432@gmail.com" style="color:#007bff;"> </a>.
                    </p>
                    <p style="font-size:12px;color:#aaa;text-align:center;margin-top:20px;">
                        © 2025 AutoStock. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        html_content = f"""
        <html>
        <body style="margin:0;padding:0;background-color:#f9f9f9;font-family:Arial,sans-serif;">
            <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 0 10px rgba(0,0,0,0.1);">
                <div style="background:#25a85b;color:#fff;padding:20px 25px;font-size:20px;font-weight:600;">
                    Welcome Back!
                </div>
                <div style="padding:30px 25px;color:#333;line-height:1.6;">
                    <p>Hello {name},</p>
                    <p>Your stock subscription has been updated to <strong>{stocks}</strong>.</p>
                    <p>You’ll continue receiving your weekly insights every Sunday. If you want to expand your coverage or enable real-time updates, check out our upgrade options.</p>
                    <div style="margin:20px 0;">
                        <a href="#" style="background:#25a85b;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;">Manage Subscription</a>
                    </div>
                    <hr style="border:none;border-top:1px solid #eee;margin:30px 0;">
                    <p style="font-size:14px;color:#999;">
                        Questions? Just reply to this email or mail us at <a href="mailto:souravkumar8432@gmail.com" style="color:#007bff;">Unsubscribe</a>.
                    </p>
                    <p style="font-size:12px;color:#aaa;text-align:center;margin-top:20px;">
                        © 2025 AutoStock. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASS'))
        smtp.send_message(msg)




# Main entry
if __name__ == '__main__':
    create_users_table()
    app.run(host='0.0.0.0', port=10000)
