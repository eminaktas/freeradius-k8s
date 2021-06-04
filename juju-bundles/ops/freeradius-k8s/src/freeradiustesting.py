import ops.charm

from common import BaseRelationClient


class FreeRadiusTesting(BaseRelationClient):
    """Requires side of a Freeradius Testing Endpoint"""

    mandatory_fields = ["host"]

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name, self.mandatory_fields)

    @property
    def host(self):
        return self.get_data_from_unit("host")

    @property
    def client(self):
        return self.get_data_from_unit("client")
