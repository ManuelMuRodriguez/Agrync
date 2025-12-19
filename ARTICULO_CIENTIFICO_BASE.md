# Agrync: Plataforma de Recolección y Gestión de Telemetría IoT Industrial

## Resumen Ejecutivo

Agrync es una plataforma full-stack diseñada para la recolección, gestión y visualización de datos de telemetría procedentes de dispositivos industriales e IoT. El sistema implementa un enfoque moderno para la integración de múltiples protocolos industriales (Modbus TCP/IP, OPC UA) y facilita la interoperabilidad con plataformas IoT estándar como FIWARE, permitiendo el almacenamiento, análisis y visualización centralizada de datos en instalaciones agroindustriales.

---

## 1. Introducción y Contexto

### 1.1 Problemática
Las plantas agroindustriales tradicionales requieren la integración de múltiples dispositivos y sensores que utilizan distintos protocolos de comunicación. Estos dispositivos generan grandes volúmenes de datos de telemetría que deben ser capturados, almacenados y analizados para optimizar procesos productivos. Las soluciones existentes suelen ser:

- **Fragmentadas**: requieren múltiples sistemas desacoplados para cada protocolo
- **Complejas**: demandan configuración manual y expertos técnicos especializados
- **Costosas**: implican inversiones significativas en infraestructura
- **Poco escalables**: dificultan la adicción de nuevos sensores o dispositivos

### 1.2 Solución Propuesta
Agrync aborda estos desafíos mediante una plataforma unificada que:

- Integra múltiples protocolos industriales en un único sistema
- Proporciona una interfaz web intuitiva para gestión de sensores
- Permite tanto configuración manual como importación en lote mediante archivos JSON
- Facilita la interoperabilidad con estándares IoT (FIWARE)
- Utiliza contenedores Docker para despliegue simplificado

---

## 2. Arquitectura del Sistema

### 2.1 Estructura General

```
Agrync
├── Backend (FastAPI + Python)
│   ├── API REST para gestión de dispositivos
│   ├── Conectores Modbus TCP/IP
│   ├── Servidor OPC UA
│   ├── Integración FIWARE
│   ├── Gestión de usuarios y autenticación
│   └── Base de datos MongoDB
│
└── Frontend (React + TypeScript + Vite)
    ├── Interfaz de usuario web
    ├── Gestión de tareas y monitorización
    ├── Visualización de variables
    ├── Configuración de dispositivos
    └── Autenticación de usuarios
```

### 2.2 Componentes Principales

#### **Backend (agrync_backend/)**

**Tecnologías base:**
- Framework: FastAPI (Python 3.11+)
- Base de datos: MongoDB (mediante Beanie + Motor)
- Protocolo industrial Modbus: lectura TCP/IP
- Servidor OPC UA: exposición de datos recolectados
- Integración IoT: cliente FIWARE para reenvío de datos

**Estructura de directorios:**

| Directorio | Propósito |
|-----------|-----------|
| `routers/` | Endpoints REST organizados por dominio (auth, fiware, modbus, opc, task, user, generic) |
| `models/` | Esquemas de datos (Pydantic) y modelos ORM (Beanie) |
| `tasks/` | Servicios asíncronos: lectores Modbus, servidor OPC, integración FIWARE |
| `utils/` | Utilidades compartidas (gestión de fechas, contraseñas, tokens) |
| `static/` | Archivos estáticos (plantillas JSON, descargas) |

**Endpoints principales:**
- `POST /api/v1/auth/login` — Autenticación de usuarios
- `GET/POST /api/v1/devices` — Gestión de dispositivos
- `POST /api/v1/tasks/modbus` — Configuración de tareas Modbus
- `POST /api/v1/tasks/opc` — Configuración de servidor OPC
- `POST /api/v1/fiware/push` — Envío de datos a FIWARE

#### **Frontend (agrync_frontend/)**

