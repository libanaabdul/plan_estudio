# Guías detalladas — AWS Cloud Practitioner (CLF-C02)
# Formato: ## título · - viñeta · 1. paso · > trampa/tip · ? pregunta :: respuesta · `código` · **negrita**
G = {}

G['CP: Conceptos de nube y reserva del examen'] = """
## Qué estudiar
- **Cloud computing** = entrega bajo demanda de recursos de TI por internet con **pago por uso**. Lo opuesto: comprar servidores (CAPEX) y adivinar capacidad.
- **Las 6 ventajas oficiales** (se preguntan casi textuales):
  1. Cambiar gasto fijo (CAPEX) por gasto variable (OPEX).
  2. Beneficiarse de las economías de escala masivas (AWS compra en volumen → precios más bajos).
  3. Dejar de adivinar la capacidad (escalas según demanda real).
  4. Aumentar la velocidad y la agilidad (recursos en minutos, no semanas).
  5. Dejar de gastar en operar y mantener data centers.
  6. Volverse global en minutos (desplegar en varias regiones).
- **Modelos de servicio**: IaaS (tú gestionas SO y app: EC2), PaaS (tú solo la app: Elastic Beanstalk), SaaS (todo gestionado: Amazon WorkMail, Gmail).
- **Modelos de despliegue**: nube (todo en AWS), on-premises/privada, **híbrida** (parte en AWS conectada a tu data center).
- **Características de la nube**: autoservicio bajo demanda, acceso amplio por red, multi-tenancy y pooling de recursos, elasticidad rápida, servicio medido.

## Lo que más pregunta el examen
- Escenarios que describen una ventaja y te piden su nombre. "Ya no compran servidores para el pico de Black Friday" → **dejar de adivinar la capacidad**.
- "La empresa paga solo lo que consume" → **gasto variable**.
- Diferencia entre **elasticidad** (sube y baja automático con la demanda) y **escalabilidad** (puede crecer).

## Trampas
> "Economías de escala" se refiere a los precios que baja AWS, no a que tú escales tu app.
> Hacer lift-and-shift a EC2 sigue siendo IaaS: el parche del SO es tuyo.

## Práctica
1. Si vas a rendir en inglés: entra a la cuenta de AWS Certification (aws.training/certification) → Request Exam Accommodations → **ESL +30 MINUTES**. Hazlo ANTES de reservar.
2. Reserva el examen CLF-C02 para la fecha del banner (online OnVUE o centro Pearson).
3. Descarga el exam guide y lee la lista de servicios "in scope".
4. Crea en Anki el mazo "AWS::CP" con 10 tarjetas: las 6 ventajas + IaaS/PaaS/SaaS + elasticidad.

## Autoevaluación
? Una startup no quiere invertir en hardware antes de saber si su producto funciona. ¿Qué ventaja aplica? :: Cambiar gasto fijo por variable (y dejar de adivinar capacidad).
? ¿Elastic Beanstalk es IaaS, PaaS o SaaS? :: PaaS: subes el código y AWS gestiona la infraestructura.
? ¿Qué modelo de despliegue usa una empresa con su data center conectado a AWS por VPN? :: Híbrido.
"""

G['CP: Well-Architected y Cloud Adoption Framework'] = """
## Qué estudiar
- **AWS Well-Architected Framework: 6 pilares**
  - **Operational Excellence**: automatizar, cambios pequeños y reversibles, IaC, aprender de los fallos (runbooks, post-mortems).
  - **Security**: identidades con mínimo privilegio, trazabilidad (CloudTrail), cifrado en tránsito y reposo, seguridad en todas las capas.
  - **Reliability**: recuperarse de fallos, escalar horizontalmente, probar la recuperación, multi-AZ.
  - **Performance Efficiency**: usar el recurso correcto (serverless, tipo de instancia), ir global, experimentar.
  - **Cost Optimization**: pagar solo lo que usas, medir eficiencia, dejar de gastar en data centers.
  - **Sustainability**: minimizar el impacto ambiental, maximizar la utilización, usar instancias eficientes (Graviton).
- **Well-Architected Tool**: servicio gratuito en la consola para revisar una carga contra los pilares.
- **AWS Cloud Adoption Framework (CAF): 6 perspectivas**
  - De negocio: **Business**, **People** (cultura, capacitación), **Governance** (riesgo, portafolio).
  - Técnicas: **Platform** (arquitectura), **Security**, **Operations**.
- Fases del CAF: **Envision → Align → Launch → Scale**.

## Lo que más pregunta el examen
- Te describen una práctica y preguntan el pilar. "Recuperarse automáticamente de un fallo" → Reliability. "Usar la instancia del tamaño correcto" → Performance Efficiency o Cost Optimization (lee bien el objetivo).
- "Capacitar al personal en cloud" → perspectiva **People** del CAF.

## Trampas
> Sustainability es el 6º pilar (se agregó en 2021). Muchos materiales viejos dicen 5.
> Governance (CAF) ≠ Security: Governance es gestión de riesgo y beneficios de negocio.

## Práctica
1. Abre la Well-Architected Tool en la consola y mira las preguntas del pilar Security (solo lectura).
2. Para cada pilar escribe 1 ejemplo de tu trabajo (p. ej. "tenemos Terraform en CI" → Operational Excellence).

## Autoevaluación
? "Desplegar en varias AZs para tolerar la caída de una" ¿qué pilar? :: Reliability.
? ¿Qué perspectiva del CAF cubre la gestión de capacidades y la capacitación del equipo? :: People.
? ¿Qué pilar recomienda instancias Graviton para reducir energía? :: Sustainability (y también ahorra costo).
"""

G['CP: Infraestructura global'] = """
## Qué estudiar
- **Región**: área geográfica con varias AZs, aisladas entre sí. Los datos NO salen de la región salvo que tú lo configures (data residency).
- **Availability Zone (AZ)**: uno o más data centers con energía, red y conectividad redundantes. Cada región tiene **mínimo 3 AZs**. Las AZs están separadas físicamente y conectadas con baja latencia.
- **Edge locations / PoPs**: puntos de presencia para **CloudFront** (CDN), **Route 53** (DNS) y Global Accelerator. Son muchos más que las regiones.
- **Local Zones**: extienden una región a una ciudad para latencia de un dígito de ms.
- **Wavelength Zones**: infraestructura dentro de redes **5G** de operadores.
- **AWS Outposts**: racks de AWS instalados en TU data center (híbrido).
- **Cómo elegir región**: 1) compliance / requisitos legales de datos, 2) cercanía a los usuarios (latencia), 3) servicios disponibles en esa región, 4) precio (varía por región).
- **Servicios globales vs regionales**: IAM, Route 53, CloudFront y WAF en CloudFront son globales; EC2, RDS y la mayoría son regionales; EC2 y las subnets viven en una AZ.

## Lo que más pregunta el examen
- "Alta disponibilidad" → varias **AZs**. "Disaster recovery ante la caída de una región entera" → varias **regiones**.
- "Contenido cerca de los usuarios con baja latencia" → **edge locations + CloudFront**.
- "Los datos deben quedarse en Alemania" → elegir la región por **compliance**.

## Trampas
> Una AZ NO es un solo data center; puede ser varios.
> Las edge locations no ejecutan tus EC2.

## Práctica
1. En la consola, abre el selector de región y cuenta cuántas regiones ves. Mira en la página de infraestructura global cuántas AZs tiene us-east-1.
2. Dibuja: Región → 3 AZs → data centers; y aparte las edge locations.

## Autoevaluación
? ¿Cuál es el primer criterio para elegir región si hay leyes de residencia de datos? :: Compliance o requisitos legales.
? ¿Qué servicio pone hardware de AWS en tu propio data center? :: AWS Outposts.
? ¿Es IAM regional o global? :: Global.
"""

