import requests
import re
r = requests.get("https://myyco.com/product/golden-teacher/", headers={"User-Agent": "Mozilla/5.0"})
urls = re.findall(r'https://myyco.com/wp-content/uploads/[^"]*\.jpg', r.text)
for u in urls[:3]: print(u)