**Tecnologías base:**
- Framework: React 19+
- Lenguaje: TypeScript
- Herramienta de construcción: Vite
- Estilos: CSS moderno

**Estructura de páginas:**
- Autenticación (login/registro)
- Dashboard principal
- Gestión de dispositivos Modbus
- Configuración de variables
- Monitorización de tareas
- Administración de usuarios
- Centro de configuración

**Capas de la aplicación:**

| Capa | Responsabilidad |
|-----|-----------------|
| `pages/` | Componentes de página completa |
| `components/` | Componentes reutilizables (tablas, formularios, tarjetas) |
| `api/` | Clientes HTTP (Axios) para cada dominio |
| `hooks/` | Hooks personalizados (autenticación, datos genéricos) |
| `lib/` | Utilidades compartidas y configuración |
| `types/` | Definiciones TypeScript de tipos compartidos |

---

## 3. Características Técnicas Clave

### 3.1 Conectividad Modbus TCP/IP

**Funcionamiento:**
1. El usuario configura un esclavo Modbus especificando:
   - Dirección IP del dispositivo
   - Puerto TCP (típicamente 502)
   - ID del esclavo
2. El sistema ejecuta una tarea asíncrona que periódicamente:
   - Se conecta al dispositivo
   - Lee registros especificados (bobinas, registros de entrada, registros de retención)
   - Almacena los valores en MongoDB
   - Reporta errores de conexión

**Protocolo:**
- Modbus TCP/IP (RFC 1006)
- Lectura de múltiples tipos de datos: bobinas, entradas discretas, registros de entrada, registros de retención
- Soporte para múltiples esclavos simultáneos

### 3.2 Servidor OPC UA

**Funcionalidad:**
- Expone variables leídas de Modbus como nodos OPC UA
- Permite que clientes OPC UA (sistemas SCADA, herramientas de monitorización) se conecten
- Sincronización en tiempo real de valores

**Configuración:**
- Puerto configurable
- Autenticación opcional
- Certificados de seguridad en `tasks/certificate/`

### 3.3 Integración FIWARE

**Propósito:**
- Reenviar datos de telemetría a plataformas FIWARE
- Facilitar almacenamiento en bases de datos tiempo-series
- Integración con ecosistemas IoT estándar

**Flujo:**
1. Datos recolectados de Modbus → MongoDB
2. Tarea FIWARE → lectura de MongoDB
3. Transformación a formato FIWARE
4. Envío HTTP POST a servidor FIWARE

### 3.4 Gestión de Sensores y Variables

**Configuración manual:**
- Interfaz web para crear/editar sensores uno a uno
- Asignación de nombres, unidades, rangos de validación

**Importación en lote:**
- Subida de archivos JSON con estructura predefinida
- Plantilla disponible en `agrync_backend/static/downloads/plantilla_modbus.json`
- Validación automática de esquema

**Ejemplo de plantilla JSON:**
```json
{
  "sensores": [
    {
      "nombre": "Temperatura Invernadero A",
      "dispositivo_modbus_id": "192.168.1.100",
      "puerto": 502,
      "esclavo": 1,
      "registro": 100,
      "tipo": "temperatura",
      "unidad": "°C",
      "factor_escala": 0.1
    }
  ]
}
```

---

## 4. Procedimientos de Instalación y Lanzamiento

### 4.1 Opción 1: Despliegue Completo con Docker Compose (Recomendado)

**Requisitos previos:**
- Docker Engine 20.10+
- Docker Compose 1.29+
- Mínimo 2GB de RAM disponible
- Puertos 8000 (backend), 5173 (frontend) y 27017 (MongoDB) libres

**Pasos:**

```bash
# 1. Clonar repositorio
git clone https://github.com/ManuelMuRodriguez/Agrync.git
cd Agrync

# 2. Configurar variables de entorno (opcional)
cat > .env << EOF
MONGODB_URI=mongodb://mongo:27017/agrync
SECRET_KEY=your-secret-key-here
FIWARE_URL=http://fiware:4041
FIWARE_SERVICE=agrync
FIWARE_SERVICEPATH=/agrync
EOF

# 3. Iniciar servicios
docker compose up --build

# 4. Verificar estado
# Backend API: http://localhost:8000/api/v1/docs
# Frontend: http://localhost:5173
# MongoDB: localhost:27017
```

