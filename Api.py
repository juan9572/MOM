import http.server
import socketserver
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from users import UserHandler
from topics import TopicHandler
from queues import QueueHandler
import logging

class APIHandler(http.server.BaseHTTPRequestHandler):

    user_handler = None
    topic_handler = None
    queue_handler = None

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        if path == '/getQueue':
            user = query.get('username', [None])[0]
            self.getUserQueues(user)
        elif path == '/getAllQueues':
            self.getUserQueues(user)
        elif path == '/getTopic':
            user = query.get('username', [None])[0]
            self.handle_bye()
        elif path == '/getAllTopics':
            self.handle_bye()
        else:
            self.notFoundError(path + " in GET method")

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        if path == '/registerUser':
            self.registerUser(query)
        elif path == '/loginUser':
            self.loginUser(query)
        elif path == '/logoutUser':
            self.logoutUser()
        elif path == '/createQueue':
            self.createQueue(query)
        elif path == '/createTopic':
            self.createTopic(query)
        elif path == '/subscribeToTopic':
            self.subscribeToTopic(query)
        elif path == '/vinculateQueue':
            self.vinculateQueue(query)
        elif path == '/publishMessage':
            self.publishMessage(query)
        elif path == '/sendMessage':
            self.sendMessage(query)
        else:
            self.notFoundError(path + " in POST method")

    def sendMessage(self, query):
        username = query.get('username', [None])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        queue_handler.createTopic(username)
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())

    def vinculateQueue(self, query):
        username = query.get('username', [None])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        queue_handler.vinculateQueue(username)
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())

    def publishMessage(self, query):
        username = query.get('username', [None])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        topic_handler.subscribeToTopic(username)
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())

    def subscribeToTopic(self, query):
        username = query.get('username', [None])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        topic_handler.subscribeToTopic(username)
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())

    def createTopic(self, query):
        name = query.get('nameTopic', [None])[0]
        res = topic_handler.createTopic(name, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def createQueue(self, query):
        name = query.get('nameQueue', [None])[0]
        res = queue_handler.createQueue(name, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def registerUser(self, query):
        username = query.get('username', [None])[0]
        password = query.get('password', [None])[0]
        res = user_handler.registerUser(username, password, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def loginUser(self, query):
        username = query.get('username', [None])[0]
        password = query.get('password', [None])[0]
        res = user_handler.loginUser(username, password, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def logoutUser(self):
        res = user_handler.logoutUser(self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        if path == '/deleteUser':
            pass
        elif path == '/deleteQueue':
            pass
        elif path == '/deleteTopic':
            pass
        else:
            self.notFoundError(path + " in DELETE method")

    def notFoundError(self, path):
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            message = "Not found " + path
            self.wfile.write(message.encode())

    def getUserQueues(self, username):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())

    def getTopic(self, username):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = f"Hello, World! {username}"
        self.wfile.write(message.encode())


if __name__ == '__main__':
    logging.basicConfig(filename='operations.log', level=logging.INFO)
    load_dotenv()
    client = MongoClient("mongodb://" + os.getenv("IPMONGO") + ":" + os.getenv("PORTMONGO"))
    user_handler = UserHandler(client)
    topic_handler = TopicHandler(client)
    queue_handler = QueueHandler(client)
    port = int(os.getenv("PORTHTTP"))
    logging.info("Starting server in port: " + str(port))
    try:
        with socketserver.TCPServer(("", port), APIHandler) as httpd:
            print("Serving at port", port)
            httpd.serve_forever()
    finally:
        logging.info("Finishing server...")

'''
    Usuario:{
        name:String,
        password:String,
        active: False,
        colas: [{
            nombre_cola: String,
            id_exchange: id,
            mensaje:["Hola"]
        }],
        Topico:[{
            nombre_topico:String,
            id_topico: id_exchange,
            subscriber : [Usuarios:String]
        }]
    }
'''

