import imaplib
import email
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")

status, count = mail.select('"[Gmail]/All Mail"', readonly=True)

msg_ids = ["3996", "3997", "4419", "4657"]

for msg_id in msg_ids:
    res, msg_data = mail.fetch(msg_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = msg.get('Subject')
            body_html = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body_html = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body_html = msg.get_payload(decode=True).decode(errors='ignore')
            
            if body_html:
                soup = BeautifulSoup(body_html, "html.parser")
                text = soup.get_text(separator=' ').strip()
                # Clean up multiple spaces
                clean_text = ' '.join(text.split())
                print(f"\n==========================================")
                print(f"ID: {msg_id} | Subject: {subject}")
                print(f"CLEAN TEXT:\n{clean_text}")
                print(f"==========================================")

mail.logout()
