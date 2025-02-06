cat >hello <<EOD
#!/bin/bash
#SBATCH --job-name=test_nodes
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:05:00
#SBATCH --output=/data/fsx/test_nodes_%j.out
#SBATCH --error=/data/fsx/test_nodes_%j.err
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "SLURM_NODELIST: $SLURM_NODELIST"
srun hostname
srun free -h
srun pwd
EOD

chmod u+x hello
sbatch hello

