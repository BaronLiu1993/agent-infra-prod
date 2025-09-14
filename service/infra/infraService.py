from pydo import Client
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS = os.environ.get("DIGITALOCEAN_ACCESS")
SSH_KEY=os.environ.get("DIGITALOCEAN_SSH_FINGERPRINT")
OPENAI_KEY=os.environ.get("GEMINI_API_KEY")
GEMINI_KEY=os.environ.get("OPENAI_API_KEY")
GITHUB_ACCESS=os.environ.get("GITHUB_ACCESS")


#Start Up Script is Slow so we need to speeden it up
def createDroplet(name: str, userName: str, repoName: str, postgresUser: str, postgresPassword: str):
    client = Client(token=ACCESS)
    try:
        req = {
            "name": name,
            "region": "tor1",
            "size": "s-2vcpu-4gb",
            "image": "docker-20-04",  
            "backups": False,
            "ipv6": False,
            "ssh_keys": [SSH_KEY],
            "monitoring": False,
            "tags": ["fastapi", "demo"],
            "user_data": f"""#!/bin/bash
apt-get update -y && apt-get install -y git python3-pip docker-compose-plugin

mkdir -p /opt/app
cd /opt/app
git clone https://BaronLiu1993:{GITHUB_ACCESS}@github.com/{userName}/{repoName} .

pip3 install -r requirements.txt

cat <<EOL > /opt/app/docker-compose.yml
version: "3.9"
services:
  postgres:
    container_name: postgres
    image: pgvector/pgvector:pg14
    restart: always
    environment:
      POSTGRES_USER: {postgresUser}
      POSTGRES_PASSWORD: {postgresPassword}
      POSTGRES_DB: agentinfradb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOL

cd /opt/app
docker compose up -d

for i in {{1..20}}; do
    if docker exec -i postgres pg_isready -U {postgresUser} -d agentinfradb >/dev/null 2>&1; then
        echo "Postgres is ready!"
        break
    fi
    echo "Postgres not ready yet..."
    sleep 2
done

# Run SQL commands
docker exec -i postgres psql -U {postgresUser} -d agentinfradb <<'EOSQL'
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    data JSONB NOT NULL,
    log_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    input TEXT NOT NULL,
    prompt TEXT NOT NULL,
    output TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

EOSQL

cat <<EOL > /etc/systemd/system/fastapi.service
[Unit]
Description=Agent Infrastructure
After=network.target docker.service
Requires=docker.service

[Service]
User=root
WorkingDirectory=/opt/app
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl enable fastapi
systemctl start fastapi

ufw allow 9187
ufw allow 9090
ufw allow 8001
ufw allow 8000
ufw reload
"""
    }
        resp = client.droplets.create(body=req) 
        print(resp)
        return { "message": "Created Successfully", "success": True, "dropletId": resp['droplet']['id']}
    except Exception as e:
        print(f"Failed To Create Instance {e}")
        return { "message": "Internal Server Error", "success": False}


def getCPUMetrics(dropletId: str):
    try:
        client = Client(token=ACCESS)
        resp = client.monitoring.get_app_cpu_percentage_metrics(dropletId)
        return resp
    except Exception as e:
        return { "message": "Internal Server Error", "success": False}
    
def getBandwidthMetrics(dropletId):
    try:
        client = Client(token=ACCESS)
        resp = client.monitoring.get_droplet_bandwidth_metrics(dropletId)
        return { "message": "Fetched Successfully", "success": True, "data": resp}
    except Exception as e:
        return { "message": "Internal Server Error", "success": False}

def getMemoryMetrics(dropletId):
    try:
        client = Client(token=ACCESS)
        resp = client.monitoring.get_droplet_memory_total_metrics(dropletId)
        return { "message": "Fetched Successfully", "success": True, "data": resp}
    except Exception as e:
        return { "message": "Internal Server Error", "success": False}

        
def retrieveDropletData(dropletId: str):
    try:
        client = Client(token=ACCESS)
        resp = client.droplets.get(dropletId)
        return { "message": "Fetched Successfully", "success": True, "data": resp }
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}

    




