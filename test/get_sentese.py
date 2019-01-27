import requests
from bs4 import BeautifulSoup
import sys
import time

def get_p(url):
	#start = time.time()
	res = requests.get(url[0])
	soup = BeautifulSoup(res.content, "html.parser")
	p_tags = soup.find_all("p")
	#end = time.time()
	p_tags_texts = [ p.text for p in p_tags ]
	only_text = "".join(p_tags_texts)
	print(only_text)
	#print(p_tags_texts)
if __name__=="__main__":
    get_p(sys.argv[1:])
