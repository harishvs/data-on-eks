aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 043632497353.dkr.ecr.us-west-2.amazonaws.com
docker build -t ray-serve-inf2-llama2-ab3-harish .
docker tag ray-serve-inf2-llama2-ab3-harish:latest 043632497353.dkr.ecr.us-west-2.amazonaws.com/ray-serve-inf2-llama2-ab3-harish:latest
docker push 043632497353.dkr.ecr.us-west-2.amazonaws.com/ray-serve-inf2-llama2-ab3-harish:latest