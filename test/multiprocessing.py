import sys
sys.path.insert(0, "/home/tomohiro/workspace/web_scraping_venv/lib/python3.6/site-packages")
from multiprocessing import Process, Queue
import time
from bs4 import BeautifulSoup
import requests
import re

def scraping(queue):
    url = "http://www.itmedia.co.jp/"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    a_tag_list = soup.find_all("a")
    protocol = re.search(".*:", url).group(0)
    url_list = []

    num = 0
    # Putting links into queue one by one
    # Once the for loop has been done, put Flase into queue
    for a in a_tag_list:
        a_link = str(a.get("href"))
        print("Sent" + a_link)
        queue.put(a_link)
        num += 1
        #time.sleep(1)

    queue = False

def consume(queue):
    time.sleep(2)
    num = 0
    # While queue has some data (queue is True)
    # Processing 
    while not queue.empty():
            #time.sleep(2)
            print("Got" + str(queue.get()))
            num += 1
            queue.get()

if __name__=="__main__":
    # Passing Queue() to queue
    queue = Queue()
    p1 = Process(target=scraping, args=(queue,))
    p2 = Process(target=consume, args=(queue,))
    p1.start()
    p2.start()
# def f1(q,q3):#送信1
    

#     while q3.empty():
#         q.put("A"+str(i))
#         i +=1
#         time.sleep(2)

# def f2(q,q3):#送信2
#     i=0
#     while q3.empty():
#         q.put("B"+str(i))
#         i +=1
#         time.sleep(3)

# def f3(q):#停止
#     time.sleep(20)
#     print("stop")
#     q.put(False)

# def f4(q1,q2,q3):#表示
#     while q3.empty():
#         while not q1.empty():
#             print(q1.get())
#         while not q2.empty():
#             print(q2.get())
#         time.sleep(5)


# if __name__ == '__main__':
#     q1 = Queue()
#     q2 = Queue()
#     q3 = Queue()
#     p1 = Process(target=f1, args=(q1,q3))
#     p2 = Process(target=f2, args=(q2,q3))
#     p3 = Process(target=f3, args=(q3,))
#     p4 = Process(target=f4, args=(q1,q2,q3))
#     p1.start()
#     p2.start()
#     p3.start()
#     p4.start()
