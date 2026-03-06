# La Delicia RAG – Bruno, el Mozo Virtual

Sistema conversacional con **LangGraph** + **RAG** que actúa como mozo virtual ("Bruno") para el restaurante *La Delicia*.  
El agente consulta una base de conocimiento (Chroma) y, al cerrar la conversación, registra un informe en **Notion**.

## Integrantes 
- Pacheco, Melisa Johana
- Telesco, Lucas
- Ortiz, Matías Nicolás

## ✨ Funcionalidades
- **RAG** con `Chroma` + embeddings de Google (`models/text-embedding-004`).
- **Agentes con LangGraph**:
  - `experto_menu`: responde preguntas sobre menú/horarios usando el retriever.
  - `capitan_pedidos`: genera un resumen y lo **guarda en Notion**.
- **Tools**:
  - `consultar_menu_y_horarios` (retriever)
  - `off_topic_tool` (redirección si la consulta no es del restaurante)
  - `guardar_informe_en_notion` (persistencia externa)
- **CLI interactiva**.

---

## 📋 Requisitos del Sistema

**Opción A - Con Docker (Recomendado):**
- **Docker** y **Docker Compose** instalados
- **Git** (para clonar el repositorio)
- **Acceso a internet**

**Opción B - Instalación Manual:**
- **Python 3.10+** (recomendado 3.11 o 3.12)
- **Git** (para clonar el repositorio)
- **Acceso a internet** (para descargar dependencias)

**Cuentas y API Keys necesarias (en ambas opciones):**
  - Google Generative AI (Gemini) - **OBLIGATORIO**
  - Notion (base de datos) - **OBLIGATORIO**
  - LangSmith (observabilidad) - **OPCIONAL**

---

## 🚀 Instalación Paso a Paso

### 🐳 Opción A: Instalación con Docker (⭐ Recomendado)

Para una instalación más sencilla sin configurar Python localmente, usa Docker:

#### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/mtsortiz/ai-agents-final-project.git
cd ai-agents-final-project/
```

#### 2️⃣ Copiar archivo de configuración
```bash
cp .env.example .env
```

#### 3️⃣ Editar el archivo `.env` con tus API Keys
Reemplaza los valores placeholder con tus credenciales reales (ver sección **🔐 Configuración de Variables de Entorno** más adelante).

#### 4️⃣ Ejecutar con Docker Compose
```bash
docker-compose up
```

**¡Listo!** El aplicativo estará corriendo en el contenedor. El programa te pedirá que interactúes con Bruno.

Para obtener más instrucciones avanzadas de Docker, consulta [DOCKER.md](DOCKER.md).

---

### 💻 Opción B: Instalación Manual (Python local)

#### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/mtsortiz/ai-agents-final-project.git
cd ai-agents-final-project/
```

#### 2️⃣ Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Linux/macOS:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

#### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

## 🔐 Configuración de Variables de Entorno

### 1️⃣ Crear archivo `.env`
Crea un archivo llamado `.env` en la **raíz del proyecto** (mismo nivel que `README.md`):

```bash
touch .env  # En Linux/macOS
# En Windows: crear archivo .env manualmente
```

### 2️⃣ Obtener API Keys

#### 🔹 Google Gemini API Key (OBLIGATORIO)
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API Key"**
4. Copia la API key generada

