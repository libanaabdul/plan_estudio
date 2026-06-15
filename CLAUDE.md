# Plan de Estudio — Contexto para Claude Code

Este archivo es la fuente de verdad del proyecto para sesiones nuevas.

---

## Qué es este proyecto

Tracker personal de plan de estudio de certificaciones AWS + AI Engineer, con actividades de bebé intercaladas.
- **URL pública**: https://tracker.cloudreviews.me
- **Repo**: https://github.com/libanaabdul/plan_estudio
- **Branch de deploy**: `gh-pages` (GitHub Actions publica ahí; nunca tocar `main` directamente para pages)
- **Usuario**: Libi

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML/CSS/JS puro — un solo archivo `frontend/index.html` |
| Backend | AWS Lambda (Python 3.12) — `backend/lambda/handler.py` |
| Base de datos | AWS DynamoDB — tabla `study-plan-items`, PAY_PER_REQUEST |
| Auth | AWS Cognito User Pool + App Client (USER_PASSWORD_AUTH) |
| API | API Gateway REST — `https://dstlpawd97.execute-api.us-east-1.amazonaws.com/prod` |
| Infra | Terraform — estado en S3 bucket `plan-estudio-tfstate-libi` |
| CI/CD | GitHub Actions — dos workflows: `deploy-frontend.yml` y `deploy-backend.yml` |

---

## Estructura de archivos

```
plan_estudio/
├── frontend/
│   └── index.html          ← toda la app (UI + lógica + datos INITIAL)
├── backend/
│   └── lambda/
│       ├── handler.py      ← Lambda handler
│       └── requirements.txt
├── infrastructure/
│   ├── main.tf             ← DynamoDB, Lambda, API GW, Cognito
│   ├── variables.tf        ← project_name="plan-estudio", table_name="study-plan-items"
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── .github/workflows/
│   ├── deploy-frontend.yml ← push a main → inject secrets → gh-pages
│   └── deploy-backend.yml  ← push a main → terraform apply
└── CLAUDE.md               ← este archivo
```

---

## CI/CD — cómo funciona el deploy

### Frontend (`deploy-frontend.yml`)
- Se dispara con push a `main` si cambia `frontend/**`
- Inyecta secrets via `sed` en el HTML antes de deployar:
  - `__API_URL__` → secret `API_URL`
  - `__COGNITO_CLIENT_ID__` → secret `COGNITO_CLIENT_ID`
  - `__COGNITO_REGION__` → secret `COGNITO_REGION`
- Publica en rama `gh-pages` con `cname: tracker.cloudreviews.me`
- **Tarda ~2 min**

### Backend (`deploy-backend.yml`)
- Se dispara con push a `main` si cambia `backend/**` o `infrastructure/**`
- Corre `terraform init → validate → plan → apply`
- **Tarda ~5 min**
- Secrets necesarios: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

### GitHub Pages
- Configurado en Settings → Pages → Branch: `gh-pages`, root `/`
- Custom domain: `tracker.cloudreviews.me` (CNAME apuntando a `libanaabdul.github.io`)
- **IMPORTANTE**: el dominio debe estar configurado en Pages para que CORS funcione. El Lambda solo acepta origin `https://tracker.cloudreviews.me`

---

## Lambda — acciones disponibles

| Método | Acción | Descripción |
|--------|--------|-------------|
| GET | `?action=getAll` | Scan completo de DynamoDB, ordenado por date+id |
| POST | `{action:'saveRow', row:{}}` | Upsert de un ítem |
| POST | `{action:'saveAll', rows:[]}` | Batch write (el frontend lo llama en chunks de 50) |
| POST | `{action:'deleteRow', id:''}` | Delete de un ítem |
| POST | `{action:'deleteAll'}` | Borra toda la tabla (scan solo IDs + batch delete) |

**Reglas del Lambda:**
- Todos los responses incluyen headers CORS (`Access-Control-Allow-Origin: https://tracker.cloudreviews.me`)
- `_normalise()` filtra strings vacíos antes de escribir (DynamoDB los rechaza con ValidationException)
- El handler completo está en try/except — cualquier excepción devuelve 500 con CORS headers
- `saveAll` deduplica por `id` antes del batch write (DynamoDB rechaza duplicates en un batch)
- Timeout: **29 segundos**

---

## Frontend — funciones clave

### Datos
- `INITIAL` — array hardcodeado (~390 ítems) que es la fuente de verdad del plan
- `data` — variable global en memoria, sincronizada con DynamoDB
- `localStorage('studyplan_backup')` — cache local, solo fallback offline

### Carga de datos (`loadData`)
```
getAll (DynamoDB)
  → deduplicateData()     — dedup por content-key (no por id)
  → mergeAIEngEntries()   — agrega AI Eng desde INITIAL si faltan
  → migrateDates2026()    — redistribuye fechas si hay < '2026-06-15'
  → saveData() si cambió algo
```

### Guardado
- `saveData()` — saveAll en chunks de 50 ítems. Solo para resets/migraciones bulk.
- `saveRow(item)` — saveRow individual. Usado para marcar done, notas, etc.
- `deleteRow(id)` — deleteRow individual.

