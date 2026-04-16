# Plan de Estudio — cloudreviews.me

Tracker personal de certificaciones AWS (CCP, AI Practitioner, Terraform, CCA, SAA).

## Arquitectura

```
frontend/       → HTML/CSS/JS estático (GitHub Pages)
backend/        → AWS Lambda en Python
infrastructure/ → Terraform: DynamoDB + Lambda + API Gateway
.github/        → GitHub Actions: deploy automático
```

```
Browser → API Gateway → Lambda (Python) → DynamoDB
              (HTTPS)        (CRUD)       (persistencia)
```

---

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|-------------|----------------|-------------|
| AWS CLI | 2.x | [docs](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| Terraform | 1.6+ | [docs](https://developer.hashicorp.com/terraform/install) |
| Python | 3.12 | [python.org](https://www.python.org/downloads/) |
| Git | cualquiera | — |

---

## Despliegue inicial (una sola vez)

### 1. Configurar credenciales AWS

```bash
aws configure
# AWS Access Key ID:     <tu key>
# AWS Secret Access Key: <tu secret>
# Default region:        us-east-1
# Default output format: json
```

> Crea un usuario IAM con permisos: `AmazonDynamoDBFullAccess`, `AWSLambda_FullAccess`, `AmazonAPIGatewayAdministrator`, `IAMFullAccess`, `CloudWatchLogsFullAccess`.

### 2. Inicializar Terraform

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars si quieres cambiar región o nombres

terraform init
terraform plan    # revisa lo que va a crear
terraform apply   # escribe "yes" cuando pregunte
```

Al finalizar verás:

```
Outputs:
  api_url = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod"
```

**Copia esa URL.**

### 3. Migrar datos de Google Sheets a DynamoDB

Exporta los datos actuales desde Google Sheets como JSON y haz un `saveAll`:

```bash
# Reemplaza con la URL del paso anterior
API_URL="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"getAll"}' | jq .   # prueba que responde
```

El frontend migra los datos automáticamente la primera vez que se carga (lee de Google Sheets y los guarda en DynamoDB) — o puedes forzar desde DevTools:

```js
// En la consola del browser con la versión vieja cargada:
await saveData()
```

### 4. Configurar GitHub para deploy automático

En tu repositorio GitHub → **Settings → Secrets and variables → Actions**:

| Tipo | Nombre | Valor |
|------|--------|-------|
| Secret | `AWS_ACCESS_KEY_ID` | tu Access Key ID |
| Secret | `AWS_SECRET_ACCESS_KEY` | tu Secret Access Key |
| Secret | `API_URL` | la URL del paso 2 |
| Variable (opcional) | `CUSTOM_DOMAIN` | `cloudreviews.me` |

Luego activa GitHub Pages:
- **Settings → Pages → Source: Deploy from a branch**
- Branch: `gh-pages` / `/ (root)`

### 5. Push al repositorio

```bash
git add .
git commit -m "migrate: Google Sheets → AWS DynamoDB + Lambda"
git push origin main
```

Los workflows de GitHub Actions arrancan automáticamente y despliegan frontend + backend.

---

## Desarrollo local

### Probar el Lambda localmente

```bash
cd backend/lambda

# Simular getAll
python -c "
import json, os
os.environ['TABLE_NAME'] = 'study-plan-items'
# apunta a DynamoDB local si tienes docker:
# os.environ['AWS_ENDPOINT_URL'] = 'http://localhost:8000'
from handler import lambda_handler
event = {'httpMethod': 'GET', 'queryStringParameters': {'action': 'getAll'}}
print(json.dumps(json.loads(lambda_handler(event, None)['body'])[:2], indent=2))
"
```

### DynamoDB local con Docker (opcional)

```bash
docker run -d -p 8000:8000 amazon/dynamodb-local

# Crear tabla local
aws dynamodb create-table \
  --table-name study-plan-items \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000
```

---

## Estructura de datos (DynamoDB)

Tabla: `study-plan-items` — clave primaria: `id` (String)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | String | ID único de la actividad |
| `name` | String | Nombre de la actividad |
| `date` | String | Fecha `YYYY-MM-DD` |
| `cat` | String | Categoría: `aws`, `terraform`, `english`, etc. |
| `dur` | String | Duración estimada |
| `week` | String | Semana del plan |
| `topics` | String | Temas a cubrir |
| `course` | String | Nombre del curso |
| `links` | List | `[{label, url}, ...]` |
| `notes` | String | Notas personales |
| `realDur` | String | Duración real registrada |
| `done` | Boolean | Completada |
| `postponed` | Boolean | Pospuesta |

---

## API Reference

Base URL: `https://<id>.execute-api.us-east-1.amazonaws.com/prod`

| Método | Parámetros | Descripción |
|--------|-----------|-------------|
| `GET /?action=getAll` | — | Devuelve todas las actividades |
| `POST /` `{action:"saveRow", row:{...}}` | item completo | Crea o actualiza una actividad |
| `POST /` `{action:"saveAll", rows:[...]}` | array de items | Sobreescribe toda la tabla |
| `POST /` `{action:"deleteRow", id:"123"}` | id string | Elimina una actividad |

---

## Costos estimados

Con uso personal (< 10 000 peticiones/mes):

| Servicio | Costo mensual |
|----------|--------------|
| DynamoDB (PAY_PER_REQUEST) | ~$0.00 |
| Lambda (1M req gratis) | ~$0.00 |
| API Gateway (1M req gratis) | ~$0.00 |
| **Total** | **~$0 / mes** |

---

## Workflows de CI/CD

| Workflow | Trigger | Qué hace |
|----------|---------|----------|
| `deploy-backend.yml` | push a `backend/` o `infrastructure/` | `terraform apply` — actualiza Lambda y recursos AWS |
| `deploy-frontend.yml` | push a `frontend/` | Inyecta `API_URL`, despliega a GitHub Pages |
