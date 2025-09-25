docker logs e2977da8999f | tail -20
nvidia-smi
docker logs voicevox-api
docker logs voicevox-engine
docker logs voicevox-wrapper
nvidia-smi
docker compose down
docker compose up -d
docker compose down
docker compose down
docker compose up -d
docker compose down
docker compose up -d
docker compose down
docker compose up -d
curl -X POST http://localhost:8000/synthesize -H "Content-Type: application/json" -d "{\"speaker\":1,\"text\":\"テストです\"}"
 git config --global user.email "rubitojp@gmail.com"
  git config --global user.name "rubitojp"
