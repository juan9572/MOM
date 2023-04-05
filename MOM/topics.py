import os
import encriptacion

class TopicHandler():

    client = None
    database = None
    collection = None

    def __init__(self, client):
        self.client = client
        self.database = client["MOM"]
        self.collection = self.database["Users"]

    def createTopic(self, name_topic, ip):
        response = {}
        if name_topic and name_topic != "":
            existing_user = self.collection.find_one({'currentIp': ip})
            allUsers = self.collection.find()
            unique_topic = True
            for user in allUsers:
                for topic in user["topics"]:
                    if topic["nameTopic"] == name_topic:
                        unique_topic = False
                        break
            if existing_user and existing_user["active"] == True and unique_topic:
                updateUser = self.collection.update_one(
                    {'currentIp': ip},
                    {'$push': {
                        'topics':{
                            'nameTopic': name_topic,
                            'subscribers': []
                        }
                    }}
                )
                if updateUser.acknowledged and updateUser.modified_count > 0:
                    response["message"] = "Se creo correctamente el TOPICO " + name_topic
                    response["status"] = 200
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                if not unique_topic:
                    response["message"] = "Ya existe un topico con el nombre " + name_topic
                    response["status"] = 403
                else:
                    response["message"] = "No estas autorizado a hacer esto"
                    response["status"] = 401
        else:
            response["message"] = "Se necesita el nombre del topico"
            response["status"] = 400
        return response

    def subscribeToTopic(self, name_topic, name_queue, ip):
        response = {}
        if name_topic and name_topic != "" and name_queue and name_queue != "":
            existing_topic = self.collection.find_one({'topics.nameTopic': name_topic})
            existing_queue = self.collection.find_one({'$and':[
                {'queues.nameQueue': name_queue},
                {'currentIp': ip}
            ]})
            alreadySubscribe = False
            for queue in existing_queue["queues"]:
                if queue["associated"] == name_topic:
                    alreadySubscribe = True if queue["associated"] != "" else False
                    break
            if existing_topic and not alreadySubscribe and existing_queue and existing_queue["active"] == True:
                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            updateTopic = self.collection.update_one(
                                {'topics.nameTopic': name_topic},
                                {'$push': {
                                    'topics.$.subscribers': {'username': existing_queue["username"]}
                                }},
                            )
                            updateQueue = self.collection.update_one(
                                {'queues.nameQueue': name_queue},
                                {'$set': {
                                    'queues.$.associated': name_topic,
                                    'queues.$.type': 'topic',
                                }},
                            )
                    if updateQueue.acknowledged and updateQueue.modified_count > 0 and updateTopic.acknowledged and updateTopic.modified_count > 0:
                        response["message"] = "Te has suscrito correctamente al topico " + name_topic
                        response["status"] = 200
                    else:
                        response["message"] = "Hubo un error al comunicarse con la DB"
                        response["status"] = 500
                except Exception as e:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                if alreadySubscribe:
                    response["message"] = "La cola " + name_queue + " ya esta asociada a un topico"
                    response["status"] = 500
                elif not existing_topic:
                    response["message"] = "El topico " + name_topic + " no existe"
                    response["status"] = 400
                else:
                    if not existing_queue:
                        response["message"] = "La cola " + name_queue + " no existe"
                        response["status"] = 400
                    else:
                        response["message"] = "No estas autorizado a hacer esto"
                        response["status"] = 401
        else:
            if name_queue and name_queue != "":
                response["message"] = "Se necesita el nombre del topico"
                response["status"] = 400
            else:
                response["message"] = "Se necesita el nombre de la cola"
                response["status"] = 400
        return response

    def publishMessage(self, name_topic, message, ip):
        response = {}
        if name_topic and name_topic != "" and message and message != "":
            existing_topic = self.collection.find_one({'$and':[
                {'topics.nameTopic': name_topic},
                {'currentIp': ip}
            ]})
            if existing_topic and existing_topic["active"] == True:
                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            encrypt_message = encriptacion.encrypt(message, os.getenv("PASSWORD"))
                            updateSubscribers = self.collection.update_many(
                                {'$and':[
                                    {'queues.associated': name_topic},
                                    {'queues.type': 'topic'}
                                ]},
                                {'$push': {
                                    'queues.$.messages': encrypt_message
                                }}
                            )
                        if updateSubscribers.acknowledged and updateSubscribers.modified_count > 0:
                            response["message"] = "Se ha publicado el mensaje correctamente"
                            response["status"] = 200
                        else:
                            response["message"] = "Hubo un error al comunicarse con la DB"
                            response["status"] = 500
                except Exception as e:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                if not existing_topic:
                    response["message"] = "El topico " + name_topic + " no existe"
                    response["status"] = 400
                else:
                    response["message"] = "No estas autorizado a hacer esto"
                    response["status"] = 401
        else:
            if name_topic and name_topic != "":
                response["message"] = "Se necesita enviar un mensaje valido"
                response["status"] = 400
            else:
                response["message"] = "Se necesita el nombre del topico a donde se va a publicar"
                response["status"] = 400
        return response

    def getTopics(self, ip):
        response = {}
        existing_user = self.collection.find_one({'currentIp': ip})
        if existing_user and existing_user["active"] == True:
            message = ""
            index = 1
            for topic in existing_user["topics"]:
                message += (
                    "Topic #" + str(index) + "\n" +
                    "nameTopic: " + topic["nameTopic"] + "\n" +
                    "subscribers: [" + "\n"
                    )
                for s in topic["subscribers"]:
                    message += "username: " + s["username"] + " ,\n"
                message += "\n]\n"
                index += 1
            response["message"] = message
            response["status"] = 200
        else:
            response["message"] = "No estas autorizado a hacer esto"
            response["status"] = 401
        return response

    def deleteTopic(self, name_topic, ip):
        response = {}
        if name_topic and name_topic != "":
            existing_user = self.collection.find_one({'$and':[
                {'currentIp': ip},
                {'topics.nameTopic': name_topic}
            ]})
            if existing_user and existing_user["active"] == True:
                result = self.collection.update_one(
                    {'currentIp': ip},
                    {'$pull': {'topics': {'nameTopic': name_topic}}}
                )
                if result.acknowledged and result.modified_count > 0:
                    response["message"] = "Se elimino correctamente el topico " + name_topic
                    response["status"] = 200
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB"
                    response["status"] = 500
            else:
                response["message"] = "No estas autorizado a hacer esto"
                response["status"] = 401
        else:
            response["message"] = "Se necesita el nombre del topico"
            response["status"] = 401
        return response
