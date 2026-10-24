# Guías detalladas — AWS Solutions Architect Associate (SAA-C03)
G = {}

G['SAA: Arranque y evaluación de policies IAM'] = """
## Qué estudiar
- **El examen**: 65 preguntas (50 puntúan), 130 min (+30 con ESL), 720/1000. Dominios: Design Secure Architectures 30% · Resilient 26% · High-Performing 24% · Cost-Optimized 20%. Todo son **escenarios**.
- **Tipos de policy**: identity-based (usuario, grupo, rol), **resource-based** (bucket policy, key policy de KMS, SQS policy; tienen `Principal`), permission boundaries, SCPs/RCPs (Organizations), session policies, ACLs.
- **Lógica de evaluación**
  1. Todo empieza en **deny implícito**.
  2. Un **deny explícito** en cualquier policy gana siempre.
  3. Las SCPs y los permission boundaries ponen un **techo**: el permiso tiene que estar en la intersección.
  4. Dentro de la misma cuenta basta un allow en la identity policy **o** en la resource policy.
  5. **Entre cuentas** hacen falta los dos: la cuenta que llama debe permitirlo y el recurso debe confiar en ella.
- **Elementos**: `Effect`, `Action`, `Resource`, `Condition` (p. ej. `aws:SourceIp`, `aws:PrincipalOrgID`, `aws:SecureTransport`, `aws:RequestedRegion`).

## Práctica
1. Reserva el SAA con el voucher de 50% del AIF.
2. Abre la policy de la Lambda en `infrastructure/main.tf`: tiene DynamoDB acotado a la tabla, pero los logs con `arn:aws:logs:*:*:*`. ¿Cómo la acotarías al log group?

## Autoevaluación
? Una identity policy permite `s3:GetObject` y la bucket policy tiene Deny para ese usuario. :: Denegado: el deny explícito gana.
? ¿Qué condición fuerza HTTPS en una bucket policy? :: `aws:SecureTransport` = false → Deny.
"""

G['SAA: Roles, STS y acceso entre cuentas'] = """
## Qué estudiar
- **Rol** = identidad con permisos y **credenciales temporales** vía **STS AssumeRole**. Tiene dos policies:
  - **Trust policy**: quién puede asumirlo (`Principal`: un servicio como `ec2.amazonaws.com`, otra cuenta, un IdP).
  - **Permission policy**: qué puede hacer una vez asumido.
- **Cross-account**: la cuenta B crea un rol con trust a la cuenta A; los usuarios de A con `sts:AssumeRole` lo asumen. Alternativa: **resource-based policy** (S3, KMS, SQS…) que da acceso directo sin asumir rol (el principal conserva sus propios permisos).
- **External ID**: se agrega en la trust policy para que un tercero asuma un rol de forma segura (evita el problema del "confused deputy").
- **Federación**: SAML 2.0 (AD/ADFS, Okta), OIDC (web identity) → credenciales temporales. **IAM Identity Center**: SSO para empleados a muchas cuentas con permission sets.
- **Instance profile**: el contenedor que pasa un rol a EC2. **`iam:PassRole`**: permiso necesario para asignarle un rol a un servicio.
- **STS**: `AssumeRole`, `AssumeRoleWithSAML`, `AssumeRoleWithWebIdentity`, `GetSessionToken` (MFA).

## Práctica
- Diagrama: cuenta A (dev) asume un rol de solo lectura en la cuenta B (prod). Escribe la trust policy y la permission policy.

## Autoevaluación
? Un proveedor externo necesita acceso a tu cuenta. ¿Qué agregas a la trust policy? :: Su cuenta como principal + una condición `sts:ExternalId`.
? ¿Qué permiso necesita un dev para lanzar una EC2 con un rol? :: `iam:PassRole` sobre ese rol.
"""

G['SAA: Organizations, SCPs y Control Tower'] = """
## Qué estudiar
- **AWS Organizations**: management account + member accounts organizadas en **OUs**; consolidated billing; políticas.
- **SCPs (Service Control Policies)**: definen el **máximo** de permisos de las cuentas de una OU. **No otorgan** nada. **No afectan a la management account**. Se usan como allow-list o deny-list (p. ej. negar regiones, impedir desactivar CloudTrail).
- **RCPs (Resource Control Policies)**: techo sobre los recursos (p. ej. que ningún bucket se comparta fuera de la organización).
- **Permission boundaries**: techo para un usuario o rol concreto; útil para delegar la creación de roles sin escalar privilegios.
- **Control Tower**: arma una **landing zone** multi-cuenta con buenas prácticas: Account Factory, guardrails (controles preventivos con SCPs y detectivos con Config) y cuentas de log archive y audit.
- **AWS RAM (Resource Access Manager)**: compartir recursos entre cuentas (subnets, Transit Gateway, Route 53 Resolver rules).
- **Otras políticas de Organizations**: tag policies, backup policies.

## Lo que más pregunta el examen
- "Impedir que cualquier cuenta use regiones fuera de la UE" → SCP con deny por `aws:RequestedRegion`.
- "Montar 50 cuentas con controles estándar rápido" → Control Tower.
- "Compartir una subnet con otra cuenta" → RAM.

## Autoevaluación
? Una SCP permite S3 pero el rol no tiene permisos de S3. ¿Puede usar S3? :: No; la SCP no otorga.
? ¿Las SCPs restringen a la management account? :: No.
"""

G['SAA: Cognito y directorios'] = """
## Qué estudiar
- **Cognito User Pools**: directorio de usuarios para **autenticación** (registro, login, MFA, recuperación, federación con Google o SAML). Emite **JWT**: ID token, access token y refresh token. Se integra con **API Gateway** (Cognito authorizer) y con ALB.
- **Cognito Identity Pools**: dan **credenciales temporales de AWS** (vía STS) a usuarios autenticados (de un user pool, Google, SAML) o invitados → para acceder **directo** a S3 o DynamoDB desde la app.
- **Patrón**: user pool para el login + identity pool para credenciales AWS.
- **Directory Service**: **AWS Managed Microsoft AD** (AD real en AWS, trust con tu AD on-premises), **AD Connector** (proxy al AD on-premises, sin guardar nada en AWS), **Simple AD** (básico).

## Tu tracker como ejemplo
- El navegador llama a Cognito `InitiateAuth` (USER_PASSWORD_AUTH) → recibe el **IdToken** → lo envía en `Authorization` → API Gateway lo valida con el authorizer del **user pool** → invoca la Lambda. No usa identity pool porque nunca habla directo con DynamoDB.

## Autoevaluación
? Una app móvil necesita subir fotos directo a S3 con credenciales temporales. :: Identity pool.
? Usar el AD on-premises sin replicarlo a AWS. :: AD Connector.
"""

G['SAA: Cifrado — KMS, CloudHSM y certificados'] = """
## Qué estudiar
- **KMS**
  - Tipos de clave: **AWS owned** (no las ves), **AWS managed** (`aws/s3`, rotación automática anual, no editas la policy) y **customer managed** (tú controlas key policy, rotación y borrado).
  - Toda clave tiene una **key policy** (resource-based); sin ella nadie la usa, ni root.
  - **Envelope encryption**: KMS genera una **data key** (`GenerateDataKey`); los datos se cifran localmente con ella y la data key se guarda cifrada. `Encrypt` directo solo hasta 4 KB.
  - Rotación automática configurable en claves customer managed; **multi-region keys** para cifrar en una región y descifrar en otra.
  - Borrado con período de espera de 7–30 días. Cada uso queda en CloudTrail. Hay cuotas de requests/s.
- **CloudHSM**: HSM **dedicado (single-tenant)**, FIPS 140 nivel 3; **tú gestionas las claves y usuarios** (AWS no tiene acceso). Para requisitos regulatorios estrictos o claves que deben salir del control de AWS.
- **ACM**: certificados TLS públicos **gratis** con renovación automática para ELB, CloudFront y API Gateway (no para instalar en EC2 directamente). Para CloudFront el certificado tiene que estar en **us-east-1**.
- **Cifrado en tránsito**: TLS en ALB/NLB/CloudFront; en reposo: EBS, S3, RDS, DynamoDB integrados con KMS.

## Trampas
> Un snapshot de RDS o EBS cifrado con una clave AWS managed no se comparte con otra cuenta: hay que re-cifrarlo con una customer managed y compartir la clave.
> Para cifrar una RDS existente sin cifrar: snapshot → copia cifrada → restaurar.

## Autoevaluación
? El auditor exige que AWS no pueda acceder a las claves. :: CloudHSM.
? Cifrar archivos de 1 GB con KMS. :: Envelope encryption con GenerateDataKey.
"""

G['SAA: Repaso S1 + lab de least privilege'] = """
## Plan del sábado (120 min)
1. **40 min · Lab**
   - Escribe una policy mínima para la Lambda del tracker: `dynamodb:Scan/GetItem/PutItem/DeleteItem/BatchWriteItem` solo sobre el ARN de la tabla y `logs:CreateLogStream/PutLogEvents` solo sobre el ARN del log group `/aws/lambda/plan-estudio`.
   - Valídala en **IAM Policy Simulator** y con **IAM Access Analyzer** (policy validation).
2. **50 min · Quiz**: 25 preguntas de identidad, Organizations y cifrado.
3. **30 min · Análisis + Anki**.

## Checklist
- Evaluación de policies · trust vs permission policy · external ID · PassRole · federación e Identity Center · SCP/RCP/boundary · Control Tower · RAM · user pool vs identity pool · Directory Service · KMS (tipos, envelope, multi-region) · CloudHSM · ACM.
"""

