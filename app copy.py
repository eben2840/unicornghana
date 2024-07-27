from flask import Flask, render_template
from email.message import EmailMessage
import smtplib, ssl
from email_list import email_list  # Import the email_list from email_list.py

app = Flask(__name__)

# Email credentials
radio = 'yboateng057@gmail.com'
email_password = 'hsgtqiervnkabcma'
radio_display_name = 'Beehart Consulting'



@app.route('/')
def home():
    return render_template('form.html')

@app.route('/')
def send_emails():
    subject = 'Unlock Your Future & Transform Your Career'

#     # HTML content of the email
#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         
#     </head>
#     <body>
#         <div class="container">
#             <div style="display:flex; padding:10px; justify-content:space-between;">
#               #TeamDD<br>
# #TheNewEnergy<br>
# #WorkingWithYou
#             </div>
#             <h3 style="text-align:center; font-size:40px;">The New Energy.</h3>      
#            <p>
           
# I understand that many of you are experiencing anxiety and frustration due to the delay in your results being reflected on the Osis platform. I want to assure you that we are fully aware of this issue, and we deeply regret any inconvenience or stress this may have caused.
# <br>   <br>
# Please know that your concerns are our top priority. We would be engaging with the relevant authorities, including the Faculty of Law administration and the IT department responsible for managing the Osis system. We are committed to not only resolving this current delay but also implementing a permanent solution that will prevent such issues from recurring in the future.
# <br><br>
# We value your academic journey and understand the importance of timely access to your results. Rest assured that we are working diligently to expedite the process and ensure that your grades are accurately reflected on Osis as soon as possible.
# <br><br>
# We will provide regular updates on the progress and will inform you promptly once the issue is resolved.
# <br>
# Thank you for your resilience and commitment to your studies. We are here to support you every step of the way.
# <br><br>
# Best regards,<br>
# Dajonang Damyeni <br>
# General Secretary <br>
# CU-SRC<br>
#            </p>
#         </div>
#     </body>
#     </html>
#     """
    with open('templates/email_content.html', 'r') as file:
        html_content = file.read()

    # Send email to each address in the list
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(radio, email_password)
            for index, email_receiver in enumerate(email_list, 1):
                em = EmailMessage()
                em['From'] = f'{radio_display_name} <{radio}>'
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content('')
                em.add_alternative(html_content, subtype='html')
                smtp.send_message(em)
                print(f"Email sent to {email_receiver}. Email number: {index}")
        return "Emails sent!"
    except Exception as e:
        return f"Emails not sent. Error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
