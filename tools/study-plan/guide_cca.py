# Guías detalladas — Claude Certified Architect – Foundations (CCAR-F)
G = {}

G['CCA: Mapa del examen y primera llamada a la API'] = """
## Qué estudiar
- **El examen**: 60 preguntas de escenario, 120 min, aprobado 720/1000, solo en inglés, Pearson VUE. **5 dominios**: Agentic Architecture & Orchestration 27% · Claude Code Configuration & Workflows 20% · Prompt Engineering & Structured Output 20% · Tool Design & MCP Integration 18% · Context Management & Reliability 15%. Trae **4 de 6 escenarios** conocidos (los ves en la semana 4).
- **Messages API** (`POST /v1/messages`)
  - Obligatorios: `model`, `max_tokens`, `messages` (lista alterna de `user` y `assistant`).
  - `system` es un **parámetro de nivel superior**, no un rol dentro de messages.
  - Opcionales: `temperature`, `stop_sequences`, `tools`, `tool_choice`, `stream`, `thinking`.
  - Headers: `x-api-key`, `anthropic-version`.
- **La respuesta**: `content` es una lista de bloques (`text`, `tool_use`, `thinking`); `usage` trae `input_tokens`, `output_tokens` y, con caching, `cache_creation_input_tokens` y `cache_read_input_tokens`.
- **`stop_reason`**: `end_turn` (terminó naturalmente), `max_tokens` (se cortó: sube el límite o continúa), `stop_sequence` (encontró una secuencia de parada), `tool_use` (quiere ejecutar una herramienta), `pause_turn` y `refusal`.
- **La API no tiene estado**: cada request lleva **toda la conversación**.

## Práctica
1. Inscríbete en Anthropic Academy y descarga el exam guide oficial; reserva el examen en Pearson VUE.
2. `pip install anthropic` y haz un request con system prompt. Imprime `stop_reason` y `usage`.
3. Pon `max_tokens=20` y confirma que `stop_reason` es `max_tokens`.

## Autoevaluación
? ¿Dónde va el system prompt? :: En el parámetro `system`, no como mensaje.
? La respuesta sale cortada a la mitad. ¿Qué stop_reason esperas? :: `max_tokens`.
? ¿La API recuerda los mensajes anteriores? :: No; hay que reenviar el historial.
"""

G['CCA: Prompt engineering de producción'] = """
## Qué estudiar (dominio 4: 20%)
- **Sé claro y directo**: di qué quieres, para quién y en qué formato. Explica el **porqué** de una regla (el modelo generaliza mejor si entiende la motivación).
- **Contexto explícito**: audiencia, objetivo, restricciones, qué es un buen resultado.
- **Ejemplos (multishot)**: 3–5 ejemplos variados dentro de `<example>`; muestran el formato mejor que una descripción.
- **Etiquetas XML** para separar instrucciones, documentos y datos: `<instructions>`, `<document>`, `<data>`. Reducen la confusión y facilitan parsear la salida.
- **Rol en el system prompt** ("Eres un analista financiero senior…").
- **Pensar antes de responder**: pide razonamiento paso a paso o usa **extended thinking** (parámetro `thinking` con `budget_tokens`) en tareas complejas.
- **Documentos largos**: ponlos **al principio** y la pregunta al **final**; pide primero citas textuales relevantes y luego la respuesta.
- **Prompt chaining**: dividir una tarea compleja en varios prompts encadenados (cada uno con su salida validada).
- **System prompts de producción**: identidad, alcance, reglas, formato, manejo de casos fuera de alcance, tono.

## Lo que más pregunta el examen
- Escenarios donde la salida es inconsistente → agregar ejemplos, XML tags o formato explícito.
- Tarea compleja con errores → dividir en una cadena de prompts o dar espacio para razonar.

## Práctica
- Toma un prompt vago de tu trabajo ("resume este incidente") y reescríbelo con rol, contexto, XML tags, 2 ejemplos y formato de salida. Compara 3 salidas antes y después.

## Autoevaluación
? ¿Dónde colocar un documento de 50 páginas respecto a la pregunta? :: El documento al principio y la pregunta al final.
? ¿Para qué sirven las etiquetas XML? :: Para separar partes del prompt y estructurar la salida.
"""