G['SAA: VPC a fondo'] = """
## Qué estudiar
- **CIDR**: VPC de /16 a /28; puedes agregar CIDRs secundarios. **AWS reserva 5 IPs por subnet** (las 4 primeras y la última): una /24 deja 251 usables.
- **Subnets** en una AZ; **route tables** asociadas (la ruta `local` siempre existe).
- **Internet Gateway** (uno por VPC, HA por diseño). **Egress-only IGW**: salida IPv6 sin entrada.
- **NAT Gateway**: gestionado, en una **subnet pública** con Elastic IP, **zonal** → para alta disponibilidad, **uno por AZ** y cada subnet privada enrutada al NAT de su AZ. Cobra por hora y por GB procesado. NAT instance = opción vieja que gestionas tú.
- **Acceso a instancias privadas**: **SSM Session Manager** (sin puertos abiertos ni bastion) es lo recomendado; bastion host como alternativa clásica; **EC2 Instance Connect Endpoint**.
- **DNS en la VPC**: `enableDnsSupport`, `enableDnsHostnames`; Route 53 Resolver (endpoints inbound y outbound para DNS híbrido).
- **Elastic IP**: IPv4 pública estática (se cobra; todas las IPv4 públicas se cobran desde 2024).
- **Diseño típico de 3 capas**: subnets públicas (ALB, NAT), privadas de app y privadas de BD, en 2 o 3 AZs.

## Lo que más pregunta el examen
- "Las instancias privadas perdieron internet cuando cayó una AZ" → había un solo NAT Gateway → uno por AZ.
- "Acceso administrativo sin abrir el puerto 22" → Session Manager.

## Autoevaluación
? ¿Cuántas IPs usables tiene una subnet /28? :: 11 (16 − 5).
? ¿Un NAT Gateway es regional o zonal? :: Zonal.
"""

G['SAA: Security Groups, NACLs y VPC endpoints'] = """
## Qué estudiar
- **Security Groups**: en la ENI, **stateful**, solo allow, pueden **referenciar otros SGs** (la BD permite 5432 desde el SG de la app, no desde un CIDR). Por defecto: entrada denegada, salida permitida.
- **NACLs**: en la subnet, **stateless**, allow y deny, reglas numeradas evaluadas **de menor a mayor** (la primera que coincide gana). La NACL por defecto permite todo; una **NACL nueva niega todo**. Por ser stateless hay que permitir el **retorno por puertos efímeros (1024–65535)**.
- **VPC endpoints**
  - **Gateway endpoints**: solo **S3 y DynamoDB**, son **gratis**, se agregan como ruta en la route table; solo para tráfico desde dentro de la VPC.
  - **Interface endpoints (PrivateLink)**: una ENI con IP privada en tu subnet para casi cualquier servicio (y servicios propios de otras cuentas); tienen costo por hora y por GB; accesibles desde on-premises por VPN o DX.
  - **Endpoint policies** para limitar qué buckets o acciones se pueden usar.
- **VPC Flow Logs**: metadatos de tráfico (IP, puerto, ACCEPT/REJECT) a CloudWatch Logs o S3; a nivel de VPC, subnet o ENI.

## Lo que más pregunta el examen
- "Instancias privadas acceden a S3 sin internet y al menor costo" → **gateway endpoint**.
- "Bloquear una IP maliciosa" → **NACL** con deny (o WAF si es web).
- "Acceso privado a S3 desde on-premises por Direct Connect" → **interface endpoint** de S3.

## Autoevaluación
? La NACL permite 443 de entrada pero no hay regla de salida para puertos efímeros. :: La respuesta se bloquea (stateless).
? ¿Qué endpoint cuesta $0? :: Gateway (S3 y DynamoDB).
"""

G['SAA: Protección perimetral'] = """
## Qué estudiar
- **AWS WAF**: web ACLs con reglas (IP sets, geo match, SQL injection, XSS, tamaño, **rate-based rules** contra floods de requests, **managed rule groups** de AWS y del Marketplace, Bot Control). Se asocia a **CloudFront, ALB, API Gateway, AppSync y Cognito**. No va en un NLB.
- **Shield Standard**: gratis y automático contra DDoS de capas 3 y 4.
- **Shield Advanced**: de pago; equipo de respuesta 24/7 (SRT), protección de costos por escalado durante un ataque, mitigación en capa 7 con WAF, métricas y reportes.
- **Firewall Manager**: gestiona WAF, Shield Advanced, Security Groups y Network Firewall de forma **central en toda la Organization**.
- **AWS Network Firewall**: firewall gestionado a nivel de VPC (inspección stateful, filtrado de dominios, IPS).
- **CloudFront como escudo**: absorbe tráfico en el edge, con geo restriction, y **OAC** para que el bucket S3 solo acepte peticiones de CloudFront (bloqueas el acceso directo).

## Lo que más pregunta el examen
- "Bloquear SQL injection" → WAF. "Limitar a 2.000 requests por IP cada 5 min" → regla rate-based de WAF. "Aplicar las mismas reglas WAF en 30 cuentas" → Firewall Manager. "Protección DDoS con soporte 24/7 y reembolso de costos" → Shield Advanced.

## Autoevaluación
? ¿Se puede poner WAF en un NLB? :: No.
? El bucket solo debe servir contenido a través de CloudFront. :: Origin Access Control + bucket policy.
"""

G['SAA: Protección de datos en S3 y secretos'] = """
## Qué estudiar
- **Cifrado en S3**: **SSE-S3** (por defecto desde 2023, AES-256 gestionado por S3), **SSE-KMS** (auditoría en CloudTrail, control con key policy; usa S3 Bucket Keys para bajar el costo de KMS), **DSSE-KMS** (doble capa), **SSE-C** (tú das la clave en cada request, solo HTTPS) y cifrado en el cliente.
- Forzar cifrado o HTTPS con bucket policy (condiciones `s3:x-amz-server-side-encryption` y `aws:SecureTransport`).
- **Acceso**: bucket policies, IAM, **Block Public Access** (cuenta y bucket), ACLs deshabilitadas por defecto (Object Ownership = bucket owner enforced), **Access Points**, presigned URLs (acceso temporal a un objeto).
- **Protección contra borrado**: versioning, **MFA Delete**, **Object Lock** (WORM): modo **Governance** (usuarios con permisos especiales pueden quitarlo) vs **Compliance** (nadie, ni root, durante la retención); **Legal Hold**. **Glacier Vault Lock**.
- **Macie**: descubre PII y datos sensibles en S3.
- **Secrets Manager**: guarda secretos con **rotación automática** (integración nativa con RDS, Redshift y DocumentDB; Lambda para el resto), replicación entre regiones; cobra por secreto.
- **SSM Parameter Store**: configuración y secretos (SecureString con KMS), tier estándar gratis, sin rotación nativa.

## Lo que más pregunta el examen
- "Retención regulatoria inmodificable 7 años" → Object Lock en **Compliance mode**.
- "Rotar automáticamente la contraseña de RDS" → **Secrets Manager**.
- "Auditar quién usó la clave de cifrado" → SSE-KMS + CloudTrail.

## Autoevaluación
? ¿Qué modo de Object Lock no puede saltarse ni root? :: Compliance.
? Compartir un archivo privado por 1 hora con alguien sin cuenta AWS. :: Presigned URL.
"""

G['SAA: Detección y cumplimiento'] = """
## Qué estudiar
- **GuardDuty**: detección de amenazas con ML e inteligencia de amenazas sobre CloudTrail, VPC Flow Logs y DNS logs (+ protección para S3, EKS, RDS, Lambda, malware en EBS). Hallazgos → EventBridge → Lambda o SNS para remediar.
- **Inspector**: escaneo continuo de **vulnerabilidades** (CVEs) y exposición de red en EC2 (con SSM agent), imágenes de ECR y funciones Lambda.
- **Security Hub**: agrega los hallazgos de GuardDuty, Inspector, Macie y Config; revisa estándares (AWS Foundational Security Best Practices, CIS).
- **Detective**: investigación y causa raíz con un grafo de comportamiento.
- **AWS Config**: inventario e historial de configuración; **Config rules** (gestionadas o propias) para cumplimiento; **remediación automática** con SSM Automation; conformance packs; agregador multi-cuenta.
- **CloudTrail**: management events (por defecto), data events (S3 object-level, Lambda invoke; se pagan aparte), Insights; **organization trail** a un bucket central en la cuenta de log archive; validación de integridad de logs.
- **IAM Access Analyzer**: detecta recursos compartidos fuera de la cuenta u organización y valida policies.
- **Audit Manager**: reúne evidencia para auditorías.

## Lo que más pregunta el examen
- "Detectar minería de cripto en instancias" → GuardDuty. "CVEs en imágenes de contenedores" → Inspector. "Revertir automáticamente un SG abierto a 0.0.0.0/0" → Config rule + remediación automática.

## Autoevaluación
? Ver en un tablero los hallazgos de todos los servicios de seguridad. :: Security Hub.
? ¿Qué servicio guarda el historial de cambios de configuración de un SG? :: AWS Config.
"""

G['SAA: Repaso S1–S2 — dominio Secure'] = """
## Plan del sábado (120 min)
1. **60 min · Quiz**: 35 preguntas del dominio Secure (30% del examen).
2. **40 min · Análisis**: por qué la correcta es correcta y por qué las otras no.
3. **20 min · Anki**.

## Checklist del dominio Secure
- IAM: evaluación, roles, cross-account, federación, Identity Center, SCP/RCP/boundaries.
- Datos: KMS, CloudHSM, ACM, cifrado S3, Object Lock, Secrets Manager vs Parameter Store, Macie.
- Red: subnets, NAT por AZ, SG vs NACL, gateway vs interface endpoints, Session Manager.
- Perímetro: WAF, Shield, Firewall Manager, Network Firewall, CloudFront + OAC.
- Detección: GuardDuty, Inspector, Security Hub, Detective, Config, CloudTrail, Access Analyzer.
"""

