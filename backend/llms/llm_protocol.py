from typing import Protocol
from abc import abstractmethod
import json

class LLMProtocol(Protocol): #try aklso protocol
   
    @abstractmethod
    def process_request(self, message):
        raise NotImplementedError
    
    @abstractmethod
    def log(self, message):
        raise NotImplementedError
