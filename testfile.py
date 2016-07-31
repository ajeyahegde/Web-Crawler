import unittest
import re
import urllib.request
import datetime
#from test1 import getRobotsname
class testing(unittest.TestCase):
    def teststring(self):
        inputurl="http://www.google.com/ebooks/musica"
        output=getRobotsname(inputurl)
        print(output)
        self.assertEqual(output,("http://www.google.com/robots.txt","http://www.google.com"))

def getRobotsname(url):
    #pattern1 checks for regular expression for domain name
    urlPattern1="((http|https)://)?\w+.\w+.([^/]*)+$"
    #pattern2 is regular expression for getting URL of the form "http://www.example.com/"
    urlPattern2="(((http|https)\://)?\w*\.?.+\.\w+/)"
    #if url is of the form http://www.example.com then "/robots.txt" is added else "robots.txt" is added to www.example.com/
    if((re.match(urlPattern1,url)) == None):
        x=re.findall(urlPattern2,url)
        #print(x)
        domainName=x[0][0]
        url=x[0][0]+"robots.txt"
        return url,domainName[:-1]
    else:
        domainName=url
        url=url+"/robots.txt"
        return url,domainName

if __name__=="__main__":
    unittest.main()
