# Create the cloud platform and database

provider "aws" {
    region = "eu-west-2"
    access_key = var.AWS_KEY
    secret_key = var.AWS_SKEY
}

data "aws_db_subnet_group" "public_subnet_group" {
    name = "public_subnet_group"
}

data "aws_vpc" "cohort_10_vpc" {
    id = "vpc-0c4f01396d92e1cc7"
}

data "aws_ecs_cluster" "c10-ecs-cluster" {
    cluster_name = "c10-ecs-cluster"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

resource "aws_security_group" "court-dashboard-sec-group" {
  name   = "c10-court-dashbord-sg"
  description = "Allow traffic into court dashboard"
  vpc_id = data.aws_vpc.cohort_10_vpc.id

  ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 5000
        protocol          = "tcp"
        to_port           = 5000
    }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_task_definition" "court-api-task-def" {
  family = "c10-court-api"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu       = 1024
  memory    = 2048
  execution_role_arn = data.aws_iam_role.execution-role.arn
  container_definitions = jsonencode([
    {
      name      = "court-api"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c10-court-api:latest"
      essential = true
      "environment": [
                {
                    "name": "ACCESS_KEY_ID",
                    "value": var.AWS_KEY
                },
                 {
                    "name": "SECRET_ACCESS_KEY",
                    "value": var.AWS_SKEY
                 },
                                 {
                    "name": "DB_HOST",
                    "value": var.DB_HOST
                },
                                 {
                    "name": "DB_NAME",
                    "value": var.DB_NAME
                },
                                 {
                    "name": "DB_PORT",
                    "value": var.DB_PORT
                },
                                 {
                    "name": "DB_USER",
                    "value": var.DB_USER
                },
                                 {
                    "name": "DB_PASSWORD",
                    "value": var.DB_PASSWORD
                }
            ]
      portMappings = [
        {
                    "name": "court-api-5000-tcp",
                    "containerPort": 5000,
                    "hostPort": 5000,
                    "protocol": "tcp",
                    "appProtocol": "http"
                },
                {
                    "name": "court-api-80-tcp",
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp"
                },
                {
                    "name": "court-api-8000-tcp",
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
      ]
    }
  ])
}

resource "aws_ecs_service" "court-dashboard-service" {
    name = "c10-court-dash-service"
    cluster = data.aws_ecs_cluster.c10-ecs-cluster.cluster_name
    task_definition = aws_ecs_task_definition.court-api-task-def.arn
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
      security_groups = [aws_security_group.court-dashboard-sec-group.id]
      assign_public_ip = true
    }
}