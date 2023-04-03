

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
                if updateUser.acknowledged and updateUser.modified_count > 0:
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

    def vinculateQueue(self, name_exchange, name_queue, ip):
        response = {}
        if name_exchange and name_exchange != "" and name_queue and name_queue != "":
            existing_queue = self.collection.find_one({'$and':[
                {'currentIp': ip},
                {'queues.nameQueue': name_queue}
            ]})
            alreadyRegister = False
            for queue in existing_queue["queues"]:
                if queue["associated"] == name_exchange and queue["type"] == "direct":
                    alreadyRegister = True
                    break
            if existing_queue and existing_queue["active"] == True and not alreadyRegister:
                updateUser = self.collection.update_one(
                    {'$and':[
                        {'currentIp': ip},
                        {'queues.nameQueue': name_queue}
                    ]},
                    {'$set': {
                        'queues.$.associated': name_exchange,
                        'queues.$.type': 'direct',
                    }}
                )
                if updateUser.acknowledged and updateUser.modified_count > 0:
                    response["message"] = "Se vinculo correctamente el EXCAHNGE " + name_exchange + " a la cola " + name_queue
                    response["status"] = 200
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                if alreadyRegister:
                    response["message"] = "La cola " + name_queue + " ya esta asociada al exchange " + name_exchange
                    response["status"] = 500
                elif not existing_queue:
                    response["message"] = "La cola " + name_queue + " no existe"
                    response["status"] = 400
                else:
                    response["message"] = "No estas autorizado a hacer esto"
                    response["status"] = 401
        else:
            if name_queue and name_queue != "":
                response["message"] = "Se necesita el nombre del exchange"
                response["status"] = 400
            else:
                response["message"] = "Se necesita el nombre de la cola"
                response["status"] = 400
        return response

    def sendMessage(self, name_exchange, message, ip):
        response = {}
        if name_exchange and name_exchange != "" and message and message != "":
            existing_user = self.collection.find_one({'currentIp': ip})
            if existing_user and existing_user["active"] == True:
                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            updateQueues = self.collection.update_many(
                                {'$and':[
                                    {'queues.associated': name_exchange},
                                    {'queues.type': 'direct'}
                                ]},
                                {'$push': {
                                    'queues.$.messages': message
                                }}
                            )
                            if updateQueues.acknowledged and updateQueues.modified_count > 0:
                                response["message"] = "Se ha mandado el mensaje correctamente"
                                response["status"] = 200
                            else:
                                response["message"] = "Hubo un error al comunicarse con la DB"
                                response["status"] = 500
                except Exception as e:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                response["message"] = "No estas autorizado a hacer esto"
                response["status"] = 401
        else:
            if name_exchange and name_exchange != "":
                response["message"] = "Se necesita enviar un mensaje valido"
                response["status"] = 400
            else:
                response["message"] = "Se necesita el nombre del exhange para poder mandar el mensaje"
                response["status"] = 400
        return response
