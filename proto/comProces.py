import bson
import comunicationProcess_pb2
import comunicationProcess_pb2_grpc

class ReplicationService(comunicationProcess_pb2_grpc.ReplicationService):

    def SendReplication(self, request, context):
        replication = request.data
        bson_data = bson.loads(replication)
        response = comunicationProcess_pb2.confirmationMessage = 'Por ahi me llego'
        return response
