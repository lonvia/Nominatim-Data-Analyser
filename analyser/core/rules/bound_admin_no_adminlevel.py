from analyser.core.output_formatters import GeoJSONFormatter
from analyser.core.output_formatters import GeoJSONFeatureConverter
from analyser.core.output_formatters import LayerFormatter
from analyser.core.model import Node
from analyser.database import connect

class AdminBoundNoAdminLevel():
    """
        Implements the rule:

        "Relations with boundary=administrative without admin_level"
    """
    def __init__(self) -> None:
        super().__init__()

    def execute(self) -> bool:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ST_AsText(ST_Centroid(geometry)) FROM placex WHERE osm_type='R' AND class='boundary'
                    AND type='administrative' AND admin_level >= 15;
                """)
                points = [Node.create_from_string(geom[0]) for geom in cur]

        feature_converter = GeoJSONFeatureConverter()
        geo_formatter = GeoJSONFormatter('AdminBoundNoAL')
        layer_formatter = LayerFormatter('No admin level', 'AdminBoundNoAdminLevel', 'Every evening')
        layer_formatter.add_doc(
            'description', 'Every relation with boundary=administrative'\
            'should have a correct admin_level value set.'
        ).add_doc(
            'how_to_fix', 'An admin_level value should be set to the relation.'
        )

        feature_converter.plug_pipe(geo_formatter).plug_pipe(layer_formatter)
        feature_converter.process_and_next(points)

        return True