G['CP: EC2 y modelos de compra'] = """
## Qué estudiar
- **Familias de instancias**: General purpose (T, M: equilibradas), Compute optimized (C: batch, gaming, HPC), Memory optimized (R, X: bases de datos en memoria), Storage optimized (I, D: mucho I/O local), Accelerated (P, G, Inf, Trn: GPU/ML).
- **Modelos de compra**:
  - **On-Demand**: por segundo/hora, sin compromiso. Para cargas cortas o impredecibles.
  - **Reserved Instances (RI)**: compromiso de 1 o 3 años, **hasta ~72% de descuento**. Standard (más descuento, no cambias familia) vs Convertible (puedes cambiar de familia). Pago All/Partial/No Upfront.
  - **Savings Plans**: compromiso de **$/hora** por 1 o 3 años. **Compute SP** (flexible: cualquier familia, región, también Fargate y Lambda) vs **EC2 Instance SP** (familia fija en una región, más descuento).
  - **Spot**: capacidad sobrante, **hasta ~90% de descuento**, AWS la puede recuperar con **2 minutos de aviso**. Para cargas tolerantes a interrupciones (batch, CI, análisis).
  - **Dedicated Hosts**: servidor físico entero para ti; necesario para **licencias por socket/core (BYOL)** y compliance.
  - **Dedicated Instances**: hardware dedicado sin control del host.
  - **Capacity Reservations**: reservas capacidad en una AZ sin descuento (se combinan con SP).

## Lo que más pregunta el examen
- Carga estable 24/7 por años → **RI o Savings Plans**.
- Puede interrumpirse sin problema → **Spot**.
- Licencia de software ligada al servidor físico → **Dedicated Hosts**.
- Prueba de 2 semanas, impredecible → **On-Demand**.

## Trampas
> Spot NO sirve para una base de datos de producción ni para nada que no tolere cortes.
> Dedicated Instance ≠ Dedicated Host: solo el Host te da visibilidad de sockets y cores para licencias.

## Práctica
1. Abre la página de precios de EC2 y compara una m7g.large On-Demand con Savings Plans a 1 año.
2. Escribe 5 escenarios y su modelo de compra; justifica cada uno en una línea.

## Autoevaluación
? Un proceso batch nocturno que puede reintentarse si se corta. :: Spot.
? Quieres descuento pero vas a migrar de EC2 a Fargate el próximo año. :: Compute Savings Plan.
? Licencia de Windows Server por core físico. :: Dedicated Host.
"""

G['CP: ELB, Auto Scaling y alta disponibilidad'] = """
## Qué estudiar
- **Elastic Load Balancing** distribuye tráfico entre targets sanos con health checks.
  - **ALB** (capa 7: HTTP/HTTPS): enruta por path (`/api`) o host; ideal para web y microservicios.
  - **NLB** (capa 4: TCP/UDP): millones de req/s, latencia ultra baja, IP estática.
  - **GWLB** (capa 3): para appliances de seguridad de terceros (firewalls).
- **EC2 Auto Scaling**: agrega o quita instancias según demanda; usa un **launch template**; define mínimo, deseado y máximo. Reemplaza instancias no sanas.
- **Alta disponibilidad** = repartir en **varias AZs** detrás de un ELB.
- **Escalado vertical** (instancia más grande) vs **horizontal** (más instancias). La nube favorece el horizontal.
- **Elasticidad** (ajuste automático hacia arriba y abajo) vs **escalabilidad** (capacidad de crecer) vs **agilidad** (rapidez para experimentar).

## Lo que más pregunta el examen
- "Distribuir tráfico web entre varias instancias" → ELB (ALB).
- "Ajustar automáticamente el número de instancias" → Auto Scaling.
- "Tolerar la falla de un data center" → multi-AZ.

## Trampas
> Un ELB no escala instancias; eso lo hace Auto Scaling. Trabajan juntos.
> Que el ELB esté en varias AZs no basta: las instancias también tienen que estarlo.

## Práctica
1. Dibuja: usuarios → ALB → Auto Scaling Group (min 2, max 6) en AZ-a y AZ-b.
2. Explica en voz alta qué pasa si AZ-a cae (el ALB deja de mandar tráfico y el ASG lanza reemplazos en AZ-b).

## Autoevaluación
? ¿Qué balanceador usas para enrutar `/imagenes` y `/api` a grupos distintos? :: ALB.
? Necesitas una IP fija para el balanceador y tráfico TCP. :: NLB.
? ¿Qué es más "cloud": escalar vertical u horizontal? :: Horizontal.
"""

G['CP: Repaso S1 + lab en la consola'] = """
## Plan del sábado (90 min)
1. **15 min · Seguridad de la cuenta primero**: activa **MFA en el usuario root**, crea un usuario o acceso con Identity Center para el día a día y no uses root.
2. **10 min · Budget**: Billing → Budgets → *Zero spend budget* o un budget mensual de US$5 con alerta al 80% a tu email.
3. **20 min · Lab EC2**: lanza una instancia del free tier (t3.micro o la que diga Free Tier), Amazon Linux, sin key pair, conéctate con **EC2 Instance Connect**, ejecuta `curl http://169.254.169.254/latest/meta-data/` (verás que IMDSv2 exige token), y **termínala**.
4. **35 min · Quiz**: 25 preguntas solo de conceptos, Well-Architected, infraestructura global, EC2 y ELB.
5. **10 min · Anki**: cada fallo se vuelve una tarjeta pregunta → respuesta + "por qué".

## Qué observar en el lab
- La instancia vive en **una AZ** (mírala en los detalles).
- El **Security Group** creado por defecto permite SSH: es un firewall stateful a nivel de instancia.
- Terminate ≠ Stop: stop conserva el volumen EBS (pagas storage); terminate lo borra (si "delete on termination").

## Autoevaluación
? ¿Por qué no usar el usuario root a diario? :: Tiene acceso total sin restricciones; se protege con MFA y se usa solo para tareas que lo requieren.
? ¿Pagas EC2 con la instancia detenida? :: No pagas cómputo, pero sí el volumen EBS.
"""

