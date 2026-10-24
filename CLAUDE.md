# Plan de Estudio — Contexto para Claude Code

Este archivo es la fuente de verdad del proyecto para sesiones nuevas.

---

## Qué es este proyecto

Tracker personal de plan de estudio de certificaciones AWS + AI Engineer + inglés.
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
│   ├── index.html          ← toda la app (UI + lógica + datos INITIAL)
│   └── study-guide.js      ← GENERADO: guía detallada por sesión (window.STUDY_GUIDE)
├── backend/
│   └── lambda/
│       ├── handler.py      ← Lambda handler
│       └── requirements.txt
├── infrastructure/
│   ├── main.tf             ← DynamoDB, Lambda, API GW, Cognito
│   ├── variables.tf        ← project_name="plan-estudio", table_name="study-plan-items"
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── tools/study-plan/        ← fuente del temario y de las guías (Python, no se despliega)
│   ├── curriculum.py       ← temario → líneas de INITIAL (--apply las escribe en index.html)
│   ├── guide_{cp,tf,aif,cca,saa}.py ← guías de estudio por sesión
│   └── build_guide.py      ← guide_*.py → frontend/study-guide.js (valida cobertura 1:1)
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
- `INITIAL` — array hardcodeado: 156 ítems cert del plan vigente (`plan:PLAN_VERSION` = `'v4'`, `seq` = orden dentro del plan, `links:[{label,url}]`) + 138 aieng. Las fechas de INITIAL son placeholders: las calcula `replanAll()`
- `data` — variable global en memoria, sincronizada con DynamoDB
- `localStorage('studyplan_backup')` — cache local, solo fallback offline

### Carga de datos (`loadData`)
```
getAll (DynamoDB)
  → deduplicateData()      — dedup por content-key (no por id) + purga de zombis
  → purga de filas 'baby'  — siempre
  → mergeAIEngEntries()    — agrega AI Eng desde INITIAL si faltan
  → upgradeToPlan()        — one-shot por contenido (no hay ningún ítem con plan === PLAN_VERSION)
  → mergeEnglishEntries()  — genera el inglés si no hay week 'English S'
  → reconcileCurriculum()  — siempre: mata planes viejos resucitados y todo lo anterior a PLAN_START
  → saveData() si el dedup cambió algo y el upgrade no guardó
```
Las migraciones de julio (`migrateDates2026`, `replanCerts2026`, `upgradeCertCurriculum`, `refreshCcaInfo`, `cleanupRestart`) se **eliminaron** el 24-oct-2026: Libi nunca usó esos planes y `upgradeToPlan` reemplaza todo lo pendiente. Ojo: los flags viejos de localStorage `studyplan_mig_v4_july2026` / `studyplan_replan_v5_jul2026` no tienen relación con `PLAN_VERSION`.

### Guardado
- `saveData()` — saveAll en chunks de 50 ítems. Solo para resets/migraciones bulk.
- `saveRow(item)` — saveRow individual. Usado para marcar done, notas, etc.
- `deleteRow(id)` — deleteRow individual.

### Planificador (`replanAll` → `packCertPhases` + inglés + AI Eng)
- **Nada antes de `PLAN_START` ('2026-11-01', domingo → primera sesión lun 2-nov)**: ni ítems (el reconciliador borra cualquier cosa con fecha anterior, done o hecha a mano), ni meses en el calendario (`currentMonth` y `calBounds()` tienen piso en el mes de inicio), ni semanas (Semana 1 = la del primer día de estudio). Antes del inicio, Hoy muestra qué preparar
- **Orden de facilidad, la más fácil junto a Terraform** (`PHASE_GROUPS`): `[aws, terraform]` en paralelo → `ai` → `cca` → `saa`. Dentro de un grupo cada pista lleva 1 sesión/día; el grupo siguiente arranca el lunes posterior al último examen del grupo
- Cada pista = semanas completas lun–sáb: L–V sesión de 40–60 min, **sábado sesión larga** (lab / repaso / simulacro). El examen cae el día de estudio siguiente a la última sesión de su pista, nunca en la misma fecha que otro examen (`used`)
- El CP está diseñado en 5 semanas para convivir con TF (3): el sábado del examen TF el ítem de CP es un repaso de 30 min. Si se cambia el temario de cualquiera de los dos, revisar que esa coincidencia se mantenga
- Domingos y `HOLIDAYS` = descanso. `HOLIDAYS` son jue–sáb de Navidad y Año Nuevo: 6 días = 1 semana exacta, para que los sábados largos sigan en sábado. Al agregar feriados, hacerlo en bloques que no rompan la semana
- Inglés: 1 sesión/día lun–sáb en paralelo, salta días de examen. AI Eng: **en pausa** hasta el lunes posterior al último examen
- Orden dentro de una pista: `byDateSeq` (fecha, luego `seq`, luego id). Si hoy ya hay una sesión done de esa pista, arranca mañana (`trackStart`)
- Lo creado a mano en el modal lleva `plan:'user'`: el planificador NO lo mueve y el reconciliador NO lo borra (salvo que sea anterior a PLAN_START)
- Un examen `done` = cert aprobada: su pista deja de consumir calendario
- Botón "📅 Recalcular plan" (Hoy y banner de atrasadas) → `rescheduleOverdue()` → `replanAll()`: re-empaqueta todo lo pendiente desde hoy conservando el orden, nunca amontona atrasadas en un día. Si Libi se atrasa, los exámenes pueden caer entre semana
- `certPhase(d)` asigna los simulacros `repaso` a su cert por nombre (CCA/SAA/Terraform/AI, resto → aws): los nombres de simulacro DEBEN contener CP / "AI Practitioner" / Terraform / CCA / SAA
- Exámenes se encuentran por `EXAM_RE` sobre el nombre — no renombrar `🏆 EXAMEN CCA Foundations` ni quitar "Cloud Practitioner" / "AI Practitioner" / "Terraform" / "Solutions Architect"

