from flask import Flask, render_template
from flask_pymongo import PyMongo
import datetime
from bson.objectid import ObjectId


app = Flask(__name__)

#Making a connection with MongoClient and getting database
app.config["MONGO_URI"] = "mongodb://localhost:27017/testdb"
mongo = PyMongo(app)

# These are same as above MONGO_URI configuration
# Defining the client
#   app.config['MONGO_HOST'] = '127.0.0.1'
# Setting the port number
#   app.config['MONGO_PORT'] = 27017
# Creating and defining database
#   app.config['MONGO_DBNAME'] = 'testdb'

#               THESE NORMAL PYMONGO SYNTAX
# client = MongoClient('mongodb://localhost:27017/')
# db = client.testdb
#                        IS SAME AS
# app.config["MONGO_URI"] = "mongodb://localhost:27017/testdb"
# mongo = PyMongo(app)

# よって、ただのpymongoの　"db."　は　flask_pymognoの　"mongo.db."と　同じ

@app.route("/")
def home_page():
  post = {"author": "Mike",
          "text": "My first blog post!",
          "tags": ["mongodb", "python", "pymongo"],
          "date": datetime.datetime.utcnow()}
  

  #Creating collection by mongo.db.[collection name] in the same way as pymongo: db.[collection name]
  posts = mongo.db.posts

  post_id = posts.insert_one(post).inserted_id
  print(posts.find_one())
  print(posts.find_one(post_id))
  print(ObjectId(post_id))
  post_id = str(post_id)
  print(posts.find_one({"_id": post_id}))
  
  # user = mongo.db.user.find({"name": "Tomohiro"})
  # print(user)
  return("Hello")

if __name__ == "__main__":
  app.run()