G['CP: S3 — clases y ciclo de vida'] = """
## Qué estudiar
- **S3** = almacenamiento de **objetos** en **buckets** (nombre único global; el bucket vive en una región). Objetos de hasta **5 TB**. Durabilidad de **99,999999999% (11 nueves)** en todas las clases.
- **Clases de almacenamiento**
  - **Standard**: acceso frecuente, 99,99% de disponibilidad.
  - **Intelligent-Tiering**: mueve objetos solo entre niveles según el uso; sin cargos de recuperación; cobra un pequeño monitoreo por objeto. Para patrones **desconocidos o cambiantes**.
  - **Standard-IA**: acceso poco frecuente pero inmediato; cobra por GB recuperado; mínimo 30 días.
  - **One Zone-IA**: como IA pero en **una sola AZ** (más barato, se pierde si cae la AZ). Para datos re-creables.
  - **Glacier Instant Retrieval**: archivo con acceso en milisegundos, consultado ~1 vez por trimestre.
  - **Glacier Flexible Retrieval**: recuperación de minutos a horas.
  - **Glacier Deep Archive**: lo más barato; recuperación en **hasta 12 h** (bulk hasta 48 h). Retención legal de 7–10 años.
- **Lifecycle rules**: transicionan objetos (p. ej. Standard → IA a los 30 días → Glacier a los 90) o los expiran.
- **Versioning**: guarda versiones y protege contra borrados accidentales. **Replicación**: CRR (otra región) / SRR (misma región); requiere versioning.
- **Seguridad**: bucket policies, **Block Public Access** (activado por defecto), cifrado por defecto (SSE-S3).
- **Static website hosting**.

## Lo que más pregunta el examen
- "Archivo que se consulta casi nunca, puede esperar horas" → **Glacier Deep Archive**.
- "Patrón de acceso desconocido" → **Intelligent-Tiering**.
- "Copias que se pueden regenerar, al menor costo con acceso inmediato" → **One Zone-IA**.

## Trampas
> Todas las clases tienen 11 nueves de **durabilidad**; lo que cambia es la **disponibilidad** y el costo de acceso.
> S3 no es un disco montable para un SO: para eso existen EBS o EFS.

## Práctica
1. Crea un bucket, sube un archivo y cambia su clase a Standard-IA desde la consola.
2. Crea una lifecycle rule: a los 30 días → Standard-IA, a los 90 → Glacier Flexible, a los 365 → expirar.
3. Activa versioning, borra el archivo y recupéralo quitando el delete marker.

## Autoevaluación
? Logs que se analizan el primer mes y luego se guardan 7 años por ley. :: Lifecycle: Standard → (IA) → Glacier Deep Archive.
? ¿Qué se necesita activar para replicar a otra región? :: Versioning en origen y destino.
? ¿Qué clase guarda datos en una sola AZ? :: One Zone-IA.
"""

G['CP: EBS, EFS, backup y transferencia'] = """
## Qué estudiar
- **Tipos de almacenamiento**: **bloque** (EBS: disco de una instancia), **archivo** (EFS / FSx: sistema de archivos compartido), **objeto** (S3: por HTTP).
- **EBS**: volumen de red atado a **una AZ**; normalmente se conecta a una instancia a la vez. Persiste aunque detengas la instancia. **Snapshots** incrementales que se guardan en S3 (regionales, se copian entre regiones). Tipos: SSD gp3/io2, HDD st1/sc1.
- **Instance Store**: disco físico del host, muy rápido pero **efímero** (se pierde al detener o terminar).
- **EFS**: NFS gestionado para **Linux**, compartido por **muchas instancias en varias AZs**, crece solo. Clases Standard e Infrequent Access.
- **FSx**: sistemas de archivos de terceros gestionados: **FSx for Windows File Server** (SMB, Active Directory), **FSx for Lustre** (HPC, ML), NetApp ONTAP, OpenZFS.
- **AWS Backup**: backups centralizados y programados de EBS, RDS, DynamoDB, EFS, etc., con políticas.
- **Storage Gateway**: conecta on-premises con almacenamiento AWS (File, Volume, Tape Gateway).
- **Snow Family**: dispositivos físicos para mover **TB–PB offline** cuando la red es lenta.
- **DataSync**: transferencia **online** programada desde NFS/SMB a S3, EFS o FSx.

## Lo que más pregunta el examen
- "Varias instancias Linux comparten archivos" → **EFS**.
- "Windows con SMB y AD" → **FSx for Windows**.
- "Disco para una base de datos en EC2" → **EBS**.
- "Migrar 500 TB con poco ancho de banda" → **Snowball**.

## Trampas
> EBS no se comparte entre AZs; para mover un volumen: snapshot → crear el volumen en otra AZ.
> Instance store pierde los datos al detener la instancia.

## Práctica
1. Arma una tabla de 3 columnas (EBS / EFS / S3) con: tipo, alcance (AZ, región), acceso (1 instancia, muchas, HTTP), caso de uso.
2. Reprodúcela de memoria al final de la sesión.

## Autoevaluación
? ¿Dónde se guardan los snapshots de EBS? :: En S3, gestionado por AWS, a nivel regional.
? ¿Qué servicio usas para replicar archivos on-premises a S3 cada noche por la red? :: DataSync.
? ¿Qué almacenamiento desaparece si detienes la instancia? :: Instance Store.
"""

G['CP: VPC y seguridad de red'] = """
## Qué estudiar
- **VPC**: tu red privada aislada en una región, con un rango CIDR (p. ej. 10.0.0.0/16).
- **Subnets**: viven en **una AZ**. **Pública** = su route table tiene ruta 0.0.0.0/0 → **Internet Gateway**. **Privada** = no tiene esa ruta; sale a internet por un **NAT Gateway** que está en una subnet pública.
- **Internet Gateway**: permite tráfico entre la VPC e internet.
- **NAT Gateway**: permite que instancias privadas **salgan** a internet sin ser accesibles desde afuera.
- **Security Group** (a nivel de instancia o ENI): **stateful** (la respuesta vuelve sola), **solo reglas allow**, por defecto niega toda entrada y permite toda salida.
- **Network ACL** (a nivel de subnet): **stateless** (hay que permitir el retorno), reglas **allow y deny** numeradas y evaluadas en orden.
- **VPC Peering**: conecta 2 VPCs con IPs privadas (no es transitivo). **VPC Flow Logs**: registro del tráfico IP.
- **Conectividad on-premises**: Site-to-Site VPN (por internet, cifrada) o Direct Connect (línea dedicada).

## Lo que más pregunta el examen
- "Bloquear una IP específica a nivel de subnet" → **NACL** (los SG no pueden denegar).
- "Firewall stateful a nivel de instancia" → **Security Group**.
- "Servidores de base de datos sin acceso desde internet" → **subnet privada**.

## Trampas
> Los Security Groups no tienen reglas de deny.
> Un NAT Gateway da salida, no entrada.

## Práctica
1. Dibuja una VPC con subnet pública (web) y privada (BD) en 1 AZ, con IGW, NAT Gateway y las route tables.
2. Pon un SG en cada capa: web permite 443 desde 0.0.0.0/0; BD permite 5432 solo desde el SG web.

## Autoevaluación
? ¿Qué hace que una subnet sea pública? :: Su route table tiene una ruta a un Internet Gateway.
? ¿SG o NACL para "deny explícito"? :: NACL.
? ¿Una instancia privada que necesita descargar parches sale por...? :: NAT Gateway.
"""

