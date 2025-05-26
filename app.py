# --- app.py ---
from flask import Flask, render_template, request, jsonify
import psycopg2
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import traceback
import pickle
load_dotenv()
app = Flask(__name__)

with open("data/dropdown_data.pkl", "rb") as f:
    stocks =  pickle.load(f)
with open("data/crypto_dropdown_data.pkl", "rb") as f:
    crypto =  pickle.load(f)

with open("data/mutual_dropdown_data.pkl", "rb") as f:
    mutual =  pickle.load(f)

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
            Stocks VARCHAR(100) ,
            category VARCHAR(100)
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




# print(stocks)
@app.route('/request', methods=['GET', 'POST'], endpoint='request')
def request_page():
    # POST method to handle form submission
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phoneno']
            category = request.form['category']
            item = request.form['Item']

            selected_item = item  
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cur.fetchone()

            if existing_user:
                cur.execute("UPDATE users SET stocks = %s, category = %s WHERE email = %s", (selected_item, category, email))
                message = f"Account exists. Updated your preferences to {selected_item}."
                send_email(name, email, selected_item, is_new_user=False)
                status = "updated"
            else:
                cur.execute("INSERT INTO users (name, email, phoneno, stocks, category) VALUES (%s, %s, %s, %s, %s)",
                            (name, email, phone, selected_item, category))
                message = f"Thank you {name}! You subscribed for {selected_item}."
                send_email(name, email, selected_item, is_new_user=True)
                status = "subscribed"

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"status": status, "message": message})

        except Exception as e:
            print("Error:", e)
            return jsonify({"status": "error", "message": "An error occurred. Please try again."})

    # ✅ This now correctly uses the global stocks and crypto
    return render_template("request.html", stocks=stocks, crypto=crypto,  mutual=mutual)

