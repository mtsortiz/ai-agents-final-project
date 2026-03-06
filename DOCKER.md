# Guía Docker para ai-agents-final-project

## 📦 Archivos Agregados

- **Dockerfile**: Configuración multi-stage para construir la imagen
- **.dockerignore**: Archivos a excluir del build
- **docker-compose.yml**: Orquestación de contenedores
- **.env.example**: Template de variables de entorno

---

## 🚀 Inicio Rápido

### 1. Preparar Variables de Entorno

```bash
# Copiar el template de .env
cp .env.example .env

# Editar .env con tus credenciales
# GEMINI_API_KEY=tu_api_key_de_gemini
# NOTION_API_KEY=tu_api_key_de_notion
# NOTION_DATABASE_ID=tu_database_id
```

### 2. Construir la Imagen Docker

```bash
# Opción A: Usando docker directamente
docker build -t ai-agents-final-project:latest .

# Opción B: Usando docker-compose
docker-compose build
```

### 3. Ejecutar el Contenedor

```bash
# Opción A: Usando docker directamente
docker run -it --env-file .env \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  ai-agents-final-project:latest

# Opción B: Usando docker-compose (recomendado)
docker-compose up
```

### 4. Detener el Contenedor

```bash
# Con docker-compose
docker-compose down

# O con docker
docker stop ai-agents-final-project
docker rm ai-agents-final-project
```

---

## 📋 Comandos Útiles

### Ver logs
```bash
docker-compose logs -f ai-agents
```

### Ejecutar comando en el contenedor
```bash
docker-compose exec ai-agents python -c "print('Hello from Docker')"
```

### Limpiar (remover imagen y contenedor)
```bash
docker-compose down --rmi all
```

### Reconstruir sin cache
```bash
docker-compose build --no-cache
```

---

## 🔧 Personalización

### Cambiar el puerto (si la app lo requiere)
Editar `docker-compose.yml`:
```yaml
ports:
  - "8000:8000"  # puerto_host:puerto_contenedor
```

### Agregar volúmenes adicionales
```yaml
volumes:
  - ./src:/app/src  # Desarrollo en vivo
  - ./data:/app/data
```

### Variables de entorno
Todas se definen en el archivo `.env` o directamente en `docker-compose.yml`

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
→ Reconstruir la imagen: `docker-compose build --no-cache`

### "API Key not found"
→ Verificar que `.env` tenga las credenciales correctas y esté en la raíz del proyecto

### "Permission denied"
→ El contenedor usa usuario no-root (appuser). Si necesitas permisos root:
```yaml
user: "0"  # En docker-compose.yml
```

---

## 📝 Notas Importantes

- **Multi-stage build**: Optimiza el tamaño de la imagen (~300-400 MB)
- **Usuario no-root**: Mejor seguridad (corre como `appuser` en lugar de `root`)
- **Health check**: Valida que el contenedor esté saludable
- **Variables de entorno**: Sensibles - nunca las commiteés a git

---

## 🚀 Deployment

Para deployar en producción:

1. Usar un registro privado (Docker Hub, ECR, GCR, etc.)
   ```bash
   docker tag ai-agents-final-project:latest tu-registry/ai-agents:v1.0
   docker push tu-registry/ai-agents:v1.0
   ```

2. Usar secretos seguros (no .env en producción)
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - Kubernetes Secrets

3. Configurar CI/CD para auto-builds
   - GitHub Actions
   - GitLab CI
   - Jenkins
