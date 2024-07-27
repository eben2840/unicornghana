import csv
import os
import re
from flask import Flask, jsonify, render_template, request
from email.message import EmailMessage
import smtplib, ssl
import datetime
import threading
import openai
from werkzeug.utils import secure_filename
from email_list import email_list  # Import the email_list from email_list.py

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email credentials
radio = 'yboateng057@gmail.com'
email_password = 'hsgtqiervnkabcma'
# radio_display_name = 'Beehart Consulting'

openai.api_key = 'sk-proj-6EoUuVeWirgozrP29xybT3BlbkFJFH6KrT9M01XtvjoWFuiJ'

@app.route('/')
def email():
    return render_template('email.html')

@app.route('/form')
def home():
    return render_template('form.html')

def format_emails(email_string):
    # Replace whitespace between emails with commas
    formatted_string = re.sub(r'\s+', ',', email_string.strip())
    # Add commas if not present
    formatted_string = re.sub(r'(?<!@[^,])\s', ',', formatted_string)
    # Remove any extra commas
    formatted_string = re.sub(r',+', ',', formatted_string)
    return formatted_string

def sanitize_input(input_string):
    # Remove any linefeed or carriage return characters
    return re.sub(r'[\r\n]+', ' ', input_string).strip()

def send_email(radio_display_name, subject, emails, html_content):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(radio, email_password)
            for index, email_receiver in enumerate(emails, 1):
                email_receiver = email_receiver.strip()
                if email_receiver:  # Ensure the email address is not empty
                    em = EmailMessage()
                    em['From'] = f'{radio_display_name} <{radio}>'
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content('')
                    em.add_alternative(html_content, subtype='html')
                    smtp.send_message(em)
                    print(f"Email sent to {email_receiver}. Email number: {index}")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check your username and password.")
    except smtplib.SMTPRecipientsRefused:
        print("The server didn't accept the recipient address.")
    except smtplib.SMTPSenderRefused:
        print("The server didn't accept the sender address.")
    except smtplib.SMTPDataError:
        print("The server replied with an unexpected error code (other than a refusal of a recipient or sender).")
    except Exception as e:
        print(f"Emails not sent. Error occurred: {e}")