G['SAA: EC2 a fondo'] = """
## Qué estudiar
- **Nombres**: `m7g.large` = familia **m**, generación **7**, atributo **g** (Graviton/ARM), tamaño **large**. Otros atributos: `i` (Intel), `a` (AMD), `n` (red mejorada), `d` (instance store).
- **Placement groups**
  - **Cluster**: misma AZ, mismo rack → latencia mínima y ancho de banda alto (HPC); riesgo de falla conjunta.
  - **Spread**: cada instancia en hardware distinto (máximo **7 por AZ**) → para pocas instancias críticas.
  - **Partition**: grupos de racks aislados (hasta 7 particiones por AZ) → Hadoop, Cassandra, Kafka.
- **Red**: ENI (interfaz), **ENA** (enhanced networking hasta 100+ Gbps), **EFA** (HPC con baja latencia entre nodos).
- **Almacenamiento**: EBS-optimized, instance store (efímero y rapidísimo).
- **User data** (script de arranque) y **metadata**: **IMDSv2** (con token de sesión, protege contra SSRF) → exígelo.
- **Hibernate**: guarda la RAM en el EBS raíz (cifrado) para arrancar rápido.
- **AMIs**: regionales (se copian entre regiones); golden AMIs con EC2 Image Builder.
- **Estados**: stop (conserva EBS, pierde la IP pública salvo Elastic IP) vs terminate.
- **Status checks**: system (hardware de AWS) vs instance (tu SO); la acción de CloudWatch **recover** mueve la instancia a otro host.

## Autoevaluación
? Nodos de HPC que necesitan la mínima latencia entre sí. :: Cluster placement group (+ EFA).
? 5 instancias críticas que no deben fallar juntas. :: Spread placement group.
"""

G['SAA: Load balancers'] = """
## Qué estudiar
- **ALB (capa 7)**: HTTP, HTTPS, gRPC y WebSocket; routing por **path, host, headers, query string y método**; target groups de instancias, IPs o **Lambda**; redirecciones y respuestas fijas; autenticación con Cognito u OIDC; WAF. La IP del cliente llega en `X-Forwarded-For`.
- **NLB (capa 4)**: TCP, UDP y TLS; **millones de req/s**, latencia ultra baja; **IP estática por AZ** (y Elastic IPs); preserva la IP de origen; puede ser target de un ALB; es la base de PrivateLink.
- **GWLB (capa 3)**: para insertar **appliances de terceros** (firewalls, IDS) de forma transparente; protocolo GENEVE (puerto 6081).
- **Cross-zone load balancing**: ALB activado por defecto y gratis; NLB y GWLB desactivado por defecto (cobra transferencia entre AZs).
- **Sticky sessions** (cookies), **deregistration delay** (connection draining; por defecto 300 s), **health checks**.
- **Certificados**: ACM + **SNI** para varios dominios en un listener.
- **CLB** es legacy: no lo elijas en el examen salvo que lo mencione.

## Lo que más pregunta el examen
- Microservicios por path → ALB. IP fija para whitelisting del cliente → NLB. Tráfico UDP de un juego → NLB. Firewall virtual de terceros → GWLB.

## Autoevaluación
? ¿Puede un ALB invocar una Lambda? :: Sí, como target.
? El cliente necesita poner en su firewall la IP fija de tu balanceador. :: NLB con Elastic IPs (o Global Accelerator).
"""

G['SAA: Auto Scaling'] = """
## Qué estudiar
- **Launch template** (versionado; reemplaza a launch configuration) con AMI, tipo, SG, user data e IAM role.
- **Capacidad**: mínimo, deseada y máxima. Varias AZs para HA; el ASG reequilibra entre AZs.
- **Políticas**
  - **Target tracking**: mantener una métrica en un valor (CPU 50%, requests por target). La más simple y recomendada.
  - **Step scaling**: escalones según el tamaño de la alarma.
  - **Simple scaling**: un ajuste y espera el cooldown (legacy).
  - **Scheduled**: por horario conocido (lunes 9:00).
  - **Predictive**: ML sobre el historial para escalar **antes** del pico diario.
- **Cooldown / warm-up** (por defecto 300 s) para no escalar en exceso.
- **Health checks**: EC2 (estado de la instancia) o **ELB** (la app responde); actívalo con ELB para reemplazar instancias que no sirven.
- **Lifecycle hooks**: pausar al lanzar o terminar (instalar algo, sacar logs). **Warm pools**: instancias pre-inicializadas para escalar rápido. **Instance refresh**: rolling update.
- **Mixed instances policy**: On-Demand + Spot y varios tipos en el mismo ASG.
- **Termination policy** por defecto: AZ con más instancias → la de launch template más viejo → la más cercana a la siguiente hora de facturación.

## Autoevaluación
? Tráfico con pico conocido todos los días a las 9. :: Scheduled o predictive scaling.
? Instancias "running" pero la app no responde y no se reemplazan. :: Activar health checks de ELB en el ASG.
"""

G['SAA: Lambda a fondo'] = """
## Qué estudiar
- **Límites clave**: timeout máximo **15 min**; memoria de 128 MB a **10.240 MB** (la CPU escala con la memoria); `/tmp` hasta 10 GB; payload síncrono de 6 MB; concurrencia por región de **1.000 por defecto** (ampliable).
- **Concurrencia**: **reserved** (garantiza y limita la concurrencia de una función) vs **provisioned** (instancias pre-calentadas: elimina cold starts, tiene costo).
- **Cold starts**: provisioned concurrency, **SnapStart** (Java, Python, .NET), paquetes más chicos.
- **Invocación**: síncrona (API Gateway, ALB), **asíncrona** (S3, SNS, EventBridge; reintenta 2 veces → DLQ o destinations) y **event source mapping** (SQS, Kinesis, DynamoDB Streams: Lambda hace polling por lotes).
- **En VPC**: se conecta con ENIs a tus subnets para llegar a RDS; para salir a internet necesita un NAT Gateway; para llegar a S3 o DynamoDB, usa endpoints.
- **RDS Proxy** para que miles de Lambdas no agoten las conexiones de la base.
- **Layers**, **container images** de hasta 10 GB, **Function URLs**, versiones y aliases (despliegue canario).
- **Lambda@Edge** (Node y Python, eventos viewer y origin, más pesado) vs **CloudFront Functions** (JavaScript liviano, solo viewer request y response, sub-milisegundo, millones de req/s).

## Tu tracker
> La Lambda tiene timeout de 29 s porque **API Gateway REST corta la integración a los 29 s por defecto**: un timeout mayor no serviría para requests síncronos.

## Autoevaluación
? Proceso de 40 min. ¿Lambda? :: No (máximo 15); usa Fargate/ECS, Batch o Step Functions.
? Miles de Lambdas agotan las conexiones de PostgreSQL. :: RDS Proxy.
"""

G['SAA: Contenedores'] = """
## Qué estudiar
- **ECS**: orquestador de AWS. Conceptos: cluster, **task definition** (imagen, CPU y memoria, puertos, rol), task, **service** (mantiene N tareas detrás de un ALB, con auto scaling).
- **Launch types**: **EC2** (gestionas las instancias del cluster; más control y más barato a gran escala) vs **Fargate** (serverless: pagas CPU y memoria por tarea).
- **IAM**: **task role** (permisos de la app dentro del contenedor) vs **task execution role** (para que ECS descargue la imagen de ECR y escriba logs).
- **EKS**: Kubernetes gestionado; nodos con managed node groups, self-managed o Fargate; cuando hay que ser portable o el equipo ya usa K8s.
- **ECR**: registro privado con escaneo de imágenes (Inspector) y replicación.
- **App Runner**: despliegue de web apps desde un contenedor o código fuente sin gestionar nada.
- **Almacenamiento persistente para contenedores**: EFS (ECS y EKS, también con Fargate).
- **AWS Batch**: trabajos batch en contenedores, con Spot.

## Cómo decidir
- Evento corto (< 15 min) → Lambda. Contenedor de larga duración sin gestionar servidores → ECS/EKS con Fargate. Ya tienen manifiestos de Kubernetes → EKS. Mínimo esfuerzo para una web → App Runner.

## Autoevaluación
? ¿Qué rol necesita la app del contenedor para escribir en DynamoDB? :: Task role.
? Volumen compartido persistente entre tareas Fargate. :: EFS.
"""

G['SAA: Lab — arquitectura de 3 capas altamente disponible'] = """
## Diseño (60 min)
- **Route 53** (alias) → **CloudFront** (opcional, con WAF) → **ALB** en subnets públicas de 2–3 AZs → **ASG** en subnets privadas de app (min 2, target tracking) → **RDS Multi-AZ** (o Aurora) en subnets privadas de BD → **ElastiCache** para sesiones o caché.
- NAT Gateway **por AZ**; gateway endpoint para S3; Session Manager para administrar.
- SGs encadenados: ALB (443 desde internet) → app (puerto de la app solo desde el SG del ALB) → BD (5432 solo desde el SG de la app).
- **Sesiones fuera de la instancia** (ElastiCache o DynamoDB) para que las instancias sean stateless.

## Recorrido de fallas (preguntas que debes poder contestar)
- Cae una instancia → health check del ALB + reemplazo del ASG.
- Cae una AZ → el ALB deja de enviarle tráfico, el ASG lanza en las otras AZs y RDS hace failover al standby (1–2 min; el endpoint DNS no cambia).
- Pico de tráfico → target tracking + caché.
- Caída de región → no cubierto (eso es DR, semana 4).

## Quiz (40 min) + análisis (20 min)
- 25 preguntas de cómputo, ELB, Auto Scaling, Lambda y contenedores.
"""

