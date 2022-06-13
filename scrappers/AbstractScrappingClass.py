from abc import ABC, abstractmethod, abstractproperty


class AbstractScrappingClass(ABC):

    @abstractproperty
    def baseURL(self):
        pass

    @abstractmethod
    def login(user, password):
        pass

    @abstractmethod
    def process():
        pass
