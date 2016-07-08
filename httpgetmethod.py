import urllib.request
import re

#Function to get details of a page
def httpGet(url):
    #way of calling http GET method in python,html form is stored in s
    htmlContent=urllib.request.urlopen(url).read()                      
    global html
    #string form of s is stored in html
    html=str(htmlContent)                                               
    print(htmlContent)
    


#Function to extract Urls    
def extractUrls():
    tempUrlList=[]
    #mainUrlList - List to store all the links of the page
    global mainUrlList
    mainUrlList=[]
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
    for link in mainUrlList:  
        print(link)
        


#Method which initiates crawling
def main():
    global Url
    Url="http://www.python.org"
    httpGet(Url)
    extractUrls()

    
main()    
    
