# Rocket.Chat — Stacker Deploy HOWTO

Two containers: app (rocket.chat:latest) + mongo:7.0.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Post-deploy: initialize mongo replica set

Rocket.Chat requires a MongoDB replica set. After first deploy, run:

```bash
ssh root@<SERVER_IP> "docker exec project-mongo-1 mongosh --eval 'rs.initiate()'"
```

The app container will automatically restart and connect once the replica set is ready.

## Verify

```bash
curl -I http://<SERVER_IP>:3000/
```

## Notes

- Port: 3000
- mongo on localhost:27017
- Named volumes: mongo_data
- MongoDB version 7.0 is deprecated for Rocket.Chat 9.0+; upgrade to mongo:8.0
