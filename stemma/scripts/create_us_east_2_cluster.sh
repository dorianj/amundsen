#!/bin/bash

export EKS_REGION="us-east-2"
# Please change the name of the cluster to make it same as in the file
export EKS_CLUSTER="stemma-${EKS_REGION}"
export EKS_KEY="stemma-${EKS_REGION}-key"
export AWS_ACCOUNT_ID='061631484647'

if [[ -z $AWS_ACCOUNT_ID ]]; then
  echo "AWS_ACCOUNT_ID is not set in the script. Terminating"
  exit 125
fi

# Create the KeyPair
aws ec2 create-key-pair --region $EKS_REGION --key-name $EKS_KEY

# Create the Cluster
eksctl create cluster -f scripts/clusters/us_east_2_cluster.yaml

# View Services
kubectl get services -o wide

# Install the TargetGroupBinding custom resource definitions.
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

# Add eks-charts repo
helm repo add eks https://aws.github.io/eks-charts

# Install the AWS Load Balancer Controller
helm upgrade -i aws-load-balancer-controller eks/aws-load-balancer-controller --set clusterName=$EKS_CLUSTER --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller -n kube-system

# Verify that the controller is installed.
kubectl get deployment -n kube-system aws-load-balancer-controller