G['CP: Route 53, CloudFront y conectividad'] = """
## Qué estudiar
- **Route 53**: DNS gestionado + registro de dominios + **health checks**. Políticas de routing: simple, weighted (porcentajes), latency (región más cercana), failover (activo-pasivo), geolocation (según el país del usuario).
- **CloudFront**: CDN que **cachea** contenido en edge locations; reduce la latencia y la carga en el origen (S3, ALB, EC2). Integra **AWS Shield Standard** y WAF.
- **Global Accelerator**: usa la red global de AWS con **2 IPs anycast estáticas** para TCP/UDP; **no cachea**; failover rápido entre regiones.
- **Site-to-Site VPN**: túnel **IPsec cifrado sobre internet**; se arma en minutos; ancho de banda y latencia variables.
- **Direct Connect (DX)**: conexión **física dedicada** a AWS; latencia consistente y mucho ancho de banda; tarda **semanas** en instalarse; **no cifrada por defecto** (se puede poner una VPN encima).
- **AWS Client VPN**: para que usuarios individuales se conecten a la VPC.

## Lo que más pregunta el examen
- "Latencia consistente y alto ancho de banda hacia el data center" → **Direct Connect**.
- "Conexión cifrada rápida y barata" → **Site-to-Site VPN**.
- "Distribuir video y contenido estático globalmente" → **CloudFront**.
- "Enviar al usuario a la región con menor latencia" → Route 53 **latency routing**.

## Trampas
> Global Accelerator no es una CDN: no guarda caché.
> Direct Connect no va por internet, pero tampoco está cifrado por defecto.

## Práctica
1. Para 3 escenarios (backup nocturno de 50 TB por mes / oficina pequeña / trading con latencia estable) elige DX o VPN y justifica.
2. Escribe qué política de Route 53 usarías para enviar el 10% del tráfico a una versión nueva (weighted).

## Autoevaluación
? Necesitas conectividad on-premises mañana mismo. :: Site-to-Site VPN (DX tarda semanas).
? ¿Qué servicio cachea en el edge? :: CloudFront.
? ¿Política de Route 53 para activo-pasivo con health checks? :: Failover.
"""

G['CP: Bases de datos — cuál para cada caso'] = """
## Qué estudiar
- **RDS**: bases relacionales gestionadas (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2). AWS hace parches, backups automáticos y snapshots.
  - **Multi-AZ**: réplica **standby** síncrona en otra AZ con failover automático → **alta disponibilidad** (no sirve para leer).
  - **Read Replicas**: copias asíncronas para **escalar lecturas** (pueden estar en otra región).
- **Aurora**: relacional compatible con MySQL/PostgreSQL creada por AWS; más rendimiento, 6 copias en 3 AZs, Aurora Serverless.
- **DynamoDB**: NoSQL **key-value**, serverless, latencia de milisegundos a cualquier escala, global tables. (Este tracker la usa.)
- **ElastiCache** (Redis/Valkey/Memcached): caché en memoria → microsegundos; reduce la carga de la BD.
- **Redshift**: **data warehouse** para analítica (OLAP) con SQL sobre grandes volúmenes.
- **Otras**: DocumentDB (documentos, compatible con MongoDB), Neptune (grafos: redes sociales, fraude), Keyspaces (Cassandra), Timestream (series de tiempo), QLDB fue retirado.
- **DMS**: Database Migration Service para migrar BDs con mínimo downtime.

## Lo que más pregunta el examen
- "Alta disponibilidad de la BD relacional" → **RDS Multi-AZ**. "Escalar lecturas" → **Read Replicas**.
- "Analítica sobre petabytes" → **Redshift**. "Relaciones complejas entre entidades" → **Neptune**.
- "Responsabilidad del cliente en RDS": la configuración, el acceso y los datos; el parche del SO lo hace AWS.

## Trampas
> Multi-AZ no mejora el rendimiento de lectura; las Read Replicas sí.
> Si te piden "instalar Oracle en EC2", la gestión es toda tuya; con RDS es gestionada.

## Práctica
1. 6 casos para asignar BD: carrito de compras serverless (DynamoDB), ERP con SQL (RDS/Aurora), ranking en tiempo real (ElastiCache), BI de 5 años de ventas (Redshift), recomendaciones "amigos de amigos" (Neptune), migración de MongoDB (DocumentDB).

## Autoevaluación
? ¿Qué ofrece DynamoDB que RDS no? :: Serverless key-value con escala prácticamente ilimitada y latencia de ms.
? La aplicación lee mucho y la BD RDS va lenta. :: Read Replicas (o ElastiCache).
"""

G['CP: Repaso S2 + mini-quiz'] = """
## Plan del sábado (90 min)
1. **15 min · Relee tus fallos** de la semana en Anki.
2. **40 min · Quiz de 30 preguntas**: S3, EBS/EFS, VPC, Route 53/CloudFront, bases de datos. Sin mirar apuntes, a ritmo de ~1 min por pregunta.
3. **25 min · Análisis**: por cada error escribe "elegí X porque…, la correcta es Y porque…".
4. **10 min · Tarjetas**: los fallos van a Anki.

## Mini-repaso para antes del quiz
- S3 = objetos · EBS = bloque en 1 AZ · EFS = archivos Linux multi-AZ · FSx = Windows/Lustre.
- Subnet pública = ruta al IGW · NAT = salida · SG stateful allow · NACL stateless allow+deny.
- DX = dedicado, semanas · VPN = cifrado, minutos · CloudFront = caché · Global Accelerator = IPs estáticas.
- Multi-AZ = HA · Read Replica = lectura · Redshift = analítica · DynamoDB = key-value serverless.

## Meta
- ≥80%. Si sacas menos, vuelve a leer la guía de la sesión con más errores antes del lunes.
"""

