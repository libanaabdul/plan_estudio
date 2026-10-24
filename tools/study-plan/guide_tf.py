# Guías detalladas — Terraform Associate (004)
G = {}

G['TF: Diagnóstico 004 y reserva del examen'] = """
## Qué estudiar hoy
- **Los 8 objetivos del 004**: 1 IaC con Terraform · 2 Fundamentos (providers, state) · 3 Workflow core · 4 Configuración (resources, data, variables, expresiones, dependencias, **custom conditions**, **datos sensibles**) · 5 Módulos · 6 State management (backends, locking, drift) · 7 Mantener infraestructura (import, inspeccionar state, logging) · 8 **HCP Terraform** (workspaces, **projects**, gobernanza, integraciones).
- **Qué cambió respecto al 003**: se agregaron lifecycle/depends_on explícitos (4f), **custom conditions** (4g), **valores ephemeral y argumentos write-only** + Vault (4h) y **projects de HCP Terraform** (8c). Se evalúa sobre **Terraform 1.12**.
- **Formato**: ~57 preguntas en 60 min, solo en inglés. Tipos: opción múltiple, respuesta múltiple, verdadero/falso y completar el texto (p. ej. escribir un comando).

## Práctica
1. Lee el exam content list del 004 y ponte nota de 1 a 5 en cada uno de los 37 sub-objetivos.
2. Haz las **sample questions oficiales** sin estudiar: te dicen dónde estás de verdad.
3. Reserva **dos exámenes** hoy: Terraform (fecha del banner) y Cloud Practitioner. Con fecha puesta se estudia distinto.
4. En Anki crea el mazo con sub-barajas: `Certs::TF` y `Certs::CP`.

## Cómo usar tu experiencia diaria
> Lo que usas en el trabajo te da el 60%. El otro 40% son cosas que casi nunca escribes: la sintaxis exacta de las constraints, comandos poco usados (`force-unlock`, `state rm`, `-replace`), HCP Terraform y las novedades del 004. Ahí van tus horas.

## Autoevaluación
? ¿Qué versión de Terraform evalúa el 004? :: 1.12.
? ¿Qué objetivos son nuevos frente al 003? :: Custom conditions, ephemeral/write-only + Vault, lifecycle explícito y projects de HCP Terraform.
"""

G['TF: Providers, versiones y multi-cloud'] = """
## Qué estudiar
- **IaC**: definir infraestructura en archivos versionados → reproducible, revisable en PR, menos errores manuales, documentación viva.
- **Terraform es declarativo**: describes el estado deseado y Terraform calcula los pasos. Agnóstico de la nube gracias a los **providers** (plugins que hablan con las APIs).
- **Bloque terraform**:
```
terraform {
  required_version = ">= 1.12"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}
```
- **Operadores de versión**: `=` exacta, `!=` excluye, `>`, `>=`, `<`, `<=`, y **`~>` (pessimistic)**: solo permite crecer el **último número escrito**.
  - `~> 6.0` → `>= 6.0, < 7.0`
  - `~> 6.0.1` → `>= 6.0.1, < 6.1.0`
- **Source address**: `[hostname/]namespace/type` → `hashicorp/aws` equivale a `registry.terraform.io/hashicorp/aws`.
- **Dependency lock file `.terraform.lock.hcl`**: guarda la versión exacta y los **hashes** de cada provider elegido. **Se commitea**. No guarda versiones de módulos. Para subir de versión: `terraform init -upgrade`.
- **Varios providers y alias**:
```
provider "aws" { region = "us-east-1" }
provider "aws" { alias = "eu", region = "eu-west-1" }
resource "aws_s3_bucket" "b" { provider = aws.eu  bucket = "x" }
```
- Para pasar un alias a un módulo: `providers = { aws = aws.eu }`.

## Lo que más pregunta el examen
- Qué versiones acepta una constraint.
- Qué hace el lock file y si se versiona (sí).
- Cómo usar 2 regiones del mismo provider (alias).

## Trampas
> `~> 6.0` NO acepta 7.0. `~> 6.0.1` NO acepta 6.1.
> El lock file no fija versiones de módulos: eso lo hace el argumento `version` del bloque module.

## Práctica
1. Escribe de memoria el bloque terraform{} con aws y random, y un segundo provider aws con alias.
2. Corre `terraform init` y abre `.terraform.lock.hcl`: identifica `version`, `constraints` y `hashes`.
3. Cambia la constraint y corre `terraform init` sin y con `-upgrade`: compara el resultado.

## Autoevaluación
? ¿Qué rango acepta `~> 1.2.0`? :: >= 1.2.0 y < 1.3.0.
? ¿Hay que commitear `.terraform.lock.hcl`? :: Sí.
? ¿Cómo eliges un provider con alias en un recurso? :: Con el meta-argumento `provider = aws.alias`.
"""

