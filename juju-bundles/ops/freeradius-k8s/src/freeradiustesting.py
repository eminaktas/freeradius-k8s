import ops.charm

from common import BaseRelationClient


class FreeRadiusTesting(BaseRelationClient):
    """Requires side of a Freeradius Testing Endpoint"""

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name)

    @property
    def host(self):
        return self.get_data_from_unit("host")

    @property
    def client(self):
        return self.get_data_from_unit("client")
