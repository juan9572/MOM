from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Replica(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _any_pb2.Any
    def __init__(self, data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class confirmationMessage(_message.Message):
    __slots__ = ["messageOfConfirmation"]
    MESSAGEOFCONFIRMATION_FIELD_NUMBER: _ClassVar[int]
    messageOfConfirmation: str
    def __init__(self, messageOfConfirmation: _Optional[str] = ...) -> None: ...
