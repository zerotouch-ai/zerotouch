variable "aws_region" {
  description = "AWS region to deploy in"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.xlarge"
}

variable "ami_id" {
  description = "Amazon Machine Image ID — Ubuntu 22.04 LTS us-east-1"
  type        = string
  default     = "ami-0c7217cdde317cfec"
}

variable "public_key_path" {
  description = "Path to your local SSH public key"
  type        = string
  default     = "~/.ssh/zerotouch.pub"
}

variable "private_key_path" {
  description = "Path to your local SSH private key"
  type        = string
  default     = "~/.ssh/zerotouch"
}

variable "github_repo" {
  description = "GitHub repo URL to clone"
  type        = string
  default     = "https://github.com/zerotouch-ai/zerotouch.git"
}
