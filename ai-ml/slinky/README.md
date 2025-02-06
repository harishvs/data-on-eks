In the current directory: 

```terraform init```

```./install.sh```

```bash
kubectl delete nodeset slurm-compute-debug -n slurm
kubectl delete statefulset slurm-controller -n slurm #wait till it terminated
kubectl apply -f slurm-controller-statefulset.yaml -n slurm
```

Wait till the controller comes up

```bash
kubectl apply -f gpu-nodeset.yaml -n slurm
```


