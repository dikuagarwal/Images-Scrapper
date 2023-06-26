from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os
import time

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")


@app.route("/review", methods = ["POST","GET"])
def result():
    if request.method=="POST":
        try:
            query = request.form["content"].replace(" ","")

            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            url = f"https://www.google.com/search?sxsrf=APwXEdeMxFD5t2t51EC_z0lJ141eF1ZHgw:1687783876321&q={query}&tbm=isch&sa=X&ved=2ahUKEwjP9Z7z_OD_AhX6glYBHXKKBlsQ0pQJegQIChAB&biw=1536&bih=746&dpr=1.25"

            soup = BeautifulSoup((requests.get(url)).content,"html.parser")
            time.sleep(5)
            img_tag = soup.find_all("img")

            img_data = []
            for index,i in enumerate(img_tag):
                try:
                    # get the images url
                    img_url = i['src']
                    images = requests.get(img_url).content

                    with open(os.path.join(save_dir,f"{query}_{index}.jpg"),'wb')as f:
                        f.write(images)

                    mdic = {"index":index,"image":images}
                    img_data.append(mdic)

                except Exception as e:
                    logging.info(e)
                
                    
            # store images at MongoDB database
            client = pymongo.MongoClient("mongodb+srv://dikujalan:virat100@cluster0.hzgttjg.mongodb.net/")
            db = client['Scrapped_Images']
            review_col = db[f'image_of_{query}']
            review_col.insert_many(img_data) 
        
            return "image loaded"  

            
        except Exception as e:
                    logging.INFO(e)

                    return "fail"



if __name__ == "__main__":
    app.run(host='0.0.0.0')