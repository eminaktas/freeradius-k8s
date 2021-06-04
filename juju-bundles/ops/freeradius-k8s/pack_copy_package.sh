#!/bin/bash

echo "Packaging the charm and copying the files in ../juju-bundles/charms/freeradius-k8s"
charmcraft build && rm -rf ../../charms/freeradius-k8s/* && cp -r ./build/* ../../charms/freeradius-k8s
echo "Done!"