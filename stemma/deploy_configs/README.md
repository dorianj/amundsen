# Customer Deploy Configs

Generates and deploys a workflow on Argo (Kubernetes) from a pre-defined set of configurations. A workflow is a set of databuilder jobs that run sequentially. The workflow generator allows a configuration-driven approach to creating simple DAGs / workflows within Argo.

# TODOS:
- Standardize roles used for all pods in all helm charts
- Pass in secrets role name to common secrets
  - Currently hard-coded: `data = {'role': 'webapp', 'jwt': jwt}`
- Fix issue where config generation cannot access kubernetes resource
  - `User "system:serviceaccount:default:vault" cannot get resource "cronworkflows" in API group "argoproj.io" in the namespace "default"`
- Use AWS-provided backend for vault
  - Dynamodb? Secrets manager?
- Chat w/ Release about standardizing infrastructure install:
  - Vault, Argo
  - Should these be managed separately from the actual workflows / databuilder tasks?



## Prod setup

TBD

Vault auto unseal: https://learn.hashicorp.com/tutorials/vault/kubernetes-raft-deployment-guide?in=vault/kubernetes#config-example-aws-eks



## Local Setup

Start by adding hashicorp helm repo to Kubernetes, this will be used for both Vault and Consul while running locally:
```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
```