G['TF: Workflow core y comandos'] = """
## Qué estudiar
- **Workflow**: Write → **init** → **plan** → **apply** (→ destroy).
- **`terraform init`**: descarga providers a `.terraform/providers`, módulos a `.terraform/modules`, configura el **backend** y crea o actualiza el lock file. Es seguro correrlo muchas veces.
  - `-upgrade` (nuevas versiones dentro de las constraints) · `-reconfigure` (ignora la config de backend previa) · `-migrate-state` (mueve el state al nuevo backend) · `-backend-config=archivo` (configuración parcial).
- **`terraform validate`**: sintaxis y consistencia interna (tipos, referencias). **Requiere init**; no llama a las APIs ni lee el state remoto.
- **`terraform fmt`**: estilo canónico. `-check` (falla si hay cambios, para CI), `-recursive`, `-diff`.
- **`terraform plan`**: refresca el state y muestra el diff (`+` crear, `-` destruir, `~` cambiar, `-/+` reemplazar). `-out=tfplan` guarda el plan; `-var`, `-var-file`, `-target`, `-refresh=false`, `-destroy`.
- **`terraform apply`**: sin argumentos hace un plan y pide confirmación; `apply tfplan` aplica el plan guardado **sin pedir confirmación**; `-auto-approve`; `-replace=aws_instance.web` fuerza recrear (reemplaza al viejo `taint`).
- **`terraform destroy`** = `apply -destroy`.
- **Otros**: `terraform show`, `output`, `console`, `graph`, `providers`, `version`, `login`.

## Lo que más pregunta el examen
- Qué hace cada comando y en qué orden.
- `validate` vs `fmt`. `plan -out` + `apply tfplan`. `-replace` vs `taint` (taint está deprecado).

## Trampas
> `terraform validate` no detecta que un AMI no existe: eso falla recién en plan o apply.
> `terraform fmt` no valida nada; solo formatea.

## Práctica
1. Directorio de prueba con el provider `local` y un `local_file`.
2. Antes de cada comando escribe qué esperas: init, validate, fmt -check, plan -out=p, apply p, apply -replace, destroy.
3. Compara con la salida real.

## Autoevaluación
? ¿Qué comando usarías en CI para fallar si el código no está formateado? :: `terraform fmt -check -recursive`.
? ¿Qué reemplaza a `terraform taint`? :: `terraform apply -replace=ADDRESS`.
? ¿Aplicar un plan guardado pide confirmación? :: No.
"""

G['TF: Estado, backends y locking'] = """
## Qué estudiar
- **State**: mapea los recursos del código con los objetos reales (IDs), guarda metadatos y dependencias y mejora el rendimiento. Archivo `terraform.tfstate` (+ `terraform.tfstate.backup`).
- **El state contiene secretos en texto plano** (contraseñas, outputs sensitive) → backend cifrado con acceso restringido.
- **Backend local** (por defecto): el archivo en el directorio de trabajo. Malo para equipos.
- **Backend remoto**: S3, azurerm, gcs, `cloud` (HCP Terraform)… Beneficios: compartido, **locking**, cifrado y versiones.
```
terraform {
  backend "s3" {
    bucket       = "mi-tfstate"
    key          = "app/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true   # locking nativo en S3 (TF 1.10+)
  }
}
```
- **State locking**: evita que 2 applies escriban a la vez. En S3, `use_lockfile` reemplaza a la tabla DynamoDB (`dynamodb_table` está deprecado). Si queda un lock colgado: `terraform force-unlock LOCK_ID`.
- **El bloque backend no admite variables** → usa configuración parcial con `-backend-config`.
- **Migrar de local a remoto**: agregar el bloque y correr `terraform init` (pregunta si quieres copiar el state) o `init -migrate-state`.
- **`terraform_remote_state`**: data source para leer outputs del state de otra configuración (mejor usar data sources del provider si se puede).

## Ejercicio con tu repo
> `infrastructure/main.tf` tiene backend S3 **sin** `use_lockfile` ni `dynamodb_table` → **no hay locking**. Si dos pipelines aplican a la vez, pueden corromper el state. Arreglo: agregar `use_lockfile = true`.

## Trampas
> Marcar un output como `sensitive` NO lo saca del state.
> Workspaces de la CLI no sirven como aislamiento fuerte entre ambientes (comparten backend y credenciales).

## Autoevaluación
? ¿Dónde guarda el state el backend por defecto? :: En `terraform.tfstate` en el directorio de trabajo (backend local).
? ¿Comando para liberar un lock colgado? :: `terraform force-unlock LOCK_ID`.
? ¿Puedes usar `var.region` dentro del bloque backend? :: No; usa configuración parcial.
"""

