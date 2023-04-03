

class QueueHandler():

    client = None
    database = None
    collection = None

    def __init__(self, client):
        self.client = client
        self.database = client["MOM"]
        self.collection = self.database["Users"]

    def createQueue(self, name_queue, ip):
        response = {}
        if name_queue and name_queue != "":
            existing_user = self.collection.find_one({'currentIp': ip})
            unique_queue = True
            for queue in existing_user["queues"]:
                if queue["nameQueue"] == name_queue:
                    unique_queue = False
                    break
            if existing_user and existing_user["active"] == True and unique_queue:
                updateUser = self.collection.update_one(
                    {'currentIp': ip},
                    {'$push': {
                        'queues':{
                            'nameQueue': name_queue,
                            'type': '',
                            'associated': '',
                            'messages': []
                        }
                    }}
                )
                if updateUser.acknowledged:
                    response["message"] = "Se creo correctamente la QUEUE " + name_queue
                    response["status"] = 200
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                if not unique_queue:
                    response["message"] = "Ya existe una cola con el nombre " + name_queue
                    response["status"] = 400
                else:
                    response["message"] = "No estas autorizado a hacer esto"
                    response["status"] = 401
        else:
            response["message"] = "Se necesita el nombre de la cola"
            response["status"] = 400
        return response

    def vinculateQueue(self):
        pass
    def getUserQueue(username):
        pass