G['SAA: S3 a fondo'] = """
## Qué estudiar
- **Clases y mínimos**: Standard-IA y One Zone-IA cobran mínimo **30 días** y 128 KB por objeto; Glacier Instant y Flexible, **90 días**; Deep Archive, **180 días**. Intelligent-Tiering no cobra recuperación (cobra monitoreo por objeto).
- **Recuperación de Glacier Flexible**: expedited (1–5 min), standard (3–5 h), bulk (5–12 h). Deep Archive: standard hasta 12 h, bulk hasta 48 h.
- **Lifecycle**: transiciones y expiración por prefijo o tag; expirar versiones viejas y multipart incompletos.
- **Replicación**: CRR (otra región: compliance, latencia, DR) y SRR (misma región: agregación de logs, cuentas de prod y test); requiere versioning; solo replica objetos nuevos (los existentes con **Batch Replication**); **RTC** con SLA de 15 min.
- **Rendimiento**: al menos 3.500 PUT y 5.500 GET por segundo **por prefijo**; **multipart upload** (recomendado desde 100 MB, obligatorio desde 5 GB); **Transfer Acceleration** (subidas desde lejos vía edge); byte-range fetches.
- **Eventos**: S3 Event Notifications → SNS, SQS, Lambda o **EventBridge** (más filtros y destinos).
- **Otros**: S3 Select, Storage Lens, Requester Pays, presigned URLs, static website (con CloudFront para HTTPS), Access Points, Object Lambda, **S3 Express One Zone** (latencia de un dígito de ms).

## Autoevaluación
? Usuarios de todo el mundo suben archivos grandes lentamente a un bucket en us-east-1. :: Transfer Acceleration + multipart upload.
? Replicar también los objetos que ya existen. :: S3 Batch Replication.
"""

G['SAA: EBS, EFS y FSx'] = """
## Qué estudiar
- **EBS**
  - **gp3**: SSD de propósito general, base de **3.000 IOPS y 125 MB/s** sin importar el tamaño; IOPS y throughput se suben por separado (más barato que gp2).
  - **gp2**: IOPS ligadas al tamaño (3 IOPS por GB, con burst).
  - **io2 Block Express / io1**: IOPS provisionadas para bases de datos críticas; **Multi-Attach** (varias instancias en la misma AZ).
  - **st1** (HDD de throughput: big data, logs) y **sc1** (HDD frío, el más barato); **no pueden ser volumen de arranque**.
  - Atado a una AZ; snapshots incrementales; copia entre regiones; **Fast Snapshot Restore**; **Recycle Bin**; cifrado con KMS; Data Lifecycle Manager para automatizar snapshots.
- **Instance store**: máximo IOPS, efímero → caché, buffers, datos replicados.
- **EFS**: NFS v4 para **Linux**, multi-AZ (o One Zone), escala sola; modos de throughput **Elastic**, Provisioned y Bursting; clases Standard, IA y Archive con lifecycle; access points; se monta en EC2, ECS, EKS, Fargate y Lambda.
- **FSx**
  - **Windows File Server**: SMB, Active Directory, DFS → apps Windows.
  - **Lustre**: HPC y ML con alto rendimiento, se integra con S3 (modos scratch y persistent).
  - **NetApp ONTAP**: NFS, SMB e iSCSI a la vez, snapshots y deduplicación → migrar NetApp.
  - **OpenZFS**: NFS compatible con ZFS.

## Autoevaluación
? Base de datos con 50.000 IOPS sostenidas. :: io2 Block Express.
? Archivos compartidos para servidores Windows con AD. :: FSx for Windows File Server.
? Disco de arranque con st1. :: No se puede.
"""

G['SAA: Migración y transferencia de datos'] = """
## Qué estudiar
- **Online**
  - **DataSync**: agente on-premises → copia **programada** e incremental de NFS, SMB, HDFS u object storage hacia S3, EFS o FSx (y entre servicios de AWS); cifra y verifica integridad.
  - **Transfer Family**: endpoints **SFTP, FTPS, FTP y AS2** gestionados sobre S3 o EFS (para socios que solo hablan SFTP).
  - **Storage Gateway** (acceso **continuo e híbrido**, no solo migración): **S3 File Gateway** (NFS/SMB → objetos S3 con caché local), **FSx File Gateway**, **Volume Gateway** (iSCSI; cached o stored, con backups como snapshots EBS) y **Tape Gateway** (cintas virtuales para software de backup existente).
- **Offline**: **Snowball Edge** (decenas a cientos de TB por dispositivo, con cómputo en el edge); se usa cuando por la red tardaría semanas.
- **Bases de datos**: **DMS** (full load + **CDC** para replicación continua con downtime mínimo) + **SCT** para cambiar de motor (Oracle → Aurora PostgreSQL).
- **Servidores**: **Application Migration Service (MGN)**: replicación a nivel de bloque y cutover a EC2 (rehost).
- **Regla de cálculo**: 100 TB por un enlace de 1 Gbps al 80% ≈ 100×8.000 Gb / 0,8 Gb/s ≈ 1.000.000 s ≈ **11–12 días**.

## Autoevaluación
? Mantener los servidores on-premises usando S3 como si fuera un NAS. :: S3 File Gateway.
? Migrar Oracle a Aurora con mínima caída. :: DMS (full load + CDC) + SCT.
"""

G['SAA: Backup y recuperación ante desastres'] = """
## Qué estudiar
- **RPO** (cuántos datos puedes perder: tiempo desde el último respaldo) y **RTO** (cuánto puedes tardar en volver).
- **Estrategias** (de más barata y lenta a más cara y rápida):
  1. **Backup & restore**: backups en otra región; RPO y RTO de **horas**.
  2. **Pilot light**: datos replicados en vivo (réplica de BD) y el núcleo mínimo listo; al desastre se levanta el resto (IaC, AMIs) → **decenas de minutos**.
  3. **Warm standby**: copia completa **reducida** corriendo; se escala al desastre → **minutos**.
  4. **Multi-site active-active**: ambas regiones sirven tráfico → **casi cero**, lo más caro.
- **AWS Backup**: planes centralizados (frecuencia, retención, copia entre regiones y cuentas), **Vault Lock** (backups inmutables), backup policies de Organizations, soporta EC2, EBS, RDS, Aurora, DynamoDB, EFS, FSx, S3.
- **Elastic Disaster Recovery (DRS)**: replicación continua de servidores a AWS con recuperación en minutos.
- **Piezas**: snapshots y AMIs copiados entre regiones, S3 CRR, réplicas de lectura cross-region, Aurora Global Database, DynamoDB global tables, Route 53 failover, IaC para re-crear la infraestructura.

## Lo que más pregunta el examen
- Elegir la estrategia según RPO/RTO **y** costo: la más barata que cumpla.

## Autoevaluación
? RTO de 4 h, presupuesto mínimo. :: Backup & restore.
? RTO de minutos con costo moderado. :: Warm standby.
"""

G['SAA: RDS y Aurora'] = """
## Qué estudiar
- **RDS Multi-AZ**
  - **Instancia**: standby **síncrono** en otra AZ, **no sirve lecturas**; failover automático en 1–2 min con el mismo endpoint DNS.
  - **Cluster Multi-AZ** (MySQL, PostgreSQL): 1 writer + 2 standbys **legibles**, failover más rápido.
- **Read replicas**: asíncronas, hasta 15, en la misma región o en otra; se pueden **promover** (DR o migración); la app debe usar su endpoint.
- **Backups**: automáticos con retención de **1–35 días** y point-in-time restore; snapshots manuales sin vencimiento.
- **Aurora**: storage compartido que crece solo (sin aprovisionar), **6 copias en 3 AZs**; hasta 15 réplicas con failover en segundos; **reader endpoint** (balancea lecturas) y writer endpoint; **Aurora Serverless v2** (escala en ACUs para cargas variables); **Global Database** (región primaria + secundarias, replicación típica < 1 s, failover a otra región en ~1 min); clonación rápida; Backtrack (MySQL).
- **RDS Proxy**: pool de conexiones, failover más rápido, IAM auth; ideal con Lambda.
- **Seguridad**: cifrado solo al crear (para cifrar una existente: snapshot → copia cifrada → restaurar); IAM database authentication; SSL.
- **RDS Custom**: acceso al SO para Oracle o SQL Server.

## Autoevaluación
? La BD debe sobrevivir a la caída de una AZ automáticamente. :: Multi-AZ.
? Reportes pesados ralentizan la BD de producción. :: Read replica para los reportes.
? DR entre regiones con RPO de 1 s. :: Aurora Global Database.
"""

G['SAA: Repaso S3–S4 — dominio Resilient'] = """
## Plan del sábado (120 min)
1. **60 min · Quiz**: 35 preguntas de resiliencia (ELB, ASG, multi-AZ, S3, EBS/EFS/FSx, DR, RDS/Aurora).
2. **40 min · Análisis**.
3. **20 min · Anki**.

## Checklist del dominio Resilient
- Desacople y escalado (empieza la próxima semana con SQS/SNS) · multi-AZ en cada capa · ASG + ELB con health checks · NAT por AZ.
- Storage: replicación S3, snapshots, EFS multi-AZ.
- BD: Multi-AZ vs read replica vs Aurora Global.
- DR: 4 estrategias con RPO/RTO y costo · AWS Backup · DRS.
"""