G['CP: Serverless y mensajería'] = """
## Qué estudiar
- **Serverless** = no gestionas servidores, escala automática y pagas por uso.
- **AWS Lambda**: ejecuta código por eventos; se cobra por número de invocaciones + duración (ms) × memoria; máximo **15 min** por ejecución. Triggers: API Gateway, S3, DynamoDB Streams, SQS, EventBridge.
- **Amazon SQS**: **cola** de mensajes; desacopla productor y consumidor; los mensajes esperan hasta que alguien los procese (pull). Standard vs FIFO (orden exacto).
- **Amazon SNS**: **pub/sub**; un mensaje llega a muchos suscriptores a la vez (push: email, SMS, Lambda, SQS).
- **EventBridge**: bus de eventos con reglas (eventos de AWS, SaaS o propios) + scheduler.
- **API Gateway**: crea APIs REST/HTTP/WebSocket delante de Lambda u otros backends.
- **Step Functions**: orquesta pasos (workflows visuales) con reintentos y ramas.
- **Fargate**: contenedores serverless (lo ves mañana).

## Arquitectura de este tracker (tu ejemplo real)
- Navegador → **API Gateway** (con authorizer de **Cognito**) → **Lambda** (Python) → **DynamoDB**. No hay un solo servidor que parchear.

## Lo que más pregunta el examen
- "Desacoplar componentes para que un pico no tumbe al consumidor" → **SQS**.
- "Notificar a varios sistemas al mismo tiempo" → **SNS** (fan-out).
- "Ejecutar código sin servidores cuando se sube un archivo a S3" → **Lambda**.

## Trampas
> SQS es pull (el consumidor pregunta); SNS es push.
> Lambda no es para procesos de horas; se corta a los 15 min.

## Práctica
1. 4 escenarios: pedidos que se procesan en orden (SQS FIFO), alerta a email + Slack (SNS), job cada noche a las 2 (EventBridge Scheduler + Lambda), proceso de 3 pasos con reintentos (Step Functions).
2. Explica en voz alta el flujo de este tracker.

## Autoevaluación
? ¿Cómo se cobra Lambda? :: Por invocaciones y por duración × memoria asignada.
? Un mensaje debe llegar a 5 colas distintas. :: SNS con 5 colas SQS suscritas (fan-out).
"""

G['CP: Contenedores, despliegue e IaC'] = """
## Qué estudiar
- **Amazon ECS**: orquestador de contenedores propio de AWS. **Amazon EKS**: Kubernetes gestionado (para quien ya usa K8s o quiere portabilidad).
- **Launch types**: **EC2** (tú gestionas las instancias del cluster) o **Fargate** (serverless: solo defines CPU y memoria por tarea).
- **ECR**: registro privado de imágenes de contenedores.
- **Elastic Beanstalk**: **PaaS**; subes el código y crea EC2, ELB, ASG y monitoreo por ti. Tú sigues teniendo acceso a los recursos.
- **CloudFormation**: **IaC** nativo de AWS (YAML/JSON → stacks). Es el equivalente de Terraform. **AWS CDK**: IaC en lenguajes de programación que genera CloudFormation.
- **Otros**: **Lightsail** (VPS sencillo a precio fijo), **Amplify** (web y móvil full-stack), **App Runner** (web desde un contenedor o código sin gestionar nada), CodePipeline, CodeBuild y CodeDeploy (CI/CD), Systems Manager (gestión de flotas).

## Lo que más pregunta el examen
- "Desplegar una web sin saber de infraestructura" → **Elastic Beanstalk** (o Lightsail si es simple).
- "Infraestructura como código, repetible en varias cuentas y regiones" → **CloudFormation**.
- "Contenedores sin gestionar servidores" → **Fargate**.
- "Ya usamos Kubernetes on-premises" → **EKS**.

## Trampas
> Beanstalk no es serverless: crea EC2 que puedes ver.
> CloudFormation no cuesta (pagas los recursos que crea).

## Práctica
1. Escribe en 2 frases la diferencia Beanstalk vs CloudFormation.
2. Relaciónalo con tu trabajo: ¿qué equivale en CloudFormation a un módulo de Terraform? (nested stacks / módulos).

## Autoevaluación
? ¿Qué servicio guarda imágenes Docker privadas? :: Amazon ECR.
? Contenedores, sin EC2 que parchear. :: ECS o EKS con Fargate.
"""

G['CP: IAM a fondo'] = """
## Qué estudiar
- **Root user**: el email con el que creaste la cuenta; acceso total. Activa **MFA**, no crees access keys y úsalo solo para tareas que lo exigen (cambiar plan de soporte, cerrar la cuenta, cambiar email de root).
- **IAM users** (personas o apps con credenciales de largo plazo), **groups** (asignar permisos a muchos usuarios), **roles** (credenciales **temporales** que se asumen: servicios como EC2/Lambda, otras cuentas, federación).
- **Policies**: documentos JSON con `Effect`, `Action`, `Resource` y `Condition` opcional. AWS managed vs customer managed vs inline.
- **Principio de mínimo privilegio**: dar solo los permisos necesarios.
- **Buenas prácticas**: MFA, roles en vez de access keys para apps en AWS, rotar credenciales, usar grupos, **IAM Access Analyzer**, credential report.
- **IAM Identity Center** (ex-AWS SSO): acceso de la fuerza laboral a varias cuentas con un solo login.
- **AWS Organizations**: agrupa cuentas en **OUs**, **consolidated billing**, y **SCPs** (Service Control Policies) que **limitan** lo máximo que pueden hacer las cuentas.
- **Amazon Cognito**: identidades para usuarios de **tus aplicaciones** (este tracker lo usa para el login).

## Lo que más pregunta el examen
- "Una instancia EC2 necesita leer S3" → **IAM role** con instance profile, nunca access keys en la instancia.
- "Restringir que ninguna cuenta del grupo use una región" → **SCP**.
- "Tarea que solo puede hacer root" → p. ej. cambiar el plan de soporte o cerrar la cuenta.

## Trampas
> IAM es global (no se elige región).
> Una SCP no otorga permisos; solo pone un techo.

## Práctica
1. Lee una policy de ejemplo y di qué permite.
2. 4 escenarios: desarrollador nuevo (usuario/Identity Center + grupo), Lambda que escribe en DynamoDB (rol), auditor externo de otra cuenta (rol cross-account), app móvil con login (Cognito).

## Autoevaluación
? ¿Por qué un rol es mejor que una access key en EC2? :: Las credenciales son temporales y rotan solas; no hay secreto guardado en la instancia.
? ¿Qué servicio limita permisos de todas las cuentas de una OU? :: Organizations con SCPs.
"""