G['TF: Drift, import y CLI de estado'] = """
## Qué estudiar
- **Drift**: alguien cambió el recurso fuera de Terraform. `terraform plan` lo detecta (refresca por defecto). Para **aceptar** la realidad en el state sin tocar la infraestructura: `terraform apply -refresh-only` (ver antes con `plan -refresh-only`). `terraform refresh` está deprecado.
- **Import (config-driven, recomendado)**:
```
import {
  to = aws_s3_bucket.logs
  id = "mi-bucket-de-logs"
}
```
  `terraform plan -generate-config-out=generated.tf` escribe el bloque resource por ti. Luego `apply`.
- **`terraform import ADDRESS ID`** (CLI, viejo): importa al state pero **no genera código**; tienes que escribirlo.
- **Inspeccionar el state**: `terraform state list`, `state show ADDRESS`, `terraform show`, `state pull`.
- **Modificar el state**: `state mv` (renombrar o mover a un módulo), `state rm` (dejar de gestionar sin destruir), `state push` (peligroso).
- **Refactor declarativo**:
```
moved { from = aws_instance.web  to = aws_instance.app }
removed {
  from = aws_s3_bucket.viejo
  lifecycle { destroy = false }   # lo saca del state sin borrarlo
}
```
- **Logging**: `TF_LOG=TRACE|DEBUG|INFO|WARN|ERROR` (también `JSON`), `TF_LOG_PATH=./tf.log`, y `TF_LOG_CORE` / `TF_LOG_PROVIDER` por separado.

## Lo que más pregunta el examen
- Cuál es el comando para cada situación: renombrar sin destruir (moved o state mv), dejar de gestionar (removed o state rm), adoptar existente (import), forzar recreación (-replace), aceptar drift (apply -refresh-only).
- El nivel de log más detallado: **TRACE**.

## Trampas
> `terraform import` por CLI no crea el código.
> `state rm` no destruye el recurso real.

## Práctica
1. Crea un bucket S3 a mano en la consola.
2. Escribe un import block y corre `terraform plan -generate-config-out=generated.tf`.
3. Revisa el código generado, haz `apply` y verifica que `plan` diga "No changes".
4. Renómbralo con un bloque `moved` y confirma que no hay destroy.

## Autoevaluación
? Cambiaron un tag a mano y quieres que el state lo refleje sin modificar nada. :: `terraform apply -refresh-only`.
? ¿Qué variable define el archivo de log? :: `TF_LOG_PATH`.
"""

G['TF: Repaso S1 + lab de refactor'] = """
## Plan del sábado (60 min)
1. **25 min · Quiz**: 20 preguntas de los objetivos 1, 2, 3, 6 y 7.
2. **25 min · Lab**:
   - Toma un config con 2 recursos.
   - Renombra uno con `moved`, mete el otro en un módulo local con `moved { from = aws_x.y  to = module.m.aws_x.y }`.
   - `terraform plan` → debe mostrar solo "moved", sin destroy.
3. **10 min · Anki** con los fallos.

## Checklist de la semana
- Constraints `~>` · lock file · alias.
- init (-upgrade, -reconfigure, -migrate-state) · validate vs fmt · plan -out · apply -replace.
- Backend S3 + use_lockfile · force-unlock · state con secretos.
- refresh-only · import block + generate-config-out · state mv/rm · moved/removed · TF_LOG.
"""

