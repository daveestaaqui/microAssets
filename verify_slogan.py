import re
path = "_landing_page/index.html"
with open(path, "r") as f:
    content = f.read()
if "cultivating intelligent workflows" in content:
    print("FOUND correct slogan in HTML")
else:
    print("MISSING correct slogan in HTML")