G['CP: Responsabilidad compartida y servicios de seguridad'] = """
## Qué estudiar
- **Modelo de responsabilidad compartida**
  - **AWS: seguridad DE la nube**: hardware, data centers, red física, hipervisor, software de los servicios gestionados.
  - **Cliente: seguridad EN la nube**: datos, IAM, configuración de SG/NACL, cifrado, SO y parches en EC2, código de la app.
  - Cambia según el servicio: en **EC2** el cliente parchea el SO; en **RDS/Lambda/S3** AWS gestiona más (el SO y los parches de la plataforma).
  - **Controles compartidos**: patch management, configuration management y awareness/training (cada uno en su capa).
- **Servicios de seguridad**
  - **AWS Shield**: DDoS. Standard (gratis, automático, capas 3/4) y Advanced (de pago, equipo de respuesta 24/7, protección de costos).
  - **AWS WAF**: firewall de aplicaciones web (capa 7): SQL injection, XSS, rate limiting; en CloudFront, ALB, API Gateway.
  - **GuardDuty**: detección de **amenazas** con ML sobre CloudTrail, VPC Flow Logs y DNS.
  - **Inspector**: **vulnerabilidades** (CVEs) en EC2, imágenes ECR y Lambda.
  - **Macie**: encuentra **datos sensibles/PII** en S3.
  - **Security Hub**: tablero central de hallazgos y cumplimiento de estándares. **Detective**: investigación de causa raíz.
  - **KMS**: gestión de claves de cifrado. **Secrets Manager**: guarda y **rota** secretos. **ACM**: certificados TLS gratis.
  - **AWS Artifact**: descarga de **reportes de cumplimiento** (SOC, ISO, PCI) y acuerdos.
  - **Trusted Advisor**: recomendaciones en 5 categorías: costo, rendimiento, seguridad, tolerancia a fallos y límites de servicio.

## Lo que más pregunta el examen
- "¿Quién parchea el SO de una EC2?" → **cliente**. "¿Y de RDS?" → **AWS**.
- "Reporte SOC 2 de AWS para un auditor" → **Artifact**.
- "Detectar llamadas a la API desde una IP maliciosa" → **GuardDuty**.

## Trampas
> Inspector = vulnerabilidades de software; GuardDuty = comportamiento sospechoso; Macie = datos sensibles en S3.
> Shield Standard ya viene incluido sin hacer nada.

## Práctica
1. Clasifica 8 tareas: cifrar datos (cliente), mantener el hipervisor (AWS), configurar SG (cliente), seguridad física (AWS), parche del SO de EC2 (cliente), parche del motor de RDS (AWS), IAM (cliente), red global (AWS).

## Autoevaluación
? ¿Qué servicio descarga certificaciones ISO de AWS? :: AWS Artifact.
? Escaneo de CVEs en imágenes de contenedores. :: Amazon Inspector.
? Protección contra SQL injection. :: AWS WAF.
"""

G['CP: Billing, precios y planes de soporte'] = """
## Qué estudiar
- **Principios de precio**: pagas por uso; pagas menos al reservar; pagas menos por unidad al usar más (descuentos por volumen). Normalmente la **transferencia de datos entrante es gratis** y la saliente a internet se cobra.
- **Herramientas**
  - **Pricing Calculator**: estimar el costo **antes** de desplegar.
  - **Cost Explorer**: visualizar y analizar el gasto **pasado** y pronosticar.
  - **AWS Budgets**: alertas cuando el costo o el uso **superan** un umbral (también para RI/SP).
  - **Cost and Usage Report (CUR)**: el detalle más granular, a S3, para analizar con Athena.
  - **Cost Anomaly Detection**: detecta gastos inusuales con ML. **Cost allocation tags**: repartir costos por proyecto.
- **Organizations + consolidated billing**: una factura, descuentos por volumen combinados y RI/SP compartidos.
- **Free Tier**: always free (p. ej. Lambda 1M requests/mes), 12 meses (para cuentas antiguas) y trials. Las cuentas nuevas desde julio 2025 usan un plan con créditos.
- **Planes de soporte**
  - **Basic** (gratis): docs, foros, Health Dashboard y checks básicos de Trusted Advisor; sin soporte técnico.
  - **Developer**: email en horario laboral; respuesta < 24 h general / < 12 h sistema afectado.
  - **Business**: 24/7 teléfono y chat; < 1 h si producción está caída; **todos los checks de Trusted Advisor**.
  - **Enterprise On-Ramp**: < 30 min crítico; pool de TAMs.
  - **Enterprise**: < 15 min crítico; **TAM dedicado**, Concierge, Infrastructure Event Management.
- **AWS Marketplace**: comprar software de terceros. **AWS Partner Network**, **AWS Professional Services**, **AWS re:Post** (comunidad).

## Lo que más pregunta el examen
- "Saber cuánto costará antes de migrar" → **Pricing Calculator**. "Alerta si me paso de $500" → **Budgets**. "Ver en qué gasté los últimos 6 meses" → **Cost Explorer**.
- "Necesita un TAM dedicado" → **Enterprise**. "Soporte 24/7 por teléfono al menor costo" → **Business**.

## Trampas
> Cost Explorer mira hacia atrás (y pronostica); Pricing Calculator estima antes de existir.
> El plan Developer no tiene teléfono ni 24/7.

## Práctica
1. Estima en Pricing Calculator: 2 t3.medium 24/7 + 100 GB S3 + 50 GB de salida a internet.
2. Elige plan de soporte para 4 casos: estudiante (Basic), startup en pruebas (Developer), app en producción 24/7 (Business), banco con TAM (Enterprise).

## Autoevaluación
? ¿Qué herramienta da el detalle más granular por hora y recurso? :: Cost and Usage Report.
? ¿Desde qué plan tienes todos los checks de Trusted Advisor? :: Business.
"""

G['CP: Repaso ligero de la semana (día del examen TF)'] = """
## Hoy no estudies nada nuevo
- Hoy es el examen de Terraform: la prioridad es esa.
- Después del examen (o en la noche), **20–30 min de Anki** solo de esta semana: IAM, responsabilidad compartida, servicios de seguridad, billing y soporte.

## Las 10 tarjetas que no pueden fallar
- Root → MFA, sin access keys.
- Rol > access keys.
- SCP limita, no otorga.
- AWS = seguridad DE la nube; cliente = EN la nube.
- EC2: el cliente parchea el SO; RDS: AWS.
- GuardDuty amenazas / Inspector vulnerabilidades / Macie PII.
- Shield DDoS / WAF capa 7.
- Artifact = reportes de compliance.
- Pricing Calculator (antes) / Cost Explorer (pasado) / Budgets (alertas).
- Business = 24/7; Enterprise = TAM dedicado.
"""

