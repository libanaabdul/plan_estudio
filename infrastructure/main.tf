terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "plan-estudio-tfstate-libi"
    key    = "plan-estudio/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# ── DynamoDB ─────────────────────────────────────────────────────────────────

resource "aws_dynamodb_table" "study_plan" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project     = "plan-estudio"
    Environment = var.environment
  }
}

# ── IAM role for Lambda ───────────────────────────────────────────────────────

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "${var.project_name}-dynamodb-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
        ]
        Resource = aws_dynamodb_table.study_plan.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# ── CloudWatch log group ───────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = 3
}

# ── Lambda package ────────────────────────────────────────────────────────────

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/lambda"
  output_path = "${path.module}/.build/lambda.zip"

  excludes = ["requirements.txt", "__pycache__", "*.pyc"]
}

# ── Lambda function ───────────────────────────────────────────────────────────

resource "aws_lambda_function" "study_plan_api" {
  function_name    = var.project_name
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.study_plan.name
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy.lambda_dynamodb,
  ]

  tags = {
    Project     = "plan-estudio"
    Environment = var.environment
  }
}

# ── API Gateway ───────────────────────────────────────────────────────────────

resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api"
  description = "Plan de Estudio — REST API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Proxy resource: catches all paths
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

# ANY method on proxy — requiere Cognito JWT en Authorization header
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "proxy_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_any.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.study_plan_api.invoke_arn
}

# Root resource — requiere Cognito JWT en Authorization header
resource "aws_api_gateway_method" "root_any" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_rest_api.api.root_resource_id
  http_method   = "ANY"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "root_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_rest_api.api.root_resource_id
  http_method             = aws_api_gateway_method.root_any.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.study_plan_api.invoke_arn
}

# Deployment triggers on every plan change
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy,
      aws_api_gateway_method.proxy_any,
      aws_api_gateway_integration.proxy_lambda,
      aws_api_gateway_method.proxy_options,
      aws_api_gateway_integration.proxy_options,
      aws_api_gateway_method.root_any,
      aws_api_gateway_integration.root_lambda,
      aws_api_gateway_method.root_options,
      aws_api_gateway_integration.root_options,
      aws_api_gateway_authorizer.cognito,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "prod"

  tags = {
    Project     = "plan-estudio"
    Environment = var.environment
  }
}

# Permission: API Gateway can invoke Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.study_plan_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# ── Cognito User Pool ─────────────────────────────────────────────────────────
#
# Un User Pool es el "directorio de usuarios" de Cognito.
# Aquí configuramos:
#   - email como identificador de login
#   - verificación automática de email
#   - política de contraseñas
#   - tokens JWT con 1h de vida (se renuevan con refresh token)

resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-users"

  # Los usuarios se identifican por email (no por username)
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  # Cognito envía un código de verificación al crear la cuenta
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  # Configuración de los JWT tokens que emite Cognito
  user_pool_add_ons {
    advanced_security_mode = "OFF"
  }

  tags = {
    Project     = "plan-estudio"
    Environment = var.environment
  }
}

# ── Cognito App Client ────────────────────────────────────────────────────────
#
# El App Client representa la aplicación frontend dentro del User Pool.
# Sin "client secret" porque es una SPA pública (no puede guardar secretos).
# Habilitamos USER_PASSWORD_AUTH para que el frontend pueda hacer login
# enviando email + password directamente a la API de Cognito.

resource "aws_cognito_user_pool_client" "frontend" {
  name         = "${var.project_name}-frontend"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false # SPA pública — sin secreto

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",  # login con email+password
    "ALLOW_REFRESH_TOKEN_AUTH",  # renovar tokens sin re-login
    "ALLOW_USER_SRP_AUTH",       # SRP (más seguro, para futuro)
  ]

  # Vida de los tokens
  access_token_validity  = 1  # horas
  id_token_validity      = 1  # horas (este es el que enviamos a API Gateway)
  refresh_token_validity = 30 # días

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
}

# ── API Gateway: Cognito Authorizer ───────────────────────────────────────────
#
# El Authorizer le dice a API Gateway: "antes de pasar la request a Lambda,
# valida que el header Authorization contenga un IdToken válido de este User Pool".
# Si el token es inválido o está expirado → 401 Unauthorized sin llegar a Lambda.

resource "aws_api_gateway_authorizer" "cognito" {
  name          = "cognito-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.main.arn]

  # API Gateway busca el JWT en este header
  identity_source = "method.request.header.Authorization"
}

# ── CORS: OPTIONS con MOCK (sin auth) ─────────────────────────────────────────
#
# El browser envía una preflight OPTIONS antes de cada POST/GET cross-origin.
# Si OPTIONS requiriera Cognito auth, el preflight fallaría antes de que el
# usuario pudiera siquiera hacer login. Por eso OPTIONS usa MOCK (sin Lambda)
# y authorization = NONE. Las rutas GET/POST sí usan Cognito.

# --- OPTIONS en {proxy+} ---
resource "aws_api_gateway_method" "proxy_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "proxy_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "proxy_options_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "proxy_options_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'https://tracker.cloudreviews.me'"
  }

  depends_on = [aws_api_gateway_integration.proxy_options]
}

# --- OPTIONS en / (root) ---
resource "aws_api_gateway_method" "root_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_rest_api.api.root_resource_id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "root_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_rest_api.api.root_resource_id
  http_method = aws_api_gateway_method.root_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "root_options_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_rest_api.api.root_resource_id
  http_method = aws_api_gateway_method.root_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "root_options_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_rest_api.api.root_resource_id
  http_method = aws_api_gateway_method.root_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'https://tracker.cloudreviews.me'"
  }

  depends_on = [aws_api_gateway_integration.root_options]
}

# ── Aplicar Cognito Authorizer a los métodos ANY existentes ───────────────────
#
# Terraform no puede modificar recursos in-place cambiando solo el authorizer,
# así que redefinimos los métodos con authorization = COGNITO_USER_POOLS.
# Nota: los recursos aws_api_gateway_method.proxy_any y root_any que ya existen
# serán reemplazados (destroy + create) en el próximo terraform apply.
