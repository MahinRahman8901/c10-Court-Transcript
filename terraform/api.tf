resource "aws_security_group" "court-api-sec-group" {
  name   = "c10-court-api-sg"
  description = "Allow traffic into court api"
  vpc_id = data.aws_vpc.cohort_10_vpc.id

  ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 5000
        protocol          = "tcp"
        to_port           = 5000
    }

  ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 80
        protocol          = "tcp"
        to_port           = 80
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

resource "aws_alb" "court_api_alb" {
  name               = "c10-court-api-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.court-api-sec-group.id]
  subnets            = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
}

resource "aws_alb_listener" "court_front_end" {
  load_balancer_arn = aws_alb.court_api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.alb-court-api-tg.arn
    type             = "forward"
  }
}

resource "aws_alb_target_group" "alb-court-api-tg" {
  name        = "c10-court-api-lb-alb-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = var.VPC_ID
  target_type = "ip"
}

resource "aws_ecs_service" "court-api-service" {
    name = "c10-court-api-service"
    cluster = data.aws_ecs_cluster.c10-ecs-cluster.cluster_name
    task_definition = aws_ecs_task_definition.court-api-task-def.arn
    desired_count = 1
    launch_type = "FARGATE"

    load_balancer {
      target_group_arn = aws_alb_target_group.alb-court-api-tg.arn
      container_name = "court-api"
      container_port = 5000
    }
    
    network_configuration {
      subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
      security_groups = [aws_security_group.court-api-sec-group.id]
      assign_public_ip = true
    }
}