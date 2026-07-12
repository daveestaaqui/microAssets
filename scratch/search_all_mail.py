import imaplib
import email
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")

# List all folders/mailboxes
status, folders = mail.list()
print("Mailboxes:")
for f in folders:
    print(f.decode())

# Select "[Gmail]/All Mail" or search standard folder
# In Gmail, [Gmail]/All Mail is where all archived and active emails live.
print("\nSearching '[Gmail]/All Mail'...")
status, count = mail.select('"[Gmail]/All Mail"', readonly=True)
if status != "OK":
    print("Could not select [Gmail]/All Mail, trying INBOX...")
    mail.select("inbox", readonly=True)

# Search queries
search_terms = ['goaffpro', 'refersion', 'affiliate', 'myyco']
found_messages = []

for term in search_terms:
    # Use general search (search body, subject, etc.)
    status, messages = mail.search(None, f'TEXT "{term}"')
    if status == "OK" and messages[0]:
        found_messages.extend(messages[0].split())

# De-duplicate
found_messages = list(set(found_messages))
print(f"\nFound {len(found_messages)} matched emails in All Mail.")

# Fetch details of matched emails, sorted in reverse order (most recent first)
found_messages = sorted(found_messages, key=lambda x: int(x), reverse=True)[:30]

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
