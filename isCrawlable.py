import urllib.request
import re
import datetime
robotsFileContent=""
#Crawled list contins tuples with first element domain name and second element previous crawled time
global crawledList
crawledList=[]


#Takes Url and return name of robots.txt file
def getRobotsname(url):
    pattern1="(http|https)://www.\w+.\w{3}$"
    pattern2="((http|https)\://\w*\.?.+\.\w+/)"
    if((re.match(pattern1,url)) == None):
        x=re.findall(pattern2,url)
        domainName=x[0][0]
        url=x[0][0]+"robots.txt"
        return url,domainName
    else:
        domainName=url
        url=url+"/robots.txt"
        return url,domainName



#Takes robots.txt file content and returns Disallowed path lists and crawl delay
def getDisallowedList(robotsFileContent):
    listOfLinesOfRobots=robotsFileContent.split(r"\n")
    disallowedlist=[]
    crawlDelay=0
    for i in listOfLinesOfRobots:
        if(i.startswith("Disallow")):
            j=i.split(":")
            if j[1] not in disallowedlist:
                disallowedlist.append(j[1])
        if(i.startswith("Crawl-delay")):
            j=i.split(":")
            crawlDelay=j[1]
            crawlDelay=int(crawlDelay)
    return disallowedlist,crawlDelay



#Checks if any of the disallowed links are present in current Url,if present returns True
def isallowed(url,disallowedlist):
    print(url)
    for i in disallowedlist:
        pattern=i
        print(pattern)
        if "*" in pattern:
            pattern=pattern.replace("*",".*")
        if(re.search(pattern,url) != None):
            return True



#Checks if system time is less than previous crawled time stored in crawled list and return true if system time is less
def checkCrawledList(domainName):
    if domainName.endswith("/"):
        domainName=domainName[:-1]
    print(domainName)
    for tuples in crawledList:
        if domainName in tuples[0]:
            currenttime=datetime.datetime.now()
            print("currenttime",currenttime)
            if(currenttime < tuples[1]):
                return True



#function that takes an Url and return True if it cannot be crawled 
def isCrawlable(url):
    robotUrl,domainName=getRobotsname(url)
    s=urllib.request.urlopen(robotUrl).read()
    global robotsFileContent
    robotsFileContent=str(s)
    print(robotsFileContent)
    disallowedlist,crawlDelay=getDisallowedList(robotsFileContent)
    #for i in disallowedlist:
     #   print(i)
    print("Crawl Delay:",crawlDelay)
    x=isallowed(url,disallowedlist)
    print(x)
    if(x==True):
        return True
    x=checkCrawledList(domainName)
    print(x)
    if(x==True):
        return True
    return False


p=50
t1=datetime.datetime.now()
t2=t1+datetime.timedelta(seconds=p)
print(t1)
print(t2)
crawledList.append(("http://www.google.com",t2))
crawledList.append(("http://www.facebook.com",t1))
print(crawledList)
url="http://www.google.com/ebooks/musica"
print(isCrawlable(url))

