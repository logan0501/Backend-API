import smtplib
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()


EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
fromaddr = EMAIL
toaddr = "loganvk18@gmail.com"

msg = MIMEMultipart('alternative')
msg['Subject'] = "Verification of notes"
msg['From'] = fromaddr
msg['To'] = toaddr

html = """<!DOCTYPE html>
<html lang="en">
  <head></head>
  <body>
    <h1>Greetings from Notely</h1>
    <p>Your notes on Operating system got successfully verified.</p>
    <h4>Thank you</h4>
    <p>Regards,</p>
    <p>Team Notely.</p>
  </body>
</html>
"""
msg.attach(MIMEText(html, 'html'))

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login(EMAIL, PASSWORD)
message = msg.as_string()
s.sendmail(EMAIL, "loganvk18@gmail.com", message)
s.quit()