**Servicios iniciados:**
- `agrync-backend` — API FastAPI en puerto 8000
- `agrync-frontend` — App React en puerto 5173
- `mongo` — Base de datos MongoDB en puerto 27017
- `fiware` (opcional) — Plataforma FIWARE

**Detener servicios:**
```bash
docker compose down
```

### 4.2 Opción 2: Desarrollo Local (Backend)

**Requisitos:**
- Python 3.11+
- pip o poetry
- MongoDB en ejecución (local o remota)

**Pasos:**

```bash
# 1. Navegar al backend
cd agrync_backend

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# o en Windows:
# .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export MONGODB_URI=mongodb://localhost:27017/agrync
export SECRET_KEY=dev-secret-key

# 5. Ejecutar servidor
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. Acceder a documentación API
# Swagger UI: http://localhost:8000/api/v1/docs
# ReDoc: http://localhost:8000/api/v1/redoc
```

**Detalles de ejecución:**
- `--reload`: Reinicia automáticamente ante cambios en código
- Hot-reload habilitado para desarrollo rápido

### 4.3 Opción 3: Desarrollo Local (Frontend)

**Requisitos:**
- Node.js 18+
- npm, yarn o pnpm

**Pasos:**

```bash
# 1. Navegar al frontend
cd agrync_frontend

# 2. Instalar dependencias
npm install
# o: yarn install, pnpm install

# 3. Configurar API base (si es necesario)
# Editar src/api/axios.ts con URL del backend
# Ej: http://localhost:8000/api/v1

# 4. Iniciar servidor de desarrollo
npm run dev

# 5. Acceder a aplicación
# http://localhost:5173
```

**Características de desarrollo:**
- Hot Module Replacement (HMR) — cambios reflejados instantáneamente
- TypeScript strict mode — validación de tipos en tiempo de desarrollo
- ESLint configuration — análisis de calidad de código

### 4.4 Construcción de Imágenes Docker Individuales

**Backend:**
```bash
docker build -f Dockerfile.backend -t agrync-backend:latest .
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/agrync \
  agrync-backend:latest
```

**Frontend:**
```bash
docker build -f Dockerfile.frontend -t agrync-frontend:latest .
docker run -p 5173:5173 agrync-frontend:latest
```

---

## 5. Flujo de Datos y Funcionamiento

### 5.1 Flujo de Configuración

```
Usuario (Web UI)
    ↓
[Frontend React]
    ↓ POST /api/v1/devices
[Backend API FastAPI]
    ↓
[Validación Pydantic]
    ↓
[MongoDB]
    ↓ Confirmación
[Frontend] ← Dispositivo configurado
```

### 5.2 Flujo de Recolección de Datos

```
[Tarea Modbus Asíncrona]
    ↓ Conexión TCP/IP
[Dispositivo Modbus]
    ↓ Lectura de registros
[Tarea Modbus] ← Valores leídos
    ↓ Transformación y validación
[MongoDB] ← Almacenamiento de lecturas
    ↓
[Servidor OPC UA] ← Sincronización de valores
    ↓
[Clientes OPC UA] ← Variables disponibles
```

### 5.3 Flujo de Integración FIWARE

```
[MongoDB] ← Datos históricos
    ↓
[Tarea FIWARE]
    ↓ Transformación a formato FIWARE
[FIWARE API]
    ↓
[Base de datos tiempo-serie FIWARE]
    ↓
[Dashboards y análisis]
```

### 5.4 Flujo de Autenticación

