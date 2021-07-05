from __future__ import annotations
from analyser.core.exceptions import YAMLSyntaxException
import importlib
import typing

if typing.TYPE_CHECKING:
    from analyser.core.qa_rule import ExecutionContext

class PipeFactory():
    """
        Factory to assemble pipes.
    """
    @staticmethod
    def assemble_pipe(node_data: dict, exec_context: ExecutionContext):
        """
            Instantiate a pipe based on the given node_data
        """
        if not node_data['type']:
            raise YAMLSyntaxException("Each node of the tree (module) should have a 'type' defined.")

        module = importlib.import_module('analyser.core.pipes')

        try:
            dclass = getattr(module, node_data['type'])
        except AttributeError:
            raise YAMLSyntaxException(f"The type {node_data['type']} doesn't exist.")

        create = getattr(dclass, 'create_from_node_data')
        assembled_pipe = create(node_data, exec_context)
        return assembled_pipe