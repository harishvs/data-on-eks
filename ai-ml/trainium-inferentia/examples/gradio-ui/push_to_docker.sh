aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 043632497353.dkr.ecr.us-west-2.amazonaws.com
docker build --platform linux/amd64 -t chatbot-app .
docker tag chatbot-app:latest 043632497353.dkr.ecr.us-west-2.amazonaws.com/chatbot-app:latest
docker push 043632497353.dkr.ecr.us-west-2.amazonaws.com/chatbot-app:latest