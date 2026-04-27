import imaplib
import email
from email.header import decode_header
import warnings
import os

warnings.filterwarnings("ignore", category=DeprecationWarning)

def process_emails():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
        mail.select("inbox")

        # Search for all emails from Lena Voss
        # Note: If we don't know the exact email, we'll search for "Lena" or "CEO"
        status, messages = mail.search(None, 'FROM "Lena Voss"')
        if status != "OK" or not messages[0]:
             # Try searching for Lena in general
             status, messages = mail.search(None, 'OR FROM "Lena" SUBJECT "Lena"')

        if status == "OK" and messages[0]:
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} emails from Lena Voss.")
            
            for e_id in email_ids:
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg.get("Subject")
                        sender = msg.get("From")
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
                        
                        print(f"\n--- EMAIL ID: {e_id.decode()} ---")
                        print(f"FROM: {sender}")
                        print(f"SUBJECT: {subject}")
                        print(f"BODY:\n{body.strip()}")
                        print("----------------------------")
                        
                        # Mark for deletion
                        # mail.store(e_id, '+FLAGS', '\\Deleted')
        else:
            print("No emails found from Lena Voss.")

        # mail.expunge() # Uncomment to actually delete
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_emails()
