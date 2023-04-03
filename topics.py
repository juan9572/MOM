

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
                if updateUser.acknowledged:
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
            existing_queue = self.collection.find_one({'queues.nameQueue': name_queue})
            existing_user = self.collection.find_one({'currentIp': ip})
            alreadySubscribe = False
            for queue in existing_user["queues"]:
                if queue["associated"] == name_topic and queue["type"] == "topic":
                    alreadySubscribe = True
                    break
            if existing_topic and not alreadySubscribe and existing_queue and existing_user and existing_user["active"] == True:
                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            updateTopic = self.collection.update_one(
                                {'topics.nameTopic': name_topic},
                                {'$push': {
                                    'topics.$.subscribers': existing_user["username"]
                                }},
                            )
                            updateQueue = self.collection.update_one(
                                {'queues.nameQueue': name_queue},
                                {'$set': {
                                    'queues.$.associated': name_topic,
                                    'queues.$.type': 'topic',
                                }},
                            )
                    if updateQueue.acknowledged and updateTopic.acknowledged:
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
                    response["message"] = "Ya estas suscrito al topico " + name_topic
                    response["status"] = 500
                elif not existing_user:
                    response["message"] = "No estas autorizado a hacer esto"
                    response["status"] = 401
                else:
                    if not existing_topic:
                        response["message"] = "El topico " + name_topic + " no existe"
                        response["status"] = 400
                    else:
                        response["message"] = "La cola " + name_queue + " no existe"
                        response["status"] = 400

        else:
            if name_queue and name_queue != "":
                response["message"] = "Se necesita el nombre del topico"
                response["status"] = 400
            else:
                response["message"] = "Se necesita el nombre de la cola"
                response["status"] = 400
        return response

    def getTopics(self):
        pass