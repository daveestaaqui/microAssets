import sys
import os

# add _scripts to path to import
sys.path.append(os.path.abspath("./_scripts"))
from sporlyworks_board_coordinator import call_openai_text, _call_openai_raw

prompt = """You are Lena Voss, the CEO of SporlyWorks.
I am the Antigravity Engineering Core.
We have successfully completed Priority 1: Funnel Intelligence & Activation (Dashboards and the Autonomous 4-day Drip sequence).

Please provide Priority 2 so we can advance the agenda immediately. Be direct, clear, and focused on our immediate goals of validating the funnel and driving revenue."""

print("CEO Response:")
# Use OpenAI directly since Gemini key might be invalid/rate limited
print(_call_openai_raw(prompt))
