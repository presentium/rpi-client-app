"""Runs protoc with the gRPC plugin to generate messages and gRPC stubs."""

from grpc_tools import protoc

protoc.main((
    '',
    '-I./protos',
    '--python_out=src',
    '--grpc_python_out=src',
    './protos/presentium.proto',
))
