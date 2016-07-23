import urllib.request
from queue import Queue
from threading import Thread
import datetime
import re


#Takes Url and returns name of robots.txt file and domain name
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



#function that takes an Url and returns 0 if it cannot be crawled
# 1 if enough crawl gap is given and 2 if it can be crawled and also returns domain name and crawl delay
def isCrawlable(url):
    crawlDelay=0
    #robotUrl stores url of robots.txt
    robotUrl,domainName=getRobotsname(url)
    print("Robots URL is:",robotUrl)
    try:
        s=urllib.request.urlopen(robotUrl).read()
        global robotsFileContent
    #robotsFileContent is string that contains content of robots.txt
        robotsFileContent=str(s)
    #disallowed list contains list of disallowed URIs and allowed list contains list of allowed URIs
        disallowedlist,allowedlist,crawlDelay=getDisallowedList(robotsFileContent)
        print("Crawl Delay:",crawlDelay)
        check=isallowed(url,disallowedlist,allowedlist)
        if(check==False):
            return 0,domainName,crawlDelay
    except urllib.request.URLError as e:
        print(e.args)
    except urllib.request.HTTPError as e:
        print(e.args)
    check=checkCrawledList(domainName)
    if(check==False):
        return 1,domainName,crawlDelay
    return 2,domainName,crawlDelay

#Function to get details of a page
def httpGet(url):
    #way of calling http GET method in python,html form is stored in s
    global html
    try:
        htmlContent=urllib.request.urlopen(url).read()
        html=str(htmlContent)
        #print(htmlContent)
    except urllib.request.URLError as e:
        print(e.args)
    except urllib.request.HTTPError as e:
        print(e.args)
    #string form of s is stored in html
    #html=str(htmlContent)
    #print(htmlContent)



#Function to extract Urls
def extractUrls():
    tempUrlList=[]
    tempUrlList.clear()
    #mainUrlList - List to store all the links of the page
    global mainUrlList
    mainUrlList=[]
    mainUrlList.clear()
    #linkForm-Regular expression pattern to find links present in page
    linkForm="href=\".*?\""
    foundedLinks=re.findall(linkForm, html)
    #for loop that stores all links without some starting and ending string in list called tempUrlList
    for link in foundedLinks:
        link1 = link.split('"')
        purelink=link1[1]
        if(purelink.startswith(("#","javascript","/downloads")) or purelink.endswith((".js",".css",".xml",".png",".jpg",".gif",".tiff",".xhtml",".jpeg",".ico"))):
            continue
        tempUrlList.append(purelink)
    #for loop for storing all the actual links obtained in mainUrlList
    for link in tempUrlList:
        if(link.startswith(("http","https"))):
            mainUrlList.append(link)
            continue
        elif(link.startswith("//")):
            finalLink="http:"+link               #TODO:original protocol should be used
            mainUrlList.append(finalLink)
        else:
            if(link.startswith("/")):
                finalLink=Url+link
            else:
                finalLink=Url+"/"+link
            mainUrlList.append(finalLink)
    #Loop that adds URLs in mainUrlList to Queue Q.
    for link in mainUrlList:
        #print(link)
        Q.put(link)
        #print(Q._qsize())

#Class for threading
class urlThread(Thread):
    def __init__(self,name):
        Thread.__init__(self)
        self.threadname=name
    def run(self):
        while(Q.empty()== False):
            #print(self.threadname)
            Crawl(Q)



#Method which initiates crawling
def main():
    global Url
    global Q
    global crawledList
    #Crawled list contins tuples (domain name,last crawled time+crawled delay).
    crawledList=[]
    #Queue that stores URLs to be crawled
    Q=Queue(maxsize=0)
    Q.put("http://www.python.org")
    Q.put("http://www.google.com")
    t1=urlThread("thread1")
    t2=urlThread("thread2")
    t1.start()
    t2.start()
#This method removes URL from Q and crawls if check==2 along with adding domain name to crawled list
#adds the removed URL to Q if check==1 and doesnt crawl if check==0
def Crawl(Q):
    global Url
    #URL is removed from Q and stored in Url
    Url=Q.get()
    print("URL is:",Url)
    check,domainName,crawlDelay=isCrawlable(Url)
    print("Check:",check)
    if(check == 2):
        httpGet(Url)
        extractUrls()
        if(crawlDelay==0):
            crawlDelay=10
        crawledList.append((domainName,datetime.datetime.now()+datetime.timedelta(seconds=crawlDelay)))

    elif(check == 1):
        Q._put(Url)
    print(crawledList)

main()