G['CCA: Salida estructurada y validación'] = """
## Qué estudiar
- **Opciones para obtener JSON confiable**
  1. **Structured outputs**: le das un JSON schema y la API restringe la salida para que lo cumpla.
  2. **Tool use forzado**: defines una tool cuyo `input_schema` es el formato deseado y pones `tool_choice: {"type": "tool", "name": "..."}`; el `input` del bloque tool_use es tu JSON.
  3. Instrucciones + ejemplos + validación (lo más frágil).
- **Siempre valida** (jsonschema, Pydantic). Si falla: **reintenta** enviando el error de validación al modelo ("el campo `fecha` debe ser ISO 8601"). Limita el número de reintentos.
- **Evitar campos inventados**: permite valores nulos o "desconocido" de forma explícita; pide que no infiera lo que no está en el texto.
- **Enums** para valores cerrados; `required` solo para lo que siempre existe.
- **Validación semántica** además de la sintáctica (p. ej. que el total sea la suma de las líneas).

## Lo que más pregunta el examen
- Un pipeline de extracción falla a veces con JSON inválido → structured outputs o tool forzada + validación con reintento.
- El modelo inventa datos faltantes → permitir null o "desconocido" e instruir que no infiera.

## Práctica
1. Schema con 5 campos (nombre, email, empresa, fecha ISO, intención: enum).
2. 10 emails de prueba, algunos sin todos los datos.
3. Extrae con tool forzada, valida y reintenta con el error. Mide cuántos pasan al primer intento.

## Autoevaluación
? ¿Cómo fuerzas a Claude a responder con una tool específica? :: `tool_choice: {"type": "tool", "name": "nombre"}`.
? Falla la validación. ¿Qué haces? :: Reintentar enviando el error concreto, con un límite de intentos.
"""

G['CCA: Tool use — el ciclo completo'] = """
## Qué estudiar (dominio 2: 18%)
- **Definir una tool**: `name`, `description` (lo más importante: cuándo y cómo usarla) e `input_schema` (JSON Schema).
- **El ciclo**
  1. Envías `tools` + mensaje.
  2. Claude responde con `stop_reason: "tool_use"` y uno o más bloques `tool_use` (`id`, `name`, `input`).
  3. **Tú** ejecutas la tool.
  4. Envías un mensaje `user` con bloques `tool_result` (`tool_use_id`, `content`, y `is_error: true` si falló).
  5. Repites hasta `end_turn`.
- **tool_choice**: `auto` (por defecto: decide si usar tools), `any` (debe usar alguna), `tool` (una específica), `none` (ninguna). `disable_parallel_tool_use` para una sola por turno.
- **Tools en paralelo**: Claude puede pedir varias en un turno; devuelve **todos** los resultados en el **mismo** mensaje user.
- **Errores**: devuelve `is_error: true` con un mensaje útil para que Claude se corrija o pruebe otra estrategia; no rompas el loop.
- **Client tools** (las ejecutas tú) vs **server tools** (las ejecuta Anthropic: web search, code execution).

## Lo que más pregunta el examen
- Qué va en cada mensaje del ciclo; cómo reportar un error; cuándo usar cada tool_choice.

## Práctica
- Implementa 2 tools (`get_weather` falso y `calculator`). Haz que una falle a propósito y devuelve `is_error`. Verifica que Claude se recupere.

## Autoevaluación
? ¿En qué rol van los tool_result? :: En un mensaje `user`.
? Claude pidió 3 tools en paralelo. ¿Cuántos mensajes devuelves? :: Uno solo, con los 3 tool_result.
? ¿Qué tool_choice garantiza que use alguna herramienta? :: `any`.
"""

G['CCA: Diseño de tools para agentes'] = """
## Qué estudiar (guía "Writing effective tools for agents")
- **Elegir bien las tools**: pocas y de alto nivel según los flujos reales. Mejor `schedule_event` (busca disponibilidad y agenda) que `list_users` + `list_events` + `create_event`.
- **Namespacing**: prefijos por servicio o recurso (`jira_search`, `jira_create_issue`) para que el modelo elija bien entre muchas tools.
- **Devolver contexto útil**: nombres legibles en vez de UUIDs, solo los campos relevantes. Opción `response_format` concise/detailed.
- **Eficiencia de tokens**: paginación, filtros, truncado con valores por defecto razonables; avisar cuando se truncó.
- **Errores accionables**: "falta el parámetro `project_id`; usa `jira_list_projects` para obtenerlo" en vez de un stack trace.
- **Descripciones como para un empleado nuevo**: qué hace, cuándo usarla, formato de cada parámetro, ejemplos, límites.
- **Evaluar las tools**: con tareas realistas, midiendo éxito, número de llamadas, tokens y errores; iterar las descripciones.
- **Poka-yoke**: diseñar parámetros para que sea difícil usarlas mal (p. ej. rutas absolutas en vez de relativas).

## Práctica
- Reescribe las descripciones de tus 2 tools de ayer siguiendo esta guía y agrega un mensaje de error accionable.

## Autoevaluación
? Tienes 40 tools y Claude se confunde. ¿Qué haces? :: Consolidar en menos tools de alto nivel, namespacing y mejores descripciones.
? ¿Qué devuelves: el ID interno o el nombre del cliente? :: El nombre legible (y el ID solo si hace falta para otra llamada).
"""

