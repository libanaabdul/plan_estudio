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
  - `__COGNITO_CLIENT_ID__` → secret `COGNITO_CLIENT_ID`
  - `__COGNITO_REGION__` → secret `COGNITO_REGION`
- El build **falla** si faltan los secrets de Cognito o si queda algún placeholder sin reemplazar
- `API_URL` **NO se inyecta**: está hardcodeada en `frontend/index.html` (es pública en el HTML servido; Cognito es lo que protege el API). Si se recrea el API Gateway, actualizar la constante con `terraform output api_url`
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

### Replan v5 (`replanCerts2026`)
- One-shot (flag `studyplan_replan_v5_jul2026` + detección por fechas de examen viejas: SAA 2026-12-20 o CCA 2027-03-15)
- Reagenda TODOS los ítems cert pendientes 1/día lun–sáb desde hoy, **empaquetados por fase** en orden aws → ai → terraform → cca → saa; SAA no arranca antes de 2027-01-11
- Cada examen se coloca 2 días después del último ítem de su fase (evitando domingos y las fechas de examen v4)
- `certPhase(d)` asigna los simulacros `repaso` a su cert por nombre (CCA/SAA/Terraform/AI, resto → aws)
- Al correr, setea también el flag de la migración v4 como done (queda obsoleta)
- Corre ANTES de `mergeEnglishEntries` para que el plan de inglés salte las fechas de examen nuevas

### Currículo v2 CP/AI/Terraform (`upgradeCertCurriculum`)
- Temario rediseñado: **64 sesiones diarias segmentadas** (CP 23, AI Pract 17, TF 24) — un solo tema por sesión de 30-45 min (nunca S3+VPC+EC2 juntos), semanas temáticas (`CP S1..S4`, `AI Pract S1..S3`, `TF S1..S4`), repaso semanal con mini-quiz, simulacros al cierre de cada cert
- Cada topics incluye: temario del día | por qué ese tema ahora | ▶ práctica concreta | ✅ criterio de logro
- Links: cursos existentes del usuario (Maarek CP/AI, Zeal Vora + KodeKloud TF, Neal Davis y TD practice) + docs oficiales (developer.hashicorp.com, docs.aws.amazon.com/bedrock, tutorialsdojo cheat sheets)
- One-shot cross-device (detecta por prefijo de week `'CP S'`): borra los ítems pendientes viejos de esas 3 certs con sus simulacros, inserta el temario nuevo desde INITIAL y llama `packCertPhases()` (extraído de replanCerts2026) para recalcular fechas y exámenes

### Reconciliador permanente (`reconcileCurriculum`)
- Corre en **cada carga**, sin flags: elimina cualquier ítem pendiente del temario viejo que "resucite" por el race last-write-wins entre pestañas/dispositivos (cert de aws/ai/terraform cuya week no empiece con `CP S`/`AI Pract S`/`TF S`, o english sin week `English S`)
- Si encontró algo, re-empaqueta las fases con `packCertPhases()` (restaura 1 cert/día y recalcula exámenes) — convergente: en cargas limpias no hace nada
- **Regla**: los ítems nuevos de cert DEBEN llevar week con esos prefijos o el reconciliador los borrará

### Limpieza de reinicio (`cleanupRestart`)
- Complementa el replan: NADA queda antes de `RESTART_CUTOFF` ('2026-07-13') — ni pendiente ni done (Libi no quiere ver ningún día anterior al reinicio; el historial viejo se elimina)
- done viejos y baby/descanso pendientes viejos → eliminados; certs pendientes viejos (huérfanos de dedup) → movidos a hoy; aieng pendiente → re-empaquetado 1/día desde hoy; inglés → regenerado desde EN_START si quedó con el arranque viejo y nada done
- Idempotente cross-device: corte fijo + detección por contenido