G['SAA: DynamoDB a fondo'] = """
## Qué estudiar
- **Modelo**: tabla con **partition key** (y opcionalmente **sort key**); item máximo **400 KB**; esquema flexible.
- **Capacidad**: **on-demand** (paga por request, tráfico impredecible) vs **provisioned** (RCU/WCU + auto scaling, más barato si es estable).
  - 1 **RCU** = 1 lectura fuertemente consistente/s de hasta 4 KB (o 2 eventualmente consistentes). 1 **WCU** = 1 escritura/s de hasta 1 KB.
- **Índices**: **GSI** (otra partition y sort key, se crea en cualquier momento, eventualmente consistente, con su propia capacidad) vs **LSI** (misma partition key con otra sort key, **solo al crear la tabla**, admite lectura fuertemente consistente).
- **Query** (por key, eficiente) vs **Scan** (lee toda la tabla, caro y lento).
- **Hot partitions**: evítalas con partition keys de alta cardinalidad.
- **Funciones**: **Streams** (cambios por 24 h → Lambda), **TTL** (borra items vencidos gratis), **global tables** (multi-región activo-activo), **DAX** (caché en memoria con latencia de **microsegundos**), **PITR** (35 días), backups on-demand, transacciones, export a S3.

## Tu tracker
> La tabla `study-plan-items` tiene solo PK `id` y el frontend hace **Scan** completo en cada carga. Con 600 filas no importa, pero no escala. Diseño por access patterns: PK = `USER#<id>`, SK = `DATE#<fecha>#<id>` → un Query trae el plan de un usuario ordenado por fecha; GSI por categoría si hiciera falta.

## Autoevaluación
? Lecturas de microsegundos sobre DynamoDB sin cambiar mucho la app. :: DAX.
? ¿Puedes agregar un LSI a una tabla existente? :: No; un GSI sí.
"""

G['SAA: Caché'] = """
## Qué estudiar
- **ElastiCache**
  - **Redis / Valkey**: estructuras de datos ricas, persistencia, réplicas y **Multi-AZ con failover**, pub/sub, sorted sets (rankings), backups. ElastiCache Serverless.
  - **Memcached**: simple, multi-hilo, **sin persistencia ni replicación**; escala horizontal por sharding.
- **Patrones**
  - **Lazy loading (cache-aside)**: la app lee la caché; si falla (miss), lee la BD y escribe en caché. Solo cachea lo que se pide; datos pueden quedar viejos (usa TTL).
  - **Write-through**: escribe en la caché al escribir en la BD; datos siempre frescos, pero cachea cosas que quizá nunca se lean.
  - **TTL** para invalidar.
- **MemoryDB for Redis**: base de datos **durable** en memoria (no solo caché).
- **DAX** solo para DynamoDB; **ElastiCache** para cualquier fuente (RDS, APIs).
- **CloudFront** = caché en el edge para contenido HTTP. **API Gateway caching** para respuestas de API.
- **Sesiones**: guardarlas en ElastiCache o DynamoDB para tener instancias stateless.

## Autoevaluación
? Ranking de un juego en tiempo real. :: ElastiCache Redis (sorted sets).
? Caché que no debe perder datos al reiniciarse y debe tener failover. :: Redis con réplicas y Multi-AZ (o MemoryDB si es la BD principal).
"""

G['SAA: Bases de datos de propósito específico'] = """
## Qué estudiar (patrón de acceso → BD)
- **Relacional, transacciones y joins** → RDS / Aurora.
- **Key-value a gran escala con baja latencia** → DynamoDB.
- **Documentos JSON, compatible con MongoDB** → **DocumentDB**.
- **Grafos** (relaciones: redes sociales, fraude, recomendaciones) → **Neptune**.
- **Cassandra (CQL)** → **Keyspaces**.
- **Series de tiempo** (IoT, métricas) → **Timestream**.
- **Búsqueda full-text y análisis de logs** → **OpenSearch**.
- **Ledger inmutable**: QLDB fue retirado; hoy se resuelve con Aurora PostgreSQL + auditoría o un ledger propio (por si aparece en materiales viejos).
- **Data warehouse (OLAP)** → **Redshift**.
- **En memoria durable** → **MemoryDB**.

## Práctica
- 6 casos: catálogo con atributos variables en JSON (DocumentDB o DynamoDB), "amigos de amigos" (Neptune), lecturas de sensores cada segundo (Timestream), buscador de productos con texto libre (OpenSearch), migración de Cassandra (Keyspaces), reportes de 5 años de ventas (Redshift).

## Autoevaluación
? Detectar anillos de fraude por relaciones entre cuentas. :: Neptune.
? Logs de aplicación con búsqueda y dashboards. :: OpenSearch.
"""

G['SAA: Analítica'] = """
## Qué estudiar
- **Data lake en S3** con formatos columnares (**Parquet, ORC**) y particiones (por fecha) para bajar costos de consulta.
- **AWS Glue**: **Data Catalog** (metadatos; lo usan Athena, Redshift Spectrum y EMR), **crawlers** (detectan el schema), **Glue ETL jobs** (Spark serverless), DataBrew (limpieza visual).
- **Athena**: SQL **serverless** sobre S3; se paga **por TB escaneado** → Parquet y particiones reducen costo; federated query a otras fuentes.
- **Lake Formation**: gobierno del data lake con permisos a nivel de columna y fila sobre el catálogo.
- **Redshift**: data warehouse columnar MPP; **Redshift Serverless**; **Spectrum** (consulta datos en S3 sin cargarlos); RA3 con managed storage; data sharing.
- **EMR**: Hadoop y Spark gestionados (también EMR Serverless) para procesamiento masivo.
- **QuickSight**: BI y dashboards serverless, con Q (lenguaje natural).
- **OpenSearch**: búsqueda y analítica de logs.

## Práctica
- Pipeline: logs de la app → Firehose → S3 (Parquet, particionado por día) → Glue crawler → Athena → QuickSight. Justifica cada pieza.

## Autoevaluación
? Bajar el costo de las consultas de Athena. :: Parquet + particiones + compresión.
? Permisos por columna sobre el data lake. :: Lake Formation.
"""

G['SAA: Streaming'] = """
## Qué estudiar
- **Kinesis Data Streams**: streaming en **tiempo real** con **retención** (24 h por defecto, hasta 365 días) y **replay**; varios consumidores; modo **on-demand** o provisioned por **shards** (cada shard: 1 MB/s o 1.000 registros/s de entrada, 2 MB/s de salida); orden por partition key; enhanced fan-out.
- **Amazon Data Firehose**: entrega **casi en tiempo real** (buffer por tamaño o tiempo) a S3, Redshift, OpenSearch, Splunk o HTTP; serverless; transforma con Lambda y convierte a Parquet; **sin retención ni replay**.
- **MSK**: Apache Kafka gestionado (y MSK Serverless) cuando ya usan Kafka.
- **Managed Service for Apache Flink**: análisis de streams en tiempo real (ventanas, agregaciones).
- **SQS vs Kinesis**: SQS = cola de tareas, cada mensaje lo procesa un consumidor y se borra; Kinesis = flujo ordenado que varios consumidores leen y se puede re-leer.

## Autoevaluación
? Clickstream que leen 3 aplicaciones distintas y se debe poder reprocesar. :: Kinesis Data Streams.
? Llevar logs a S3 en Parquet sin código. :: Data Firehose.
"""

G['SAA: Repaso S5 — dominio High-Performing'] = """
## Plan del sábado (120 min)
1. **60 min · Quiz**: 35 preguntas de BD, caché, analítica y streaming (+ EC2 y storage de alto rendimiento).
2. **40 min · Análisis**. **20 min · Anki**.

## Checklist del dominio High-Performing
- Cómputo: familias de EC2, placement groups, Lambda (memoria y concurrencia), contenedores.
- Storage: gp3 vs io2, EFS vs FSx, S3 (prefijos, multipart, Transfer Acceleration).
- BD: Aurora, read replicas, DynamoDB (on-demand, GSI, DAX), ElastiCache, BD de propósito específico.
- Red y edge: CloudFront, Global Accelerator (próxima semana).
- Datos: Kinesis vs Firehose vs MSK, Athena, Glue, Redshift, EMR.
"""

G['SAA: SQS, SNS y EventBridge'] = """
## Qué estudiar
- **SQS**
  - **Standard**: throughput casi ilimitado, **al menos una vez**, orden aproximado. **FIFO**: orden exacto y **exactly-once processing**, 300 msg/s (3.000 con batching, más con high throughput mode), nombre terminado en `.fifo`, message group ID.
  - **Visibility timeout** (por defecto 30 s, máximo 12 h): ajústalo al tiempo real de proceso o habrá duplicados.
  - Retención de 4 días por defecto (máximo 14). **Long polling** (hasta 20 s) reduce requests vacíos y costo. **Delay queues** (hasta 15 min).
  - **DLQ** con `maxReceiveCount` para mensajes que fallan una y otra vez.
  - Escalar consumidores: ASG por la métrica `ApproximateNumberOfMessagesVisible` (backlog por instancia).
- **SNS**: pub/sub push; suscriptores SQS, Lambda, HTTP, email, SMS; **message filtering**; FIFO topics.
- **Fan-out**: SNS → varias colas SQS (cada sistema procesa a su ritmo y no se pierden mensajes).
- **EventBridge**: bus de eventos con **reglas por contenido** (eventos de AWS, de SaaS y propios), archive y replay, schema registry, **Pipes** y **Scheduler** (cron).
- **Amazon MQ**: ActiveMQ o RabbitMQ gestionado para migrar apps que usan protocolos estándar (AMQP, MQTT, JMS) sin reescribir.

## Autoevaluación
? Pedidos que se deben procesar en orden y sin duplicados. :: SQS FIFO.
? Un mensaje se procesa dos veces porque el proceso tarda 60 s. :: Subir el visibility timeout.
? App on-premises con JMS que migra sin cambiar código. :: Amazon MQ.
"""

