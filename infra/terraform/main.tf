terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Key Pair ─────────────────────────────────────────────────────────────────
resource "aws_key_pair" "zerotouch_key" {
  key_name   = "zerotouch-key"
  public_key = file(var.public_key_path)
}

# ── Security Group ────────────────────────────────────────────────────────────
resource "aws_security_group" "zerotouch_sg" {
  name        = "zerotouch-sg"
  description = "ZeroTouch security group - all required ports"

  # SSH
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # FastAPI target app
  ingress {
    description = "FastAPI"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Prometheus
  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana
  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Locust
  ingress {
    description = "Locust"
    from_port   = 8089
    to_port     = 8089
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Streamlit
  ingress {
    description = "Streamlit"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # MLflow
  ingress {
    description = "MLflow"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Ollama
  ingress {
    description = "Ollama"
    from_port   = 11434
    to_port     = 11434
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "zerotouch-sg"
    Project = "zerotouch"
  }
}

# ── EC2 Instance ──────────────────────────────────────────────────────────────
resource "aws_instance" "zerotouch" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  availability_zone      = "us-east-1a"
  key_name               = aws_key_pair.zerotouch_key.key_name
  vpc_security_group_ids = [aws_security_group.zerotouch_sg.id]

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
  }

  tags = {
    Name    = "zerotouch-server"
    Project = "zerotouch"
    Team    = "graduation"
  }
}

# ── Elastic IP (keeps IP stable across restarts) ──────────────────────────────
resource "aws_eip" "zerotouch_ip" {
  instance = aws_instance.zerotouch.id
  domain   = "vpc"

  tags = {
    Name    = "zerotouch-eip"
    Project = "zerotouch"
  }
}
