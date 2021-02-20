from _typeshed import SupportsKeysAndGetItem
from flask import Flask, render_template, request, json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore 
import os
import logging
import time

LOG_FORMAT = "%(asctime)s %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

config_url = os.path.join(SITE_ROOT, "static/requestSchema", "config.json")
firebaseConfig = json.load(open(config_url))
LOG.info("Initialize Configuration")
cred = credentials.Certificate(firebaseConfig)
firebase_admin.initialize_app(cred)
LOG.info("Initailized DB client")
db = firestore.client()

app = Flask(__name__)

def generateUniqueOrderId():
    return str(round(time.time() * 1000))

def create_order_details(response):
    LOG.info("Creating Json Structure of the Order Details")
    order_url = os.path.join(SITE_ROOT, "static/requestSchema", "order.json")
    bookDetails_url = os.path.join(SITE_ROOT, "static/requestSchema", "bookDetails.json")
    order = json.load(open(order_url))
    book_detail_dict = {}
    LOG.info("Started parsing Json Data")
    for key, value in response.items():
        if key == 'submit':
            continue
        elif len(key.split('_')) == 2:
            book_detail_key = int(key.split('_')[1])
            if book_detail_key not in book_detail_dict:
                book_detail_dict[book_detail_key] = ['', '']
            if 'bookName' in key:
                book_detail_dict[book_detail_key][0] = value
            else:
                book_detail_dict[book_detail_key][1] = value
        else:
            order[key] = value
    for _, bookDetails in book_detail_dict.items():
        bookDetailsStruc = json.load(open(bookDetails_url))
        bookDetailsStruc['bookName'] = bookDetails[0]
        bookDetailsStruc['publisherName'] = bookDetails[1]
        order['orderList'].append(bookDetailsStruc)
    return order
         
@app.route('/', methods = ['GET'])
def place_order():
    return render_template('index.html')

@app.route('/success', methods = ['POST'])
def save_order():
    order = create_order_details(request.form.to_dict(flat=True))
    LOG.info("Creating unique orderId")
    orderId = generateUniqueOrderId()
    order['orderId'] = orderId
    LOG.info("Push Data")
    res = db.collection('Order').document(orderId).set(order)
    LOG.info("Information pushed to Db")
    LOG.info(res)
    return render_template('success.html', orderId = orderId)

if __name__ == '__main__':
   app.run(debug = True)    