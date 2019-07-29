# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 19:41:40 2019

@author: Fujibayashi
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime
import time, re, sys, json

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/22.0'}
reply_pattern = re.compile(r'>>?N?o?\.?\d\d\d\d\d\d\d\d')

def get_table(goal=1):
    table = []
    
    for i in range(0,goal):
        time.sleep(0.2)
        
        url = "https://sora.komica.org/00/pixmicat.php?mode=module&load=mod_threadlist&page="+str(i)
        req = Request(url=url, headers=headers)
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
    	
        #尋找列表列欄
        rows = soup.find("table").findAll('tr')
        
        for row in rows:
            columns = row.findAll('td')
            tds = [j.text.strip() for j in columns]
            thread = {}

            if tds != []:
                if "&#x" not in tds[1]:
                    id_text = re.search(r'ID:.*', tds[4]).group()
                    id_text = re.sub("ID:", "", id_text)
                    
                    post_time = re.sub("\(.*\)", "", tds[4])
                    post_time = re.search(r'.*\d\.\d\d\d.?ID', post_time).group()
                    post_time = re.sub("\.\d\d\d.?ID", "", post_time)
                    
                    thread['number'] = tds[0]
                    thread['ID'] = id_text
                    thread['time'] = post_time
                    thread['replies'] = tds[3]
            				
                    table.append(thread)

        sys.stdout.write('\r')
        sys.stdout.write("("+str(round((100*(i+1)/(goal)), 2))+"%) "+"讀取第 "+str(i+1)+"/"+str(goal)+" 頁...")
        sys.stdout.flush()
    #table = [x for x in table if x != []]
    print("共索引了 "+str(len(table))+" 串。")
    #print("讀取完畢!")
    return table

def read_thread(table):
    print("正在讀取共 "+str(len(table))+" 串。\n")

    for i, thread in enumerate(table):
        time.sleep(0.9)
        posts = []

        url = "https://sora.komica.org/00/pixmicat.php?res="+thread['number']
        try:
            req = Request(url=url, headers=headers)
            html = urlopen(req, timeout=5).read()
            
            sys.stdout.write('\r')
            sys.stdout.write("("+str(round((100*(i+1)/len(table)), 2))+"%) "+"讀取第 "+str(i+1)+"/"+str(len(table))+" 篇...位於 "+url)
            sys.stdout.flush()
            
        except Exception as e:
            print(str(e))
        
        soup = BeautifulSoup(html, "html.parser")
        meta = soup.find_all("div", "post-head")
        quote = soup.find_all("div", "quote")
        for divQ, divM in zip(quote, meta):
            post = {}
            
            #抓取meta
            divM = divM.encode()
            divM = BeautifulSoup(divM, "html.parser")
            
            post['number'] = divM.find("input")["name"]
            
            div_identity = divM.find("span", "now").text.strip()
            div_timing = re.sub("\(.*\)", "", div_identity)
            div_timing = re.search( r'.*\d\.\d\d\d.?ID', div_timing).group()
            post['posttime'] = re.sub("\.\d\d\d.?ID", "", div_timing)
            
            div_ID = re.search( r'ID:.*', div_identity).group()
            post['ID'] = re.sub("ID:", "", div_ID)
            
            #抓取內容
            post_text = divQ.text.strip()
            post_reply = reply_pattern.findall(post_text)
            
            for j, reply in enumerate(post_reply):
                post_reply[j] = re.sub(r'>>?N*o*\.*', "", reply)
            if post_reply == []:
                if post['number'] == thread['number']:
                    post_reply = None
                else:
                    post_reply = [thread['number']]
            
            post_text = re.sub(">>?N?o?\.?\d\d\d\d\d\d\d\d", "", post_text)

            if post_text == '':
                post_text = "無本文"
            post['content'] = post_text
            post['replyTo'] = post_reply
            posts.append(post)
            
        table[i]['posts'] = posts
        data = {'full':table}
        with open('Full_thread.json', 'w') as f:
            json.dump(data, f)
            
    print('讀取完成！檔案已經存在 Full_thread.json 中。')

'''備用區
if div_text != re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", div_text):
div_text = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", div_text)
div_text = re.sub("\u3000", "", div_text)
div_text = re.sub("\xa0", "", div_text)
post['posttime'] = datetime.strptime(div_timing, "%Y/%m/%d %H:%M:%S")
post_time = datetime.strptime(post_time, "%Y/%m/%d %H:%M:%S")'''

table = get_table(220)
read_thread(table)