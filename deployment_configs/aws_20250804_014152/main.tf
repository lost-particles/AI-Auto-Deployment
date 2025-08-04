```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"  # Replace with your desired AWS region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "flask-demo-vpc"
  }
}

resource "aws_subnet" "public_subnet_a" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a" #Replace with appropriate AZ
  map_public_ip_on_launch = true

  tags = {
    Name = "flask-demo-public-subnet-a"
  }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b" #Replace with appropriate AZ
  map_public_ip_on_launch = true

  tags = {
    Name = "flask-demo-public-subnet-b"
  }
}


resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "flask-demo-igw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "flask-demo-public-rt"
  }
}

resource "aws_route_table_association" "public_subnet_a_assoc" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_subnet_b_assoc" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}


resource "aws_security_group" "flask_sg" {
  name        = "flask-demo-sg"
  description = "Allow inbound traffic on port 8000 and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

    ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] #Consider restricting to your IP
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "flask-demo-sg"
  }
}

resource "aws_launch_template" "flask_lt" {
  name_prefix   = "flask-demo-launch-template"
  image_id      = "ami-0c55b1a9434c894e3" # Replace with a suitable AMI for your region.  e.g. Ubuntu 20.04
  instance_type = "t2.micro"  # Adjust instance size as needed
  security_group_names = [aws_security_group.flask_sg.name]

  user_data = base64encode(<<EOF
#!/bin/bash
sudo apt update
sudo apt install -y python3-pip
pip3 install flask
# Simple Flask app (replace with your actual application)
cat > app.py <<END
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
END

python3 app.py &
EOF
  )

  network_interface {
    associate_public_ip_address = true
    subnet_id                   = aws_subnet.public_subnet_a.id  # Or public_subnet_b.id, or use a more sophisticated distribution strategy.
    security_groups             = [aws_security_group.flask_sg.id]
  }
}


resource "aws_autoscaling_group" "flask_asg" {
  name                 = "flask-demo-asg"
  desired_capacity     = 2
  max_size             = 2
  min_size             = 1
  vpc_zone_identifier  = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id] #Use all public subnets
  launch_template {
    id      = aws_launch_template.flask_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "flask-demo-instance"
    propagate_at_launch = true
  }
}

resource "aws_lb" "alb" {
  name               = "flask-demo-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups   = [aws_security_group.flask_sg.id]
  subnets            = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]

  tags = {
    Name = "flask-demo-alb"
  }
}

resource "aws_lb_target_group" "flask_tg" {
  name     = "flask-demo-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path = "/" #customize if needed
    protocol = "HTTP"
    port = "8000"

  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.flask_tg.arn
  }
}

resource "aws_autoscaling_attachment" "asg_attachment" {
  autoscaling_group_name = aws_autoscaling_group.flask_asg.name
  lb_target_group_arn    = aws_lb_target_group.flask_tg.arn
}

output "alb_dns_name" {
  value = aws_lb.alb.dns_name
  description = "The DNS name of the ALB"
}
```