G['TF: resource vs data, referencias y lifecycle'] = """
## Qué estudiar
- **resource**: crea y gestiona un objeto. **data**: **lee** algo que ya existe (no lo gestiona).
```
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter { name = "name"  values = ["al2023-ami-*-x86_64"] }
}
resource "aws_instance" "web" { ami = data.aws_ami.al2023.id }
```
- **Referencias**: `TIPO.NOMBRE.ATRIBUTO`, `data.TIPO.NOMBRE.ATRIBUTO`, `module.NOMBRE.OUTPUT`, `var.X`, `local.X`.
- **Dependencias implícitas**: si un recurso referencia a otro, Terraform construye el grafo y los crea en orden. Lo que no depende entre sí se crea **en paralelo** (por defecto 10 operaciones, `-parallelism`).
- **`depends_on`**: solo para dependencias **ocultas** que Terraform no puede ver (p. ej. una policy IAM que debe existir antes de que una app la use). También funciona con módulos.
- **lifecycle**:
  - `create_before_destroy = true`: crea el reemplazo antes de borrar el viejo (sin downtime).
  - `prevent_destroy = true`: el plan **falla** si implica destruir el recurso.
  - `ignore_changes = [tags]` (o `all`): ignora cambios hechos fuera de Terraform.
  - `replace_triggered_by = [aws_x.y.id]`: recrea cuando otro recurso cambia.
  - `precondition` / `postcondition` (sesión de custom conditions).

## Ejercicio con tu repo
> En `infrastructure/main.tf`: `prevent_destroy` está en la tabla DynamoDB (protege los datos del tracker) y `create_before_destroy` en el deployment de API Gateway (para que el stage no se quede sin deployment). Explícalos en voz alta.

## Trampas
> `prevent_destroy` solo protege mientras el bloque existe: si borras el bloque resource completo del código, la protección desaparece con él y Terraform sí lo destruye.
> No uses `depends_on` cuando ya hay una referencia: es redundante.

## Autoevaluación
? ¿data o resource para usar una VPC creada por otro equipo? :: data.
? ¿Qué lifecycle evita el downtime al reemplazar? :: create_before_destroy.
"""

G['TF: Variables, outputs y tipos complejos'] = """
## Qué estudiar
- **variable**: `type`, `default`, `description`, `validation`, `sensitive`, `nullable`, `ephemeral`.
- **Precedencia** (de menor a mayor; la última gana):
  1. variables de entorno `TF_VAR_nombre`
  2. `terraform.tfvars`
  3. `terraform.tfvars.json`
  4. `*.auto.tfvars` / `*.auto.tfvars.json` (en orden alfabético)
  5. `-var` y `-var-file` en la línea de comandos (en el orden en que se escriben)
- Si una variable no tiene default ni valor, Terraform **la pide interactivamente** (o falla con `-input=false`).
- **Tipos**: primitivos `string`, `number`, `bool`; colecciones `list(T)`, `set(T)`, `map(T)`; estructurales `object({...})` y `tuple([...])`; `any`.
```
variable "app" {
  type = object({
    name     = string
    replicas = optional(number, 2)
    tags     = optional(map(string), {})
  })
}
```
- **output**: `value`, `description`, `sensitive`, `depends_on`, `precondition`. Se ven con `terraform output` (`-json`, `-raw`).
- **locals**: valores calculados internos (`local.nombre`); no se pueden setear desde afuera.

## Trampas
> `terraform.tfvars` se carga solo, pero `prod.tfvars` NO: necesita `-var-file=prod.tfvars`.
> `sensitive = true` en una variable la oculta en la salida pero queda en el state.

## Práctica
1. Variable object con optional y validation (`replicas >= 1`).
2. Define la misma variable en `TF_VAR_`, `terraform.tfvars` y `-var` y comprueba cuál gana con `terraform console`.

## Autoevaluación
? Un valor en `x.auto.tfvars` y otro con `-var`. ¿Cuál gana? :: `-var`.
? ¿Qué diferencia hay entre list y set? :: list tiene orden y admite duplicados; set no tiene orden ni duplicados.
"""

