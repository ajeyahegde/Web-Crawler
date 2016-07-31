import unittest
import re
import urllib.request
import datetime
#from test1 import getRobotsname
class testing(unittest.TestCase):
    def teststring(self):
        inputurl="http://www.bitbucket.com/robots.txt"
        s=urllib.request.urlopen(inputurl).read()
        content=str(s)
        output=getDisallowedList(content)
        print(output)
        self.assertGreaterEqual(len(output[0]),0)
        self.assertGreaterEqual(len(output[1]),0)
        self.assertGreaterEqual(output[2],0)


def getDisallowedList(robotsFileContent):
    listOfLinesOfRobots=robotsFileContent.split(r"\n")
    disallowedlist=[]
    allowedlist=[]
    crawlDelay=0
    #user=1 if User-agent = * and user=0 if otherwise
    user=0
    for i in listOfLinesOfRobots:
        if("User-agent" in i):
            j=i.split(":")
            j[1]=j[1].strip()
            #print(j)
            if(j[1]=="*"):
                user=1
                continue
            else:
                user=0
        if(i.startswith("Disallow") and user == 1):
            j=i.split(":")
            if j[1] not in disallowedlist:
                disallowedlist.append(j[1])
        if(i.startswith("Allow") and user == 1):
            j=i.split(":")
            if j[1] not in allowedlist:
                allowedlist.append(j[1])
        if(i.startswith("Crawl-delay")):
            j=i.split(":")
            crawlDelay=j[1]
            crawlDelay=int(crawlDelay)
    return disallowedlist,allowedlist,crawlDelay


if __name__=="__main__":
    unittest.main()
