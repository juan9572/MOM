import os
import grpc
import tempfile
import communicationProcess_pb2
import communicationProcess_pb2_grpc
from bson.json_util import (loads, dumps)

class ReplicationServiceServicer(communicationProcess_pb2_grpc.ReplicationServiceServicer):

    collection = None

    def __init__(self, collection):
        self.collection = collection

    def SendReplication(self, request, context):
        message = ''
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(request.data)
                tmp_file_path = tmp_file.name
                self.collection.drop()
                with open(tmp_file_path, "rb") as bson_file:
                    insertOperation = self.collection.insert_many(loads(bson_file))
                    if insertOperation.acknowledged:
                        message = 'Archivo BSON cargado exitosamente en la base de datos.'
                    else:
                        message = 'Error de comunicacion'
                os.unlink(tmp_file_path)
        except Exception as e:
            print(e)
            message = f'Error {e}'
        return communicationProcess_pb2.confirmationMessage(
            messageOfConfirmation = message
        )

    def getReplication(self, request, context):
        try:
            data = None
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                bson_data = list(self.collection.find())
                dict_list = dumps(loads(dumps(bson_data))).encode('ascii')
                print(dict_list)
                tmp_file.write(dict_list)
                tmp_file_path = tmp_file.name
                print(dict_list.decode('ascii'))
                with open(tmp_file_path, "rb") as bson_file:
                    data = bson_file.read()
                os.unlink(tmp_file_path)
                print(data)
            return communicationProcess_pb2.Replica(data=data)
        except Exception as e:
            print(e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return communicationProcess_pb2.Replica()
