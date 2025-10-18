# La Delicia RAG – Bruno, el Mozo Virtual

Sistema conversacional con **LangGraph** + **RAG** que actúa como mozo virtual (“Bruno”) para el restaurante *La Delicia*.  
El agente consulta una base de conocimiento (Chroma) y, al cerrar la conversación, registra un informe en **Notion**.

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

## 🧱 Requisitos
- Python 3.10+ (recomendado 3.11 o 3.12)
- Cuenta/API Key de **Google Generative AI (Gemini)**
- Base de datos en **Notion** (con `NOTION_API_KEY` y `NOTION_DATABASE_ID`)
- (Opcional para la rúbrica) Cuenta en **LangSmith** para tracing

---

## ⚙️ Instalación

```bash
# 1) Clonar el repo
git clone https://github.com/mtsortiz/ai-agents-final-project.git
cd ai-agents-final-project/


# 2) Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3) Instalar dependencias
pip install -r requirements.txt
```

---

## 🔐 Variables de entorno

Crear un archivo **.env** en la raíz del proyecto:

```env
# Google Gemini
GEMINI_API_KEY=tu_api_key_de_gemini

# Notion
NOTION_API_KEY=tu_api_key_de_notion
NOTION_DATABASE_ID=tu_database_id

# (Opcional pero requerido por la rúbrica) LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=tu_api_key_de_langsmith
LANGCHAIN_PROJECT=la-delicia
```


---

## ▶️ Ejecución

```bash
python -m src.main
```

Flujo típico:
1. Escribí consultas como “hola”, “¿tenés platos con arroz?”, etc.
2. Para finalizar: **“gracias”, “chau”, “salir”** (el router derivará el cierre al Capitán y se guardará en Notion).

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

## ✅ Estado del proyecto vs. Requisitos

- [x] **LangGraph con 2 agentes** (`experto_menu`, `capitan_pedidos`)
- [x] **RAG** con Chroma + Embeddings
- [x] **Persistencia en Notion** (tool `guardar_informe_en_notion`)
- [x] **Observabilidad (LangSmith)**: *Falta activarlo y adjuntar el link de Project Run en la documentación*
- [ ] **Cierre 100% por grafo**: *Asegurar que la despedida vaya por router → `capitan_pedidos` y no llamar la tool Notion desde el loop principal*
- [ ] **Edge de retorno del Capitán**: *Verificar que exista `graph.add_edge("tools", "capitan_pedidos")` para completar el ciclo tras la tool*

### Qué falta para completar la rúbrica
1. **Activar LangSmith** (no desactivar tracing).  
   - Mantener en `.env`:  
     ```
     LANGCHAIN_TRACING_V2=true
     LANGCHAIN_API_KEY=...
     LANGCHAIN_PROJECT=la-delicia
     ```
   - Correr una sesión real y **pegar el link de la Project Run** aquí en el README.
2. **Cierre por grafo** (no manual):  
   - Quitar el bypass que llama Notion directo en `main()` para despedidas, y dejar que el **router** derive a `capitan_pedidos`.
3. **Edge del Capitán**:  
   - Asegurar en `build_graph(...)`:
     ```python
     graph.add_edge("tools", "capitan_pedidos")
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

## 🧷 Troubleshooting rápido

- **`InvalidArgument: GenerateContentRequest.contents is not specified`**  
  Asegurate de que **siempre** haya al menos un `HumanMessage` antes de invocar el LLM. En el cierre, dejá que el router envíe al Capitán (que agrega un `HumanMessage` propio).
- **Bucle infinito / Recursion limit**  
  Limitá las tools por nodo (ya está hecho) y añadí los edges de regreso correctos.  
- **No se guarda en Notion**  
  Revisa `NOTION_API_KEY` y `NOTION_DATABASE_ID`. El DB debe tener propiedades: `Consulta` (title), `Resumen` (rich_text), `Fecha` (date).

---

## 📜 Licencia
MIT (o la que prefieran)
