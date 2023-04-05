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
            print(loads(request.data))
            insertOperation = self.collection.insert_many(loads(request.data))
            if insertOperation.acknowledged:
                message = 'Archivo BSON cargado exitosamente en la base de datos.'
            else:
                message = 'Error de comunicacion'
        except Exception as e:
            message = f'Error {e}'
        return communicationProcess_pb2.confirmationMessage(
            messageOfConfirmation = message
        )

    def getReplication(self, request, context):
        try:
            bson_data = list(self.collection.find())
            dict_list = dumps(loads(dumps(bson_data))).encode('ascii')
            data = dict_list
            return communicationProcess_pb2.Replica(data=data)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return communicationProcess_pb2.Replica()