### Purga de zombis (en `loadData`, tras dedup)
- **Bug histórico**: `deduplicateData` ocultaba duplicados en pantalla pero NUNCA los borraba de DynamoDB → la tabla llegó a 1230 filas con ~596 reales (baby multiplicados ×5)
- Ahora los ids descartados por dedup se borran de la BD (`_deleteRows`, chunks de 25, sin await). Cinturones: tope 800 ids y dataset retenido >= 200

### Migración de fechas (`migrateDates2026`) — obsoleta tras el replan v5
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

### Plan de inglés A2→B1 (`ENGLISH_PLAN` + `buildEnglishEntries`)
- Curso estructurado de 24 semanas (6 módulos de 4: 3 contenido + 1 repaso/evaluación), lun–sáb desde **2026-07-13** (mismo día del reinicio del plan), 30–40 min/día
- Los ítems NO viven en INITIAL: se **generan** con `buildEnglishEntries()` desde `ENGLISH_PLAN` (24 semanas) × `EN_ROLES` (ciclo semanal fijo: Gramática → Vocab+Reading → Listening → Speaking → Writing → Repaso+test)
- Repaso espaciado automático: cada semana referencia el vocab de las semanas de contenido ≈ n-1 y n-3 (las de repaso se saltan)
- Salta domingos y fechas de examen (el ítem se omite, no se corre)
- `mergeEnglishEntries()` (en `loadData`) lo agrega una vez a datos existentes — detecta por prefijo de week `'English S'` — y elimina las "Clase de inglés" genéricas pendientes (las done quedan como historial)
- `cat='english'` NO está en `CERT_CATS`: es pista independiente, no entra en la redistribución de certs
- Aparece en Hoy/calendario/tabla/semanas como una actividad diaria más

### Vista AI Eng (`view-aieng`)
- Tab propio "🧠 AI Eng" en el nav — separado de la vista Hoy
- Los ítems `aieng` NO aparecen en Hoy/overdue/mañana/esta semana ni en `rescheduleOverdue`
- Muestra progress bar global + semanas colapsables con fecha de inicio por semana
- Usa la misma estructura grid 4 columnas de `.week-item` (checkbox | fecha | name | topics)
- `toggleDone` llama `renderAiEng()` cuando esa vista está activa

---

## Plan de certificaciones

**Replan del 13 de julio 2026**: 4 certs en 2026 (CP → AI Pract → Terraform → Claude Architect F.) y SAA desplazada a 2027. Las fechas de examen las calcula `replanCerts2026()` en runtime según el progreso real (cada examen cae 2 días después de terminar su fase de estudio). Fechas estimadas en el peor caso (0 progreso previo):

| Cert | Sesiones | Pista | Fecha estimada |
|------|----------|-------|-------------|
| AWS Cloud Practitioner | 23 | secuencial | ~10 Agosto 2026 |
| Terraform Associate | 24 | **paralela diaria desde 13-jul** | ~11 Agosto 2026 |
| AWS AI Practitioner | 17 | secuencial | ~2 Septiembre 2026 |
| Claude Certified Architect – Foundations (CCAR-F) | 22 | secuencial | ~1 Octubre 2026 |
| AWS SAA | 27 | secuencial | ~12 Febrero 2027 (estudio arranca 11 Ene) |
| AI Engineer | — | paralela | Q1 2027 |

**Terraform es pista paralela** (Libi lo usa a diario en el trabajo): 1 sesión TF/día junto a la sesión del track secuencial → 2 sesiones cert/día hasta ~8 de agosto, luego 1. Los exámenes CP (10 ago) y TF (11 ago) quedan seguidos — se pueden separar moviendo el examen a mano (persiste salvo que el reconciliador encuentre basura y re-empaquete).

Si hay ítems `done`, las fechas reales serán anteriores. El banner de fases del header se rellena dinámicamente (`renderPhases()`) desde los ítems `examen` en los datos — nunca editar fechas de fases en el HTML.

