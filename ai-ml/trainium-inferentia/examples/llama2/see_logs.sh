PODNAME=$(kubectl get pods -l job-name=test-mpi-train-launcher,training.kubeflow.org/job-role=launcher -o name)
U_ID=$(kubectl get $PODNAME -o json | jq -r ".metadata.uid")
GREP_BY=$1
if [[ -z "$GREP_BY" ]]; then
	kubectl exec -it test-mpi-train-worker-2 -- tail -f /shared/nemo_experiments/$U_ID/0/log 
else 
	kubectl exec -it test-mpi-train-worker-2 -- tail -f /shared/nemo_experiments/$U_ID/0/log |grep -i $GREP_BY 
fi
