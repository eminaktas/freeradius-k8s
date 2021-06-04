#!/usr/bin/env python3
# Copyright 2021 root
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from mysql import MysqlClient
from freeradiustesting import FreeRadiusTesting
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    MaintenanceStatus,
)

logger = logging.getLogger(__name__)


class FreeradiusK8SCharm(CharmBase):
    """Charm the service."""

    state = StoredState()
    db_host = "mariadb-k8s"
    db_port = "3306"
    db_user = "radius"
    db_password = "radpass"
    db_root_password = "radius"
    db_name = "radius"
    rad_debug = "no"
    freeradius_host = "10.233.95.0/24"

    def __init__(self, *args):
        super().__init__(*args)
        self.state.set_default(spec=None)

        # Basic hooks
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.leader_elected, self._apply_spec)

        # Action hooks
        self.framework.observe(self.on.custom_action, self._on_custom_action)

        # Relation hooks
        self.mysql_client = MysqlClient(self, "mysql")
        self.framework.observe(self.on.mysql_relation_changed, self._apply_spec)
        self.framework.observe(self.on.mysql_relation_broken, self._apply_spec)

        self.freeradiustesting_client = FreeRadiusTesting(self, "freeradiustesting")
        self.framework.observe(self.on.mysql_relation_changed, self._apply_spec)
        self.framework.observe(self.on.mysql_relation_broken, self._apply_spec)

    def _apply_spec(self, _=None):
        # Only apply the spec if this unit is a leader.
        if not self.framework.model.unit.is_leader():
            return
        new_spec = self.make_pod_spec()
        if new_spec == self.state.spec:
            return
        self.framework.model.pod.set_spec(new_spec)
        self.state.spec = new_spec

    def make_pod_spec(self):
        config = self.framework.model.config

        ports = [
            {
                "name": "port-1",
                "containerPort": config["port-1"],
                "protocol": "UDP",
            },
            {
                "name": "port-2",
                "containerPort": config["port-2"],
                "protocol": "UDP",
            }
        ]

        spec = {
            "version": 3,
            "containers": [
                {
                    "name": self.framework.model.app.name,
                    "image": "{}".format(config["image"]),
                    "ports": ports,
                    "envConfig": {  # Environment variables that wil be passed to the container
                        "DB_HOST": self.mysql_client.host or self.db_host,
                        "DB_PORT": self.mysql_client.port or self.db_port,
                        "DB_NAME": self.mysql_client.database or self.db_name,
                        "DB_USERNAME": self.mysql_client.user or self.db_user,
                        "DB_PASS": self.mysql_client.password or self.db_password,
                        "RAD_CLIENTS": self.freeradius_host,  # self.freeradiustesting_client.client or
                        "RAD_DEBUG": config.get("debug") or self.rad_debug,
                    }

                }
            ],
        }

        return spec

    def _on_config_changed(self, event):
        """Handle changes in configuration"""
        unit = self.model.unit
        unit.status = MaintenanceStatus("Applying new pod spec")
        self._apply_spec()
        unit.status = ActiveStatus("Ready")

    def _on_custom_action(self, event):
        """Define an action"""
        # TODO
        return


if __name__ == "__main__":
    main(FreeradiusK8SCharm)
