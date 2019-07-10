# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 07:27:18 2019

@author: Fujibayashi
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime
import time, re
import pickle

class mainPost:
    def __init__(self, number, ID, postTime, replies):
        self.number = number
        self.ID = ID
        self.postTime = postTime
        self.replies = replies
        self.replyTo = None
        self.content = None
        self.has_img = False
        self.has_html = False
        
class Post:
    def __init__(self, number, ID, postTime, replyTo, content):
        self.number = number
        self.ID = ID
        self.postTime = postTime
        self.replyTo = replyTo
        self.content = content
        #self.has_img = False
        self.has_html = False
        	
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/22.0'}

def get_table():
    alltable = []
    
    for i in range(0,220):
        time.sleep(0.2)
        
        url = "https://sora.komica.org/00/pixmicat.php?mode=module&load=mod_threadlist&page="+str(i)
        req = Request(url=url, headers=headers)
        
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
    	
        #尋找列表
        catalog = soup.find("table")
        
        #選擇列欄    
        rows = catalog.findAll('tr')
        for row in rows:
            columns = list(row.findAll('td'))
            tds = []

            for column in columns:
                sub_html = column.encode()
                s = BeautifulSoup(sub_html, "html.parser")
                tds.append(s.find('td').text.strip())
                #print(tds)
            if tds != []:
                if "&#x" not in tds[1]:
                    id_text = re.search( r'ID:.*', tds[4]).group()
                    id_text = re.sub("ID:", "", id_text)
                    post_time = re.sub("\(.*\)", "", tds[4])
                    post_time = re.search( r'.*\d\.\d\d\d.?ID', post_time).group()
                    post_time = re.sub("\.\d\d\d.?ID", "", post_time)
                    post_time = datetime.strptime(post_time, "%Y/%m/%d %H:%M:%S")
            				
                    newPost = mainPost(tds[0], id_text, post_time, tds[3])
                    alltable.append(newPost)
                    #print(newPost.number)
                    #print(newPost.ID)
                    #print(newPost.postTime)
                    #print(newPost.replies)
        print("讀取第"+str(i)+"頁...")
        
    alltable = [x for x in alltable if x != []]
    print("共索引了 "+str(len(alltable))+" 串。")
    print("讀取完畢!")
    return alltable
    
def read_thread(table):
    print("正在讀取共 "+str(len(table))+" 串。")
    full = []
    
    for a in range(len(table)):
        time.sleep(0.9)
        thread = []
        thread.append(table[a])
        post_quote = []
        post_meta = []
        
        url = "https://sora.komica.org/00/pixmicat.php?res="+table[a].number
        try:
            req = Request(url=url, headers=headers)
            html = urlopen(req, timeout=5).read()
            print("正在讀取位於 "+url+" 的文件...第"+ str(a) +"篇 ")
        except Exception as e:
            print(str(e))

        soup = BeautifulSoup(html, "html.parser")
        reply_pattern = re.compile(r'>>?N?o?\.?\d\d\d\d\d\d\d\d')
        
        main =  soup.find("div", "post threadpost").encode()
        main = BeautifulSoup(main, "html.parser")
        if main.find("a", "file-thumb") != None:
            table[a].has_img = True
        
        '''由於網頁問題無法擷取回復中的圖片
        rep_img = []
        rep = soup.find_all("div", "post reply")
        for div in rep:
            div = div.encode()
            div = BeautifulSoup(div, "html.parser")
            if div.find("a", "file-thumb") != None:
                rep_img.append(True)
            else:
                rep_img.append(False)
        '''
        
        quote = soup.find_all("div", "quote")
        for div in quote:
            div = div.encode()
            div = BeautifulSoup(div, "html.parser")
            has_img = False
            has_html = False
            
            div_text = div.find("div", "quote").text.strip()
            
            div_reply = reply_pattern.findall(div_text)
            for i in range(len(div_reply)):
                div_reply[i] = re.sub(r'>>?N*o*\.*', "", div_reply[i])
            if div_reply == []:
                div_reply = [table[a].number]
            
            div_text = re.sub(">>?N?o?\.?\d\d\d\d\d\d\d\d", "", div_text)
            if div_text != re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", div_text):
                has_html = True            
            div_text = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", div_text)
            div_text = re.sub("\u3000", "", div_text)
            div_text = re.sub("\xa0", "", div_text)

            if div_text == '':
                div_text = "無本文"
                
            post_quote.append([div_reply, div_text, has_html])
            table[a].content = post_quote[0][1]
            table[a].has_html = post_quote[0][2]
        #print(post_quote)
            
        meta = soup.find_all("div", "post-head")
        for div in meta:
            div = div.encode()
            div = BeautifulSoup(div, "html.parser")
            
            div_number = div.find("input")["name"]
            
            div_identity = div.find("span", "now").text.strip()
            div_timing = re.sub("\(.*\)", "", div_identity)
            div_timing = re.search( r'.*\d\.\d\d\d.?ID', div_timing).group()
            div_timing = re.sub("\.\d\d\d.?ID", "", div_timing)
            div_timing = datetime.strptime(div_timing, "%Y/%m/%d %H:%M:%S")
            
            div_ID = re.search( r'ID:.*', div_identity).group()
            div_ID = re.sub("ID:", "", div_ID)
            
            post_meta.append([div_number, div_ID, div_timing])
        
        for i in range(len(post_meta)-1):
            newReply = Post(post_meta[i+1][0], post_meta[i+1][1], post_meta[i+1][2], post_quote[i+1][0], post_quote[i+1][1])
            #newReply.has_img = rep_img[i]
            newReply.has_html = post_quote[i+1][2]
            
            thread.append(newReply)
            
        full.append(thread)
        
        file_Name = "Full_thread"
        fullObject = open(file_Name,'wb') 
        pickle.dump(full, fullObject)   
        fullObject.close()
        
    return full

def old_Viewer(full):
    for i in full:
        print(str(i[0].number))
        for j in i:
            print("    ", end='')
            print(str(j.number) + " ｜ " + str(j.postTime) + " ｜ ID："+str(j.ID)+" ｜ URL："+str(j.has_html)+" ｜ 內文："+str(j.content.encode("utf-8"))+" ｜ Reply to "+str(j.replyTo))

def main():
    start = time.time()
    
    data = get_table()
    read_thread(data)
    end = time.time()
    print(end-start)
   
if __name__ == '__main__':
    main()