### Upgrade de plan (`upgradeToPlan`)
- One-shot cross-device: corre si ningún ítem tiene `plan === PLAN_VERSION`. Para publicar un temario nuevo: subir `PLAN_VERSION` y regenerar las líneas de INITIAL con ese valor
- Borra todo lo pendiente de cert/repaso/examen/descanso (+ inglés si no hay inglés done), inserta el temario vigente desde INITIAL (salvo certs con examen done) y regenera el inglés; luego `replanAll()` + `saveData()`
- Autocurativo: si una pestaña con código viejo reescribe filas sin el campo `plan`, la próxima carga no ve la versión y re-ejecuta el upgrade

### Reconciliador permanente (`reconcileCurriculum`)
- Corre en **cada carga**, sin flags: borra todo ítem con fecha < `PLAN_START`; todo ítem pendiente cert/repaso/examen/descanso con `plan` distinto de `PLAN_VERSION` y `'user'`; y el inglés sin week `English S`
- Si encontró algo, `replanAll()` + `saveData()` — convergente: en cargas limpias no hace nada
- **Regla**: todo ítem cert nuevo en INITIAL DEBE llevar `plan:PLAN_VERSION` y `seq`, o el reconciliador lo borrará

### Purga de zombis (en `loadData`, tras dedup)
- **Bug histórico**: `deduplicateData` ocultaba duplicados en pantalla pero NUNCA los borraba de DynamoDB → la tabla llegó a 1230 filas con ~596 reales
- Ahora los ids descartados por dedup se borran de la BD (`_deleteRows`, chunks de 25, sin await). Cinturones: tope 800 ids y dataset retenido >= 200

### Sin actividades de bebé (eliminadas 24-oct-2026)
- La categoría `baby` ya no existe: ni en INITIAL, ni generador diario, ni filtro, ni opción en el modal, ni plantillas, ni CSS
- `loadData` borra en cada carga cualquier fila `cat==='baby'` que quede en DynamoDB (permanente, sin flag: también mata las que resuciten desde otra pestaña). Es el único sitio donde aparece `'baby'` en el código — no reintroducir

### Dedup (`deduplicateData`)
- Clave: `cat|week|topics(40ch)|name(30ch)`
- Gana el ítem con mayor score: done(+10) + notes(+3) + realDur(+2)

### Reset de emergencia (`purgeAndReset`)
- Botón "🗑 Purgar BD y reiniciar" en la UI (header, semitransparente)
- Llama `deleteAll` → limpia DynamoDB → reinicializa desde INITIAL → saveData

### Multi-select
- Botón "Seleccionar" en la vista diaria para seleccionar actividades y moverlas a otra fecha

### Plan de inglés A2→B1 (`ENGLISH_PLAN` + `buildEnglishEntries`)
- Curso estructurado de 24 semanas (6 módulos de 4: 3 contenido + 1 repaso/evaluación), lun–sáb desde `EN_START = PLAN_START` (primera sesión 2026-11-02), **20–30 min/día** (cabe junto a la sesión cert)
- Los ítems NO viven en INITIAL: se **generan** con `buildEnglishEntries()` desde `ENGLISH_PLAN` (24 semanas) × `EN_ROLES` (ciclo semanal fijo: Gramática → Vocab+Reading → Listening → Speaking → Writing → Repaso+test)
- Repaso espaciado automático: cada semana referencia el vocab de las semanas de contenido ≈ n-1 y n-3 (las de repaso se saltan)
- `buildEnglishEntries()` genera los 144 ítems con fechas provisionales; `replanAll()` los corre para saltar domingos, feriados y días de examen (ningún ítem se pierde)
- La semana 6 es "Inglés de examen": superlativos y keywords de las preguntas AWS/TF (most cost-effective, least operational overhead…)
- `mergeEnglishEntries()` (en `loadData`) lo agrega una vez a datos existentes — detecta por prefijo de week `'English S'` — y elimina las "Clase de inglés" genéricas pendientes (las done quedan como historial)
- `cat='english'` NO está en `CERT_TRACK`: es pista independiente con su propio empaquetado
- Aparece en Hoy/calendario/tabla/semanas como una actividad diaria más

