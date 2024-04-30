resource "aws_security_group" "court-dashboard-sec-group" {
  name   = "c10-court-dashbord-sg"
  description = "Allow traffic into dashboard"
  vpc_id = data.aws_vpc.cohort_10_vpc.id

  ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 8200
        protocol          = "tcp"
        to_port           = 8200
    }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_task_definition" "court-dashboard-task-definition" {
    family = "c10-court-dashboard-td"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    memory = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
    container_definitions = jsonencode([
        {
            name      = "court-dashboard-td"
            image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c10-court-dashboard:latest"
            essential = true
            portMappings = [
                {
                containerPort = 8200
                hostPort      = 8200
                }
            ],
            "environment": [
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
        }
    ])
}

resource "aws_ecs_service" "court-dashboard-service" {
    name = "c10-court-dashboard-service"
    cluster = data.aws_ecs_cluster.c10-ecs-cluster.cluster_name
    task_definition = aws_ecs_task_definition.court-dashboard-task-definition.arn
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
      security_groups = [aws_security_group.court-dashboard-sec-group.id]
      assign_public_ip = true
    }
}