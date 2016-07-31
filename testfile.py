import unittest
import re
import urllib.request
import datetime
#from test1 import getRobotsname
class testing(unittest.TestCase):
    def teststring(self):
        inputurl="www.google.com"
        global  crawledDomainList
        crawledDomainList=[]
        crawledDomainList.append(("http://www.bitbucket.com",datetime.datetime.now()+datetime.timedelta(seconds=10)))
        crawledDomainList.append(("http://www.google.com",datetime.datetime.now()+datetime.timedelta(seconds=5)))
        crawledDomainList.append(("http://www.facebook.com",datetime.datetime.now()+datetime.timedelta(seconds=-5)))
        output=checkCrawledList(inputurl)
        print(crawledDomainList)
        print(output)
        self.assertFalse(output)


def checkCrawledList(domainName):
    if domainName.endswith("/"):
        domainName=domainName[:-1]
    #print(domainName)
    for tuples in crawledDomainList:
        if domainName in tuples[0]:
            #current time contains current system time
            currenttime=datetime.datetime.now()
            print("currenttime",currenttime)
            if(currenttime < tuples[1]):
                return False

if __name__=="__main__":
    unittest.main()
