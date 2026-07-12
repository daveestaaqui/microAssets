import imaplib
import email
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")

status, count = mail.select('"[Gmail]/All Mail"', readonly=True)

# Fetch body of messages 3996 and 3997
for msg_id in ["3996", "3997"]:
    res, msg_data = mail.fetch(msg_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = msg.get('Subject')
            sender = msg.get('From')
            date = msg.get('Date')
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                        try:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                        except:
                            pass
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            
            print(f"\n==========================================")
            print("ID:", msg_id)
            print("SUBJECT:", subject)
            print("SENDER:", sender)
            print("DATE:", date)
            print("BODY:")
            print(body.strip()[:2000])
            print(f"==========================================")

mail.logout()
