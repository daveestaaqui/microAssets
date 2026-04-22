import urllib.request
import json
import os

with open("./_scripts/.env", "r") as f:
    for line in f:
        if line.startswith("OPENAI_API_KEY="):
            os.environ["OPENAI_API_KEY"] = line.strip().split("=", 1)[1]

prompt = """You are Lena Voss, the CEO of SporlyWorks.
I am the Antigravity Engineering Core.
We have successfully completed Priority 1: Funnel Intelligence & Activation (Dashboards and the Autonomous 4-day Drip sequence).

Our conversation previously truncated. Please provide Priority 2 so we can advance the agenda immediately. Be direct, clear, and focused on our immediate goals of validating the funnel and driving revenue."""

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
}
data = json.dumps({
    "model": "gpt-4o",
    "messages": [{"role": "system", "content": prompt}],
    "temperature": 0.4,
}).encode("utf-8")

req = urllib.request.Request(url, data=data, headers=headers)
with urllib.request.urlopen(req, timeout=90) as response:
    result = json.loads(response.read().decode("utf-8"))
    print(result["choices"][0]["message"]["content"].strip())
