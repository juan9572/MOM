import os
import bson
import grpc
import logging
import http.server
import socketserver
import tempfile
from users import UserHandler
from dotenv import load_dotenv
from concurrent import futures
from topics import TopicHandler
from queues import QueueHandler
from pymongo import MongoClient
import communicationProcess_pb2
import communicationProcess_pb2_grpc
from urllib.parse import urlparse, parse_qs
from serviceDefinition import ReplicationServiceServicer

servers_mom = None

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
        if path == '/getQueues':
            self.getQueues()
        elif path == '/getTopics':
            self.getTopics()
        elif path == '/consumeMessage':
            self.consumeMessage(query)
        else:
            self.notFoundError(path + " in GET method")

    def consumeMessage(self, query):
        nameQueue = query.get('nameQueue', [None])[0]
        res = queue_handler.consumeMessage(nameQueue, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def getTopics(self):
        res = topic_handler.getTopics(self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def getQueues(self):
        res = queue_handler.getQueues(self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        recognize = True
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
            recognize = False
            self.notFoundError(path + " in POST method")
        if recognize:
            dump(user_handler.collection)

    def sendMessage(self, query):
        nameE = query.get('nameExchange', [None])[0]
        message = query.get('message', [None])[0]
        res = queue_handler.sendMessage(nameE, message, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def publishMessage(self, query):
        nameT = query.get('nameTopic', [None])[0]
        message = query.get('message', [None])[0]
        res = topic_handler.publishMessage(nameT, message, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def vinculateQueue(self, query):
        nameE = query.get('nameExchange', [None])[0]
        nameQ = query.get('nameQueue', [None])[0]
        res = queue_handler.vinculateQueue(nameE, nameQ, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def subscribeToTopic(self, query):
        nameT = query.get('nameTopic', [None])[0]
        nameQ = query.get('nameQueue', [None])[0]
        res = topic_handler.subscribeToTopic(nameT, nameQ, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
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
        recognize = True
        if path == '/deleteQueue':
            self.deleteQueue(query)
        elif path == '/deleteTopic':
            self.deleteTopic(query)
        else:
            self.notFoundError(path + " in DELETE method")
            recognize = False
        if recognize:
            dump(user_handler.collection)

    def deleteTopic(self, query):
        name = query.get('nameTopic', [None])[0]
        res = topic_handler.deleteTopic(name, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def deleteQueue(self, query):
        name = query.get('nameQueue', [None])[0]
        res = queue_handler.deleteQueue(name, self.client_address[0])
        self.send_response(res["status"])
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = res["message"]
        logging.info(res["message"])
        self.wfile.write(message.encode())

    def notFoundError(self, path):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = "Not found " + path
        self.wfile.write(message.encode())

def dump(collection):
    logging.info("Init dump...")
    server = 0
    i = 0
    while True:
        ip = servers_mom[server]["ip"]
        port = servers_mom[server]["port"]
        current_server = f"{ip}:{port}"
        logging.info(f"Trying to send data to {current_server}... Try #{i + 1}")
        status = False
        try:
            with grpc.intercept_channel(current_server) as channel:
                stub = communicationProcess_pb2_grpc.ReplicationServiceStub(channel)
                request = communicationProcess_pb2.Replica()
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    bson_data = bson.dumps(list(collection.find()))
                    tmp_file.write(bson_data)
                    tmp_file_path = tmp_file.name
                    with open(tmp_file_path, "rb") as bson_file:
                        request.data = bson_file.read()
                    os.unlink(tmp_file_path)
                response = stub.SendReplication(request)
                if not response.messageOfConfirmation.startswith("Error"):
                    status = True
        except Exception as e:
            status = False
        if not status:
            if i == 1:
                server += 1
                i = -1
        else:
            server += 1
        if server == len(servers_mom):
            break
        i += 1
    logging.info("Finish dump...")

def restore(collection):
    logging.info("Init restore...")
    server = 0
    i = 0
    while True:
        ip = servers_mom[server]["ip"]
        port = servers_mom[server]["port"]
        current_server = f"{ip}:{port}"
        logging.info(f"Trying to fetch data from {current_server}... Try #{i + 1}")
        status = False
        try:
            with grpc.insecure_channel(current_server) as channel:
                print("viendo si funciona esto")
                stub = communicationProcess_pb2_grpc.ReplicationServiceStub(channel)
                print("Cree el stub")
                request = communicationProcess_pb2.confirmationMessage()
                print("Cree el request")
                response = stub.getReplication(request)
                print(response)
                if response.data:
                    print("si me llego el dato")
                    collection.drop()
                    operation = collection.insert_many(bson.loads(response.data))
                    if operation.acknowledged:
                        status = True
        except Exception as e:
            print(f"Error connecting to {current_server}: {e}")
            status = False
        if status:
            break
        if i == 2:
            server += 1
            i = -1
        if server == len(servers_mom):
            break
        i += 1
    logging.info("Finish restore...")

if __name__ == '__main__':
    logging.basicConfig(filename='operations.log', level=logging.INFO)
    load_dotenv()
    servers_mom = [
        {
            'ip':os.getenv("SERVERIP1"),
            'port':os.getenv("PORTSERVER1")
        },
        {
            'ip':os.getenv("SERVERIP2"),
            'port':os.getenv("PORTSERVER2")
        }
    ]
    logging.info("Starting MongoDB...")
    client = MongoClient("mongodb://" + os.getenv("IPMONGO") + ":" + os.getenv("PORTMONGO"))
    logging.info("MongoDB ready")
    user_handler = UserHandler(client)
    topic_handler = TopicHandler(client)
    queue_handler = QueueHandler(client)
    portHttp = int(os.getenv("PORTHTTP"))
    portGrpc = os.getenv("PORTGRPC")
    logging.info("Starting server API in port: " + str(portHttp))
    logging.info("Starting server for MOM's in port: " + portGrpc)
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
        communicationProcess_pb2_grpc.add_ReplicationServiceServicer_to_server(ReplicationServiceServicer(client["MOM"]["Users"]), server)
        server.add_insecure_port("[::]:" + portGrpc)
        server.start()
        with socketserver.TCPServer(("", portHttp), APIHandler) as httpd:
            print("Listening at port", portHttp)
            logging.info("Listening at port " + str(portHttp))
            restore(client["MOM"]["Users"])
            httpd.serve_forever()
        server.wait_for_termination()
    finally:
        logging.info("Finishing server...")
