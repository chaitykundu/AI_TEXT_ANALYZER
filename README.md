main.py → loads routes → app starts

##run module
python -m uvicorn app.main:app --reload

##build docker image
docker build -t ai-text-analyzer .

docker run -p 8000:8000 ai-text-analyzer

http://localhost:8000/docs