```
Usuario ingresa credenciales
    ↓
[Frontend] → POST /api/v1/auth/login
    ↓
[Backend] → Validación en MongoDB
    ↓ Token JWT generado
[Frontend] ← Token almacenado en localStorage
    ↓
[Solicitudes posteriores] incluyen Authorization: Bearer <token>
```

---

## 6. Modelo de Datos Principales

### 6.1 Esquema de Usuario

```python
class Usuario(BaseModel):
    email: str  # Identificador único
    contraseña_hash: str  # Almacenada con salt
    nombre_completo: str
    rol: Literal["admin", "operador", "visualizador"]
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
```

### 6.2 Esquema de Dispositivo Modbus

```python
class DispositivoModbus(BaseModel):
    nombre: str
    direccion_ip: str
    puerto: int = 502
    id_esclavo: int
    intervalo_lectura: int  # segundos
    variables: List[Variable]
    activo: bool
    creado_en: datetime
```

### 6.3 Esquema de Variable

```python
class Variable(BaseModel):
    nombre: str
    registro: int
    tipo_registro: Literal["coil", "discrete_input", "input_register", "holding_register"]
    unidad: str
    factor_escala: float = 1.0
    minimo: float
    maximo: float
    descripcion: str
    activo: bool
```

### 6.4 Esquema de Lectura de Telemetría

```python
class LecturaTelemetria(BaseModel):
    id_dispositivo: ObjectId
    id_variable: str
    valor: float
    timestamp: datetime
    estado: Literal["ok", "error", "fuera_rango"]
    mensaje_error: Optional[str]
```

---

## 7. Configuración y Variables de Entorno

### 7.1 Variables Backend Requeridas

| Variable | Descripción | Ejemplo |
|----------|------------|---------|
| `MONGODB_URI` | Cadena conexión MongoDB | `mongodb://localhost:27017/agrync` |
| `SECRET_KEY` | Clave para firmar tokens JWT | `super-secret-key-123` |
| `FIWARE_URL` | URL servidor FIWARE | `http://localhost:4041` |
| `FIWARE_SERVICE` | Servicio FIWARE | `agrync` |
| `FIWARE_SERVICEPATH` | Ruta de servicio FIWARE | `/agrync` |
| `OPC_PORT` | Puerto servidor OPC UA | `4840` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### 7.2 Variables Frontend Requeridas

| Variable | Descripción | Ejemplo |
|----------|------------|---------|
| `VITE_API_BASE_URL` | URL base API backend | `http://localhost:8000/api/v1` |

### 7.3 Archivo `.env.example`

```text
# Backend
MONGODB_URI=mongodb://mongo:27017/agrync
SECRET_KEY=your-secret-key-change-in-production
FIWARE_URL=http://fiware:4041
FIWARE_SERVICE=agrync
FIWARE_SERVICEPATH=/agrync
OPC_PORT=4840
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Docker
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password
```

---

## 8. Consideraciones de Seguridad

### 8.1 Autenticación y Autorización

- **JWT Tokens**: Tokens de corta duración para autenticación sin estado
- **Roles**: RBAC (Role-Based Access Control) con roles predefinidos
- **Hashing**: Contraseñas almacenadas con algoritmos criptográficos modernos

### 8.2 Conexiones Seguras

- **HTTPS**: Recomendado para producción (configurar reverse proxy)
- **Certificados OPC UA**: Soportados en `tasks/certificate/`
- **MongoDB Authentication**: Credenciales configurables

### 8.3 Validación de Datos

- **Validación Pydantic**: Esquemas tipados en backend
- **Validación TypeScript**: Sistema de tipos en frontend
- **Límites de solicitud**: Rate limiting recomendado

---

## 9. Limitaciones y Mejoras Futuras

### 9.1 Limitaciones Actuales

1. **Monousuario en desarrollo**: MongoDB sin autenticación por defecto
2. **Sin tests automatizados**: No hay suite de tests unitarios/integración
3. **Logging básico**: Sistema de logging manual, podría mejorar con estructurado
4. **Documentación**: README básico, carece de guías detalladas

