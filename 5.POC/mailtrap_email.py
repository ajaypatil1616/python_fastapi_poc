import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException

MAILTRAP_HOST = 'sandbox.smtp.mailtrap.io'
MAILTRAP_PORT = 2525
MAILTRAP_USERNAME = '836cf7eb4e0f0c'
MAILTRAP_PASSWORD = '0ed1870cb77257'

def send_email(recipient_email : str, subject:str, body :str):
    try :
        smtp_server = smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT)
        smtp_server.starttls()
        smtp_server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
        
        message = MIMEMultipart()
        message['From'] = MAILTRAP_USERNAME
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        
        smtp_server.send_message(message)
        smtp_server.quit()
        
    except Exception as e :
        raise HTTPException(status_code= 500, detail=f"Failed to send email: :{str(e)}")