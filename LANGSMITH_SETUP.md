## 📊 ¿Cómo usar LangSmith?

### Después de ejecutar tu aplicación:
1. Ve a [smith.langchain.com](https://smith.langchain.com/)
2. Selecciona el proyecto **"la-delicia"**
3. Verás todas las trazas de tus conversaciones

### En cada traza verás:
- **Entrada del usuario** y **respuesta de Bruno**
- **Llamadas a herramientas** (retriever, Notion)
- **Decisiones del router** (experto_menu vs capitán)
- **Tiempos de respuesta** y **tokens utilizados**
- **Errores** si los hubiera

### Ejemplos de trazas:
- `route_decision` → ¿Fue a Bruno o al Capitán?
- `experto_menu_node` → ¿Qué herramientas usó Bruno?
- `consultar_menu_y_horarios` → ¿Qué documentos recuperó?
- `guardar_informe_en_notion` → ¿Se guardó correctamente?

## 🔍 Beneficios para tu proyecto:

1. **Debugging**: Si algo falla, verás exactamente dónde
2. **Optimización**: Identifica cuellos de botella
3. **Rúbrica**: Cumples el requisito de observabilidad ✅
4. **Producción**: Monitoreo en tiempo real