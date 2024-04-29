resource "aws_lambda_function" "judges-pipeline-terraform" {
  function_name = "c10-judges-pipeline-terraform"

  package_type  = "Image"
  role          = aws_iam_role.lambda_execution_role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c10-court-judges:latest"

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
    }
  }
}