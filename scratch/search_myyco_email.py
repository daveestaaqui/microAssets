import imaplib
import email
from email.header import decode_header
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
mail.select("inbox")

# Search for emails containing "myyco"
status, messages = mail.search(None, 'BODY "myyco"')
found_messages = []
if status == "OK" and messages[0]:
    found_messages.extend(messages[0].split())

# Also search subject for "myyco"
status_subj, messages_subj = mail.search(None, 'SUBJECT "myyco"')
if status_subj == "OK" and messages_subj[0]:
    found_messages.extend(messages_subj[0].split())

# De-duplicate and sort
found_messages = sorted(list(set(found_messages)), key=lambda x: int(x), reverse=True)[:5]
print(f"Found {len(found_messages)} relevant MYYCO emails.")

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