G['CCA: Lab — extractor de datos estructurados'] = """
## Escenario oficial: Structured Data Extraction (120 min)
- **Arquitectura**
  1. Documento (texto o PDF) → prompt con instrucciones + schema.
  2. Extracción con structured outputs o tool forzada.
  3. Validación sintáctica (schema) y semántica (reglas de negocio).
  4. Reintento con el error (máximo 2).
  5. Campos sin evidencia → null + flag de revisión.
  6. Confianza baja o validación fallida → **cola de revisión humana**.
  7. Métricas: % válidos al primer intento, % tras reintento, % a humano.
- **Decisiones que el examen evalúa**: forzar el formato con la API en vez de solo pedirlo; no dejar que invente campos; humano en el loop para casos dudosos; Batches API si el volumen es grande y no urgente.

## Práctica
- Construye el pipeline con 20 documentos de prueba (facturas o emails). Anota en Notas las tres métricas.

## Autoevaluación
? 50.000 documentos para procesar esta semana, sin urgencia. :: Message Batches API (más barata, asíncrona).
? El documento no trae la fecha. :: El campo queda null y se marca para revisión; no se infiere.
"""

G['CCA: MCP — arquitectura y primitivos'] = """
## Qué estudiar
- **MCP (Model Context Protocol)**: estándar abierto para conectar aplicaciones de IA con herramientas y datos. Basado en **JSON-RPC 2.0**.
- **Participantes**
  - **Host**: la app de IA (Claude Code, Claude Desktop, un IDE).
  - **Client**: componente dentro del host que mantiene **una conexión 1:1** con un server.
  - **Server**: programa que expone capacidades.
- **Primitivos del server**
  - **Tools**: funciones que el **modelo** decide invocar (acciones).
  - **Resources**: datos de contexto (archivos, registros) identificados por URI; los controla la **aplicación**.
  - **Prompts**: plantillas reutilizables que elige el **usuario** (p. ej. slash commands).
- **Primitivos del client**: sampling (el server pide una generación al modelo del host), elicitation (pedir datos al usuario), roots.
- **Transports**: **stdio** (proceso local, el host lo lanza) y **Streamable HTTP** (servers remotos; reemplazó a HTTP+SSE). Autenticación OAuth para remotos.
- **Ciclo de vida**: initialize → negociación de capacidades → operación → cierre.
- **MCP vs tool use directo**: MCP cuando quieres reutilizar integraciones en varios hosts o usar servers de terceros; tool use directo para una app propia con pocas tools.

## Práctica
- Dibuja Claude Code (host) con 2 clients conectados a un server local (stdio, filesystem) y otro remoto (HTTP, GitHub). Marca qué primitivos expone cada uno.

## Autoevaluación
? ¿Quién controla cuándo se usa una tool? :: El modelo.
? ¿Y un prompt de MCP? :: El usuario.
? ¿Qué transport usarías para un server remoto? :: Streamable HTTP.
"""

