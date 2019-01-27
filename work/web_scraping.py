"""
ToDoList
    Deleting extra initial urls.
    Expediting proccess speed.
    Creating other methods,
        being able to get to find specific date's artcile.
        getting sentences and images of articles from <p> tag
    Storing data
    Differentiating headlines having the keyword as my purpose and one containing the keyword in the other word
"""
from bs4 import BeautifulSoup
import requests
import re
import sys
import json
import time

def get_a_tags(url):
    """
    Getting the news site's url
    """
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        print("Protocol error")
        sys.exit()

    # status = res.status_code

    # while status != 200:
    #     res = requests.get(url)
    #     status = res.status_code
    #     print("requesting")
    #     time.sleep(1)
    """
    Getting initial links' urls
    """
    # To avoid garbled Japanese, passing "res.content" to bs
    soup = BeautifulSoup(res.content, "html.parser")
    # Finding all of <a> tags
    a_tag_list = soup.find_all("a")
    # Defining whether http or https
    protocol = re.search(".*:", url).group(0)

    return({"a_tag_list": a_tag_list, "protocol": protocol})

def get_p(url):
	#start = time.time()
	res = requests.get(url)
	soup = BeautifulSoup(res.content, "html.parser")
	p_tags = soup.find_all("p")
	#end = time.time()
	p_tags_texts = [ p.text for p in p_tags ]
	only_text = "".join(p_tags_texts)
	return(only_text)
	#print(p_tags_texts)

def scraping(args):
    """
    Checking on whether the arguments are right
    """
    try:
        url = args[0]
        word = args[1]
        if not url.endswith("/"):
            url = url + "/"
    except IndexError:
        print("Error: 引数に　”URL”　と　”キーワード”　を指定してください")
        sys.exit()
    
    print(url)
    
    returns = get_a_tags(url)
    a_tag_list = returns["a_tag_list"]
    protocol = returns["protocol"]
    url_list = []

    for a in a_tag_list:
        a_link = str(a.get("href"))
        # If <a> tag's link url doesn't make sense, do nothing
        if not re.match(".*/.*", a_link):
            print("This hasn't been added to the list  " + a_link)
        # If the url starts with "//", add it after protocol which you've got in advance
        elif a_link.startswith("//"):
            full_url = protocol + a.get("href")
            url_list.append(full_url)
        # If the url starts with "/", delete first "/" and add it after url which you've got in advance
        #elif a_link.startswith("/"):
            # Replacing first "/" from the link and adding it to initial url
            # full_url = url + a_link.replace("/", "", 1)
            # url_list.append(full_url)
        elif a_link.startswith("/") or a_link.startswith("./"):
            full_url = url + re.sub(r".?/", "", a_link, count=1)
            url_list.append(full_url)
            print(full_url)
        elif re.match(r"^\w+/", a_link):
            full_url = url + a_link
            url_list.append(full_url)
            print(full_url)
        else:    
            url_list.append(a.get("href"))
    link_list = []

    #link_list = [u for u in url_list if not u.endswith("html") and not re.match(".*article.*", u)]
    for u in url_list:
        # If the formed url contains "artcile" or "=", do nothing
        if re.match(".*article.*|.*=.*", u):
            print("This hasn't been added to the list " + u)
        #if not u.endswith("html") and not re.match(".*article.*", u):
            #link_list.append(u)
        else:
            link_list.append(u)
    
    link_list = sorted(set(link_list))
    
    #To delete duplicated domain url, after getting link_list
    #you need to compare greater index fator to lower index one.
    #Then if greater one has lower one's domain, delete it

    print("\n\n\nSearching for \"{}\" \n\n\n".format(word))
    
    """
    From initial urls, Getting urls having the contents of keyword
    """
    
    duplicate_a_dict_list = []
    
    # What this for loop is doing is basically same as former for loop
    # From the url list, you pick up one by one
    # From those each url, you are finding other links where you will search for the keyword
    for l in link_list:
        returns = get_a_tags(l)
        a_tag_list = returns["a_tag_list"]
        protocol = returns["protocol"]
        # REPLACE "if re.match(".*{}.*".format(word), a.text"  to  "if word in a.text"
        # duplicate_a_dict_list = [{"head": re.sub("・|\u3000|\n", "", a.text), "url": a.get("href")} 
        #                         for a in a_tag_list if re.match(".*{}.*".format(word), a.text)]
        for a in a_tag_list:
            a_link = str(a.get("href"))
            if re.match(".*{}.*".format(word), a.text):
                if not re.match(".*/.*", a_link):
                    print("This was passed  " + a_link)
                elif a_link.startswith("//"):
                    print("This url starts with // " + a_link)
                    article = protocol + a_link
                    print("This url has been formed as " + article)
                elif a_link.startswith("/") or a_link.startswith("./"):
                    print("This url starts with / or ./ " + a_link)
                    article = l + re.sub(r".?/", "", a_link, count=1)
                    res = requests.get(article)
                    if res.status_code != 200:
                        print("\n")
                        print(res.status_code)
                        article = url + re.sub(r".?/", "", a_link, count=1)
                        print("The status code wasn't 200, so formed the url as " + article)
                elif re.match(r"^\w+/", a_link):
                    print("This url starts with alphanumeric")
                    article = l + a_link
                    res = requests.get(article)
                    if res.status_code != 200:
                        print(res.status_code)
                        article = url + a_link
                        print("The status code wasn't 200, so formed the url as " + article)
                else:    
                    article = a.get("href")
                    print(article)
                # Creating a list having multiple duplicated dictionaries
                # Deleting full-width blank and dot. 
                duplicate_a_dict_list.append({
                    "head": re.sub("・|\u3000|\n|\r|\t", "", a.text),
                    "url": article,
                    #"sentense": get_p(article)
                    })
        print("I have got through " + l)

    # Sorting a list habing mutiple duplicated dictionaries based on items
    sorted_a_dict_list = [dict(t) for t in sorted([tuple(d.items()) for d in duplicate_a_dict_list])]
    length_sadl = len(sorted_a_dict_list)
    delete_index = []

    for x in range(length_sadl):
        try:
            # If the small index head is same as big one, keep the index number
            if sorted_a_dict_list[x]["head"] in sorted_a_dict_list[x + 1]["head"]:
                delete_index.append(x)
        except Exception as e:
            print(e)
    print("\n\n\nDone")
    # Reversing the index number
    reversed_delete_index = sorted(delete_index, reverse=True)
    
    # Deleting those indexes' head and url
    for x in reversed_delete_index:
        sorted_a_dict_list.pop(x)

    for x in sorted_a_dict_list:
        print(x)

    #return(sorted_a_dict_list)

##Executing scraping function if this python file is called in Command Line
if __name__=="__main__":
	scraping(sys.argv[1:])