#### 🔹 Notion API Key y Database ID (OBLIGATORIO)
1. Ve a [Notion Integrations](https://www.notion.so/my-integrations)
2. Haz clic en **"+ New integration"**
3. Nombre: `La Delicia RAG`
4. Selecciona tu workspace
5. Copia el **Internal Integration Secret** (esta es tu API Key)

**Para la Database ID:**
1. Crea una nueva página en Notion
2. Agrega una **Database - Table**
3. Configura las columnas EXACTAMENTE así:
   - `Consulta` (tipo: **Title**)
   - `Resumen` (tipo: **Text**)
   - `Fecha` (tipo: **Date**)
4. Comparte la página con tu integración (⋯ → Add connections → selecciona tu integración)
5. Copia la URL de la database y extrae el ID (parte entre `/` y `?`)

#### 🔹 LangSmith API Key (OPCIONAL)
1. Ve a [LangSmith](https://smith.langchain.com/)
2. Regístrate/Inicia sesión
3. Ve a Settings → API Keys
4. Crea una nueva API Key

### 3️⃣ Configurar archivo `.env`
Edita el archivo `.env` y reemplaza los valores placeholder:

```env
# Google Gemini (OBLIGATORIO)
GEMINI_API_KEY=AIzaSyD...tu_api_key_real_aquí

# Notion (OBLIGATORIO)
NOTION_API_KEY=secret_...tu_api_key_real_aquí
NOTION_DATABASE_ID=tu_database_id_aquí

# LangSmith (OPCIONAL - para observabilidad)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...tu_api_key_aquí
LANGCHAIN_PROJECT=la-delicia
```

---

## ▶️ Ejecución del Programa

### 1️⃣ Activar entorno virtual (si no está activado)
```bash
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 2️⃣ Ejecutar el programa
```bash
python -m src.main
```

### 3️⃣ Interactuar con Bruno
```
👤 Cliente: hola
🤖 Bruno: ¡Hola! Bienvenido a La Delicia...

👤 Cliente: ¿qué platos tienen arroz?
🤖 Bruno: Tenemos el Risotto de Hongos...

👤 Cliente: gracias
🤖 Bruno: [Guarda conversación en Notion y se despide]
✅ Conversación finalizada
```

### 4️⃣ Palabras clave para finalizar
Para cerrar la conversación y guardar en Notion, usa cualquiera de estas palabras:
- `gracias`
- `chau`
- `salir`
- `listo`
- `perfecto`

---

## 🛠️ Troubleshooting

### ❌ Error: "ModuleNotFoundError"
```bash
# Asegúrate de tener el entorno virtual activado
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### ❌ Error: "Falta GEMINI_API_KEY en .env"
- Verifica que el archivo `.env` esté en la raíz del proyecto
- Verifica que `GEMINI_API_KEY` tenga un valor válido
- No uses comillas en el archivo `.env`

### ❌ Error: "No se guarda en Notion"
- Verifica `NOTION_API_KEY` y `NOTION_DATABASE_ID`
- Asegúrate de que la base de datos tenga las columnas correctas
- Verifica que la integración tenga permisos en la base de datos

### ❌ El programa se queda "colgado"
- Presiona `Ctrl+C` para salir
- Verifica tu conexión a internet
- Verifica que las API keys sean válidas

---

## 🧠 Cómo funciona (resumen técnico)

- **Documentos**: el menú y la info del negocio se cargan como `Document` y se partean con `RecursiveCharacterTextSplitter`.
- **Vectorstore**: se indexa en **Chroma** (persistente en `.chroma/la-delicia`).
- **Retriever**: `vectorstore.as_retriever(search_kwargs={"k": 3})`.
  - `k` es cuántos *chunks* más similares trae por consulta (más `k` = más contexto, pero también más ruido/costo).
- **LangGraph**:
  - Router → deriva a `experto_menu` o `capitan_pedidos` según el último mensaje humano (despedida).
  - `experto_menu` solo puede llamar `consultar_menu_y_horarios` u `off_topic_tool`.
  - `capitan_pedidos` solo puede llamar `guardar_informe_en_notion`.

---

## 📁 Estructura del Proyecto

```
ai-agents-final-project/
├── src/
│   └── main.py                    # Código principal del sistema
├── .chroma/                       # Base de datos vectorial (auto-generada)
│   └── la-delicia/
├── .venv/                         # Entorno virtual (auto-generado)
├── .env                           # Variables de entorno (TU DEBES CREARLO)
├── requirements.txt               # Dependencias de Python
├── README.md                      # Este archivo
├── LANGSMITH_SETUP.md            # Guía de configuración LangSmith
└── NOTION_SETUP.md               # Guía de configuración Notion
```

---

## 🧪 Guía de Pruebas

### Consultas de ejemplo para probar:

#### 🔹 Consultas sobre el menú:
```
👤 "¿Qué aperitivos tienen?"
👤 "¿Tenés platos con arroz?"
👤 "¿Cuál es el precio del lomo?"
👤 "¿Hay opciones vegetarianas?"
```

#### 🔹 Consultas sobre horarios:
```
👤 "¿A qué hora abren?"
👤 "¿Están abiertos los lunes?"
👤 "¿Horario de cena?"
```

#### 🔹 Consultas off-topic (debería redirigir):
```
👤 "¿Qué tal el clima?"
👤 "¿Cómo está Messi?"
👤 "¿Qué hora es?"
```

#### 🔹 Finalizar conversación:
```
👤 "gracias"
👤 "chau"
👤 "salir"
👤 "listo"
👤 "perfecto"
```

### Flujo esperado:
1. **Saludo**: Bruno responde cordialmente
2. **Consultas**: Bruno busca información y responde
3. **Despedida**: Bruno guarda conversación en Notion y se despide
4. **Sistema termina**: Automáticamente después de guardar

---

## 🚨 Problemas Comunes y Soluciones

### ❌ "GEMINI_API_KEY no válida"
**Solución**: 
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Verifica que tu API key esté activa
3. Crea una nueva si es necesario

### ❌ "Error al guardar en Notion"
**Solución**:
1. Verifica que la base de datos tenga las columnas exactas: `Consulta`, `Resumen`, `Fecha`
2. Verifica que la integración tenga permisos en la base de datos
3. Consulta `NOTION_SETUP.md` para instrucciones detalladas

### ❌ "No encuentra módulos" 
**Solución**:
```bash
# Verificar que el entorno virtual esté activado
which python  # Linux/macOS
where python  # Windows

# Si no muestra la ruta a .venv/, activar:
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### ❌ "El programa no responde"
**Solución**:
1. Presiona `Ctrl+C` para cancelar
2. Verifica conexión a internet
3. Verifica que las API keys sean correctas

---

## 📊 Observabilidad con LangSmith

Si configuraste LangSmith (opcional), puedes:

1. Ver todas las conversaciones en [smith.langchain.com](https://smith.langchain.com/)
2. Monitorear el proyecto "la-delicia"
3. Analizar traces de cada interacción
4. Debuggear problemas en tiempo real

---

## 🤝 Soporte

Para obtener ayuda adicional:
- **Notion**: Consulta `NOTION_SETUP.md`
- **LangSmith**: Consulta `LANGSMITH_SETUP.md`
- **Errores técnicos**: Revisa los logs del terminal

---

## 📜 Licencia
MIT

---

## 🧩 Estructura (sugerida)

```
.
├─ src/
│  └─ main.py
├─ .chroma/                # (persistencia local de Chroma)
├─ .env
├─ requirements.txt
└─ README.md
```

---


## 🧪 Consejos de prueba

- Preguntas ejemplo:
  - “¿Tenés platos con arroz?” → debería citar el *Risotto de Hongos*.
  - “¿Horario de cena?” → debería recuperar los horarios del documento.
  - “¿Qué tal Messi?” → debería activar `off_topic_tool`.
- Cierre:
  - Escribir “gracias” → router → `capitan_pedidos` → tool de Notion → despedida.

---
