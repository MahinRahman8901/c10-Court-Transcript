# Create the eventbridge rules for judge seeding

resource "aws_lambda_permission" "allow_event_bridge_judges" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.judges-pipeline-terraform.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.judges-pipeline-terraform.arn
}

resource "aws_cloudwatch_event_rule" "judges-pipeline-terraform" {
  name                = "c10-court-judges-terraform"
  description         = "Triggers judges pipeline every first day of the month at midnight"
  schedule_expression = "cron(0 0 1 * ? *)"
}

resource "aws_cloudwatch_event_target" "judges_lambda_target" {
  rule      = aws_cloudwatch_event_rule.judges-pipeline-terraform.name
  target_id = "MyLambdaFunctionTarget"
  arn       = aws_lambda_function.court-pipeline-terraform.arn
}
