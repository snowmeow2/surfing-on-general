from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
#from collections import Counter
import time, re
#re, sys, 

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/22.0'}

def get_table():

    #print("Input the keywords, separate each with spaces.")
    #keywords = input().replace(" ", "+")
    #keywords = sys.argv[1]
    alltable = []
    #if True:
    for i in range(0, 101):
        time.sleep(0.2)
        
        url = "https://sora.komica.org/00/pixmicat.php?mode=module&load=mod_threadlist&page="+str(i)
        req = Request(url=url, headers=headers)
        #print("Reading: " + url)
        
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
    
        content = soup.find("table")
            
        rows = content.findAll('tr')
        for row in rows:
            columns = list(row.findAll('td'))
            tds = []

            for column in columns:
                sub_html = column.encode()
                s = BeautifulSoup(sub_html, "html.parser")
                tds.append(s.find('td').text.strip())
            
            if tds != []:            
                if int(tds[3]) > 0 and tds[1].encode("utf-8") != '無題'.encode("utf-8"):
                    if "&#x" not in tds[1]:
                        alltable.append(tds)
                        #print(tds)
        print("讀取第"+str(i)+"頁...")
    alltable = [x for x in alltable if x != []]
    #print(alltable)
    print("共檢視了 "+str(len(alltable))+" 串.")
    print("讀取完畢!")
    return alltable
    
def read_thread(table):
#    word_count = 0
#    word_count2 = 0
#    open('copy_info.txt','w')
    print("正在讀取共 "+str(len(table))+" 串.")
    full = []
    for a in range(len(table)):
        time.sleep(1)

        
        textt = []
        url = "https://sora.komica.org/00/pixmicat.php?res="+table[a][0]
        try:
            req = Request(url=url, headers=headers)
            html = urlopen(req, timeout=5).read()
            print("第"+ str(a) +"篇: "+table[a][1])
            #print("正在讀取位於"+url+" 的文件...("+str(b_time)+"-"+str(passtime)+"/"+total_len+")")
        except Exception as e:
            print(str(e))
        
        #req = Request(url=url, headers=headers)
        
        #html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
        
        text = soup.find_all("div", "quote")
        for div in text:
            div_e = div.encode()
            div_eb = BeautifulSoup(div_e, "html.parser")
            all_text = div_eb.find("div", "quote").text.strip()
            all_text = re.sub(">>.......\d", "", all_text)
            all_text = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", all_text)
            all_text = re.sub("無本文", "", all_text)
            all_text = re.sub("\u3000", "", all_text)
            all_text = re.sub("\xa0", "", all_text)
            if len(all_text.encode("utf-8")) > 300:
                continue
            if all_text != '':
                textt.append(all_text)
        #print(textt)
        if len(textt) > 1:
            full.append(textt)
            
    return full

def createTarget(table):
    input = []
    for i in table:
        for j in range(len(i)):
            if j != 0:
                if j == 1:
                    input.append(i[0]+'##====##'+i[j])
                elif j == 2:
                    input.append(i[0]+' '+i[j-1]+'##====##'+i[j])
                else:
                    input.append(i[0]+' '+i[j-2]+' '+i[j-1]+'##====##'+i[j])
    #print(input)
    with open('thread_info.txt', 'wb') as f:
        for k in input:
            #word = k.encode("utf-8")
            f.write(k.encode("utf-8"))
            f.write("\n".encode("utf-8"))
    #
def main():
    start = time.time()
    
    data = get_table()
    table = read_thread(data)
    createTarget(table)
    
    end = time.time()
    print(end-start)
   
if __name__ == '__main__':
    main()