G['CCA: Construye y conecta un MCP server'] = """
## Qué estudiar
- **Server con el SDK de Python** (FastMCP): decoradores `@mcp.tool()`, `@mcp.resource("uri://...")`, `@mcp.prompt()`; los type hints y docstrings generan el schema y la descripción.
- **Manejo de errores**: devuelve errores de tool claros (como en tool use) en vez de tumbar el server; valida entradas.
- **Conectar a Claude Code**
  - `claude mcp add mi-server -- python server.py` (stdio).
  - `claude mcp add --transport http github https://...` (remoto).
  - **Scopes**: `local` (por defecto, solo tú en este proyecto), `project` (se guarda en `.mcp.json` en el repo, compartido con el equipo), `user` (todos tus proyectos).
  - `/mcp` dentro de Claude Code para ver estado y autenticar.
- **Seguridad**: solo servers de confianza; un server puede exponer datos o ser vector de **prompt injection**; mínimo privilegio en las credenciales del server.
- **Debug**: MCP Inspector.

## Práctica
1. Server con 2 tools (p. ej. `list_tasks` y `add_task` sobre un JSON local) y 1 resource.
2. `claude mcp add` con scope project → revisa el `.mcp.json` generado.
3. Pídele a Claude Code una tarea que use las tools.

## Autoevaluación
? ¿Qué scope compartes con el equipo vía git? :: `project` (`.mcp.json`).
? ¿Qué comando lista y gestiona los servers dentro de Claude Code? :: `/mcp`.
"""

G['CCA: Workflows vs agentes'] = """
## Qué estudiar (dominio 1: 27%, el más grande; "Building effective agents")
- **Workflows**: los LLM y las tools siguen **caminos predefinidos en código**. **Agentes**: el LLM **decide dinámicamente** sus pasos y las tools que usa.
- **Empieza simple**: un solo llamado bien diseñado con retrieval y ejemplos suele bastar; agrega complejidad solo si mejora resultados medibles. Los agentes cuestan más (latencia y tokens).
- **Bloque base**: el **augmented LLM** (LLM + retrieval + tools + memoria).
- **Patrones de workflow**
  - **Prompt chaining**: pasos secuenciales con **gates** de validación (generar un outline → validarlo → escribir).
  - **Routing**: clasificar la entrada y mandarla a un prompt o modelo especializado (consultas simples a un modelo barato).
  - **Parallelization**: **sectioning** (subtareas independientes en paralelo) o **voting** (varias ejecuciones y se combinan).
  - **Orchestrator-workers**: un LLM divide dinámicamente la tarea y delega en workers (las subtareas no se conocen de antemano).
  - **Evaluator-optimizer**: un LLM genera y otro evalúa e itera con feedback.
- **Agentes**: para problemas abiertos con número de pasos impredecible; necesitan tools bien documentadas (**ACI**: agent-computer interface), condiciones de parada y guardrails; probar en sandbox.

## Lo que más pregunta el examen
- Elegir el patrón correcto para un escenario. Elegir un workflow antes que un agente cuando los pasos se conocen.

## Práctica
- Para 3 problemas de tu trabajo (p. ej. clasificar tickets, generar un post-mortem, revisar PRs) elige el patrón y justifica.

## Autoevaluación
? Clasificar consultas y mandar las fáciles a Haiku y las difíciles a Opus. :: Routing.
? Traducción que un segundo LLM revisa y devuelve con correcciones. :: Evaluator-optimizer.
"""

G['CCA: El loop agéntico y el Claude Agent SDK'] = """
## Qué estudiar
- **Loop agéntico**: mientras `stop_reason == "tool_use"` → ejecutar tools → agregar resultados → volver a llamar. Termina en `end_turn` o por un **límite** (máximo de turnos, presupuesto de tokens o tiempo).
- **Claude Agent SDK** (Python y TypeScript): el mismo harness de Claude Code como librería. Trae tools integradas (leer y editar archivos, bash, búsqueda), gestión de contexto y compactación, permisos, hooks, subagentes y MCP.
  - Opciones típicas: `system_prompt`, `allowed_tools`, `permission_mode`, `max_turns`, `mcp_servers`, `hooks`, definición de subagentes, `cwd`.
- **Controles programáticos vs instrucciones**: el prompt es probabilístico; los **hooks** y permisos son **deterministas**. Para reglas que no pueden fallar (no borrar producción, no exponer secretos) usa un hook `PreToolUse` que bloquee, no solo una instrucción en el prompt. Tema recurrente del examen.
- **Loop del agente según Anthropic**: reunir contexto → actuar → verificar el trabajo (reglas, tests, linters, LLM-as-judge) → repetir.

## Práctica
- Agente con el Agent SDK que lee los archivos de una carpeta y produce un resumen. Agrega `max_turns` y un hook que bloquee `rm`.

## Autoevaluación
? Una regla de seguridad que nunca debe romperse. ¿Prompt o hook? :: Hook (control determinista).
? ¿Cuándo termina el loop agéntico? :: Con end_turn o al alcanzar un límite (turnos, tokens, tiempo).
"""

