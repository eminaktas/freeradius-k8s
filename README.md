# freeradius-k8s

## Deploy juju-bundle without OSM

Before deploying juju-bundle run `pack_copy_package.sh` to build charm and copy files to `juju-bundles/charms/freeradius-k8s`

```bash
# Add new juju model.
# Creating model will automatically switch to the new model
juju add-model testing-radius k8s-cloud

# Deploy juju model
# The applications in the model will be deployed in the new model
juju deploy ./juju-bundles

# Check status of the model
juju status

# Switch model
juju switch testing-radius
```