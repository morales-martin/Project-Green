import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fromaddr = "braulioosalcedo@gmail.com"
toaddr = "braulioosalcedo@gmail.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Test Alert"

body = "This is a test alert"
msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "TeamGreen4")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()