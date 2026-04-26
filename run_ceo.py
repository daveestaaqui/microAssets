import sys
import os
sys.path.append(os.path.join(os.getcwd(), '_scripts'))
from sporlyworks_board_coordinator import fetch_recent_emails, send_owner_reply, fallback_load_env

fallback_load_env()
summary_string, has_owner_command, raw_owner_commands = fetch_recent_emails()
print(f"Fetched commands: {len(raw_owner_commands)}")
if raw_owner_commands:
    send_owner_reply(raw_owner_commands)
    print("Sent replies.")
else:
    print("No commands to reply to.")