G['CP: Observabilidad, migración y analítica'] = """
## Qué estudiar
- **El trío que confunde**
  - **CloudWatch**: **métricas** (CPU, latencia), **alarmas**, **logs** y dashboards → "¿cómo está funcionando?".
  - **CloudTrail**: registro de **llamadas a la API** (quién hizo qué, cuándo, desde dónde) → auditoría. 90 días de historial gratis.
  - **AWS Config**: **historial de configuración** de los recursos y reglas de cumplimiento → "¿cómo estaba configurado el SG el martes?".
- **AWS Health Dashboard**: eventos de AWS que afectan a tu cuenta. **X-Ray**: trazas de peticiones en apps distribuidas.
- **Systems Manager**: gestión de flotas: Session Manager (shell sin SSH), Patch Manager, Run Command, Parameter Store.
- **Migración**
  - **Application Migration Service (MGN)**: lift-and-shift de servidores a EC2.
  - **DMS** (+ Schema Conversion Tool): migrar bases de datos, incluso entre motores distintos.
  - **Migration Hub**: seguimiento central. **Application Discovery Service**: inventario on-premises.
  - **Snow Family**: transferencia física offline.
  - **Las 7 R**: rehost, replatform, refactor, repurchase, retire, retain, relocate.
- **Analítica en 1 línea**: **Athena** (SQL sobre S3, serverless), **Glue** (ETL y catálogo), **Kinesis** (streaming en tiempo real), **QuickSight** (dashboards BI), **EMR** (Hadoop/Spark), **Redshift** (data warehouse), **OpenSearch** (búsqueda y análisis de logs).

## Lo que más pregunta el examen
- "Quién borró el bucket" → **CloudTrail**. "Alarma si la CPU supera el 80%" → **CloudWatch**. "Ver cambios de configuración y evaluar cumplimiento" → **Config**.
- "Consultar con SQL archivos CSV en S3 sin servidores" → **Athena**.

## Trampas
> CloudTrail no mide rendimiento; CloudWatch no te dice quién hizo un cambio.
> Glue prepara datos; Athena los consulta; QuickSight los visualiza.

## Práctica
1. Abre CloudTrail → Event history y busca la creación de la EC2 de tu lab del sábado.
2. Escribe el trío en 1 frase cada uno.

## Autoevaluación
? ¿Qué servicio usas para auditar llamadas a la API? :: CloudTrail.
? Migrar Oracle a Aurora PostgreSQL. :: DMS + Schema Conversion Tool.
? Dashboards de negocio para gerentes. :: QuickSight.
"""

G['CP: IA y ML en AWS (adelanto de tu próxima cert)'] = """
## Qué estudiar (nivel CP: qué servicio para qué)
- **Amazon SageMaker AI**: construir, entrenar y desplegar modelos propios de ML.
- **Amazon Bedrock**: acceso por API a **foundation models** (Claude, Llama, Amazon Nova…) para IA generativa, sin gestionar infraestructura.
- **Amazon Q**: asistente de IA generativa: **Q Business** (preguntas sobre los datos de la empresa) y **Q Developer** (código y AWS).
- **Servicios pre-entrenados**
  - **Rekognition**: imágenes y video (caras, objetos, moderación).
  - **Textract**: extrae texto, **tablas y formularios** de documentos.
  - **Comprehend**: NLP: sentimiento, entidades, idioma, PII.
  - **Transcribe**: voz → texto. **Polly**: texto → voz. **Translate**: traducción.
  - **Lex**: chatbots de voz y texto. **Kendra**: búsqueda inteligente empresarial. **Personalize**: recomendaciones.

## Lo que más pregunta el examen
- "Analizar el sentimiento de reseñas" → Comprehend. "Extraer datos de facturas escaneadas" → Textract. "Subtítulos de videos" → Transcribe.
- "Crear un chatbot" → Lex. "Usar un LLM sin entrenarlo" → Bedrock.

## Trampas
> Textract ≠ Rekognition: Textract entiende documentos (tablas, formularios); Rekognition entiende imágenes.
> Polly habla; Transcribe escucha.

## Práctica
- 8 casos rápidos: reseñas (Comprehend), DNI escaneado (Textract), video con caras (Rekognition), call center a texto (Transcribe), audiolibro (Polly), web en 5 idiomas (Translate), bot de reservas (Lex), "productos que te pueden gustar" (Personalize).

## Autoevaluación
? ¿Qué servicio usarías para un asistente que responde sobre documentos internos sin construir nada? :: Amazon Q Business.
? Moderación de imágenes subidas por usuarios. :: Rekognition.
"""

G['CP: Quiz dominios 1–2 (conceptos y seguridad)'] = """
## Por qué hoy
- Los dominios 1 (Cloud Concepts, 24%) y 2 (Security & Compliance, **30%**) suman más de la mitad del examen.

## Plan (50 min)
1. **5 min**: relee el modelo de responsabilidad compartida.
2. **30 min**: 25 preguntas solo de estos dominios (filtra por dominio en el banco de práctica si se puede).
3. **15 min**: análisis de errores y tarjetas Anki.

## Checklist para dominar
- Las 6 ventajas y los 6 pilares, de memoria.
- CAF: 6 perspectivas y 4 fases.
- Responsabilidad compartida por tipo de servicio (EC2 vs RDS vs Lambda vs S3).
- IAM: root, users, groups, roles, policies, MFA, mínimo privilegio, Identity Center, Organizations/SCP.
- Seguridad: Shield, WAF, GuardDuty, Inspector, Macie, Security Hub, Detective, KMS, Secrets Manager, ACM, Artifact, Trusted Advisor, Config, CloudTrail.
- Compliance: Artifact y la página AWS Compliance Programs.

## Autoevaluación
? ¿El cliente es responsable de la seguridad física del data center? :: No, es de AWS.
? ¿Qué servicio audita la configuración contra reglas de compliance? :: AWS Config.
"""

G['CP: Quiz dominios 3–4 (tecnología y billing)'] = """
## Por qué hoy
- El dominio 3 (Cloud Technology & Services, **34%**) es el más grande y el dominio 4 (Billing, Pricing & Support, 12%) tiene preguntas muy predecibles.

## Plan (50 min)
1. **30 min**: 25 preguntas de estos dominios.
2. **20 min**: análisis + tarjetas.

## Checklist para dominar
- Métodos de despliegue: consola, CLI, SDK, IaC (CloudFormation).
- Cómputo: EC2 (y modelos de compra), Lambda, ECS/EKS/Fargate, Beanstalk, Lightsail.
- Storage: S3 (clases), EBS, EFS, FSx, Storage Gateway, Backup, Snow.
- Red: VPC, subnets, SG/NACL, Route 53, CloudFront, Global Accelerator, VPN, Direct Connect.
- BD: RDS, Aurora, DynamoDB, ElastiCache, Redshift, DocumentDB, Neptune.
- Analítica, IA/ML, mensajería (SQS, SNS, EventBridge), observabilidad.
- Billing: Pricing Calculator, Cost Explorer, Budgets, CUR, consolidated billing, planes de soporte, Marketplace, re:Post, Health Dashboard.

## Autoevaluación
? ¿Qué plan de soporte es el más barato con soporte 24/7 por teléfono? :: Business.
? ¿Dónde compras software de terceros listo para AWS? :: AWS Marketplace.
"""

