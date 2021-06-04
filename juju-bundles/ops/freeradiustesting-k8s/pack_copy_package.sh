#!/bin/bash

echo "Packaging the charm and copying the files in ../juju-bundles/charms/freeradiustesting-k8s"
charmcraft build && rm -rf ../../charms/freeradiustesting-k8s/* && cp -r ./build/* ../../charms/freeradiustesting-k8s
echo "Done!"