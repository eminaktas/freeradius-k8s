#!/bin/bash

echo "Packaging the charm and copying the files in ../juju-bundles/charms/freeradius-k8s"
charmcraft build && rm -rf ../juju-bundles/charms/freeradiustesting-k8s/* && cp -r ./build/* ../juju-bundles/charms/freeradiustesting-k8s
echo "Done!"