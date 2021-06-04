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
                    "image": "{}".format(config["image"]),
                    "ports": ports,
                    "command": ["sh", "-c", "sleep 999999"],
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
            subprocess.run("radtest {u} {p} {h} {n} {r}".format(
                u=username,
                p=password,
                h=hostname,
                n=nas_port_number,
                r=radius_secret
            ), shell=True).check_returncode()
            event.set_results({
                "Authentication Action Completed"
            })
        except Exception as e:
            event.fail("Authentication Action Failed: {}".format(e))


if __name__ == "__main__":
    main(FreeradiusK8SCharm)
