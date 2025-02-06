#!/bin/bash
#SBATCH --job-name=test_nodes
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:05:00
#SBATCH --output=/data/fsx/test_nodes_%j.out

# Print job info
echo "Job started at: $(date)"
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "SLURM_NODELIST: $SLURM_NODELIST"

# Run hostname on each node
srun hostname

# Print some system info from each node
srun free -h

# Print current working directory from each node
srun pwd

echo "Job finished at: $(date)"