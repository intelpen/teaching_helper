from typing import Protocol
from abc import abstractmethod
import json


class RagProtocol(Protocol):  # try aklso protocol

    def log(self, message):
        pass

    # beeing abstract gives error: TypeError: Can't instantiate abstract class LLMRag with abstract method retrive_docs
    # it really needs to be abstract?

    @abstractmethod
    def retrieve_docs(self, message):
        raise NotImplementedError
