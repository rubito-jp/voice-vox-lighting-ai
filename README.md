
1 docker compose up -d 
(ensure the NVIDIA Container Toolkit is installed so the GPU reservation works); 
2 confirm https://voicevox-test-00.lacchinh.com/docs reaches the engine once DNS points at the host.

To update run
```
git pull
docker compose pull
docker compose down
docker compose up -d
```