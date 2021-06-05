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
import subprocess

from utils import get_service_ip  # , get_cidr_from_iface
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

    def __init__(self, *args):
        super().__init__(*args)
        self.state.set_default(spec=None)

        # Basic hooks
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.leader_elected, self._apply_spec)

        # Action hooks
        self.framework.observe(self.on.auth_test_action, self._on_auth_test_action)

        # Relation hooks
        self.framework.observe(
            self.on.freeradiustesting_relation_changed,
            self._on_freeradiustesting_relation_changed
        )
        self.framework.observe(
            self.on.freeradiustesting_relation_broken,
            self._on_freeradiustesting_relation_changed
        )

    def _on_freeradiustesting_relation_changed(self, event):
        if not self.framework.model.unit.is_leader():
            return
        # TODO: Use Container IP. For now, accept all connections
        service_ip = get_service_ip(self.framework.model.app.name)
        # client = get_cidr_from_iface(service_ip)
        event.relation.data[self.model.unit]["host"] = service_ip
        event.relation.data[self.model.unit]["client"] = "0.0.0.0/0"  # client

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
                "name": "not-needed",
                "containerPort": 80,
                "protocol": "TCP",
            }
        ]

        spec = {
            "version": 3,
            "containers": [
                {
                    "name": self.framework.model.app.name,
                    "image": f"{config['image']}",
                    "ports": ports,
                    "command": ["sh", "-c", "while true; do sleep 30; done;"],
                    "envConfig": {  # Environment variables that wil be passed to the container
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

    def _on_auth_test_action(self, event):
        """Testing Authentication"""
        username = event.params["username"]
        password = event.params["password"]
        hostname = event.params["hostname"]
        nas_port_number = event.params["nas-port-number"]
        radius_secret = event.params["radius-secret"]
        try:
            out = subprocess.check_output(
                f"radtest {username} {password} {hostname} {nas_port_number} {radius_secret}",
                shell=True
            )
            # Pretty output
            out = out.decode("utf-8").strip().replace("\n\t", " ").replace("\n", " ")
            event.set_results({"result": f"Authentication Action Completed: {out}"})
        except Exception as e:
            event.fail(f"Authentication Action Failed: {e}")


if __name__ == "__main__":
    main(FreeradiusK8SCharm)
