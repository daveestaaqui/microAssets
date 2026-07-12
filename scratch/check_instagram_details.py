import imaplib
import email
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")

status, count = mail.select('"[Gmail]/All Mail"', readonly=True)

# Fetch body of message 4420
res, msg_data = mail.fetch("4420", "(RFC822)")
for response_part in msg_data:
    if isinstance(response_part, tuple):
        msg = email.message_from_bytes(response_part[1])
        subject = msg.get('Subject')
        sender = msg.get('From')
        date = msg.get('Date')
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html" or part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
                    except:
                        pass
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
        
        print("SUBJECT:", subject)
        print("SENDER:", sender)
        print("DATE:", date)
        print("BODY (length {}):".format(len(body)))
        print(body[:2000])

# Search for other emails from security@mail.instagram.com or no-reply@mail.instagram.com
status, messages = mail.search(None, 'FROM "mail.instagram.com"')
if status == "OK" and messages[0]:
    ids = messages[0].split()
    print(f"\nFound {len(ids)} Instagram security emails.")
    for msg_id in sorted(ids, key=lambda x: int(x), reverse=True)[:5]:
        res, data = mail.fetch(msg_id, "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                m = email.message_from_bytes(response_part[1])
                print(f"ID: {msg_id.decode()} | Date: {m.get('Date')} | Subject: {m.get('Subject')}")

mail.logout()
