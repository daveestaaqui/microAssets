import imaplib
import email
from email.header import decode_header
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
mail.select("inbox")

# Search for emails containing "seed" or "affiliate" or "spore" or "mushrooms"
search_queries = ['SUBJECT "seed"', 'BODY "seed"', 'SUBJECT "affiliate"', 'BODY "affiliate"', 'SUBJECT "spore"', 'SUBJECT "mushroom"']

found_messages = []

for query in search_queries:
    status, messages = mail.search(None, query)
    if status == "OK" and messages[0]:
        found_messages.extend(messages[0].split())

# De-duplicate
found_messages = list(set(found_messages))
print(f"Found {len(found_messages)} relevant emails.")

# Fetch details of top 10 most recent matched emails
found_messages = sorted(found_messages, key=lambda x: int(x), reverse=True)[:10]

for msg_id in found_messages:
    res, msg_data = mail.fetch(msg_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = msg.get('Subject')
            sender = msg.get('From')
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
            print(f"ID: {msg_id.decode()}")
            print(f"FROM: {sender}")
            print(f"SUBJECT: {subject}")
            print(f"BODY:\n{body.strip()[:1000]}")
            print(f"==========================================")

mail.logout()
