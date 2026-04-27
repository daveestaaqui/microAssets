import imaplib
import email
from email.header import decode_header
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
mail.select("inbox")

status, messages = mail.search(None, 'ALL')
if status == "OK" and messages[0]:
    latest_id = messages[0].split()[-1]
    res, msg_data = mail.fetch(latest_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    pass
            print(f"--- LATEST EMAIL FROM: {msg.get('From')} ---")
            print(f"Subject: {msg.get('Subject')}")
            print(body.strip())
            print("-----------------------------------")
else:
    print("No emails found.")

mail.logout()
