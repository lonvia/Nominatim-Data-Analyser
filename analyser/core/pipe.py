from __future__ import annotations
from abc import ABCMeta, abstractmethod
from analyser.core.exceptions.yaml_syntax_exception import YAMLSyntaxException
import typing
import uuid

if typing.TYPE_CHECKING:
    from analyser.core.qa_rule import ExecutionContext

class Pipe(metaclass=ABCMeta):
    """
        This is the base class for every pipe.
    """
    def __init__(self, data: dict, exec_context: ExecutionContext = None) -> None:
        self.id = uuid.uuid1()
        self.exec_context = exec_context
        self.data = data
        self._next_pipes = set()
        self.on_created()

    def plug_pipe(self, pipe: Pipe) -> Pipe:
        self._next_pipes.add(pipe)
        return pipe

    def process_and_next(self, data: any = None) -> any:
        """
            Process this pipe and process the plugged ones
            by giving them the result of this execution.
        """
        result = self.process(data)
        for pipe in self._next_pipes:
            pipe.process_and_next(result)
        return None

    def __str__(self):
        return type(self).__name__ + ' ' + str(self.id)

    @abstractmethod
    def process(self, data: any = None) -> any:
        """
            Contains the execution logic of this pipe.
        """
        return

    def on_created(self) -> None:
        """
            This method is called when the pipe is created.

            It should be overriden by the child pipe if any action is needed
            at the creation. 
            
            This is needed because child pipes can't have their own
            constructor since pipes are created dynamically.
        """
        pass

    def extract_data(self, name: str, default: any = None, required: bool = False) -> any:
        """
            Tries to get data from the data dictionary.

            If the data name provided exists in the dictionary it gets pop out and it gets returned. 
            But if it doesn't exist, the default value provided is returned (None by default).

            if the required value is set to True and if the data can't be found, a YAMLSyntaxException is raised.
        """
        if name in self.data:
             return self.data.pop(name)
        elif required == False:
            return default
        else:
            raise YAMLSyntaxException(f'The field "{name}" is required for the pipe of type {type(self).__name__}')