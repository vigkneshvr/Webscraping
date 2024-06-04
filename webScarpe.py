import requests
from bs4 import BeautifulSoup
import shutil
import os
import pandas as pd


os.makedirs("/images", exist_ok=True)

url = "https://books.toscrape.com/"

response = requests.get(url)

if response.status_code==200:
    print("Request succesful")
else:
    print("Request failed")

soup= BeautifulSoup(response.text, "html.parser") # Parse HTML
category_links = []
category_name= []
for link in soup.find_all("a", href=True):
    if link["href"].startswith("catalogue/category/"):
        category_links.append(link["href"])

for name in category_links:
    n= name.split("/")[3]
    n=n.split("_")[0]
    category_name.append(n)

category_name=category_name[1:]
category_links=category_links[1:]

books_data=[]

for catgeory_index,category_link in enumerate(category_links):
    page_index=1
    image_directory= f"images/{category_name[catgeory_index]}"
    os.makedirs(image_directory, exist_ok=True)
    book_number=1
    while(True):
        if page_index>1:
            modified_link= category_link.split("/")
            modified_link[-1]= f"page-{page_index}.html"
            modified_link=  "/".join(modified_link)
            link= url+modified_link
        else:
            link= url+category_link

        book_response= requests.get(link)
        book_response_status= book_response.status_code
        if(book_response_status!=200):
            break
        
        book_soup= BeautifulSoup(book_response.text, "html.parser")
        books = book_soup.find_all("article", class_="product_pod")
        book_images= book_soup.findAll('img')
        for image in book_images:
            i= image["src"].replace("../../../../","")
            image_link= url+i
            r = requests.get(image_link, stream=True)
            if r.status_code == 200:                     #200 status code = OK
                with open(f"images/{category_name[catgeory_index]}/book_{book_number}.jpg", 'wb') as f: 
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    book_number+=1

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").get_text().strip()
            rating = book.p["class"][1]
            stock = book.find("p", class_="instock availability").get_text().strip()
            category= category_link.split("/")[3].split("_")[0]

            books_data.append([title, price, rating, category, stock])
  
        page_index+=1

df= pd.DataFrame(books_data, columns=["title", "price", "rating", "category", "stock"])
df.to_csv("scraped_books.csv")