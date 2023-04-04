import os
import pymongo
import encriptacion
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
            alreadyInUse = False
            for queue in existing_queue["queues"]:
                if queue["nameQueue"] == name_queue:
                   alreadyInUse = True if queue["associated"] != "" else False
                   break
            if existing_queue and existing_queue["active"] == True and not alreadyInUse:
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
                if alreadyInUse:
                    response["message"] = "La cola " + name_queue + " ya esta asociada a un exchange"
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
                            encrypt_message = encriptacion.encrypt(message, os.getenv("PASSWORD"))
                            updateQueues = self.collection.update_many(
                                {'$and':[
                                    {'queues.associated': name_exchange},
                                    {'queues.type': 'direct'}
                                ]},
                                {'$push': {
                                    'queues.$.messages': encrypt_message
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

    def getQueues(self, ip):
        response = {}
        existing_user = self.collection.find_one({'currentIp': ip})
        if existing_user and existing_user["active"] == True:
            message = ""
            index = 1
            for queue in existing_user["queues"]:
                message += (
                    "Queue #" + str(index) + "\n" +
                    "nameQueue: " + queue["nameQueue"] + "\n" +
                    "associated: " + queue["associated"] + "\n" +
                    "type: " + queue["type"] + "\n" +
                    "messages: [" + "\n"
                    )
                for q in queue["messages"]:
                    message += q + " ,\n"
                message += "\n]\n"
                index += 1
            response["message"] = message
            response["status"] = 200
        else:
            response["message"] = "No estas autorizado a hacer esto"
            response["status"] = 401
        return response

    def consumeMessage(self, name_queue, ip):
        response = {}
        if name_queue and name_queue != "":
            existing_user = self.collection.find_one({'$and':[
                {'currentIp': ip},
                {'queues.nameQueue': name_queue}
            ]})
            if existing_user and existing_user["active"] == True:
                result = self.collection.find_one_and_update(
                    {'$and':[
                        {'currentIp': ip},
                        {'queues.nameQueue': name_queue}
                    ]},
                    {'$pop':{'queues.$.messages': -1}},
                    return_document=pymongo.ReturnDocument.BEFORE
                )
                if result is not None:
                    mensaje = next(filter(lambda x: x['nameQueue'] == name_queue, result["queues"]), None)
                    if len(mensaje["messages"]) > 0:
                        decrypt_message = encriptacion.decrypt(mensaje["messages"][0], os.getenv("PASSWORD"))
                        response["message"] = decrypt_message
                        response["status"] = 200
                    else:
                        response["message"] = "No hay más mensajes en la cola " + name_queue
                        response["status"] = 200
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                response["message"] = "No estas autorizado a hacer esto"
                response["status"] = 401
        else:
            response["message"] = "Se necesita el nombre de la cola"
            response["status"] = 401
        return response

    def deleteQueue(self, name_queue, ip):
        response = {}
        if name_queue and name_queue != "":
            existing_user = self.collection.find_one({'$and':[
                {'currentIp': ip},
                {'queues.nameQueue': name_queue}
            ]})
            if existing_user and existing_user["active"] == True:
                name_topic = ""
                is_topic = False
                for queue in existing_user["queues"]:
                    if queue["nameQueue"] == name_queue:
                        name_topic = queue["associated"]
                        is_topic = True if queue["type"] == "topic" else False
                        break
                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            result = self.collection.update_one(
                                {'currentIp': ip},
                                {'$pull': {'queues': {'nameQueue': name_queue}}}
                            )
                            if is_topic:
                                updateTopic = self.collection.update_one(
                                    {'topics.nameTopic': name_topic},
                                    {'$pull': {'topics.$.subscribers': {'username': existing_user["username"]}}}
                                )
                                if result.acknowledged and result.modified_count > 0 and updateTopic.acknowledged and updateTopic.modified_count > 0:
                                    response["message"] = "Se elimino correctamente la cola " + name_queue
                                    response["status"] = 200
                                else:
                                    response["message"] = "Hubo un error al comunicarse con la DB"
                                    response["status"] = 500
                            else:
                                if result.acknowledged and result.modified_count > 0:
                                    response["message"] = "Se elimino correctamente la cola " + name_queue
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
            response["message"] = "Se necesita el nombre de la cola"
            response["status"] = 401
        return response
