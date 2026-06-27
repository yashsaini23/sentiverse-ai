#!/bin/bash
# SentiVerse Production Deployment Script
# Target Region: AWS ap-south-1 (Mumbai)

echo "Initiating deployment to AWS ap-south-1..."

# 1. Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker & Docker Compose
sudo apt-get install -y docker.io docker-compose

# 3. Secure the environment
# Enforce strict firewall rules allowing only HTTP/HTTPS and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 4. Pull the latest codebase (Assuming SSH keys are configured)
git pull origin main

# 5. Build and launch the cluster in detached mode
echo "Building Docker images for production..."
docker-compose -f docker-compose.prod.yml build

echo "Starting SentiVerse Engine..."
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment successful. API is live on ap-south-1."