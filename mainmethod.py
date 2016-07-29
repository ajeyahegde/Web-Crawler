import urllib.request
from queue import Queue
import threading
import datetime
import re
from tinydb import TinyDB,Query

#Takes Url and returns name of robots.txt file and domain name
def getRobotsname(url):
    #pattern1 checks for regular expression for domain name
    urlPattern1="(http|https)://\w+.\w+.([^/]*)+$"
    #pattern2 is regular expression for getting URL of the form "http://www.example.com/"
    urlPattern2="((http|https)\://\w*\.?.+\.\w+/)"
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


#Takes robots.txt file content and returns Disallowed path lists and crawl delay
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


#Checks if any of the disallowed links are present in current Url,if present returns True
def isAllowed(url,disallowedlist,allowedlist):
    domainPattern="(http|https)://\w+.\w+.[^/]*/"
    domainPattern1="(http|https)://\w+.\w+.([^/]*)+$"
    if(re.match(domainPattern1,url)):
        return True
    x=re.search(domainPattern,url)
    startingIndexofUri=x.end()-1
    #string conatins URL of the present URL
    URIstring=url[startingIndexofUri:]
    #print("URI is:",URIstring)
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
        if(re.match(pattern,URIstring) != None):
            check=False
            break
    for i in allowedlist:
        pattern=i.strip()
        if "*" in pattern:
            pattern=pattern.replace("*",".*")
        if "?" in pattern:
            pattern=pattern.replace("?","\?.*")
        #print(pattern)
        if(re.match(pattern,URIstring) != None):
            check=True
            break
    return check


#Checks if system time is less than previous crawled time stored in crawled list and return true if system time is less
def checkCrawledList(domainName):
    if domainName.endswith("/"):
        domainName=domainName[:-1]
    #print(domainName)
    for tuples in crawledDomainInfoList:
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
    #print("Robots URL is:",robotUrl)
    try:
        robotsContent=urllib.request.urlopen(robotUrl).read()
        global robotsFileContent
    #robotsFileContent is string that contains content of robots.txt
        robotsFileContent=str(robotsContent)
    #disallowed list contains list of disallowed URIs and allowed list contains list of allowed URIs
        disallowedlist,allowedlist,crawlDelay=getDisallowedList(robotsFileContent)
        #print("Crawl Delay:",crawlDelay)
        check=isAllowed(url,disallowedlist,allowedlist)
        if(check==False):
            return 0,domainName,crawlDelay
    except urllib.request.URLError as e:
        print(url)
        print("Error while opening the robots.txt file",e.args)
    except urllib.request.HTTPError as e:
        print(url)
        print("Error while opening the robots.txt file",e.args)
    check=checkCrawledList(domainName)
    if(check==False):
        return 1,domainName,crawlDelay
    return 2,domainName,crawlDelay

#Function to get details of a page
def httpGet(url):
    #way of calling http GET method in python,html form is stored in s
    try:
        htmlContent=urllib.request.urlopen(url).read()
        html=str(htmlContent)
        #print(htmlContent)
        return html
    except urllib.request.URLError as e:
        print("Error while opening url:",url,e.args)
    except urllib.request.HTTPError as e:
        print("Error while oprning url:",url,e.args)
    #string form of s is stored in html
    #html=str(htmlContent)
    #print(htmlContent)



#Function to extract Urls
def extractUrls(html,url):
    tempUrlList=[]
    tempUrlList.clear()
    #mainUrlList - List to store all the links of the page
    mainUrlList=[]
    mainUrlList.clear()
    #linkForm-Regular expression pattern to find links present in page
    linkForm="(href=\".*?\")"
    html=str(html)
    linkForm=str(linkForm)
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
                finalLink=url+link
            else:
                finalLink=url+"/"+link
            mainUrlList.append(finalLink)
    #Loop that adds URLs in mainUrlList to Queue Q.
    for link in mainUrlList:
        #print(link)
        urlQueue.put(link)
        #print(Q._qsize())

#Class for threading
class urlThread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.threadname=name
    def run(self):
        lock=threading.Lock()
        global count
        count=0
        while(urlQueue.empty()== False and count < 5):
            lock.acquire()
            try:
                print(self.threadname)
                url=getUrl()
                print(url)
            finally:
                print("Lock released")
                lock.release()
            crawl(url)
            count=count+1


#getUrl() removes url from queue and return url
def getUrl():
    url=urlQueue.get()
    return url



#Method which initiates crawling
def main():
    global urlQueue
    #Crawled list contians tuples (domain name,last crawled time+crawled delay).
    global crawledDomainInfoList
    crawledDomainInfoList=[]
    global database
    database=TinyDB("db.json")
    threadList=[]
    global noOfThreads
    noOfThreads=5
    global defaultCrawlDelay
    defaultCrawlDelay=10
    global urlQuery
    urlQuery=Query()
    database.purge()
    print(database.all())
    #Queue that stores URLs to be crawled
    urlQueue=Queue(maxsize=0)
    urlQueue.put("http://www.python.org")
    urlQueue.put("http://www.google.com")
    urlQueue.put("http://www.youtube.com")
    urlQueue.put("http://www.bbc.com")
    urlQueue.put("http://www.msrit.edu")
    database.insert({"URL":"","content":("","")})
    for i in range(noOfThreads):
        threadList.append(urlThread("thread"+str(i)))
    for i in range(noOfThreads):
        threadList[i].start()
    #for i in range(5):
    #    threadList[i].setDaemon(True)
    for i in range(noOfThreads):
        threadList[i].join()
    for i in database.all():
        print(i.get('URL'))
    checkContent=str(input("Enter Url to retrive web info"))
    print(database.get(urlQuery.URL == checkContent))



#This method takes and crawls if check==2 along with adding domain name to crawled list
#adds the removed URL to Q if check==1 and doesnt crawl if check==0
def crawl(url):
    #URL is removed from Q and stored in Url
    print("URL is:",url)
    check,domainName,crawlDelay=isCrawlable(url)
    #print("Check:",check)
    if(check == 2):
        htmlContent= httpGet(url)
        extractUrls(htmlContent,url)
        currentTime=str(datetime.datetime.now())
        if(database.contains(urlQuery.URL==url)):
            database.update({"content":(htmlContent,currentTime)},urlQuery.URL==url)
        else:
            database.insert({"URL":url,"content":(htmlContent,currentTime)})
        if(crawlDelay==0):
            crawlDelay=defaultCrawlDelay
        for tuple in crawledDomainInfoList:
            if (domainName == tuple[0]):
                index=crawledDomainInfoList.index(tuple)
                del crawledDomainInfoList[index]
        crawledDomainInfoList.append((domainName,datetime.datetime.now()+datetime.timedelta(seconds=crawlDelay)))

    elif(check == 1):
        urlQueue._put(url)
    print(crawledDomainInfoList)

main()


