import imaplib
import email
from email.header import decode_header
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
mail.select("inbox")

status, messages = mail.search(None, 'ALL')
if status == "OK" and messages[0]:
    msg_ids = messages[0].split()
    print(f"Total emails in inbox: {len(msg_ids)}")
    # Last 20 emails
    recent_ids = msg_ids[-20:]
    for msg_id in reversed(recent_ids):
        res, msg_data = mail.fetch(msg_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg.get('Subject')
                sender = msg.get('From')
                print(f"[{msg_id.decode()}] From: {sender} | Subject: {subject}")
else:
    print("No emails found.")

mail.logout()
