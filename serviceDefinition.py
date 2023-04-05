import os
import grpc
import bson
import tempfile
import communicationProcess_pb2
import communicationProcess_pb2_grpc

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
                    insertOperation = self.collection.insert_many(bson.load(bson_file))
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
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                bson.dumps(list(self.collection.find()), tmp_file)
                tmp_file_path = tmp_file.name
            with open(tmp_file_path, "rb") as bson_file:
                data = bson_file.read()
            os.unlink(tmp_file_path)
            return communicationProcess_pb2.Replica(data=data)
        except Exception as e:
            print(e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return communicationProcess_pb2.Replica()
