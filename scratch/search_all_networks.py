import imaplib
import email
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")

status, count = mail.select('"[Gmail]/All Mail"', readonly=True)
if status != "OK":
    mail.select("inbox", readonly=True)

search_terms = ['awin', 'north spore', 'real mushrooms', 'magic bag', 'shareasale', 'seed']
found_messages = []

for term in search_terms:
    status, messages = mail.search(None, f'TEXT "{term}"')
    if status == "OK" and messages[0]:
        found_messages.extend(messages[0].split())

found_messages = sorted(list(set(found_messages)), key=lambda x: int(x), reverse=True)[:30]

print(f"Found {len(found_messages)} emails.")

for msg_id in found_messages:
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
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                        except:
                            pass
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                except:
                    pass
            print(f"\n==========================================")
            print(f"ID: {msg_id.decode()} | Date: {date}")
            print(f"FROM: {sender}")
            print(f"SUBJECT: {subject}")
            print(f"BODY SNIPPET:\n{body.strip()[:600]}")
            print(f"==========================================")

mail.logout()
