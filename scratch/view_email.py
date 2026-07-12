import imaplib
import email
import warnings
import re

warnings.filterwarnings("ignore", category=DeprecationWarning)

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
mail.select('"[Gmail]/All Mail"', readonly=True)

res, msg_data = mail.fetch("4644", "(RFC822)")
for response_part in msg_data:
    if isinstance(response_part, tuple):
        msg = email.message_from_bytes(response_part[1])
        subject = msg.get('Subject')
        sender = msg.get('From')
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                c_type = part.get_content_type()
                if c_type in ["text/plain", "text/html"]:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors='ignore') + "\n"
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors='ignore')
                
        # Clean head and style tags out
        body_clean = re.sub(r'<head>.*?</head>', '', body, flags=re.DOTALL)
        body_clean = re.sub(r'<style>.*?</style>', '', body_clean, flags=re.DOTALL)
        body_clean = re.sub(r'<[^<]+?>', ' ', body_clean)
        
        # Collapse whitespace
        lines = [line.strip() for line in body_clean.split("\n") if line.strip()]
        clean_text = "\n".join(lines)
        clean_text = re.sub(r'[ \t]+', ' ', clean_text)
        
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print("\n--- CLEAN TEXT ---")
        print(clean_text[:2000])

mail.logout()