G['CCA: Sistemas multi-agente'] = """
## Qué estudiar ("How we built our multi-agent research system")
- **Orquestador + subagentes**: un agente líder planifica, lanza varios subagentes en **paralelo** (cada uno con su propio context window) y sintetiza sus resultados condensados.
- **Los subagentes NO heredan el contexto** del orquestador: hay que pasarles todo explícitamente: **objetivo**, formato de salida, tools a usar, límites y criterio de terminado. Instrucciones vagas → trabajo duplicado o huecos.
- **Escalar el esfuerzo a la complejidad**: una pregunta simple = 1 agente y pocas llamadas; una compleja = varios subagentes.
- **Costo**: los sistemas multi-agente usan muchas veces más tokens que un chat (Anthropic reporta ~15×). Solo valen la pena en tareas de alto valor y muy paralelizables.
- **Cuándo NO usarlos**: tareas con mucha dependencia entre pasos, cuando todos necesitan el mismo contexto, o tareas de código muy acopladas.
- **Buenas prácticas**: empezar con búsquedas amplias y luego acotar; extended thinking como scratchpad del plan; tools en paralelo; guardar resultados en almacenamiento externo y pasar referencias; evaluar el resultado final (LLM-as-judge con rúbrica) además de revisar trazas.
- **Fallos típicos**: resultados parciales, subagentes que no terminan, errores que se acumulan → reintentos, checkpoints y degradación elegante.

## Autoevaluación
? El subagente rehace trabajo que ya hizo otro. ¿Causa probable? :: El orquestador no le pasó un objetivo ni límites explícitos.
? ¿Por qué no usar multi-agente para todo? :: Gasta muchos más tokens y empeora en tareas acopladas.
"""

G['CCA: Lab — agente de investigación multi-agente'] = """
## Escenario oficial: Multi-Agent Research System (120 min)
1. **Orquestador**: recibe la pregunta, decide en cuántos frentes dividirla (2–3) y escribe una instrucción completa por subagente (objetivo, fuentes, formato, límite de pasos).
2. **Subagentes**: cada uno investiga su frente con sus tools y devuelve un resumen con fuentes.
3. **Síntesis**: el orquestador combina, resuelve contradicciones y cita.
4. **Robustez**: timeout por subagente; si uno falla, el informe sale con lo disponible y lo indica.
5. **Medición**: tokens totales, tiempo y calidad (rúbrica 1–5: exactitud, cobertura, citas).

## Qué anotar
- Tokens del multi-agente vs un solo agente con la misma pregunta.
- ¿El resultado mejoró lo suficiente para justificar el costo?
"""

G['CCA: Claude Code — memoria y configuración'] = """
## Qué estudiar (dominio 3: 20%)
- **Archivos CLAUDE.md (memoria)**
  - **Organización / enterprise**: política gestionada por IT para todos los usuarios.
  - **Usuario**: `~/.claude/CLAUDE.md` (tus preferencias en todos los proyectos).
  - **Proyecto**: `./CLAUDE.md` o `./.claude/CLAUDE.md` (commiteado, compartido con el equipo).
  - Se leen **subiendo** desde el directorio actual; los CLAUDE.md de subdirectorios se cargan cuando Claude trabaja con archivos de ahí.
  - **Imports**: `@ruta/archivo.md` dentro de un CLAUDE.md.
  - `/init` genera un CLAUDE.md inicial; `/memory` para editarlos.
- **settings.json** (precedencia de mayor a menor): managed (empresa) → argumentos de línea de comandos → `.claude/settings.local.json` (personal, no se commitea) → `.claude/settings.json` (proyecto, compartido) → `~/.claude/settings.json` (usuario).
- **Permisos**: reglas `allow`, `ask`, `deny` como `Bash(npm run test:*)`, `Read(./secrets/**)`; **deny gana**.
- **Permission modes**: default, acceptEdits, plan (solo lectura y planificación), bypassPermissions (peligroso).
- **Qué va en CLAUDE.md**: comandos de build y test, convenciones, arquitectura, gotchas del repo. Corto y concreto.

## Práctica
- Revisa el CLAUDE.md de este repo: ¿qué sobra? ¿qué falta (comandos de test)? Propón un `.claude/settings.json` con un deny para `Read(./infrastructure/*.tfvars)`.

## Autoevaluación
? Una regla de permisos personal que no quieres commitear. :: `.claude/settings.local.json`.
? `allow` y `deny` coinciden para el mismo comando. ¿Qué pasa? :: Gana deny.
"""