G['TF: Expresiones, funciones y for_each'] = """
## Qué estudiar
- **count vs for_each**
  - `count = 3` → `aws_instance.web[0]`, `count.index`. Problema: si sacas el elemento del medio, **se recrean** los siguientes.
  - `for_each = toset(["a","b"])` o un map → `aws_instance.web["a"]`, `each.key` / `each.value`. Keys estables → no hay recreaciones en cascada.
  - for_each acepta **map o set de strings**, y las keys deben conocerse en el plan.
- **for expressions**: `[for s in var.names : upper(s)]` · `{for k, v in var.m : k => v if v != ""}`.
- **splat**: `aws_instance.web[*].id`.
- **condicional**: `var.env == "prod" ? 3 : 1`.
- **dynamic blocks**:
```
dynamic "ingress" {
  for_each = var.ports
  content { from_port = ingress.value  to_port = ingress.value  protocol = "tcp" }
}
```
- **Funciones built-in** (no puedes definir funciones propias; los providers sí pueden exponer funciones): `lookup(map, key, default)`, `merge`, `concat`, `flatten`, `toset`, `tolist`, `length`, `element`, `join`, `split`, `format`, `replace`, `coalesce`, `zipmap`, `keys`, `values`, `try`, `can`, `file`, `templatefile`, `jsonencode`, `cidrsubnet`.
- **`terraform console`**: prueba expresiones con el state actual.

## Trampas
> No se pueden usar `count` y `for_each` en el mismo bloque.
> `for_each` con una list da error: conviértela con `toset()`.

## Práctica
- En `terraform console` evalúa: `cidrsubnet("10.0.0.0/16", 8, 2)`, `merge({a=1},{b=2})`, `flatten([[1],[2,3]])`, `lookup({x=1},"y",0)`, `[for n in ["a","b"] : upper(n)]`, `try(var.nope, "default")`, `toset(["a","a","b"])`, `join("-", ["a","b"])`.

## Autoevaluación
? `cidrsubnet("10.0.0.0/16", 8, 2)` :: "10.0.2.0/24".
? ¿Por qué preferir for_each sobre count para recursos nombrados? :: Las keys son estables; con count un cambio de orden recrea recursos.
"""

G['TF: Custom conditions y datos sensibles (nuevo 004)'] = """
## Qué estudiar (objetivos 4g y 4h, novedad del 004)
- **Validación de variables**:
```
variable "env" {
  type = string
  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env debe ser dev o prod."
  }
}
```
  Desde 1.9 la condición puede referenciar otras variables.
- **precondition / postcondition** (dentro de `lifecycle` de resources y data, o en outputs):
```
lifecycle {
  postcondition {
    condition     = self.public_ip != ""
    error_message = "La instancia debe tener IP pública."
  }
}
```
  `self` solo existe en postcondition.
- **check blocks**: aserciones que se evalúan en cada plan/apply y dan **warning** sin bloquear. Pueden tener un data source propio (p. ej. un `http` que verifica que la web responde 200).
- **sensitive**: oculta el valor en la salida de la CLI, **pero queda en el state y en el plan guardado**.
- **ephemeral** (1.10+): valores que **nunca se guardan** en state ni en plan.
  - Variables y outputs con `ephemeral = true`.
  - **Ephemeral resources**: `ephemeral "aws_secretsmanager_secret_version" "db" {...}` lee un secreto solo durante la ejecución.
- **Argumentos write-only** (1.11+): p. ej. `password_wo` y `password_wo_version` en `aws_db_instance`. Aceptan un valor ephemeral y no lo persisten; cambiar `_wo_version` dispara la actualización.
- **Vault**: el provider de Vault con data sources normales escribe el secreto en el state; con **ephemeral resources** ya no. Mejor práctica: secretos dinámicos de corta duración, nunca en el código ni en tfvars commiteados.

## Lo que más pregunta el examen
- Dónde queda un valor sensitive (en el state).
- Qué garantiza ephemeral (no se persiste).
- Diferencia entre validation (entrada), pre/postcondition (supuestos del recurso) y check (aviso continuo).

## Práctica
1. Variable con validation que falle a propósito.
2. Recurso con postcondition.
3. Check block con data `http` que valide una URL.
4. Busca en la docs del provider AWS un argumento `*_wo`.

## Autoevaluación
? ¿Un check block fallido detiene el apply? :: No, solo muestra un warning.
? ¿Dónde puedes usar `self`? :: En postconditions (y provisioners).
? ¿Qué diferencia hay entre sensitive y ephemeral? :: sensitive se oculta pero se guarda; ephemeral no se guarda.
"""