G['SAA: API Gateway, Step Functions y AppSync'] = """
## Qué estudiar
- **API Gateway**
  - **REST API**: todas las funciones (API keys y usage plans, caché, validación de requests, WAF, private APIs). **HTTP API**: más simple, barata y rápida (JWT/OIDC, Lambda, HTTP). **WebSocket API**: comunicación bidireccional.
  - Tipos de endpoint: edge-optimized, regional y private (solo desde la VPC con interface endpoint).
  - **Throttling** (por defecto 10.000 req/s por región con burst; por stage y método; usage plans por cliente), **caché** de respuestas, timeout de integración de 29 s por defecto.
  - **Authorizers**: IAM, **Cognito user pools** (como este tracker), **Lambda authorizer** (lógica propia).
- **Step Functions**: orquestación con estados (Task, Choice, Parallel, Map, Wait), reintentos y manejo de errores, integraciones directas con más de 200 servicios. **Standard** (hasta 1 año, exactly-once, auditable) vs **Express** (alto volumen, hasta 5 min, at-least-once, más barato). Patrones: espera de callback (aprobación humana con task token).
- **AppSync**: APIs **GraphQL** gestionadas con suscripciones en tiempo real y sincronización offline.

## Autoevaluación
? Cobrar a clientes de tu API según un plan de requests. :: REST API con API keys y usage plans.
? Workflow de varios pasos con aprobación humana que puede tardar días. :: Step Functions Standard con callback.
"""

G['SAA: CloudFront y Global Accelerator'] = """
## Qué estudiar
- **CloudFront**
  - **Origins**: S3 (con **OAC**; reemplaza a OAI), ALB, EC2, API Gateway, cualquier HTTP; **origin groups** para failover de origen.
  - **Cache behaviors** por path (`/api/*` sin caché, `/static/*` con TTL largo); cache policies y origin request policies; TTL por defecto 24 h; **invalidations** (tienen costo).
  - **Signed URLs** (un archivo) vs **signed cookies** (muchos archivos, p. ej. una sección premium).
  - **Geo restriction**, **field-level encryption**, WAF, Shield, HTTPS con ACM (en us-east-1).
  - **Lambda@Edge** vs **CloudFront Functions**; price classes para limitar regiones y costo.
- **Global Accelerator**
  - **2 IPs anycast estáticas** globales; el tráfico entra a la red de AWS en el edge más cercano y va al endpoint sano (ALB, NLB, EC2, Elastic IP) en una o varias regiones.
  - Funciona con **TCP y UDP**, **no cachea**, failover regional en segundos, traffic dials y pesos.

## Cómo decidir
- Contenido HTTP cacheable (web, imágenes, video) → CloudFront.
- Juegos (UDP), VoIP, IoT, IPs fijas para whitelisting o failover regional muy rápido sin depender del TTL de DNS → Global Accelerator.

## Autoevaluación
? Video premium solo para suscriptores, muchos archivos. :: CloudFront con signed cookies.
? Juego multijugador UDP global con IPs fijas. :: Global Accelerator.
"""

G['SAA: Route 53 a fondo'] = """
## Qué estudiar
- **Registros**: A, AAAA, CNAME (**no en el apex** del dominio), MX, TXT, NS. **Alias** (de Route 53): apunta a recursos de AWS (ALB, CloudFront, S3 website, API Gateway, otro registro), **funciona en el apex** y **las consultas son gratis**.
- **Hosted zones** públicas y privadas (asociadas a VPCs). TTL.
- **Políticas de routing**
  - **Simple**: un registro (puede devolver varios valores al azar, sin health checks).
  - **Weighted**: porcentajes (canary, A/B).
  - **Latency**: la región con menor latencia para el usuario.
  - **Failover**: activo-pasivo con health check en el primario.
  - **Geolocation**: según la ubicación del usuario (país, continente) + registro default; para localización o restricciones legales.
  - **Geoproximity**: según la distancia, con **bias** para mover tráfico (con Traffic Flow).
  - **Multivalue answer**: hasta 8 registros sanos al azar (no reemplaza a un ELB).
  - **IP-based**: según el rango CIDR del cliente.
- **Health checks**: a endpoints, a otros health checks (calculated) o a **alarmas de CloudWatch** (para recursos privados).
- **Route 53 Resolver**: endpoints inbound y outbound para DNS híbrido.

## Autoevaluación
? Contenido en alemán para usuarios de Alemania por ley. :: Geolocation.
? Apuntar `ejemplo.com` (apex) a un ALB. :: Registro Alias.
? Mandar el 5% del tráfico a la versión nueva. :: Weighted.
"""

G['SAA: Redes híbridas y multi-VPC'] = """
## Qué estudiar
- **Site-to-Site VPN**: 2 túneles IPsec por conexión (HA) hacia un **Virtual Private Gateway** o un **Transit Gateway**; Customer Gateway en tu lado; hasta ~1,25 Gbps por túnel; se arma en minutos. **VPN CloudHub**: varias sedes se comunican a través de AWS.
- **Direct Connect**: conexión dedicada (1, 10, 100 Gbps) o **hosted** (desde 50 Mbps vía un partner); semanas de instalación; latencia consistente; **no cifrada por defecto** → **MACsec** o VPN sobre DX. **Virtual interfaces**: private (VPC), public (servicios públicos como S3) y transit (TGW). **Direct Connect Gateway**: un DX hacia VPCs de varias regiones.
- **Alta disponibilidad**: 2 DX en ubicaciones distintas (máxima resiliencia) o **DX + VPN de respaldo** (económico).
- **VPC peering**: 1 a 1, **no transitivo**, sin CIDRs superpuestos, entre cuentas y regiones; con muchas VPCs se vuelve una malla inmanejable.
- **Transit Gateway**: hub regional **transitivo** para miles de VPCs, VPNs y DX; route tables para segmentar; peering entre regiones; se comparte con RAM; ECMP para sumar ancho de banda de VPN.
- **PrivateLink**: exponer **un servicio** (detrás de un NLB) a otras VPCs o cuentas sin peering ni exponer la red completa; funciona con CIDRs superpuestos.
- **VPC Lattice**: conectividad de servicio a servicio (capa 7) entre VPCs y cuentas.

## Autoevaluación
? Conectar 30 VPCs entre sí y con on-premises. :: Transit Gateway.
? Ofrecer tu API a 200 clientes con VPCs que pueden tener los mismos CIDRs. :: PrivateLink (endpoint service con NLB).
? DX ya existe; respaldo barato. :: Site-to-Site VPN de backup.
"""

G['🎯 Simulacro SAA 1'] = """
## Cómo hacerlo (150 min)
- 65 preguntas en 130 min (160 si usarás ESL), condiciones reales, sin pausa.
- **Técnica SAA**
  1. Lee la **última frase** (qué piden y con qué criterio: costo, overhead, disponibilidad, rendimiento).
  2. Subraya los requisitos del escenario (RPO, "sin gestionar servidores", "mínimo cambio de código").
  3. Descarta las opciones que no cumplen un requisito duro.
  4. Entre las 2 que quedan, elige la que cumple el criterio con **menos esfuerzo operativo**.
- 20 min de análisis rápido por dominio (el análisis a fondo es el viernes).

## Referencia
- A esta altura 55–65% es normal. El aprobado (720) equivale a ~72%.
"""

G['SAA: Observabilidad para arquitectos'] = """
## Qué estudiar
- **CloudWatch Metrics**: EC2 trae métricas de hipervisor (CPU, red, disco); **memoria y espacio en disco requieren el CloudWatch agent**. Detailed monitoring = 1 min (por defecto 5 min). Métricas propias (custom) y de alta resolución (1 s).
- **Alarmas**: acciones a SNS, Auto Scaling y EC2 (stop, terminate, reboot, **recover**); composite alarms para reducir ruido.
- **CloudWatch Logs**: log groups con retención, **Logs Insights** (consultas), metric filters (crear métricas desde logs), subscription filters (a Lambda, Firehose u OpenSearch), export a S3.
- **EventBridge** para reaccionar a eventos (p. ej. cambios de estado de EC2).
- **X-Ray**: trazas distribuidas, mapa de servicios, latencias por segmento.
- **CloudTrail vs Config** (ya visto): quién hizo qué vs cómo estaba configurado.
- **Systems Manager**: Session Manager, Patch Manager, Run Command, State Manager, **Automation** (runbooks), Parameter Store, Inventory.
- **AWS Health**: eventos de AWS que afectan tus recursos (con EventBridge para automatizar).

## Tu tracker
- 3 alarmas útiles: errores de la Lambda > 0 en 5 min, duración p99 > 20 s (cerca del límite de 29 s) y 5XX de API Gateway > 1%.

## Autoevaluación
? Monitorear la memoria de una EC2. :: CloudWatch agent.
? Contar las veces que aparece "ERROR" en los logs y alertar. :: Metric filter + alarma.
"""

