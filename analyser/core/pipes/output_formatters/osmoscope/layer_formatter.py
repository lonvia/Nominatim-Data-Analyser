from __future__ import annotations
from analyser.core.model.paths import Paths
from analyser.core import Pipe
from pathlib import Path
import json
import typing

if typing.TYPE_CHECKING:
    from analyser.core.qa_rule import ExecutionContext

class LayerFormatter(Pipe):
    """
        Handles the creation of the layer JSON file.
    """
    def __init__(self, data: dict, exec_context: ExecutionContext) -> None:
        super().__init__(exec_context)
        self.file_name = data.pop('file_name')
        self.data_format_url = data.pop('data_format_url')
        self.data = data
        self.data['id'] = 'SuspectsData'
        self.base_folder_path = Path('/srv/nominatim/data-files')

    def add_doc(self, key: str, content: str) -> LayerFormatter:
        """
            Add content under the 'doc' tag of the layer file.
        """
        self.data['doc'][key] = content
        return self

    def process(self, paths: Paths) -> None:
        """
            Create the JSON layer file containing the right data.
            
            It gets the GeoJSON url as data parameter and set it
            inside the layer file.
        """
        self.data[self.data_format_url] = paths.web_path

        folder_path = Path(self.base_folder_path / Path('layers')).resolve()
        folder_path.mkdir(parents=True, exist_ok=True)
        full_path = folder_path / Path(self.file_name + '.json')

        with open(full_path, 'w') as json_file:
            json.dump(self.data, json_file)
        
        file_url = 'https://gsoc2021-qa.nominatim.org/QA-data/layers/' + self.file_name + '.json'
        self.add_layer_to_global_layers_file(file_url)

    def add_layer_to_global_layers_file(self, path: str) -> None:
        """
            Add the newly created layer to the global layers file.
            If the global layers file doesn't exist it is created.
        """
        folder_path = self.base_folder_path.resolve()
        folder_path.mkdir(parents=True, exist_ok=True)
        full_path = folder_path / Path('layers.json')
        full_path.touch(exist_ok=True)

        with open(full_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except:
                data = {
                    'name': 'Nominatim suspects',
                    'layers': []
                }
        if path not in data['layers']:
            data['layers'].append(path)
        with open(full_path, 'w') as json_file:
            json.dump(data, json_file)

    @staticmethod
    def create_from_node_data(data: dict, exec_context: ExecutionContext) -> LayerFormatter:
        """
            Assembles the pipe with the given node data.
        """
        layer_formatter = LayerFormatter(data, exec_context)
        # if 'docs' in data:
        #     for k, v in data['docs'].items():
        #         layer_formatter.add_doc(k, v)
        #     data.pop('docs')
        return layer_formatter
