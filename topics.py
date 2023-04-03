

class TopicHandler():

    database = None
    collection = None

    def __init__(self, client):
        self.database = client["MOM"]
        self.collection = self.database["Users"]

    def createTopic(self, name_topic, ip):
        response = {}
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
                        'messages': [],
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
        return response

    def subscribeToTopic(self):
        pass

    def getTopics(self):
        pass