@app.route('/send_emails', methods=['POST'])
def send_emails():
    radio_display_name = sanitize_input(request.form['radio_display_name'])
    subject = sanitize_input(request.form['subject'])
    raw_emails = sanitize_input(request.form['emails'])
    message = sanitize_input(request.form['message'])
    send_datetime_str = request.form['send_datetime']

    formatted_emails = format_emails(raw_emails)
    emails = formatted_emails.split(',')

    # Process uploaded CSV file
    if 'csv_file' in request.files:
        csv_file = request.files['csv_file']
        if csv_file.filename != '':
            filename = secure_filename(csv_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            csv_file.save(filepath)
            with open(filepath, newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    emails.extend(row)

    emails = list(set(emails))  # Remove duplicates

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .email-header {{
                background-color: #061536;
                color: #fff;
                padding: 20px;
                text-align: center;
                position: relative;
            }}
            .email-header h1 {{
                display: inline;
                font-size: 24px;
                vertical-align: middle;
            }}
            .email-body {{
                padding: 20px;
            }}
            .email-body h2 {{
                font-size: 20px;
                color: #333;
            }}
            .email-body p {{
                font-size: 16px;
                color: #666;
                line-height: 1.5;
            }}
            .email-body strong {{
                color: #333;
            }}
            .email-footer {{
                padding: 20px;
                background-color: #f4f4f9;
                text-align: center;
            }}
            .email-footer img {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: block;
                margin: 0 auto;
            }}
            .email-footer h3 {{
                margin: 10px 0 5px;
                font-size: 18px;
                color: #333;
            }}
            .email-footer p {{
                margin: 0;
                font-size: 14px;
                color: #666;
            }}
            .email-footer a {{
                display: inline-block;
                margin: 10px 5px;
                color: #fff;
                background-color: #3a64c9;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
            }}
            .social-icons a {{
                display: inline-block;
                margin: 0 5px;
                color: #3a64c9;
                font-size: 20px;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>{radio_display_name}</h1>
            </div>
            <div class="email-body">
                {message}
            </div>
            <div class="email-header">
                <h1>Best regards</h1>
            </div>
        </div>
    </body>
    </html>
    """

    # Schedule email sending
    if send_datetime_str:
        send_datetime = datetime.datetime.strptime(send_datetime_str, '%Y-%m-%dT%H:%M')
        delay = (send_datetime - datetime.datetime.now()).total_seconds()
        threading.Timer(delay, send_email, args=[radio_display_name, subject, emails, html_content]).start()
        result_message = f"Emails scheduled to be sent at {send_datetime_str}."
    else:
        send_email(radio_display_name, subject, emails, html_content)
        result_message = "Emails sent successfully!"

    return render_template('result.html', result=result_message)

# @app.route('/send_emails', methods=['POST'])
# def send_emails():
#     radio_display_name = sanitize_input(request.form['radio_display_name'])
#     subject = sanitize_input(request.form['subject'])
#     raw_emails = sanitize_input(request.form['emails'])
#     message = sanitize_input(request.form['message'])
#     send_datetime_str = request.form['send_datetime']

#     formatted_emails = format_emails(raw_emails)
#     emails = formatted_emails.split(',')

#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
       
# body {{
#             font-family: Arial, sans-serif;
#             background-color: #f4f4f9;
#             margin: 0;
#             padding: 0;
#         }}

#         .email-container {{
#             max-width: 600px;
#             margin: 20px auto;
#             background-color: #fff;
#             border-radius: 8px;
#             box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
#             overflow: hidden;
#         }}

#         .email-header {{
#             background-color: #061536;
#             color: #fff;
#             padding: 20px;
#             text-align: center;
#             position: relative;
#         }}

#         .email-header img {{
#             width: 30px;
#             vertical-align: middle;
#             margin-right: 10px;
#         }}

#         .email-header h1 {{
#             display: inline;
#             font-size: 24px;
#             vertical-align: middle;
#         }}

#         .email-body {{
#             padding: 20px;
#         }}

#         .email-body h2 {{
#             font-size: 20px;
#             color: #333;
#         }}

#         .email-body p {{
#             font-size: 16px;
#             color: #666;
#             line-height: 1.5;
#         }}

#         .email-body strong {{
#             color: #333;
#         }}

#         .email-footer {{
#             padding: 20px;
#             background-color: #f4f4f9;
#             text-align: center;
#         }}

#         .email-footer img {{
#             width: 50px;
#             height: 50px;
#             border-radius: 50%;
#             display: block;
#             margin: 0 auto;
#         }}

#         .email-footer h3 {{
#             margin: 10px 0 5px;
#             font-size: 18px;
#             color: #333;
#         }}

#         .email-footer p {{
#             margin: 0;
#             font-size: 14px;
#             color: #666;
#         }}

#         .email-footer a {{
#             display: inline-block;
#             margin: 10px 5px;
#             color: #fff;
#             background-color: #3a64c9;
#             padding: 10px 20px;
#             border-radius: 5px;
#             text-decoration: none;
#         }}

#         .social-icons a {{
#             display: inline-block;
#             margin: 0 5px;
#             color: #3a64c9;
#             font-size: 20px;
#             text-decoration: none;
#         }}
       
#         </style>
#     </head>
#     <body>
#     <div class="email-container">
#         <div class="email-header">
#             <!--<img src="https://img.icons8.com/ios-filled/50/ffffff/airplane-take-off.png" alt="E-Marketing Logo">-->
#             <h1>{radio_display_name}</h1>
#         </div>
#         <div class="email-body">
#         {message}
#         </div>
        
#         <div class="email-header">
#             <!--<img src="https://img.icons8.com/ios-filled/50/ffffff/airplane-take-off.png" alt="E-Marketing Logo">-->
#             <h1>Best regards</h1>
#         </div>
        
#     </div>
        
#     </body>
#     </html>
#     """

#     # Schedule email sending
#     if send_datetime_str:
#         send_datetime = datetime.datetime.strptime(send_datetime_str, '%Y-%m-%dT%H:%M')
#         delay = (send_datetime - datetime.datetime.now()).total_seconds()
#         threading.Timer(delay, send_email, args=[radio_display_name, subject, emails, html_content]).start()
#         result_message = f"Emails scheduled to be sent at {send_datetime_str}."
#     else:
#         send_email(radio_display_name, subject, emails, html_content)
#         result_message = "Emails sent successfully!"

#     return render_template('result.html', result=result_message)

def generate_message_with_retry(prompt, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message['content'].strip()
        except openai.error.RateLimitError:
            retries += 1
            print(f"Rate limit exceeded, retrying... ({retries}/{max_retries})")
            datetime.time.sleep(5) 
    raise Exception("Rate limit exceeded, all retries failed.")

@app.route('/generate_message', methods=['POST'])
def generate_message():
    data = request.json
    prompt = data.get('prompt', '')

    try:
        generated_message = generate_message_with_retry(prompt)
        return jsonify({'generated_message': generated_message})
    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