### 9.2 Mejoras Propuestas

1. **Internacionalización (i18n)**
   - Implementar react-i18next para soporte multiidioma
   - Traducir interfaz a múltiples lenguas

2. **Suite de Tests**
   - Tests unitarios con pytest (backend)
   - Tests integración con Docker Compose
   - Tests E2E con Cypress/Playwright (frontend)

3. **CI/CD Pipeline**
   - GitHub Actions para linting y tests
   - Construcción automática de imágenes Docker
   - Despliegue automatizado a registro

4. **Monitorización**
   - Prometheus + Grafana para métricas
   - ELK Stack para logs centralizados

5. **Escalabilidad**
   - Message queue (RabbitMQ) para tareas asíncronas
   - Redis para caché
   - Replicación MongoDB para alta disponibilidad

---

## 10. Ejemplo de Uso Completo

### Caso de uso: Monitorizar invernadero con sensores Modbus

**Paso 1: Desplegar el sistema**
```bash
docker compose up --build
# Esperar 30-60 segundos a que los servicios inicien
```

**Paso 2: Acceder a la aplicación**
```
Frontend: http://localhost:5173
API Docs: http://localhost:8000/api/v1/docs
```

**Paso 3: Crear usuario y autenticarse**
- Ir a pantalla de registro
- Crear cuenta con email y contraseña
- Iniciar sesión

**Paso 4: Configurar dispositivo Modbus**
- Ir a "Dispositivos" → "Añadir dispositivo"
- Especificar: IP (ej: 192.168.1.100), Puerto (502), Esclavo (1)
- Guardar

**Paso 5: Añadir variables**
- Ir a "Variables" → "Añadir variable"
- Especificar: Nombre, Registro Modbus, Tipo, Unidad
- Ejemplo: "Temperatura", Registro 100, tipo "input_register", unidad "°C"
- Guardar

**Paso 6: Iniciar lectura de datos**
- Ir a "Tareas" → "Modbus"
- Crear tarea para dispositivo configurado
- Establecer intervalo de lectura (ej: 10 segundos)
- Activar tarea

**Paso 7: Monitorizar datos**
- Dashboard mostrará valores actuales de variables
- Gráficos de histórico disponibles
- Alertas si valores salen de rango configurado

**Paso 8 (Opcional): Integración FIWARE**
- Ir a "Configuración" → "FIWARE"
- Especificar URL del servidor FIWARE
- Activar envío automático de datos
- Los datos se sincronizarán automáticamente

---

## 11. Conclusión

Agrync proporciona una solución integral y escalable para la recolección y gestión de telemetría en instalaciones agroindustriales. Su arquitectura modular, interfaz intuitiva y soporte para múltiples protocolos la hacen adecuada tanto para pequeñas instalaciones como para plantas de mayor escala. El uso de tecnologías modernas (FastAPI, React, Docker) garantiza mantenibilidad, escalabilidad y facilidad de despliegue.

---

## Bibliografía Recomendada para el Artículo Científico

1. **Protocolos Industriales:**
   - Modbus Organization. "MODBUS Application Protocol Specification V1.1b3"
   - OPC Foundation. "OPC UA Specification" (IEC 62541)

2. **IoT y FIWARE:**
   - Gómez, J., et al. (2020). "FIWARE: An Open Ecosystem for IoT". ArXiv preprint.
   - ETSI GS CIM 009 V1.1.1: "Context Information Management (CIM)"

3. **Tecnologías Web:**
   - Tiangolo, S. (2021). "FastAPI: Modern Python Web Framework"
   - React Documentation. "Declarative, Efficient, and Flexible JavaScript Library"

4. **IoT en Agricultura:**
   - Sharma, A., et al. (2021). "IoT-based Smart Agriculture: A Comprehensive Survey"
   - Lobell, D. B., et al. (2015). "The use of satellite data for crop yield gap analysis"

---

**Documento preparado:** 16 de diciembre de 2025
**Versión:** 1.0
