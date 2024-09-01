from pathlib import Path
import grpc

import presentium_pb2 as serializer
import presentium_pb2_grpc as grpc_lib

class GrpcConnector:
    def __init__(self, host: str, port: int, cert: str, key: str, ca: str):
        self.host = host
        self.port = port
        self.cert = self.__load(cert)
        self.key = self.__load(key)
        self.ca = self.__load(ca)

    def __load(self, path):
        with open(Path(path).expanduser(), 'rb') as f:
            data = f.read()
        return data

    def connect(self):
        # Verify we are talking to the right server and provide our own
        # certificate for verification
        credentials = grpc.ssl_channel_credentials(
            root_certificates=self.ca,
            private_key=self.key,
            certificate_chain=self.cert
        )

        # Change authority to remove the rpc. prefix
        channel = grpc.secure_channel(
            target=f'{self.host}:{self.port}', 
            credentials=credentials,
            options=[('grpc.ssl_target_name_override', self.host.replace('rpc.', ''))]
        )
        stub = grpc_lib.DeviceServiceStub(channel)
        self.stub = stub
        return stub
