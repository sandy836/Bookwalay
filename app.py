from flask import Flask, render_template, request, json
import pyrebase
import os
import logging
import time

LOG_FORMAT = "%(asctime)s %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
app = Flask(__name__)

def generateUniqueOrderId():
    return int(round(time.time() * 1000))

def create_order_details(response):
    LOG.info("Creating Json Structure of the Order Details")
    order_url = os.path.join(SITE_ROOT, "static/requestSchema", "order.json")
    bookDetails_url = os.path.join(SITE_ROOT, "static/requestSchema", "bookDetails.json")
    order = json.load(open(order_url))
    book_detail_list = []
    LOG.info("Started parsing Json Data")
    for key, value in response.items():
        if key == 'submit':
            continue
        elif len(key.split('_')) == 2:
            _len = int(key.split('_')[1])
            if len(book_detail_list) == _len:
                book_detail_list.append([value])
            else:
                book_detail_list[_len].append(value)
        else:
            order[key] = value
    for bookDetails in book_detail_list:
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
    config_url = os.path.join(SITE_ROOT, "static/requestSchema", "config.json")
    firebaseConfig = json.load(open(config_url))
    LOG.info("Initialize Configuration")
    firebase = pyrebase.initialize_app(firebaseConfig)
    LOG.info("Initialize Database")
    db = firebase.database()
    order = create_order_details(request.form.to_dict(flat=True))
    LOG.info("Creating unique orderId")
    orderId = generateUniqueOrderId()
    order['orderId'] = orderId
    LOG.info("Push Data")
    db.child(orderId).set(order)
    return 'Successfully placed order'

if __name__ == '__main__':
   app.run(debug = True)