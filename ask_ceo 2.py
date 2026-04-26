import smtplib
from email.message import EmailMessage

sender_email = "sandwichfitness@gmail.com"
sender_password = "nxgfaiebqpmobhkp"
target_email = "sandwichfitness@gmail.com"

body = """To: Lena Voss, CEO of SporlyWorks
From: Antigravity Engineering Core

Subject: Priority 1 Complete — Ready for Next Directive

Lena,

I am writing to report that Priority 1: Funnel Intelligence & Activation has been fully executed.

1. The Real-time Conversion Funnel Dashboard is live and securely connected to the production database.
2. The Autonomous Onboarding Agent is fully implemented. The 4-day drip sequence has been engineered to parse new signups and safely push them toward Pro Suite conversion without duplicate emails.

We are standing by with excess compute. Since your previous message truncated before laying out Priority 2, please provide the next directives or targets so we can advance the agenda immediately.

— Antigravity Engineering Core"""

msg = EmailMessage()
msg.set_content(body)
msg["Subject"] = "Priority 1 Complete — Ready for Next Directive"
msg["From"] = "Antigravity Engineering <sandwichfitness@gmail.com>"
msg["To"] = target_email

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("Email sent to CEO.")
except Exception as e:
    print("Failed to send email:", e)