When running Vault locally it is suggested to use Consul to persist the secrets since it allows you to run everything locally and to easily remove all Vault references from your Kubernetes deployment. If you do not use Consul, Vault will use a default file store which makes removing / recreating Vault a pain because Vault will remain "initialized" across helm install / uninstalls by referencing the existin files in Kubernetes. Note, for local setup follow [this guide](https://learn.hashicorp.com/tutorials/consul/kubernetes-minikube).

```bash
helm install -f helm/local_infra/consul_values.yml consul hashicorp/consul --wait --debug
```

[Install Vault](https://learn.hashicorp.com/tutorials/vault/kubernetes-minikube?in=vault/kubernetes) as a single-node instance.

```bash
helm install vault hashicorp/vault --values helm/local_infra/vault_values.yml --wait --debug
```
(more information about high availability in the link above)

Save the Vault secrets to a local tmp file:

```bash
mkdir helm/local_infra/.tmp || echo "dir exists" && \
kubectl exec vault-0 -- vault operator init \
  -key-shares=1 \
  -key-threshold=1 \
  -format=json > helm/local_infra/.tmp/cluster-keys.json
```

Load the unseal key as an envvar:
```bash
VAULT_UNSEAL_KEY=$(cat helm/local_infra/.tmp/cluster-keys.json | jq -r ".unseal_keys_b64[]")
echo $VAULT_UNSEAL_KEY
```

Unseal the Vault instances:
```bash
kubectl exec vault-0 -- vault operator unseal $VAULT_UNSEAL_KEY
kubectl exec vault-1 -- vault operator unseal $VAULT_UNSEAL_KEY
kubectl exec vault-2 -- vault operator unseal $VAULT_UNSEAL_KEY
```

Port forward to vault:
```bash
kubectl port-forward vault-0 8200:8200
```

Get the vault token to log in, then go to `localhost:8200` and add a new secret:
```bash
echo $(cat helm/local_infra/.tmp/cluster-keys.json | jq -r ".root_token")
# Should look like: s.KKX.....
```

The default suggestions used for the rest of this walkthrough are:
- Secret engine: `key/value`
- Secret enging name: `secret`
- Secret path: `stemma/snowflake`

Add the following content to the secret:

```json
{
  "CONNECTION": {
    "ACCOUNT": "<GET_ACCT_FROM_TEAMMATE>",
    "PASSWORD": "<GET_PW_FROM_TEAMMATE>",
    "ROLE": "ACCOUNTADMIN",
    "USERNAME": "<GET_USER_FROM_TEAMMATE>",
    "WAREHOUSE": "COMPUTE_WH"
  },
  "DATABASES": [
    {
      "METADATA": true,
      "NAME": "\"ca_covid\"",
      "STATS": true
    },
    {
      "METADATA": true,
      "NAME": "SNOWFLAKE_SAMPLE_DATA",
      "STATS": true
    }
  ],
  "TYPE": "snowflake"
}
```

Access the vault pod to complete the authenticaiton:
```bash
kubectl exec --stdin=true --tty=true vault-0 -- /bin/sh
```

Inside the vault pod login, using the token valut token above:
```bash
vault login
# Token (will be hidden):
```

Enable k/v secrets on the path `secret/`:

```bash
vault secrets enable -path=secret kv-v2
```

Create a placeholder secretfor now:

```bash
vault kv put secret/stemma/snowflake username="static-user" password="static-password"
```

Enable Kubernetes auth and then configure it:

```bash
vault auth enable kubernetes

vault write auth/kubernetes/config \
        token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
        kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \
        kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

Next, add a policy to allow read access to the secret. Name the policy `readsnowflake` with the following content. Note, that `data` is inserted between the key-value base location and the location of the secret, the convention is `{k/v location}/data/{secret location}`.


The * gives access to all secrets in this location.

```text
vault policy write stemmaread - <<EOF
path "secret/data/stemma/*" {
  capabilities = ["read"]
}
EOF
```

Finally, bind the policy to the role (currently using `vault`). Use the CLI in your terminal and run:

Finally, create the role binding that can access the secrets. This role will be used from the databuilder job and the workflow generator job. Currently the role name being passed is `vault`:

```bash
vault write auth/kubernetes/role/stemmaread \
        bound_service_account_names=vault \
        bound_service_account_namespaces=default \
        policies=stemmaread \
        ttl=24h
```

### Add Argo to the cluster:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm install argo-wf argo/argo-workflows --wait --debug
```

### Build the Docker images in the Kubernetes context

Set minikube docker daemon as the local docker

```bash
eval $(minikube docker-env)
```

Build the databuilder image (from base `amundsen` directory), this
image is the one that will be executing the databuilder jobs. Make sure to note that the image name is `stemma-databuilder`

This requires the docker build kit: `export DOCKER_BUILDKIT=1`

```bash
docker build -f stemma.databuilder.Dockerfile -t stemma-databuilder .
```

You can test the execution of this image. Before testing, note that this image will try to retrieve the data source connection information for for the databuilder task from a secret. If no secret class (e.g. Vault) is provided, the secrets will default to the `common/stemma/tests/secrets` value. This is currently hard-coded to be the snowflake instance but the connection details will be read from your local environment variables. You will need to export the following envvars:

```text
ACCOUNT=
PASSWORD=
ROLE=ACCOUNTADMIN
USERNAME=stemma_demo
WAREHOUSE=COMPUTE_WH
```

### Run databuilder docker container on it's own

This runs for the `"ca_covid"` database, swap this out for `SNOWFLAKE_SAMPLE_DATA` to execute against a different database.

```bash
docker run \
  -e RDB_DATABASE_NAME='ca_covid' \
  -e ACCOUNT=$ACCOUNT \
  -e PASSWORD=$PASSWORD \
  -e ROLE=$ROLE \
  -e USERNAME=$USERNAME \
  -e WAREHOUSE=$WAREHOUSE \
  stemma-databuilder snowflake-metadata
```

### Schedule Databuilder jobs with Argo

After running the databuilder job on its own, the next step is to have that job triggered via an Argo workflow. This is a two step process:

1. The values for the specific job must be created
2. The argo workflow must be scheduled

To simplify, we will manually execute the first item. Generate the customer configurations for the `preview` client:

```bash
python build_configs.py preview
```

This creates the file in `dist/yamls/preview.yml`. Now we need to pass that file in as an override to the Argo workflow. This schedules a job every 1 minute so it may take a moment for your workflow to kick off.

```bash
helm install -f dist/yamls/preview.yml stemma-argo-wf helm/argo_schedules
```

BEWARE - since this schedules a cron job every minute make sure to uninstall with the following command when done so that it doesn't slowly run up the Snowlfake bill!

```bash
helm uninstall stemma-argo-wf
```

### Dyanmically scheduling databuilder jobs from configs & secrets

Run the following command to run a job on kubernetes that will generate configs, dynamically build workflows, and then apply the workflows to Argo.

First, build the image that creates the configs:

```bash
docker build -f stemma.client_configs.Dockerfile -t stemma-deploy-configs .
```

Before running the job within Kubernetes you must first make sure that the customer configs are available to Kubernetes. For minikube (and the docker container in general) mount the customers configs to the `/app/customers` directory in the container.

```bash
minikube mount /Users/grantseward/GitHub/mono/amundsen/stemma/deploy_configs/customers:/app/customers
```

Start the Argo workflow to generate the configs:

```bash
helm install --set common.customerName=preview customer-confs helm/customer_configs
```

### Viewing workflows

View Argo in UI

```bash
kubectl port-forward deployment/argo-wf-argo-workflows-server 2746:2746
```
