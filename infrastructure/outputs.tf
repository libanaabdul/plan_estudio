output "api_url" {
  description = "Base URL for the API — use this as API_URL in the frontend"
  value       = aws_api_gateway_stage.prod.invoke_url
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.study_plan.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.study_plan_api.function_name
}