G['CCA: Claude Code extensible — skills, subagentes y hooks'] = """
## Qué estudiar
- **Slash commands personalizados**: archivos Markdown en `.claude/commands/` (proyecto) o `~/.claude/commands/` (usuario); `$ARGUMENTS` para parámetros. Los invoca el usuario.
- **Skills**: carpetas `.claude/skills/<nombre>/SKILL.md` con frontmatter (`name`, `description`) + archivos de apoyo. **Claude las carga sola** cuando la descripción coincide con la tarea (progressive disclosure: solo carga el contenido completo cuando la usa).
- **Subagentes**: `.claude/agents/<nombre>.md` con frontmatter (`name`, `description`, `tools`, `model`) y su system prompt. Trabajan en **su propio context window** y devuelven un resumen → protegen el contexto principal. Se invocan automáticamente por la descripción o de forma explícita.
- **Hooks** (en settings.json): comandos que corren en eventos del ciclo de vida.
  - `PreToolUse` (antes de una tool; puede **bloquear**), `PostToolUse` (p. ej. formatear tras editar), `UserPromptSubmit`, `Stop`, `SubagentStop`, `SessionStart`, `PreCompact`, `Notification`.
  - `matcher` por nombre de tool (p. ej. `Bash`, `Edit|Write`).
  - **Exit code 2 = bloquear** y el stderr se le muestra a Claude.
- **Plugins**: paquetes que agrupan commands, agents, skills, hooks y MCP servers; se instalan desde marketplaces.
- **Plan mode**: Claude investiga y propone un plan sin modificar archivos.
- **Gestión de sesión**: `/clear`, `/compact`, `/context`.

## Práctica
1. Hook PreToolUse sobre `Bash` que bloquee `terraform apply` con exit 2 y un mensaje.
2. Subagente `reviewer` con solo tools de lectura que revise el último diff.

## Autoevaluación
? ¿Qué diferencia una skill de un slash command? :: La skill la invoca Claude según su descripción; el slash command lo invoca el usuario.
? ¿Cómo bloquea un hook una acción? :: Saliendo con código 2 (el stderr vuelve a Claude).
? ¿Por qué usar un subagente para revisar código? :: Trabaja en su propio contexto y no llena el contexto principal.
"""

G['CCA: Claude Code en CI/CD'] = """
## Qué estudiar
- **Modo headless**: `claude -p "prompt"` ejecuta sin interfaz y termina.
  - `--output-format text | json | stream-json` (json trae resultado, costo y session_id).
  - `--allowedTools` / `--disallowedTools`, `--permission-mode`, `--max-turns`, `--append-system-prompt`, `--resume` / `--continue`.
- **GitHub Actions**: acción oficial `anthropics/claude-code-action`; se configura con `/install-github-app`; responde a menciones `@claude` en issues y PRs o corre en eventos (PR abierto). Secretos: `ANTHROPIC_API_KEY` (o Bedrock/Vertex con OIDC).
- **Permisos mínimos en CI**: solo las tools necesarias (lectura + comentar), nunca bypassPermissions en repos con secretos; permisos del token de GitHub acotados (`contents: read`, `pull-requests: write`).
- **Casos**: revisión automática de PRs, generar tests, triage de issues, arreglar lint, migraciones.
- **Riesgos**: prompt injection desde el contenido del PR o issue; limita las tools y revisa los cambios antes de mergear.

## Práctica
- Diseña un workflow para este repo: en cada PR, `claude -p` revisa el diff de `frontend/index.html` y comenta. Define `--allowedTools` y los permisos del job.

## Autoevaluación
? ¿Qué flag da la salida en JSON para parsearla en el pipeline? :: `--output-format json`.
? ¿Qué riesgo trae procesar el texto de un PR externo? :: Prompt injection; se mitiga limitando tools y permisos.
"""

