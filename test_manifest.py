import json, urllib.request

def check_cws(cws_id):
    url = f"https://chromewebstore.google.com/detail/{cws_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        return res.status == 200
    except:
        return False

print("fkjkpijpiecandcaehphllpjiehofmad:", check_cws("fkjkpijpiecandcaehphllpjiehofmad"))
print("fake1234fake1234fake1234fake1234:", check_cws("fake1234fake1234fake1234fake1234"))
