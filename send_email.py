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

html ="""<!DOCTYPE html>
<html lang="en">
  <head></head>
  <body>
    <h1>Notely : Notification for verifying the notes</h1>
    <p>
      Loganathan has published a note on operating system, we would like to know
      wether the content in the note shared by him is approriate and relavant.
      After reviewing the attachment kindly accept or reject the notes.
    </p>

    <a href="http://localhost:5000/note-accept">Click Here</a>
    <span> to accept the note.</span>
    <br />

    <a href="http://localhost:5000/note-reject">Click Here</a>
    <span> to reject the note.</span>
    <h4>Thank you</h4>
    <p>Regards,</p>
    <p>Team Notely.</p>
  </body>
</html>

    """

msg.attach(MIMEText(html, 'html'))

filename = "temp.pdf"
attachment = open("temp.pdf", "rb")

# instance of MIMEBase and named as p
p = MIMEBase('application', 'octet-stream')
  
# To change the payload into encoded form
p.set_payload((attachment).read())
  
# encode into base64
encoders.encode_base64(p)
   
p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
  
# attach the instance 'p' to instance 'msg'
msg.attach(p)

s = smtplib.SMTP('smtp.gmail.com', 587)
 
# start TLS for security
s.starttls()
 
# Authentication
s.login(EMAIL,"udvgimfcrssasnlf")
 
# message to be sent
message = msg.as_string()
 
# sending the mail
s.sendmail(EMAIL, "loganvk18@gmail.com", message)

s.quit()