output "instance_public_ip" {
  description = "Public IP of the ZeroTouch EC2 instance"
  value       = aws_eip.zerotouch_ip.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.zerotouch.id
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/zerotouch ubuntu@${aws_eip.zerotouch_ip.public_ip}"
}

output "dashboard_url" {
  description = "Streamlit dashboard URL"
  value       = "http://${aws_eip.zerotouch_ip.public_ip}:8501"
}

output "grafana_url" {
  description = "Grafana URL"
  value       = "http://${aws_eip.zerotouch_ip.public_ip}:3000"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${aws_eip.zerotouch_ip.public_ip}:9090"
}

output "mlflow_url" {
  description = "MLflow URL"
  value       = "http://${aws_eip.zerotouch_ip.public_ip}:5000"
}

output "locust_url" {
  description = "Locust URL"
  value       = "http://${aws_eip.zerotouch_ip.public_ip}:8089"
}
