import urllib.request
import re
def HttpGet(url):
    s=urllib.request.urlopen(url).read()
    global html
    html=str(s)
    #print(s)
def ExtractUrls():
    links = re.findall('"((http|ftp)s?://.*?)"', html)
    for link in links:
        print(link)
HttpGet("http://www.wikipedia.com")
ExtractUrls()
