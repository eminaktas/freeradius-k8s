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

It requires MySQL database restored. Manually, you can use these steps

```bash
# Copy backup file to container
kubectl cp mysql/radius.sql.gz mariadb-k8s-0:/tmp/backup.sql.gz -n testing-freeradius -c mariadb-k8s
# Run restore action
juju run-action mariadb-k8s/0 restore path="/tmp" -m testing-freeradius
```

## Auth test action 
```bash
juju run-action freeradiustesting-k8s/<unit-number> auth-test hostname=freeradius-k8s username=testing password=password nas-port-number=2 radius-secret=testing123 --wait -m testing-freeradius
```