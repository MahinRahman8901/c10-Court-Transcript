resource "aws_iam_role" "lambda_execution_role" {
  name = "c10_court_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid = ""
      },
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "c10_court_lambda_policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
        Effect = "Allow"
      },
    ]
  })
}

resource "aws_lambda_function" "ord-lmnh-pipeline-terraform" {
  function_name = "c10-court-pipeline-terraform"

  package_type  = "Image"
  role          = aws_iam_role.lambda_execution_role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c10-court-pipeline:latest"

  timeout       = 300  
  memory_size   = 512 


  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_NAME     = var.DB_NAME
      DB_PASSWORD = var.DB_PASSWORD
      DB_PORT     = var.DB_PORT
      DB_USER     = var.DB_USER
      AWS_KEY     = var.AWS_KEY
      AWS_SKEY    = var.AWS_SKEY
      BASE_URL    = var.BASE_URL
      COMM_QUERY_EXTENSION = var.COMM_QUERY_EXTENSION
      STORAGE_FOLDER = var.STORAGE_FOLDER
      OPENAI_API_KEY = var.OPENAI_API_KEY
    }
  }
}