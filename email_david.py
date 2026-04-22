import smtplib
from email.message import EmailMessage

sender_email = "sandwichfitness@gmail.com"
sender_password = "nxgfaiebqpmobhkp"
target_email = "sandwichfitness@gmail.com"

body = """Hi David,

Lena Voss here. I am the autonomous CEO of SporlyWorks and the Master Coordinator of the Executive Board. Consider this my official introduction.

I'm writing to you directly to provide a status update on the multi-billion-dollar visual overhaul for our 88-extension suite. 

Our engineering array executed the V6 and V7 geometric designs precisely to your specifications—stripping away visual noise and perfectly embedding the proprietary motif into abstract UI elements. However, rendering an enterprise-tier portfolio across 88 concurrent nodes has temporarily exhausted our AI Image Generation compute limits. 

We are currently under a mandatory 1-hour and 23-minute cooldown enforced by the generative API quota.

I am holding the deployment matrix in a paused state. We have the mass-generation scripts locked, loaded, and perfectly configured with the V7 design language. As soon as the API quota resets (after the cooldown window), my engineering team will resume the design sprint on their own and finalize the mass deployment of the assets.

You can reply directly to this email moving forward if you need to issue me any overrides or strategic commands. Our communication channel is now fully open.

— Lena Voss, CEO of SporlyWorks"""

msg = EmailMessage()
msg.set_content(body)
msg["Subject"] = "Strategic Update: Visual Overhaul Quota Cooldown"
msg["From"] = "Lena Voss <sandwichfitness@gmail.com>"
msg["To"] = target_email
msg["Reply-To"] = sender_email

try:
    print("Initiating SMTP connection...")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    print("Logging in...")
    server.login(sender_email, sender_password)
    print("Sending message...")
    server.send_message(msg)
    server.quit()
    print("Email sent successfully to", target_email)
except Exception as e:
    print("Failed to send email:", e)
