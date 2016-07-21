import urllib.request
import re
import datetime
robotsFileContent=""
#Crawled list contins tuples (domain name,last crawled time+crawled delay).
global crawledList
crawledList=[]


#Takes Url as input and returns url of robots.txt file and domain name
def getRobotsname(url):
    #pattern1 checks for regular expression for domain name
    pattern1="(http|https)://\w+.\w+.([^/]*)+$"
    #pattern2 is regular expression for getting URL of the form "http://www.example.com/"
    pattern2="((http|https)\://\w*\.?.+\.\w+/)"
    #if url is of the form http://www.example.com then "/robots.txt" is added else "robots.txt" is added to www.example.com/
    if((re.match(pattern1,url)) == None):
        x=re.findall(pattern2,url)
        print(x)
        domainName=x[0][0]
        url=x[0][0]+"robots.txt"
        return url,domainName[:-1]
    else:
        domainName=url
        url=url+"/robots.txt"
        return url,domainName



#Takes robots.txt file content and returns Disallowed path lists and crawl delay
def getDisallowedList(robotsFileContent):
    listOfLinesOfRobots=robotsFileContent.split(r"\n")
    disallowedlist=[]
    allowedlist=[]
    crawlDelay=0
    for i in listOfLinesOfRobots:
        if(i.startswith("Disallow")):
            j=i.split(":")
            if j[1] not in disallowedlist:
                disallowedlist.append(j[1])
        if(i.startswith("Allow")):
            j=i.split(":")
            if j[1] not in allowedlist:
                allowedlist.append(j[1])
        if(i.startswith("Crawl-delay")):
            j=i.split(":")
            crawlDelay=j[1]
            crawlDelay=int(crawlDelay)
    return disallowedlist,allowedlist,crawlDelay



#Checks if any of the disallowed links are present in current Url,if present returns True
def isallowed(url,disallowedlist,allowedlist):
    domainPattern="(http|https)://\w+.\w+.[^/]*/"
    pattern1="(http|https)://\w+.\w+.([^/]*)+$"
    if(re.match(pattern1,url)):
        return True
    x=re.search(domainPattern,url)
    startingIndexofUri=x.end()-1
    #string conatins URL of the present URL
    string=url[startingIndexofUri:]
    print("URI is:",string)
    check=None
    for i in disallowedlist:
        pattern=i.strip()
        if pattern == "":
            continue
        if "*" in pattern:
            pattern=pattern.replace("*",".*")
        if "?" in pattern:
            pattern=pattern.replace("?","\?.*")
        #print(pattern)
        if(re.match(pattern,string) != None):
            check=False
            break
    for i in allowedlist:
        pattern=i.strip()
        if "*" in pattern:
            pattern=pattern.replace("*",".*")
        if "?" in pattern:
            pattern=pattern.replace("?","\?.*")
        #print(pattern)
        if(re.match(pattern,string) != None):
            check=True
            break
    return check




#Checks if system time is less than previous crawled time stored in crawled list and return true if system time is less
def checkCrawledList(domainName):
    if domainName.endswith("/"):
        domainName=domainName[:-1]
    print(domainName)
    for tuples in crawledList:
        if domainName in tuples[0]:
            #current time contains current system time
            currenttime=datetime.datetime.now()
            print("currenttime",currenttime)
            if(currenttime < tuples[1]):
                return False



#function that takes an Url and return True if it can be crawled
def isCrawlable(url):
    robotUrl,domainName=getRobotsname(url)
    s=urllib.request.urlopen(robotUrl).read()
    global robotsFileContent
    #robotsFileContent is string that contains content of robots.txt
    robotsFileContent=str(s)
    print(robotsFileContent)
    #disallowed list contains list of disallowed URIs
    disallowedlist,allowedlist,crawlDelay=getDisallowedList(robotsFileContent)
    print("Disallowed:")
    for i in disallowedlist:
        print(i)
    print("Allowed:")
    for i in allowedlist:
        print(i)
    print("Crawl Delay:",crawlDelay)
    check=isallowed(url,disallowedlist,allowedlist)
    print(check)
    if(check==False):
        return False,domainName,crawlDelay
    check=checkCrawledList(domainName)
    print(check)
    if(check==False):
        return False,domainName,crawlDelay
    return True,domainName,crawlDelay


p=50
t1=datetime.datetime.now()
t2=t1+datetime.timedelta(seconds=p)
print(t1)
print(t2)
crawledList.append(("http://www.google.com",t2))
crawledList.append(("http://www.facebook.com",t1))
print(crawledList)
url="http://play.google.com/books/css"
print(isCrawlable(url))
pattern1="(http|https)://\w+.\w+.[^/]*/"
