

class UserHandler():
    database = None
    collection = None

    def __init__(self, client):
        self.database = client["MOM"]
        self.collection = self.database["Users"]

    def registerUser(self, username, password, ip):
        response = {}
        if username and password and username != "" and password != "":
            existing_user = self.collection.find_one({'username': username})
            # Falta la lógica para encriptar los datos
            if existing_user:
                response["message"] = "La cuenta " + username + " ya existe y por lo tanto no se puede crear"
                response["status"] = 409
            else:
                new_user = {
                    'username': username,
                    'password': password,
                    'queues': [],
                    'topics': [],
                    'active': True,
                    'currentIp': ip
                }
                resultOperation = self.collection.insert_one(new_user)
                if resultOperation.acknowledged:
                    response["message"] = "Se creo la cuenta " + username + " y se agrego a la DB"
                    response["status"] = 201
                else:
                    response["message"] = "Hubo un error al comunicarse con la DB, no se pudo crear el usaurio " + username
                    response["status"] = 500
        else:
            response["message"] = "Se esperaba un username y password, no se recibieron..."
            response["status"] = 400
        return response

    def loginUser(self, username, password, ip):
        response = {}
        if username and password and username != "" and password != "":
            existing_user = self.collection.find_one({'username': username})
            # Falta la lógica para desencriptar los datos
            if existing_user and password == existing_user["password"]:
                if existing_user["active"] == True:
                    response["message"] = "Ya estas logeado " + username
                    response["status"] = 200
                else:
                    activeUser = self.collection.update_one(
                        {'username': username},
                        {'$set': {
                            'active': True,
                            'currentIp': ip
                        }}
                    )
                    if activeUser.acknowledged:
                        response["message"] = "Bienvenido " + username
                        response["status"] = 200
                    else:
                        response["message"] = "Hubo un error al comunicarse con la DB"
                        response["status"] = 500
            else:
                response["message"] = "La cuenta o password no son correctas"
                response["status"] = 401
        else:
            response["message"] = "Se esperaba un username y password, no se recibieron..."
            response["status"] = 400
        return response

    def logoutUser(self, ip):
        response = {}
        activeUser = self.collection.update_one(
            {'currentIp': ip},
            {'$set': {
                'active': False,
                'currentIp': ''
            }}
        )
        if activeUser.acknowledged:
            response["message"] = "Adios, "+ ip + " vuelve pronto."
            response["status"] = 200
        else:
            response["message"] = "Hubo un error al comunicarse con la DB"
            response["status"] = 500
        return response