# Instruction to deploy the app in local cluster
- Comment the external secret/, and uncomment the secrets/
- Prerequisite: U must have 3 databases, if u use local db, u can apply the spec from local/postgres directory
- kubectl apply -k infra/k8s-spec/manifests/base