### Guías de estudio detalladas (`study-guide.js` + visor 📖)
- Cada una de las 156 sesiones cert tiene una guía: **Qué estudiar** (conceptos con datos concretos), **Lo que más pregunta el examen**, **Trampas**, **Práctica** paso a paso y **Autoevaluación** (preguntas con respuesta desplegable). Simulacros, repasos y exámenes traen el método (cómo hacerlo y cómo analizar)
- Clave = **nombre exacto del ítem**. Si se renombra una sesión, hay que renombrar su guía (build_guide.py falla si no coinciden)
- El contenido NO va a DynamoDB: es estático en `frontend/study-guide.js` (se carga con `<script src>` antes del script principal). Si no carga, la app funciona igual sin botones 📖
- UI: botón 📖 en Hoy / mañana / esta semana / tabla, link "📖 Guía de estudio" en Semanas, botón en el modal de edición; en el calendario un clic abre la guía si existe (`openItem`). Visor `#guide-overlay` → `openGuide(id)` con links, "Editar" y "Marcar como hecha"
- `renderGuide()` = mini-markdown propio (## · - · 1. · > · `? pregunta :: respuesta` · bloques ``` · `código` · **negrita**), escapa HTML. Ligaduras de fuente desactivadas en código (`~>` y `>=` deben verse literales)
- **Para editar una guía**: cambiar `tools/study-plan/guide_*.py` → `python3 tools/study-plan/build_guide.py` → commit de ambos. Nunca editar `study-guide.js` a mano
- **Para editar el temario**: `tools/study-plan/curriculum.py` → `--apply`; si el cambio es incompatible con lo guardado en DynamoDB, subir `PLAN_VERSION` (en index.html y curriculum.py) para que `upgradeToPlan` lo reemplace

### Vista AI Eng (`view-aieng`)
- Tab propio "🧠 AI Eng" en el nav — separado de la vista Hoy
- En pausa durante las certs: `replanAll()` los agenda desde el lunes posterior al último examen
- Muestra progress bar global + semanas colapsables con fecha de inicio por semana
- Usa la misma estructura grid 4 columnas de `.week-item` (checkbox | fecha | name | topics)
- `toggleDone` llama `renderAiEng()` cuando esa vista está activa

---

## Plan de certificaciones

**Plan v4 (24 de octubre 2026)**: certificarse pasó a ser **obligatorio**; Libi nunca había usado los planes anteriores (0 progreso). Pedidos explícitos de Libi: **todo empieza el 1 de noviembre** (no quiere ver nada del calendario antes) y las certs van **por orden de facilidad, con la más fácil junto a Terraform**. Fechas calculadas por `replanAll()` con 0 progreso:

| Grupo | Cert | Versión | Semanas | Sesiones | Examen estimado |
|---|------|---------|---------|----------|-----------------|
| 1 | AWS Cloud Practitioner (la más fácil) | CLF-C02 | 5 | 29 | sáb 5 dic 2026 |
| 1 | Terraform Associate (en paralelo) | **004** (TF 1.12) | 3 | 17 | sáb 21 nov 2026 |
| 2 | AWS AI Practitioner | AIF-C01 | 4 (+1 de fiestas) | 23 | sáb 9 ene 2027 |
| 3 | Claude Certified Architect – Foundations | CCAR-F | 4 | 23 | sáb 6 feb 2027 |
| 4 | AWS Solutions Architect Associate | SAA-C03 | 10 | 59 | sáb 17 abr 2027 |
| — | Inglés A2→B1 | — | 24 | 144 | termina ~30 abr 2027 |
| — | AI Engineer | — | en pausa | 138 | desde 19 abr 2027 |

**Carga**: semanas 1–3 (CP + TF en paralelo) son las más pesadas: L–V ~1 h 50 (CP 45–50 + TF 40–45 + inglés 20–30), sábados hasta ~3 h 15. Desde la semana 4: L–V ~75–90 min, sábado 2–3 h, domingo libre.

**Facilidad**: CP (fundamentos, 700/1000) < AI Practitioner (fundamentos + ML) < Claude Architect F. (escenarios, 720, poco material externo) < SAA (associate, temario enorme). Terraform (associate) va con la primera porque Libi lo usa a diario. CP → AIF encadenan (vocabulario AWS + voucher de 50% de AWS al aprobar).

**Datos de examen verificados (oct 2026)**: Terraform Associate 004 (desde ene 2026; 8 objetivos, nuevos: custom conditions, ephemeral/write-only, HCP projects; ~57 preguntas / 60 min, solo inglés). AWS: CLF-C02 y AIF-C01 90 min / 65 preguntas, SAA-C03 130 min; **ESL +30 min** para no nativos que rinden en inglés (se pide una vez en la cuenta de AWS Certification, antes de agendar). CCAR-F: 60 preguntas de escenario / 120 min, 720/1000, US$125, Pearson VUE, solo inglés, 5 dominios (Agentic 27%, Claude Code 20%, Prompts 20%, Tools/MCP 18%, Context 15%), 4 de 6 escenarios; prep oficial gratis en Anthropic Academy. Docs de Claude ahora en `platform.claude.com/docs` y `code.claude.com/docs`.

**Formato de cada ítem cert**: `tema | por qué ahora | ▶ práctica | ✅ criterio de logro` + links con label (cursos que Libi ya tiene: Maarek CP/AIF/SAA, Zeal Vora TF, Neal Davis, Tutorials Dojo, Krausen; + docs oficiales). Cada primera sesión de fase incluye "reserva el examen". Las sesiones usan los labs sobre este mismo repo (main.tf, Cognito, DynamoDB) como material práctico.

El banner de fases (`renderPhases()`) se rellena desde los ítems `examen` — nunca editar fechas en el HTML.

---

## Categorías y colores

| cat | Label | Color |
|-----|-------|-------|
| `aws` | ☁️ AWS (CP) | ámbar `#f59e0b` |
| `ai` | 🤖 AI Pract. | naranja `#fb923c` |
| `aieng` | 🧠 AI Eng | verde (`#4ade80`) |
| `terraform` | 🟣 Terraform | índigo `#818cf8` |
| `cca` | ✨ CCA | violeta `#a78bfa` |
| `saa` | 🏗️ SAA | cian `#22d3ee` |
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

### saveAll timeout (10s Lambda)
- **Fix 1**: timeout subido a 29s en Terraform
- **Fix 2**: frontend divide en chunks de 50 ítems por request

### Vista Semanas agrupada por etiqueta de texto (desorganizada tras el replan)
- **Causa**: `renderWeekly` agrupaba por el string `item.week` — tras el replan convivían etiquetas viejas ("Semana 1", "Semana 12 CCA") con nuevas ("CP S1", "English S03") y el orden salía del orden de los datos
- **Fix**: agrupa por semana **calendario** (lunes–domingo) derivada de `item.date` con `weekStartOf()`, numerada desde el primer día de estudio (Semana 1 = la del 2026-11-02), orden cronológico, solo la semana actual abierta. La etiqueta `item.week` se muestra como tag de contexto solo si tiene formato nuevo (se ocultan las `/^Semana /` viejas)

### week-item grid roto en vistas nuevas
- **Causa**: `.week-item` usa `grid-template-columns: 26px 82px auto 1fr` (4 cols). Si una vista nueva usa flex o distinto número de hijos, queda visualmente roto.
- **Fix**: siempre usar exactamente 4 hijos: `checkbox-cell | week-item-date | div(name) | week-item-topics`. Ver `renderAiEng` como referencia.

---

## Variables de entorno / Secrets en GitHub

| Secret | Dónde se usa |
|--------|-------------|
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

## Estado actual (24 de octubre 2026)

- **Plan v4** listo para arrancar el lunes 2026-11-02 (nada antes del 1-nov): CP + TF en paralelo → AI → CCA → SAA + inglés diario; AI Engineer en pausa. Certificarse es obligatorio para Libi
- Al primer load con el código nuevo, `upgradeToPlan` reemplaza en DynamoDB todo el plan viejo pendiente (~500 deletes + saveAll; tarda unos segundos)
- Actividades de bebé eliminadas de todo el proyecto (purga permanente en `loadData`)
- Lambda funcional: CORS correcto, strings vacíos filtrados, dedup por ID
- DynamoDB con PITR (35 días) + deletion protection + `prevent_destroy` en Terraform
- Fechas: TODO en hora local del navegador — usar `fmtLocalDate`/`parseLocalDate`, nunca `toISOString()` ni `new Date('YYYY-MM-DD')`
- Calendario: límites de navegación dinámicos (`calBounds()` deriva min/max de los datos)