@app.route('/get-items')
def get_items():
    category = request.args.get('category', 'Stocks').lower()
    term = request.args.get('term', '').lower()

    if category == 'crypto':
        options = crypto

    elif category == 'mutual':
        options = mutual
    else:
        options = stocks

    matched = [opt for opt in options if term in opt.lower()]
    return jsonify([{'id': opt, 'text': opt} for opt in matched[:50]])


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
    msg['From'] = os.getenv('EMAIL')
    msg['To'] = email

    if is_new_user:
        msg['Subject'] = "Welcome to AutoStock - Your Subscription Confirmed!"
        html_content = f"""
        <html>
        <body style="margin:0;padding:0;background-color:#f9f9f9;font-family:'Segoe UI',Arial,sans-serif;">
            <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 0 20px rgba(0,0,0,0.1);">
                <div style="background:linear-gradient(135deg, #25a85b 0%, #1e8449 100%);color:#fff;padding:30px;text-align:center;">
                    <h1 style="margin:0;font-size:28px;font-weight:700;">Welcome to AutoStock!</h1>
                    <p style="margin:10px 0 0;opacity:0.9;font-size:16px;">Your financial insights journey begins</p>
                </div>
                <div style="padding:40px 30px;color:#333;line-height:1.7;">
                    <p style="font-size:18px;margin-top:0;">Hi {name},</p>
                    <p>Thank you for joining AutoStock! We're thrilled to have you on board. You've successfully subscribed to receive updates on <strong style="color:#25a85b;">{stocks}</strong>.</p>
                    
                    <div style="background:#f0fdf4;border-radius:8px;border-left:5px solid #22c55e;padding:20px;margin:25px 0;">
                        <h3 style="margin-top:0;color:#166534;">What to expect:</h3>
                        <ul style="padding-left:20px;margin-bottom:0;">
                            <li>Weekly market insights delivered every Sunday</li>
                            <li>Performance analysis of {stocks}</li>
                            <li>Expert commentary and predictions</li>
                            <li>Personalized investment recommendations</li>
                        </ul>
                    </div>
                    
                    <p>To get the most out of your subscription, we recommend exploring our mobile app for real-time notifications.</p>
                    
                    <div style="text-align:center;margin:30px 0;">
                        <a href="#" style="background:linear-gradient(to right, #25a85b, #1e8449);color:#fff;padding:14px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;box-shadow:0 4px 10px rgba(37,168,91,0.3);">Explore Premium Features</a>
                    </div>
                    
                    <hr style="border:none;border-top:1px solid #eee;margin:30px 0;">
                    
                    <div style="background:#f8f9fa;border-radius:8px;padding:20px;font-size:14px;">
                        <p style="margin-top:0;"><strong>Need help getting started?</strong></p>
                        <p style="margin-bottom:0;">Our support team is available 24/7. Simply reply to this email or contact us at <a href="mailto:support@autostock.com" style="color:#25a85b;text-decoration:none;font-weight:500;">support@autostock.com</a></p>
                    </div>
                    
                    <p style="font-size:14px;color:#666;margin-top:30px;text-align:center;">
                        To unsubscribe or manage your email preferences, <a href="#" style="color:#25a85b;text-decoration:none;">click here</a>
                    </p>
                    
                    <p style="font-size:12px;color:#999;text-align:center;margin-top:20px;border-top:1px solid #eee;padding-top:20px;">
                        © 2025 AutoStock. All rights reserved.<br>
                        123 Finance Street, Market City, MC 12345
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        msg['Subject'] = "Welcome Back to AutoStock - Subscription Updated"
        html_content = f"""
        <html>
        <body style="margin:0;padding:0;background-color:#f9f9f9;font-family:'Segoe UI',Arial,sans-serif;">
            <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 0 20px rgba(0,0,0,0.1);">
                <div style="background:linear-gradient(135deg, #3498db 0%, #2980b9 100%);color:#fff;padding:30px;text-align:center;">
                    <h1 style="margin:0;font-size:28px;font-weight:700;">Welcome Back!</h1>
                    <p style="margin:10px 0 0;opacity:0.9;font-size:16px;">Your subscription has been updated</p>
                </div>
                <div style="padding:40px 30px;color:#333;line-height:1.7;">
                    <p style="font-size:18px;margin-top:0;">Hello {name},</p>
                    <p>We're glad to see you again! Your subscription has been successfully updated to <strong style="color:#3498db;">{stocks}</strong>.</p>
                    
                    <div style="background:#ebf8ff;border-radius:8px;border-left:5px solid #3498db;padding:20px;margin:25px 0;">
                        <p style="margin:0;"><strong>Your weekly insights</strong> will continue to be delivered every Sunday, now featuring your updated preferences.</p>
                    </div>
                    
                    <p>Is there anything else you'd like to customize about your subscription? Our premium tier offers additional features like:</p>
                    
                    <ul style="padding-left:20px;">
                        <li>Real-time price alerts</li>
                        <li>Advanced technical analysis</li>
                        <li>Portfolio integration</li>
                        <li>Personalized investment strategies</li>
                    </ul>
                    
                    <div style="text-align:center;margin:30px 0;">
                        <a href="#" style="background:linear-gradient(to right, #3498db, #2980b9);color:#fff;padding:14px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;box-shadow:0 4px 10px rgba(52,152,219,0.3);">Manage Subscription</a>
                    </div>
                    
                    <hr style="border:none;border-top:1px solid #eee;margin:30px 0;">
                    
                    <p style="font-size:14px;color:#666;text-align:center;">
                        Questions or feedback? Reply to this email or contact us at <a href="mailto:support@autostock.com" style="color:#3498db;text-decoration:none;">support@autostock.com</a>
                    </p>
                    
                    <p style="font-size:12px;color:#999;text-align:center;margin-top:20px;border-top:1px solid #eee;padding-top:20px;">
                        © 2025 AutoStock. All rights reserved.<br>
                        To unsubscribe from these emails, <a href="#" style="color:#3498db;text-decoration:none;">click here</a>
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