G['CCA: Gestión de contexto'] = """
## Qué estudiar (dominio 5: 15%)
- **El contexto es un recurso finito**: a más tokens, más cuesta y más se degrada la atención ("context rot"). Objetivo: el **conjunto mínimo de tokens de alta señal**.
- **Técnicas ("Effective context engineering")**
  - **Compaction**: resumir la conversación al acercarse al límite (Claude Code lo hace con auto-compact y `/compact`).
  - **Borrar resultados de tools viejos** que ya no aportan.
  - **Notas estructuradas / memoria externa**: el agente escribe progreso en archivos (NOTES.md, TODO) y los relee.
  - **Subagentes**: exploran en su propio contexto y devuelven un resumen.
  - **Recuperación just-in-time**: guardar referencias (rutas, IDs) y cargar el contenido solo cuando haga falta.
- **Prompt caching**
  - Marca bloques con `cache_control: {"type": "ephemeral"}`; se cachea el **prefijo** en el orden tools → system → messages.
  - Hasta **4 breakpoints**; hay un mínimo de tokens por bloque cacheable.
  - TTL por defecto **5 minutos** (se renueva con cada uso); opción de 1 hora.
  - Escribir en caché cuesta algo más que el input normal; **leer cuesta ~10%**. Ideal para system prompts largos, documentos y definiciones de tools que se repiten.
- **Documentos largos**: al principio del prompt, con metadatos en `<document>`; pedir citas; usar la función de citations.

## Práctica
- En tu lab, agrega `cache_control` al system prompt largo, haz 2 requests seguidos y compara `cache_creation_input_tokens` y `cache_read_input_tokens`.

## Autoevaluación
? ¿Qué parte del prompt se puede cachear? :: El prefijo (tools, system, mensajes iniciales) hasta el breakpoint.
? El agente pierde el hilo en sesiones largas. :: Compactación, notas externas y subagentes.
"""

G['CCA: Confiabilidad en producción'] = """
## Qué estudiar
- **Errores de la API**: 400 (request inválido), 401 (API key), 403 (permiso), 404, 413 (request muy grande), **429 rate_limit_error** (respeta el header `retry-after`), 500 (error interno), **529 overloaded_error**.
- **Reintentos con backoff exponencial + jitter** solo para errores transitorios (429, 5xx, 529); no reintentes un 400. Los SDKs oficiales ya reintentan (2 veces por defecto).
- **Rate limits**: requests por minuto y tokens de entrada y salida por minuto según tu tier.
- **Timeouts y streaming** para respuestas largas.
- **Message Batches API**: procesamiento asíncrono (resultados en hasta 24 h) con **50% de descuento**; para cargas grandes no urgentes.
- **Reducir alucinaciones**: permitir "no lo sé", pedir citas textuales antes de responder, restringir al material dado, verificar cada afirmación contra la fuente, citations.
- **Evals antes de cambiar un prompt o de modelo**: criterios de éxito medibles, casos de prueba con edge cases, calificación por código (exact match), por LLM con rúbrica o por humanos. Compara la versión nueva contra la vieja.
- **Humano en el loop** para acciones irreversibles o de baja confianza.
- **Guardrails**: validar entradas y salidas, detectar prompt injection, moderar contenido.

## Práctica
- Agrega a tu lab reintentos con backoff ante 429/529 y simula un error. Escribe 5 casos de eval para tu extractor.

## Autoevaluación
? Recibes un 400. ¿Reintentas? :: No; el request está mal y hay que corregirlo.
? 10.000 resúmenes para mañana, al menor costo. :: Message Batches API.
"""

G['🎯 Simulacro CCA 1'] = """
## Cómo hacerlo (120 min)
- Practice exam oficial de Anthropic Academy en condiciones reales: 120 min, sin docs, en inglés.
- **Técnica para preguntas de escenario**: identifica el escenario y la restricción clave (costo, confiabilidad, seguridad, latencia). Descarta las opciones que solo "piden" algo en el prompt cuando la pregunta exige una garantía (hooks, schemas, permisos).
- Análisis por dominio con los pesos: Agentic 27 · Claude Code 20 · Prompts 20 · Tools/MCP 18 · Context 15.
"""

G['CCA: Escenarios 1–3'] = """
## Para cada escenario: arquitectura, tools, controles y qué puede fallar
- **1. Customer Support Agent**
  - Routing por intención; RAG sobre la base de conocimiento; tools para consultar pedidos y abrir tickets.
  - Guardrails: no prometer reembolsos sin aprobación, redactar PII, **escalar a un humano** si hay baja confianza o enojo.
  - Fallos: alucinar políticas (→ citar la fuente) o prompt injection del cliente (→ tools con mínimo privilegio).
- **2. Code Generation con Claude Code**
  - CLAUDE.md con convenciones y comandos de test; plan mode para cambios grandes.
  - Loop de verificación: correr tests y linters después de editar (hook PostToolUse).
  - Permisos: deny para secretos y comandos destructivos.
  - Fallos: cambios que rompen tests (→ verificar antes de terminar) o contexto lleno (→ subagentes y compactación).
- **3. Multi-Agent Research System**
  - Orquestador + subagentes en paralelo con instrucciones completas; síntesis con citas.
  - Fallos: costo en tokens, trabajo duplicado, subagentes colgados (→ timeouts, resultados parciales).

## Práctica
- Un diagrama de 1 página por escenario con: componentes, tools, controles deterministas y 2 fallos con su mitigación.
"""

