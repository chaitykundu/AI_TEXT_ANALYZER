main.py → loads routes → app starts

##run module
python -m uvicorn app.main:app --reload

##build docker image
docker build -t ai-text-analyzer .

docker run -p 8003:8003 ai-text-analyzer

docker run --env-file .env -p 8003:8003 ai-text-analyzer

http://localhost:8003/docs