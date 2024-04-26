# Create the eventbridge rules for ETL

resource "aws_lambda_permission" "allow_event_bridge_pipeline" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.court-pipeline-terraform.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.court-pipeline-terraform.arn
}

resource "aws_cloudwatch_event_rule" "court-pipeline-terraform" {
  name                = "c10-court-pipeline-terraform"
  description         = "Triggers court transript ETL every day"
  schedule_expression = "cron(0 18 * * ? *)"
}

resource "aws_cloudwatch_event_target" "pipeline_lambda_target" {
  rule      = aws_cloudwatch_event_rule.court-pipeline-terraform.name
  target_id = "MyLambdaFunctionTarget"
  arn       = aws_lambda_function.court-pipeline-terraform.arn
}
