#!/bin/bash

# ZeroTouch — Full Deployment Script
# Run this once AWS credentials are configured

set -e

echo "================================================"
echo "  ZeroTouch Deployment Script"
echo "================================================"

# ── Step 1: Generate SSH Key ──────────────────────────────────────────────────
if [ ! -f ~/.ssh/zerotouch ]; then
    echo "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/zerotouch -N "" -C "zerotouch-deploy"
    echo "SSH key generated at ~/.ssh/zerotouch"
else
    echo "SSH key already exists at ~/.ssh/zerotouch"
fi

# ── Step 2: Terraform Init & Apply ───────────────────────────────────────────
echo ""
echo "Running Terraform..."
cd "$(dirname "$0")/terraform"

terraform init
terraform validate
terraform plan
terraform apply -auto-approve

# ── Step 3: Get EC2 IP ───────────────────────────────────────────────────────
EC2_IP=$(terraform output -raw instance_public_ip)
echo ""
echo "EC2 instance IP: $EC2_IP"

# ── Step 4: Update Ansible Inventory ─────────────────────────────────────────
sed -i "s/PASTE_EC2_IP_HERE/$EC2_IP/g" ../ansible/inventory.ini
echo "Ansible inventory updated with IP: $EC2_IP"

# ── Step 5: Wait for EC2 to be Ready ─────────────────────────────────────────
echo ""
echo "Waiting 30 seconds for EC2 to initialize..."
sleep 30

# ── Step 6: Run Ansible Playbook ─────────────────────────────────────────────
echo ""
echo "Running Ansible playbook..."
cd ../ansible
ansible-playbook -i inventory.ini playbook.yml

# ── Step 7: Print Final URLs ──────────────────────────────────────────────────
echo ""
echo "================================================"
echo "  ZeroTouch is LIVE!"
echo "================================================"
echo "  Target App   → http://$EC2_IP:8000"
echo "  Prometheus   → http://$EC2_IP:9090"
echo "  Grafana      → http://$EC2_IP:3000"
echo "  Locust       → http://$EC2_IP:8089"
echo "  MLflow       → http://$EC2_IP:5000"
echo "  Ollama       → http://$EC2_IP:11434"
echo "  Streamlit    → http://$EC2_IP:8501"
echo "================================================"
