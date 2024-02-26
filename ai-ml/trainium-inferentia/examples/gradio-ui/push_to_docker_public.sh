aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/u1m6g1t5
docker build --platform linux/amd64 -t anytoy-chatbot-pubic .
docker tag anytoy-chatbot-pubic:latest public.ecr.aws/u1m6g1t5/anytoy-chatbot-pubic:latest
docker push public.ecr.aws/u1m6g1t5/anytoy-chatbot-pubic:latest