G['CCA: Escenarios 4–6'] = """
## Para cada escenario: arquitectura, tools, controles y qué puede fallar
- **4. Developer Productivity**
  - Claude Code con skills y slash commands del equipo, MCP a Jira, GitHub o la docs interna, subagentes para revisión.
  - Configuración compartida en `.claude/` del repo y `.mcp.json` con scope project.
  - Fallos: cada dev con su propia config (→ settings de proyecto commiteados) o servers MCP no confiables.
- **5. Claude Code para CI/CD**
  - `claude -p` headless con `--output-format json`, `--allowedTools` acotado, `--max-turns`.
  - GitHub Action con permisos mínimos; el humano aprueba el merge.
  - Fallos: prompt injection desde el PR, costos sin límite (→ max-turns, presupuesto) o acciones destructivas (→ deny + hooks).
- **6. Structured Data Extraction**
  - Structured outputs o tool forzada, validación + reintento, null para lo faltante, revisión humana y Batches API para volumen.
  - Fallos: JSON inválido, campos inventados o documentos largos (→ chunking y caching del schema).

## Práctica
- Completa los 3 diagramas restantes. Tienes que poder explicar cada uno en 2 minutos.
"""

G['CCA: Revisión de errores del simulacro 1'] = """
## Método (50 min)
1. Error por error: dominio, concepto y por qué la correcta es correcta.
2. Clasifica: ¿confundiste un control probabilístico (prompt) con uno determinista (hook, schema, permiso)? Es el error más común en este examen.
3. Refuerza el dominio más débil con su curso en Anthropic Academy.
4. Cada error → una tarjeta Anki.
"""

G['🎯 Simulacro CCA 2 — repaso cronometrado'] = """
## Cómo hacerlo (60 min)
- Repite el practice exam oficial a ritmo de examen (~2 min por pregunta) en tandas.
- Para cada pregunta, **explica en voz alta por qué cada opción incorrecta es incorrecta**. Si solo recuerdas la respuesta, no cuenta.
- Meta: ≥85% con explicación.
"""

G['CCA: Repaso ligero y logística del examen'] = """
## Cheat sheet
- stop_reason: end_turn · max_tokens · stop_sequence · tool_use · pause_turn · refusal.
- tool_choice: auto · any · tool · none. tool_result en un mensaje user, `is_error` para fallos.
- MCP: host / client (1:1) / server · tools (modelo) · resources (app) · prompts (usuario) · stdio vs Streamable HTTP · scopes local/project/user.
- Patrones: chaining · routing · parallelization · orchestrator-workers · evaluator-optimizer.
- Subagentes: contexto explícito, sin herencia.
- Claude Code: jerarquía de CLAUDE.md · settings (managed > CLI > local > project > user) · deny gana · hooks (exit 2 bloquea) · skills vs commands · `-p` headless.
- Contexto: compaction · notas · subagentes · just-in-time · prompt caching (5 min, lectura ~10%).
- Confiabilidad: 429/529 con backoff · Batches 50% · evals · humano en el loop.

## Logística
- OnVUE: system test, ID, cuarto despejado, check-in 30 min antes. El examen es en inglés: tómate tu tiempo para leer.
"""

G['🏆 EXAMEN CCA Foundations'] = """
## Datos del examen
- Claude Certified Architect – Foundations (CCAR-F): 60 preguntas de escenario, 120 min (~2 min por pregunta), aprobado **720/1000**, US$125, en inglés, Pearson VUE. Vigencia de 12 meses.

## Estrategia
- Identifica el escenario y la restricción que manda (garantía, costo, latencia, seguridad).
- Si la pregunta exige que algo "siempre" o "nunca" pase, busca el control determinista (hook, permiso, schema, validación en código), no una instrucción en el prompt.
- Si existe una solución más simple que un agente, suele ser la correcta.
"""