G['CP: Servicios que confunden'] = """
## Arma esta tabla y memorízala
- **SQS vs SNS vs EventBridge**: cola (pull, 1 consumidor) · pub/sub (push, muchos) · bus de eventos con reglas.
- **SG vs NACL**: instancia, stateful, allow · subnet, stateless, allow + deny.
- **CloudWatch vs CloudTrail vs Config**: métricas y logs · quién llamó a la API · historial de configuración.
- **GuardDuty vs Inspector vs Macie**: amenazas · vulnerabilidades · PII en S3.
- **Shield vs WAF**: DDoS (L3/L4) · ataques web (L7).
- **RI vs Savings Plans**: tipo de instancia reservado · compromiso de $/h (Compute SP también cubre Lambda y Fargate).
- **EBS vs EFS vs S3**: bloque 1 AZ · archivos compartidos multi-AZ · objetos.
- **Direct Connect vs VPN**: dedicado, semanas · cifrado por internet, minutos.
- **CloudFront vs Global Accelerator**: caché en el edge · IPs estáticas sin caché.
- **Multi-AZ vs Read Replica**: HA · escalar lecturas.
- **Cost Explorer vs Budgets vs Pricing Calculator**: pasado · alertas · estimar antes.
- **Beanstalk vs CloudFormation**: PaaS · IaC.
- **Trusted Advisor vs Well-Architected Tool**: chequeos automáticos de tu cuenta · revisión guiada de una arquitectura.

## Práctica
1. Hazla en papel sin mirar; luego corrígela con esta guía.
2. Los pares que fallaste van a Anki.
"""

G['🎯 Simulacro CP 1'] = """
## Cómo hacerlo (120 min)
1. **Condiciones reales**: 65 preguntas en 90 min (o 120 si vas a usar ESL +30), sin apuntes, sin pausa, celular lejos.
2. **Estrategia de tiempo**: ~1 min por pregunta. Si dudas más de 90 segundos, **marca y sigue**.
3. **Técnica**: lee la última frase primero (qué piden), descarta las 2 opciones claramente malas y decide entre las otras 2.
4. Las preguntas de respuesta múltiple dicen cuántas elegir ("Choose TWO").

## Cómo analizar (30 min)
- Anota el score total y por dominio (los 4 del exam guide).
- Para cada error: ¿no sabía el concepto, lo confundí con otro servicio o leí mal la pregunta?
- Lista de los **10 conceptos más fallados** → se repasan en la semana.

## Referencia
- Aprobado real: 700/1000. En simulacros apunta a **≥80%** para ir con margen.
"""

G['CP: Revisión de errores del simulacro 1'] = """
## Método (45 min)
1. Abre el simulacro en modo revisión.
2. Por cada pregunta fallada, escribe:
   - qué elegiste y por qué parecía correcto;
   - por qué la correcta es correcta (cita el concepto);
   - por qué cada incorrecta NO aplica.
3. Clasifica el error: **concepto** (no lo sabía) · **confusión** (servicio parecido) · **lectura** (no vi una palabra clave como "LEAST cost").
4. Los errores de concepto: relee la guía de esa sesión. Los de confusión: agrégalos a tu tabla de "servicios que confunden".

## Palabras clave que cambian la respuesta
- **most cost-effective**, **least operational overhead** (→ servicio gestionado/serverless), **highly available** (→ multi-AZ), **durable**, **global**.
"""

G['🎯 Simulacro CP 2 — parte 1'] = """
## Cómo hacerlo (50 min)
- 33 preguntas en 45 min, sin apuntes. Usa un simulacro **distinto** al del sábado.
- Antes de empezar (5 min): mira tu lista de los 10 conceptos más fallados.
- No corrijas todavía: la corrección es mañana junto con la parte 2.

## Meta
- ≥80%. Anota cuántas marcaste como dudosas.
"""

G['🎯 Simulacro CP 2 — parte 2'] = """
## Cómo hacerlo (55 min)
- 32 preguntas en 45 min + 10 min de análisis de las dos partes.
- Compara por dominio contra el simulacro 1: ¿subió el dominio que más fallabas?

## Decisión
- **≥80% global**: sigue el plan y rinde el sábado.
- **70–79%**: usa la sesión de mañana (cheat sheet) solo para el dominio más débil.
- **<70%**: considera mover el examen una semana (AWS permite reprogramar sin costo hasta 24 h antes).
"""

G['CP: Cheat sheet final y dominio más débil'] = """
## Qué hacer (40 min)
1. **20 min**: una sola hoja con lo que todavía te cuesta (servicios que confundes, planes de soporte, clases de S3, responsabilidad compartida).
2. **20 min**: 10 preguntas del dominio con menos aciertos y su análisis.

## Si te sobra tiempo
- Repasa la tabla de "servicios que confunden" y las 6 ventajas / 6 pilares.
"""

G['CP: Repaso ligero y logística del examen'] = """
## Hoy: solo repaso y logística (30 min)
1. **10 min**: tu cheat sheet, nada nuevo.
2. **10 min · OnVUE** (si rindes online): ejecuta el system test del día del examen en la misma computadora y red. Webcam, micrófono, sin segundo monitor.
3. **10 min · checklist**:
   - documento de identidad vigente con el mismo nombre que tu cuenta;
   - escritorio y paredes despejados, sin papeles;
   - check-in 30 min antes;
   - ESL +30 aplicado a la reserva (si rindes en inglés).

## Durante el examen
- No hay penalización por responder mal: **nunca dejes una pregunta en blanco**.
- Marca las dudosas y vuelve al final.
"""

G['🏆 EXAMEN AWS Cloud Practitioner'] = """
## Datos del examen (CLF-C02)
- 65 preguntas (50 puntúan y 15 no, pero no sabes cuáles), 90 min (+30 con ESL), aprobado **700/1000**.
- Dominios: Cloud Concepts 24% · Security & Compliance 30% · Cloud Technology & Services 34% · Billing, Pricing & Support 12%.

## Estrategia
- Primera pasada respondiendo todo; las dudosas se marcan.
- Segunda pasada solo por las marcadas.
- Lee la última frase de la pregunta antes que el escenario.

## Después de aprobar
- En tu cuenta de AWS Certification → **Benefits**: activa el **voucher de 50%** para el próximo examen (AI Practitioner).
- Descarga la insignia de Credly y anótalo en Notas de este ítem.
"""