G['TF: Módulos'] = """
## Qué estudiar
- **Root module** (directorio donde corres terraform) vs **child modules** (llamados con bloques `module`).
- **Fuentes**:
  - path local: `source = "./modules/db"` (no admite version)
  - Registry público o privado: `source = "terraform-aws-modules/vpc/aws"` + `version = "~> 5.0"`
  - GitHub / Git: `source = "git::https://github.com/org/repo.git//modules/x?ref=v1.2.0"`
  - HTTP, S3, GCS
- **`version` solo funciona con fuentes de registry**. En Git se fija con `?ref=`.
- **Scope**: el módulo **no ve** las variables del root ni sus recursos; todo entra por **inputs** (variables del módulo) y sale por **outputs** (`module.db.endpoint`).
- **Providers**: el child hereda la configuración por defecto del provider; los alias se pasan con `providers = { aws = aws.eu }`.
- **Estructura estándar**: `main.tf`, `variables.tf`, `outputs.tf`, `README.md`, `versions.tf`.
- Después de agregar o cambiar un módulo: `terraform init` (o `terraform get`).
- Registry público: los módulos verificados tienen insignia y siguen la convención `terraform-<PROVIDER>-<NAME>`.

## Trampas
> Un output de un child module no se ve con `terraform output` del root salvo que el root lo re-exporte.
> `version` en un source local da error.

## Práctica
1. Crea `modules/table` con la tabla DynamoDB del tracker (variables: name, tags; output: arn).
2. En el root: `module "table" { source = "./modules/table" ... }` + `moved { from = aws_dynamodb_table.study_plan  to = module.table.aws_dynamodb_table.this }`.
3. `terraform plan` → solo "moved", sin destroy. (No hagas apply en tu cuenta real.)

## Autoevaluación
? ¿Cómo fijas la versión de un módulo de GitHub? :: Con `?ref=TAG` en el source.
? ¿Puede un módulo leer `var.region` del root sin pasársela? :: No.
"""

G['🎯 Simulacro Terraform 1'] = """
## Cómo hacerlo (75 min)
1. **60 min**: 57 preguntas en condiciones reales (sin docs, sin terminal).
2. **15 min**: anota cada error con su objetivo (1a…8d).

## Tipos de pregunta del examen real
- Opción múltiple, respuesta múltiple, **verdadero/falso** y **fill-in-the-blank** (escribir un comando o subcomando exacto, p. ej. `force-unlock` o `fmt`). Practica escribir comandos completos de memoria.

## Qué hacer con los resultados
- Objetivos con 2+ errores → el lunes relees su guía.
- ≥70% en el primer simulacro es buen punto de partida.
"""

G['TF: HCP Terraform — workspaces, projects y runs'] = """
## Qué estudiar (objetivos 8a y 8c)
- **HCP Terraform** (antes Terraform Cloud): servicio SaaS de HashiCorp; **Terraform Enterprise** es la versión self-hosted.
- **Jerarquía**: Organization → **Projects** (agrupan workspaces y permiten dar permisos a equipos por proyecto) → **Workspaces** (cada uno con su state, variables, historial de runs y configuración).
- **Workspaces de HCP ≠ workspaces de la CLI**: en HCP son unidades independientes con su propio state, variables y permisos; en la CLI son solo varios states del mismo directorio.
- **Flujos de trabajo**:
  - **VCS-driven**: conectado a un repo; un PR dispara un plan especulativo y el merge dispara el run.
  - **CLI-driven**: corres `terraform plan/apply` en tu terminal, pero se ejecuta en HCP (con el bloque `cloud` + `terraform login`).
  - **API-driven**: integraciones propias.
- **Bloque cloud**:
```
terraform {
  cloud {
    organization = "mi-org"
    workspaces { name = "tracker-prod" }   # o tags = ["app:tracker"]
  }
}
```
- **Execution mode**: remote (en HCP), local (HCP solo guarda el state) o agent (agentes en tu red).
- **Variables**: de Terraform y de entorno, marcables como sensitive; **variable sets** para reutilizarlas en varios workspaces o projects.
- **Fases de un run**: plan → cost estimation → policy check → apply (con confirmación o auto-apply).

## Práctica
1. Crea una cuenta gratis en HCP Terraform, una organización, un project y un workspace CLI-driven.
2. `terraform login`, agrega el bloque `cloud` a un config con `random_pet` y corre `terraform plan`: verás el run en la web.

## Autoevaluación
? ¿Qué agrupa workspaces y permite permisos por equipo? :: Projects.
? ¿Qué comando autentica la CLI contra HCP Terraform? :: `terraform login`.
? Workspace HCP vs CLI. :: HCP: state, variables y permisos propios. CLI: varios states del mismo config en el mismo backend.
"""

