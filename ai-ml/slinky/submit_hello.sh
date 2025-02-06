cat >hello <<EOD
#!/bin/bash
#SBATCH --job-name=test_nodes
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --time=00:05:00
#SBATCH --output=/data/fsx/test_nodes_%j.out
#SBATCH --error=/data/fsx/test_nodes_%j.err
srun hostname
EOD

chmod u+x hello
sbatch hello

