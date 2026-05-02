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

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID — necesario para crear usuarios con AWS CLI"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito App Client ID — usar como COGNITO_CLIENT_ID en el frontend"
  value       = aws_cognito_user_pool_client.frontend.id
}

output "cognito_region" {
  description = "AWS region donde vive el User Pool"
  value       = var.aws_region
}