G['TF: HCP Terraform — colaboración y gobernanza'] = """
## Qué estudiar (objetivos 8b y 8d)
- **Teams y permisos** a nivel organización, project y workspace; SSO.
- **Private registry**: módulos y providers internos con versiones, publicados desde VCS.
- **Policy as code**: **Sentinel** (lenguaje de HashiCorp) u **OPA**; niveles de enforcement advisory, soft-mandatory y hard-mandatory; se evalúan entre plan y apply.
- **Run tasks**: integraciones de terceros en el run (escaneo de seguridad, costos).
- **Health assessments**: **detección de drift** y validación continua de los check blocks.
- **Cost estimation** antes del apply.
- **Dynamic provider credentials**: HCP se autentica con **OIDC** ante AWS, Azure, GCP o Vault, sin guardar access keys de larga duración.
- **No-code provisioning**: usuarios despliegan módulos aprobados sin escribir HCL.
- **Integración VCS**: GitHub, GitLab, Bitbucket, Azure DevOps.
- **Planes**: hay un plan gratis y planes de pago. Algunas funciones de gobernanza son de pago: confírmalo en la página de precios, el examen pregunta qué ofrece HCP, no precios exactos.

## Práctica
- Tabla: feature → para qué sirve → ¿lo usarías en tu trabajo? (Sentinel, private registry, drift detection, dynamic credentials, run tasks, cost estimation).

## Autoevaluación
? ¿Cómo evitas guardar access keys de AWS en un workspace? :: Dynamic provider credentials con OIDC.
? ¿En qué momento del run corren las políticas Sentinel? :: Después del plan (y de cost estimation) y antes del apply.
"""

G['🎯 Simulacro Terraform 2'] = """
## Cómo hacerlo (60 min)
- 57 preguntas en 60 min, un banco **distinto** al del simulacro 1.
- Meta: **≥80%**.
- Compara por objetivo con el simulacro 1: los objetivos que sigan en rojo son el foco de mañana.
"""

G['TF: Revisión de errores + checklist de objetivos'] = """
## Método (40 min)
1. **20 min**: los errores de los 2 simulacros: por qué la correcta es correcta.
2. **20 min**: recorre los 37 sub-objetivos y márcalos verde / amarillo / rojo. Los rojos: lee la sección de la study guide oficial.

## Cheat sheet de 1 página
- `~>` · lock file · alias · `init -upgrade/-reconfigure/-migrate-state`.
- `validate` vs `fmt -check` · `plan -out` · `apply -replace` · `apply -refresh-only` · `force-unlock`.
- Precedencia de variables · tipos · `optional()`.
- count vs for_each · dynamic · funciones clave.
- lifecycle (4 + pre/postcondition) · check blocks · sensitive vs ephemeral · write-only.
- Fuentes de módulos y `version` solo en registry.
- import block + `-generate-config-out` · moved/removed · `state mv/rm/list/show`.
- HCP: org → project → workspace · VCS/CLI/API-driven · variable sets · Sentinel/OPA · drift · OIDC.
"""

G['TF: Repaso ligero y logística del examen'] = """
## Hoy (30 min)
1. **15 min**: solo tu cheat sheet.
2. **15 min**: logística del examen online
   - Prueba de sistema del proctoring en la computadora del examen.
   - ID vigente, cuarto despejado, sin segundo monitor.
   - Revisa el email de confirmación y la hora (ojo con la zona horaria).

## Mañana
- Desayuna, conéctate 15–30 min antes.
- El examen es corto (60 min): ~1 min por pregunta, marca las dudosas.
"""

G['🏆 EXAMEN Terraform Associate (004)'] = """
## Datos del examen
- Terraform Associate (004), ~57 preguntas, **60 min**, en inglés, online con proctoring.
- Tipos: opción múltiple, respuesta múltiple, verdadero/falso y completar texto.

## Estrategia
- Las preguntas de "completar" piden el comando exacto: no pongas `terraform` si el texto ya lo incluye.
- Las de verdadero/falso suelen tener trampas de matiz ("always", "never").

## Después
- Hoy además toca un repaso corto de CP (30 min) → no hace falta más.
- Anota el resultado en Notas y comparte la insignia.
"""
