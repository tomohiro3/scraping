import sys
#sys.path.insert(0, "/home/tomohiro/workspace/web_scraping_venv/lib/python3.6/site-packages")
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bs4 import BeautifulSoup
import requests
import re
import sys
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

async_mode = None
# If the connection gets disconnected in the middle,
# A new session is gonna be created, then
# the server is gonna get not to send back the data to the same session's client
# so that set ping_timeout long not to make the socketio disconnected
ping_timeout = 300
socketio = SocketIO(app, async_mode=async_mode, ping_timeout=ping_timeout)
thread = None

app.config["MONGO_URI"] = "mongodb://localhost:27017/scrapingdb"
mongo = PyMongo(app)
urls = mongo.db.urls

@app.route("/itmedia/")
def itmedia():
	return render_template("itmedia/itmain.html")

@app.route("/nikkei/")
def nikkei():
	return render_template("nikkei/nkmain.html")

@app.route("/other/")
def other():
	return render_template("other/otmain.html")

@app.route("/bookmark/")
def bookmark():
	return render_template("bookmark/bkmain.html")


@app.route("/", methods=["POST"])
def test_db():
	url = request.form["mongo"]
	url = {"subject": url}
	urls.insert_one(url)
	result = mongo.db.urls.find({"subject": url})
	return render_template(("base.html"), urls=result)	
	


@app.route("/", methods=["GET"])
def index_return():
	#デフォルト設定でFlaskはhtmlの所在を、flaskアプリケーションと同じ階層にある
	#templatesディレクトリの中に探しに行くので下記のようなパスでよい
	return render_template("base.html")

@socketio.on("message")
def initial_response(msg):
	send("Hello!")
	print(msg)

@socketio.on("myevent")
def handle_message(array):
	url = array[0]
	word = array[1]

	#if re.match(r"(^\\[A-Z].*[a-z].*)?", word):
	# 日本語だと強制的にutf-8？にエンコードされるので、それをutf-8に再度デコード	
	word = word.encode("raw_unicode_escape")
	word = word.decode("utf-8")

	#Getting the global variable, thread
	#You can always default the thread value as None by doing this
	global thread

	if thread is None:
		#Starting the function, "sending_results" as background task
		#By doing this, you can devide the threads having the funcion to keep sokcket connection(main thread)
		#and one to send the url and keyword 
		socketio.start_background_task(target=sending_results(url, word))

def sending_results(url, word):
	start = time.time()
	
	print(url)	
	print(word)

	if url == "" or word == "":
		print("”URL”　と　”キーワード”　を指定してください")
		send("”URL”　と　”キーワード”　を指定")
		sys.exit()

	if not url.endswith("/"):
		url = url + "/"

	try:
		res = requests.get(url)
	except Exception as e:
		print(e)
		print("URLが正しくありません")
		send("URLが正しくありません")
		send(str(e))
		sys.exit()

	# Starting web scraping
	emit("startcomplete",("Executing scraping"))      

	soup = BeautifulSoup(res.content, "html.parser")
	a_tag_list = soup.find_all("a")
	protocol = re.search(".*:", url).group(0)
	url_list = []
	### ループ内で毎回appendを呼び出していると、処理が遅くなるので
	### appendにあらかじめ、url_list.appendという関数を入れておく
	append=url_list.append
	
	for a in a_tag_list:
		a_link = str(a.get("href"))
		if not re.match(".*/.*", a_link):
			print("This hasn't been added to the list  " + a_link)
		elif a_link.startswith("//"):
			full_url = protocol + a_link
			append(full_url)
		elif a_link.startswith("/") or a_link.startswith("./"):
			#Removing "./" or "/" from a_link and conbining it with url
			full_url = url + re.sub(r".?/", "", a_link, count=1)
			append(full_url)
		#Checking if a_link starts with alphanumeric + "/"
		elif re.match(r"^\w+/", a_link):
			full_url = url + a_link
			append(full_url)
		else:    
			append(a_link)
		
	#appendを初期化
	append=list.append

	perfect_url_list =sorted(set([u for u in url_list if not re.match(".*article.*|.*=.*", u )]))
	tmp_list = []
	append=tmp_list.append

	for l in perfect_url_list:
		try:
			res = requests.get(l)
		except Exception as e:
			print(e)
			#print("before for loop of a")
		
		soup = BeautifulSoup(res.content, "html.parser")
		a_tag_list = soup.find_all("a")
		for a in a_tag_list:
			try:
				a_link = str(a.get("href"))
				a_text = re.sub("・|\u3000|\n|\r|\t", "", a.text)
				if re.match(".*{}.*".format(word), a.text) and not a_text in tmp_list:
					if not re.match(".*/.*", a_link):
						pass
					elif a_link.startswith("//"):
						article = protocol + a_link
					elif a_link.startswith("/") or a_link.startswith("./"):
						article = l + re.sub(r".?/", "", a_link, count=1)
						res = requests.get(article)
						if res.status_code != 200:
							article = url + re.sub(r".?/", "", a_link, count=1)
					elif re.match(r"^\w+/", a_link):
						article = l + a_link
						res = requests.get(article)
						if res.status_code != 200:
							article = url + a_link
					else:    
						article = a.get("href")
						
					append(a_text)
					a_dict_list = {
						"head": a_text,
						"url": article,
						#"sentense": get_p(article)
						}
					emit("myresponse", a_dict_list)
			except Exception as e:
				print(e)
				
		print("Nothing to be sent to you")
	
	emit("startcomplete", "DONE")
	print("DONE")
	elapsed = time.time() - start
	print(elapsed)	           
	append=list.append    


if __name__ == "__main__":
	#socketio = SocketIO(app) により、socketio.run(app)でflaskアプリを起動できる
	socketio.run(app)


# @app.route("/next", methods=["POST"])
# def arg_check():
#     if request.method == "POST":
#         url = request.form["url"]
#         keyword = request.form["search"]
#         args = url + keyword
#     return render_template("index.html", result=args)

# @app.route("/", methods=["POST"])
# def start_scraping():
#     if request.method == "POST":
#         url = request.form["url"]
#         word = request.form["search"]

#     return render_template("index.html", result=scraping(url,word))      

# @app.route("/", methods=["POST"])
# def start_socketio():
           
# def ack():
#     print("I got your message")

# @socketio.on("my event")
# def handle_message(json):
#     time.sleep(1)
#     emit("my response", json, callback=ack)
#     print("Replied to the clinet")
