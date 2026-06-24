# ── Fill these in before running terraform apply ──────────────────────────────

aws_region       = "us-east-1"
instance_type    = "t3.xlarge"
ami_id           = "ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS us-east-1
public_key_path  = "~/.ssh/zerotouch.pub"
private_key_path = "~/.ssh/zerotouch"
github_repo      = "https://github.com/zerotouch-ai/zerotouch.git"