G['SAA: Optimización de cómputo'] = """
## Qué estudiar
- **On-Demand**: flexible y caro. **Savings Plans**: **Compute SP** (cualquier familia, región, SO, también Fargate y Lambda; hasta ~66%) vs **EC2 Instance SP** (familia y región fijas; hasta ~72%). **Reserved Instances**: Standard vs Convertible, regionales o zonales (las zonales reservan capacidad).
- **Spot**: hasta ~90% de descuento; aviso de **2 min**; **Spot Fleet / EC2 Fleet** con allocation strategies (price-capacity-optimized); ideal para batch, CI, big data, contenedores stateless. Mixto On-Demand + Spot en un ASG.
- **Capacity Reservations** (On-Demand reservado en una AZ, sin descuento, combinable con SP).
- **Right-sizing**: **Compute Optimizer** (recomendaciones con ML para EC2, ASG, EBS, Lambda y ECS), Cost Explorer.
- **Graviton** (ARM): hasta ~40% mejor precio-rendimiento.
- **Serverless y contenedores**: Lambda o Fargate para cargas intermitentes; apagar entornos de dev fuera de horario (Instance Scheduler).

## Autoevaluación
? Carga base estable + picos impredecibles. :: Savings Plans o RI para la base + On-Demand/Spot con Auto Scaling para los picos.
? Recomendaciones de tamaño de instancias basadas en el uso. :: Compute Optimizer.
"""

G['SAA: Costos de storage y de red'] = """
## Qué estudiar
- **Storage**: lifecycle a clases más baratas (respetando los mínimos de 30/90/180 días), Intelligent-Tiering para patrones desconocidos, borrar multipart incompletos y versiones viejas, gp2 → **gp3**, borrar snapshots y volúmenes huérfanos, EFS IA y Archive.
- **Transferencia de datos (trampas típicas)**
  - Entrada desde internet: **gratis**. Salida a internet: se cobra.
  - Entre AZs: se cobra en ambos sentidos; dentro de la misma AZ con IP privada: gratis.
  - Entre regiones: se cobra.
  - **NAT Gateway**: cobra por hora **y por GB**. Si el tráfico es a S3 o DynamoDB, un **gateway endpoint** lo hace gratis.
  - **CloudFront** reduce el egress del origen (y la transferencia de origen AWS a CloudFront es gratis).
  - Direct Connect: egress más barato que por internet para volúmenes grandes.
  - Mantener réplicas o tráfico chatty en la misma AZ cuando no se necesita HA en ese tramo.
- **BD**: Aurora Serverless v2 o instancias más chicas en dev; DynamoDB on-demand vs provisioned según el patrón; Redshift pausable.

## Práctica
- Lee el post "Overview of data transfer costs for common architectures" y anota 5 trampas con su solución.

## Autoevaluación
? Las instancias privadas suben 10 TB al mes a S3 por el NAT Gateway. ¿Cómo ahorras? :: Gateway endpoint de S3.
? ¿Se cobra la transferencia de internet hacia AWS? :: No.
"""

G['SAA: Herramientas de gestión de costos'] = """
## Qué estudiar
- **Cost Explorer**: análisis histórico, forecast, recomendaciones de RI y Savings Plans, rightsizing.
- **AWS Budgets**: costo, uso, cobertura y utilización de RI/SP; alertas por email o SNS; **budget actions** (aplicar una SCP o IAM policy, o detener instancias al superar el umbral).
- **Cost and Usage Report / Data Exports**: el detalle más granular a S3, para consultar con Athena o QuickSight.
- **Cost Anomaly Detection**: alertas de gastos inusuales con ML.
- **Cost allocation tags** (hay que **activarlas** en Billing para que aparezcan) y **Cost Categories**.
- **Organizations**: consolidated billing, descuentos por volumen, RI/SP compartidos (se puede desactivar el compartir).
- **Pricing Calculator** para estimar antes.

## Práctica
- Crea un Budget mensual con alerta al 80% y al 100% del pronóstico, y activa una cost allocation tag `Project`.

## Autoevaluación
? Detener automáticamente instancias de dev si el budget se pasa. :: Budget actions.
? Los tags no aparecen en Cost Explorer. :: Hay que activarlas como cost allocation tags.
"""

G['SAA: Revisión de errores del simulacro 1'] = """
## Método (50 min)
1. Pregunta por pregunta: por qué la correcta es correcta **y por qué cada incorrecta no** (en SAA las incorrectas suelen funcionar, pero con más costo u overhead).
2. Agrupa los errores por dominio y por tema.
3. Lista de los **15 conceptos más fallados** → cada uno a Anki con el contexto del escenario.
4. Si un tema aparece 3+ veces, relee su guía esta semana.
"""

G['SAA: Repaso — dominio Cost-Optimized + lab de costos'] = """
## Plan del sábado (120 min)
1. **40 min · Lab**: estima en **Pricing Calculator** el costo mensual de este tracker: API Gateway REST (~30.000 requests/mes), Lambda (128 MB, ~300 ms), DynamoDB on-demand (~1 GB, ~50.000 lecturas y escrituras), CloudWatch Logs, Cognito (1 MAU), S3 del state. Spoiler: queda en centavos; anota qué servicio dominaría si creciera 1.000×.
2. **50 min · Quiz**: 30 preguntas de costos.
3. **30 min · Análisis + Anki**.

## Checklist del dominio Cost-Optimized
- Modelos de compra y Spot · Compute Optimizer · Graviton · serverless.
- Clases de S3 y lifecycle · gp3 · snapshots huérfanos.
- Transferencia de datos: NAT vs endpoints, CloudFront, entre AZs y regiones.
- Cost Explorer, Budgets (actions), CUR, Anomaly Detection, tags.
"""

G['SAA: Cómo leer una pregunta de SAA'] = """
## Qué estudiar
- **Palabras clave → qué buscar**
  - **most cost-effective / lowest cost** → la opción más barata que cumpla (Spot, S3 IA/Glacier, serverless, gateway endpoint).
  - **least operational overhead** → servicio **gestionado o serverless** (Fargate > ECS on EC2 > EC2 a mano; Aurora > MySQL en EC2).
  - **highly available** → multi-AZ. **fault tolerant** → sin interrupción ante fallos. **disaster recovery** → otra región.
  - **minimal latency / high performance** → caché, CloudFront, placement groups, io2, DAX.
  - **decouple** → SQS, SNS, EventBridge. **real-time** → Kinesis. **minimal code changes** → lift-and-shift, servicios compatibles (RDS, Amazon MQ).
  - **securely** → cifrado, mínimo privilegio, endpoints privados.
- **Método**: requisito duro primero, luego el criterio de optimización. Desconfía de opciones que agregan componentes innecesarios o requieren scripts propios cuando hay un servicio gestionado.

## Práctica
- 20 preguntas en voz alta: para cada una di la keyword, el requisito duro y por qué descartas cada opción.

## Autoevaluación
? Dos opciones cumplen: una con EC2 + cron y otra con EventBridge Scheduler + Lambda. Pide least operational overhead. :: EventBridge Scheduler + Lambda.
"""

G['SAA: Patrones de arquitectura'] = """
## Qué estudiar (dibuja cada uno)
- **3 capas clásica**: Route 53 → ALB → ASG multi-AZ → RDS Multi-AZ + ElastiCache.
- **Web serverless**: CloudFront + S3 (frontend) → API Gateway → Lambda → DynamoDB, con Cognito para auth (este tracker, con GitHub Pages en vez de S3).
- **Event-driven**: S3 o una app emite eventos → EventBridge o SNS → colas SQS → Lambdas o ECS consumidores, con DLQs.
- **Fan-out**: SNS → varias SQS (inventario, email, analítica procesan el mismo pedido).
- **Procesamiento de archivos**: S3 upload → evento → SQS → workers con ASG por backlog → resultados en S3 y DynamoDB.
- **Microservicios**: ALB con routing por path o API Gateway → ECS/EKS por servicio, cada uno con su BD.
- **Streaming**: Kinesis Data Streams → Lambda o Flink → DynamoDB y Firehose → S3 → Athena.
- **Desacople para picos**: SQS como buffer entre la web y una BD que no escala rápido.

## Autoevaluación
? El procesamiento de imágenes se atrasa en Black Friday. :: SQS como buffer + ASG escalando por la profundidad de la cola.
"""

G['SAA: Alta disponibilidad multi-región'] = """
## Qué estudiar
- **Datos multi-región**: S3 CRR (y Multi-Region Access Points), **DynamoDB global tables** (activo-activo, last-writer-wins), **Aurora Global Database** (1 región de escritura + lectura en secundarias; failover gestionado), réplicas de RDS cross-region (se promueven), snapshots y AMIs copiados, ElastiCache Global Datastore.
- **Tráfico**: Route 53 **failover** (activo-pasivo) o **latency/geolocation** (activo-activo) con health checks; Global Accelerator para failover en segundos sin depender del TTL de DNS.
- **Infraestructura**: IaC (CloudFormation StackSets o Terraform) para re-crear todo en la otra región; AMIs y secretos replicados (Secrets Manager replication, KMS multi-region keys).
- **Activo-pasivo vs activo-activo**: el segundo exige resolver escrituras en dos lugares (DynamoDB global tables) o enrutar escrituras a una sola región.

## Práctica
- Lleva tu arquitectura de 3 capas a 2 regiones: ¿qué replicas, cómo enrutas, cuál es tu RPO y RTO?

## Autoevaluación
? Base relacional con lecturas locales en 3 continentes y DR. :: Aurora Global Database.
? Failover regional en segundos con IPs fijas. :: Global Accelerator.
"""