### Migración de fechas (`migrateDates2026`)
- Detecta si hay entradas de cert/aieng con fecha `< '2026-06-15'`
- Si detecta, redistribuye: **1 cert/día + 1 aieng/día**, lunes a sábado, saltando fechas de examen
- Categorías de cert: `aws, ai, terraform, cca, saa, repaso, english`
- Baby entries con fechas viejas se shiftan +45 días, clamped a `>= '2026-06-15'`
- Inicio del plan: **2026-06-15** (June 15, 2026 — hoy)

### Dedup (`deduplicateData`)
- Clave para cat≠baby: `cat|week|topics(40ch)|name(30ch)`
- Clave para baby: `baby|date` (máximo 1 baby por día)
- Gana el ítem con mayor score: done(+10) + notes(+3) + realDur(+2)

### Reset de emergencia (`purgeAndReset`)
- Botón "🗑 Purgar BD y reiniciar" en la UI (header, semitransparente)
- Llama `deleteAll` → limpia DynamoDB → reinicializa desde INITIAL → saveData

### Multi-select
- Botón "Seleccionar" en la vista diaria para seleccionar actividades y moverlas a otra fecha

---

## Plan de certificaciones

| Cert | Fecha target |
|------|-------------|
| AWS Cloud Practitioner | 1 Julio 2026 |
| AWS AI Practitioner | 3 Agosto 2026 |
| Terraform Associate | 23 Agosto 2026 |
| Claude CCA | 29 Septiembre 2026 |
| AWS SAA | ~24 Noviembre 2026 |
| AI Engineer | Octubre 2026 |

**Regla de 3 actividades/día**: máximo 3 por día = 1 baby (obligatoria) + 1 cert + 1 AI Eng.

---

## Categorías y colores

| cat | Label | Color |
|-----|-------|-------|
| `aws` | ☁️ AWS | naranja |
| `ai` | 🤖 AI Pract. | azul |
| `aieng` | 🧠 AI Eng | verde (`#4ade80`) |
| `terraform` | 🟣 Terraform | morado |
| `cca` | ✨ CCA | dorado |
| `saa` | 🏗️ SAA | azul oscuro |
| `baby` | 🩷 Bebé | rosa |
| `english` | 🇺🇸 English | — |
| `repaso` | 📝 Repaso | — |
| `examen` | 🎯 Examen | rojo |
| `descanso` | 😴 Descanso | — |

---

## Bugs conocidos y cómo se resolvieron

### "CORS:Missing Allow Origin" en POST
- **Causa real**: Lambda crashaba (ValidationException por strings vacíos en DynamoDB) → API GW devolvía 500 sin headers CORS
- **Fix**: `_normalise()` filtra `{k:v for k,v in item.items() if v != ""}` + wrapper try/except en `lambda_handler`

### "Provided list of item keys contains duplicates" (DynamoDB ValidationException)
- **Causa**: `deduplicateData` dedup por contenido pero no por ID → dos ítems con distinto contenido pero mismo `id` → DynamoDB rechaza el batch
- **Fix**: Lambda deduplica por `id` antes del batch. Frontend también deduplica con `new Map(data.map(d=>[String(d.id),d]))` antes de enviar

### Datos perdidos al abrir otro browser
- **Causa**: catch block de `loadData` llamaba `saveData()` sobreescribiendo DynamoDB con datos por defecto
- **Fix**: catch block sin `saveData()`; usa DynamoDB como fuente de verdad, localStorage solo como fallback offline

### Baby activities multiplicándose
- **Causa**: dedup usaba clave con contenido, múltiples babies en el mismo día pasaban
- **Fix**: clave `'baby|'+date` → máximo 1 baby por día

### saveAll timeout (10s Lambda)
- **Fix 1**: timeout subido a 29s en Terraform
- **Fix 2**: frontend divide en chunks de 50 ítems por request

---

## Variables de entorno / Secrets en GitHub

| Secret | Dónde se usa |
|--------|-------------|
| `API_URL` | URL de API Gateway, inyectada en el HTML |
| `COGNITO_CLIENT_ID` | ID del App Client de Cognito |
| `COGNITO_REGION` | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | CI backend para Terraform |
| `AWS_SECRET_ACCESS_KEY` | CI backend para Terraform |

Variable (no secret): `CUSTOM_DOMAIN` = `tracker.cloudreviews.me`

---

## Comandos útiles

```bash
# Ver estado git
git log --oneline -10
git status

# Deploy manual (normalmente basta con git push)
git push   # dispara ambos CI automáticamente según los archivos cambiados

# Ver URL del API después de terraform apply
cd infrastructure && terraform output api_url

# Si hay que limpiar DynamoDB desde la UI:
# Abrir https://tracker.cloudreviews.me → botón "🗑 Purgar BD y reiniciar"
```

---

## Estado actual (June 15, 2026)

- Plan redistribuido para empezar el 2026-06-15
- Lambda funcional: CORS correcto, strings vacíos filtrados, dedup por ID
- Frontend: chunks de 50, dedup por ID y por contenido
- Pendiente: hacer `git push` del commit `e209e7d` (cambio a Jun 15)
