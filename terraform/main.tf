# Create the cloud platform and database

provider "aws" {
    region = "eu-west-2"
    access_key = var.AWS_KEY
    secret_key = var.AWS_SKEY
}

data "aws_db_subnet_group" "public_subnet_group" {
    name = var.SUBNET_GROUP
}

data "aws_vpc" "cohort_10_vpc" {
    id = var.VPC_ID
}

data "aws_ecs_cluster" "c10-ecs-cluster" {
    cluster_name = var.ECS_CLUSTER
}

data "aws_iam_role" "execution-role" {
    name = var.ECS_ROLE
}

resource "aws_security_group" "rds_security_group" {
    name = "c10-court-db-secgroup-terraform"
    description = "Allows inbound Postgres access"
    vpc_id = data.aws_vpc.cohort_10_vpc.id

    ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 5432
        protocol          = "tcp"
        to_port           = 5432
    }
}

resource "aws_db_instance" "court-db" {
  allocated_storage            = 10
  db_name                      = "court_transcript"
  identifier                   = "c10-court-transcript-db"
  engine                       = "postgres"
  engine_version               = "16.1"
  instance_class               = "db.t3.micro"
  username                     = var.DB_USER
  password                     = var.DB_PASSWORD
  publicly_accessible          = true
  performance_insights_enabled = false
  skip_final_snapshot          = true
  db_subnet_group_name         = data.aws_db_subnet_group.public_subnet_group.name
  vpc_security_group_ids       = [aws_security_group.rds_security_group.id]
}