G['SAA: Seguridad de punta a punta en escenarios'] = """
## Qué estudiar (cómo combinar todo en un escenario)
- **Cifrado en tránsito**: TLS en CloudFront y ALB (ACM), HTTPS hasta el backend si se exige end-to-end, `aws:SecureTransport` en S3, TLS hacia RDS.
- **Cifrado en reposo**: KMS en EBS, S3, RDS, DynamoDB, EFS; customer managed keys si se necesita control o compartir entre cuentas.
- **Acceso**: roles en todas partes, Identity Center para personas, SCPs como guardarraíles, permission boundaries para delegar.
- **Red**: subnets privadas, endpoints de VPC para no salir a internet, SGs encadenados, WAF + Shield en el borde.
- **Multi-cuenta**: cuenta de **log archive** (CloudTrail de la organización, Config, VPC Flow Logs) y cuenta de **security tooling** (GuardDuty y Security Hub como administrador delegado).
- **Secretos**: Secrets Manager con rotación; nunca en el código ni en user data.
- **Detección y respuesta**: GuardDuty → EventBridge → Lambda o SSM Automation.

## Práctica
- 10 preguntas de escenario de seguridad. Meta ≥8/10.

## Autoevaluación
? Logs de CloudTrail que nadie de las cuentas de trabajo pueda borrar. :: Organization trail a un bucket en la cuenta de log archive con Object Lock y SCP que impida desactivarlo.
"""

G['SAA: Migración — las 7 R'] = """
## Qué estudiar
- **Retire**: apagar lo que ya no se usa. **Retain**: dejarlo on-premises por ahora.
- **Rehost** (lift-and-shift): mover tal cual a EC2 con **Application Migration Service (MGN)**. Rápido, con poco beneficio cloud.
- **Relocate**: mover a nivel de hipervisor (VMware Cloud on AWS) sin cambiar nada.
- **Replatform** (lift-tinker-shift): pequeños cambios para usar gestionados (MySQL en VM → RDS; app → Beanstalk).
- **Repurchase**: cambiar a SaaS (CRM propio → Salesforce).
- **Refactor / re-architect**: rediseñar cloud-native (monolito → microservicios serverless). Más beneficio y más esfuerzo.
- **Descubrimiento y planificación**: Application Discovery Service (agentes o agentless), Migration Hub, Migration Evaluator (business case).
- **Datos**: DMS + SCT, DataSync, Snow Family, Transfer Family.

## Autoevaluación
? Migrar 500 VMs al cloud en 3 meses con el menor cambio posible. :: Rehost con MGN.
? Pasar la base MySQL de una VM a un servicio gestionado sin tocar la app. :: Replatform a RDS for MySQL.
"""

G['🎯 Simulacro SAA 2'] = """
## Cómo hacerlo (150 min)
- 65 preguntas en 130 min (o 160 con ESL), banco distinto al simulacro 1.
- Aplica la técnica de keywords de esta semana.
- Análisis por dominio: este resultado define en qué te enfocas la semana que viene.

## Meta
- ≥72% (el aprobado es 720/1000).
"""

G['SAA: Refuerzo del dominio Secure'] = """
## Método (55 min)
1. Filtra los errores del simulacro 2 de este dominio.
2. Relee las guías de las sesiones correspondientes (S1–S2 del SAA).
3. 15 preguntas focalizadas.
4. Puntos que más caen: evaluación de policies, cross-account (rol vs resource policy), SCP, KMS (compartir snapshots cifrados), gateway vs interface endpoints, Object Lock, Secrets Manager vs Parameter Store, WAF vs Shield, GuardDuty vs Inspector vs Macie.
"""

G['SAA: Refuerzo del dominio Resilient'] = """
## Método (55 min)
1. Errores del simulacro 2 en este dominio → relee las guías de S3–S4 y SQS/SNS.
2. 15 preguntas focalizadas.
3. Puntos que más caen: multi-AZ en cada capa, NAT por AZ, ASG con health checks de ELB, Multi-AZ vs read replica, Aurora Global, estrategias de DR con RPO/RTO, desacople con SQS (visibility timeout, DLQ), Route 53 failover.
"""

G['SAA: Refuerzo del dominio High-Performing'] = """
## Método (55 min)
1. Errores del simulacro 2 en este dominio → relee las guías de S3 (cómputo) y S5 (bases de datos).
2. 15 preguntas focalizadas.
3. Puntos que más caen: elegir la BD por patrón de acceso, DAX vs ElastiCache, read replicas, gp3 vs io2, EFS vs FSx, S3 (multipart, Transfer Acceleration), CloudFront vs Global Accelerator, Kinesis vs Firehose, placement groups, concurrencia de Lambda.
"""

G['SAA: Refuerzo del dominio Cost-Optimized'] = """
## Método (55 min)
1. Errores del simulacro 2 en este dominio → relee las guías de S7.
2. 15 preguntas focalizadas.
3. Puntos que más caen: Savings Plans vs RI vs Spot, clases de S3 y sus mínimos, lifecycle, NAT Gateway vs gateway endpoint, transferencia entre AZs y regiones, CloudFront para egress, serverless para cargas intermitentes, DynamoDB on-demand vs provisioned, Budgets actions.
"""

G['SAA: Servicios que confunden'] = """
## Tabla final (hazla de memoria, luego corrige)
- **Gateway endpoint vs interface endpoint**: S3 y DynamoDB, gratis, ruta · casi todo, ENI, con costo, accesible desde on-premises.
- **ALB vs NLB vs GWLB**: L7 por path y host · L4, IP estática, UDP, millones de req/s · appliances.
- **SQS vs SNS vs EventBridge vs Kinesis**: cola · pub/sub · bus con reglas · stream con replay.
- **EFS vs FSx Windows vs FSx Lustre**: NFS Linux · SMB y AD · HPC con S3.
- **RDS Multi-AZ vs read replica vs Aurora Global**: HA · lecturas · DR multi-región con RPO de ~1 s.
- **DataSync vs Storage Gateway vs Transfer Family vs Snowball**: copiar online · acceso híbrido continuo · SFTP · offline.
- **CloudFront vs Global Accelerator**: caché HTTP · IPs anycast TCP/UDP.
- **Secrets Manager vs Parameter Store**: rotación, de pago · configuración, gratis.
- **Shield vs WAF vs Firewall Manager vs Network Firewall**: DDoS · L7 · gestión central · firewall de VPC.
- **GuardDuty vs Inspector vs Macie vs Detective**: amenazas · CVEs · PII · investigación.
- **Cognito user pool vs identity pool**: login y JWT · credenciales AWS.
- **DAX vs ElastiCache**: solo DynamoDB · cualquier fuente.
- **Lambda@Edge vs CloudFront Functions**: completo · liviano solo viewer.
- **Step Functions Standard vs Express**: largo y auditable · alto volumen y corto.
"""

G['🎯 Simulacro SAA 3'] = """
## Cómo hacerlo (150 min)
- Condiciones reales, banco distinto. Meta **≥78%**.
- Si estás por debajo de 72%, mueve el examen una o dos semanas: es mejor que reprobar (el reintento cuesta el examen completo y hay que esperar 14 días).
"""

G['SAA: Revisión de errores del simulacro 3'] = """
## Método (50 min)
- Solo los conceptos que **siguen** fallando después de 3 simulacros: son tus puntos ciegos.
- Actualiza tu tabla de servicios que confunden y tu cheat sheet.
- Cada error → Anki con el escenario.
"""

G['🎯 Simulacro SAA 4 — parte 1'] = """
## Cómo hacerlo (60 min)
- 33 preguntas en 65 min, banco nuevo (no repitas preguntas que ya viste: inflan el score).
- Meta ≥80%.
"""

G['🎯 Simulacro SAA 4 — parte 2'] = """
## Cómo hacerlo (60 min)
- 32 preguntas en 65 min + análisis de las dos partes.
- Compara contra los simulacros 2 y 3. Con ≥80% estás listo.
"""

G['SAA: Cheat sheet final y dominio más débil'] = """
## Qué hacer (45 min)
1. **25 min**: una hoja con todo lo que todavía te cuesta (tabla de servicios que confunden, mínimos de S3, estrategias de DR, keywords).
2. **20 min**: 10 preguntas del dominio más débil.
"""

G['SAA: Repaso ligero y logística del examen'] = """
## Hoy (30 min)
- Solo el cheat sheet. Nada nuevo.
- Logística: system test de OnVUE o ruta al centro Pearson; ID vigente; **ESL +30 aplicado** a la reserva; dormir temprano.

## Durante el examen
- 130 min (160 con ESL) para 65 preguntas: ~2 min por pregunta.
- Primera pasada completa marcando las dudosas; segunda pasada solo por las marcadas.
- No dejes nada en blanco.
"""

G['🏆 EXAMEN AWS Solutions Architect Associate'] = """
## Datos del examen (SAA-C03)
- 65 preguntas (50 puntúan), 130 min (+30 con ESL), aprobado **720/1000**.
- Dominios: Design Secure Architectures 30% · Resilient 26% · High-Performing 24% · Cost-Optimized 20%.

## Estrategia
- Lee la última frase primero: ahí está el criterio (costo, overhead, disponibilidad, rendimiento).
- Requisito duro → descarta. Criterio de optimización → elige.
- Ante la duda, el servicio gestionado con menos piezas suele ganar.

## Después
- Con esto completas las 5 certificaciones. AI Engineer arranca el lunes siguiente.
"""