**Certificación Claude (actualizada julio 2026)**: el programa de Anthropic ahora tiene 4 exámenes (Associate-F $99, Developer-F $125, Architect-F $125, Architect-P $175), todos vía Pearson VUE (OnVUE) desde julio 2026, en inglés, 720/1000, validez 12 meses. El plan apunta a **CCAR-F**: 60 preguntas / 120 min, 5 dominios (Agentic 27%, Claude Code 20%, Prompts 20%, Tools/MCP 18%, Context 15%), 4 de 6 escenarios conocidos. Prep oficial gratis en Anthropic Academy (anthropic.skilljar.com) con practice exam. `refreshCcaInfo()` actualiza una vez los ítems CCA en la BD copiando topics/links desde INITIAL (detecta por 'Pearson' en el ítem BUFFER); el nombre `🏆 EXAMEN CCA Foundations` NO se renombra (lo referencia `NEW_EXAM` en la migración).

**Regla de días cert**: 1 cert/día lunes-sábado desde 2026-06-15.
**AI Eng es independiente**: 1 aieng/día desde 2026-07-01, en su propia vista. No se mezcla con la vista Hoy.
**Inglés es independiente**: 1 english/día (30–40 min) lunes-sábado desde 2026-07-20, 24 semanas A2→B1, generado por `buildEnglishEntries()`. Sí aparece en la vista Hoy.

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

### Vista Semanas agrupada por etiqueta de texto (desorganizada tras el replan)
- **Causa**: `renderWeekly` agrupaba por el string `item.week` — tras el replan convivían etiquetas viejas ("Semana 1", "Semana 12 CCA") con nuevas ("CP S1", "English S03") y el orden salía del orden de los datos
- **Fix**: agrupa por semana **calendario** (lunes–domingo) derivada de `item.date` con `weekStartOf()`, numerada desde el reinicio (Semana 1 = 2026-07-13), orden cronológico, solo la semana actual abierta. La etiqueta `item.week` se muestra como tag de contexto solo si tiene formato nuevo (se ocultan las `/^Semana /` viejas)

### week-item grid roto en vistas nuevas
- **Causa**: `.week-item` usa `grid-template-columns: 26px 82px auto 1fr` (4 cols). Si una vista nueva usa flex o distinto número de hijos, queda visualmente roto.
- **Fix**: siempre usar exactamente 4 hijos: `checkbox-cell | week-item-date | div(name) | week-item-topics`. Ver `renderAiEng` como referencia.

---

## Variables de entorno / Secrets en GitHub

| Secret | Dónde se usa |
|--------|-------------|
| `API_URL` | **Ya no se usa** — la URL está hardcodeada en `frontend/index.html` (se puede borrar el secret) |
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

## Estado actual (July 13, 2026)

- Plan cert activo desde 2026-06-15 (Libi estudia Terraform + AWS Cloud Practitioner)
- AI Engineer separado en su propia vista; migración automática redistribuye a 2026-07-01+
- Lambda funcional: CORS correcto, strings vacíos filtrados, dedup por ID
- Frontend: chunks de 50, dedup por ID y por contenido
- DynamoDB con PITR (35 días) + deletion protection + `prevent_destroy` en Terraform
- Fechas: TODO en hora local del navegador — usar `fmtLocalDate`/`parseLocalDate`, nunca `toISOString()` ni `new Date('YYYY-MM-DD')`
- Calendario: límites de navegación dinámicos (`calBounds()` deriva min/max de los datos)
- Eliminados `index.html` y `CNAME` de la raíz (copias obsoletas; lo real vive en `frontend/`)
- Plan de inglés A2→B1 integrado: 142 actividades generadas (24 semanas desde 2026-07-20); las "Clase de inglés" genéricas fueron reemplazadas
- Replan v5 (13 Jul 2026): 4 certs en 2026 + SAA en Feb 2027; fechas de examen dinámicas según progreso; banner de fases dinámico (`renderPhases`)
