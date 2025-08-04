```terraform
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "subnet_ids" {
  description = "The IDs of the subnets"
  value = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
}
```