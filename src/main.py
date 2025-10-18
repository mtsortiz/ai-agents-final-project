import os
import re
import notion_client
from typing import Sequence, Annotated, TypedDict, Literal
from datetime import datetime
from dotenv import load_dotenv

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

def setup_environment():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(repo_root, ".env")
    load_dotenv(dotenv_path=dotenv_path)
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Falta GEMINI_API_KEY en .env")
    print(" Variables de entorno cargadas correctamente.")

def load_documents() -> list[Document]:
    menu_text = """
Aperitivos:
- Bruschetta Clásica: Pan tostado con tomates frescos, ajo, albahaca y aceite de oliva. Precio: $8. Ingredientes: pan, tomate, ajo, albahaca, aceite de oliva.
- Tabla de Quesos y Fiambres: Selección de quesos locales e importados con jamón serrano y salame. Precio: $15. Ingredientes: quesos variados, jamón serrano, salame.

Platos Principales:
- Lomo a la Pimienta: Medallón de lomo de 250g con salsa de pimienta y puré. Precio: $28. Ingredientes: lomo, pimienta, crema, puré de papas.
- Salmón a la Parrilla con Vegetales: Filete grillado con vegetales de estación. Precio: $25. Ingredientes: salmón, vegetales de estación.
- Risotto de Hongos (vegetariano): Arroz arbóreo con hongos y aceite de trufa. Precio: $22. Ingredientes: arroz, hongos, aceite de trufa, parmesano.

Postres:
- Tiramisú: Bizcocho, café, mascarpone y cacao. Precio: $9.
- Volcán de Chocolate: Centro líquido + helado de vainilla. Precio: $10.

Bebidas:
- Vino Malbec (copa): $7.
- Limonada con Menta y Jengibre: $5.
"""
    negocio_info = """
La Delicia — Av. Italia 1234, Bariloche, Río Negro, Argentina.
Propietario: Antonio Rossi. Especialidad: Cocina italiana.
Horarios: Mar-Dom (12-16h y 20-23h). Lunes cerrado.
Tel: +54 294 412-3456 — Email: reservas@ladelicia.com.ar
Ambiente familiar. Capacidad 60 cubiertos. Acepta reservas y tarjetas.
"""
    print(" Menú unificado en un solo documento.")
    print(" Información del negocio unificada en un solo documento.")
    return [
        Document(page_content=menu_text, metadata={"source": "menu.txt"}),
        Document(page_content=negocio_info, metadata={"source": "info.txt"}),
    ]

def create_or_load_vectorstore(documents: list[Document], embedding_model) -> Chroma:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = splitter.split_documents(documents)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persist_dir = os.path.join(repo_root, ".chroma", "la-delicia")
    os.makedirs(persist_dir, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory=persist_dir,
    )
    print(" Vectorstore listo (persistente).")
    return vectorstore

@tool
def off_topic_tool():
    """
    Se activa cuando el usuario pregunta algo no relacionado con el restaurante,
    el menú, los precios o los horarios. Devuelve un mensaje de redirección amable.
    """
    return (
        "Disculpe, como mozo virtual de 'La Delicia', solo puedo responder "
        "preguntas sobre nuestro menú, ingredientes, precios y horarios. "
        "¿Le gustaría saber algo sobre nuestros platos?"
    )

@tool
def guardar_informe_en_notion(consulta: str, resumen: str):
    """
    Guarda en Notion un informe con la primera consulta del cliente y un resumen final.
    
    Args:
        consulta: La primera pregunta del cliente.
        resumen: Un resumen (máx. 2 frases) de lo conversado.

    Returns:
        Mensaje de éxito o descripción del error.
    """

    notion_token = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not notion_token or not database_id:
        return "Error: faltan NOTION_API_KEY o NOTION_DATABASE_ID."
    notion = notion_client.Client(auth=notion_token)
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Consulta": {"title": [{"text": {"content": consulta}}]},
                "Resumen": {"rich_text": [{"text": {"content": resumen}}]},
                "Fecha": {"date": {"start": datetime.now().isoformat()}},
            },
        )
        return f"Informe guardado en Notion (consulta: '{consulta}')."
    except Exception as e:
        return f"Error al guardar en Notion: {e}"

def define_tools(vectorstore: Chroma) -> list:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    retriever_tool = create_retriever_tool(
        retriever,
        name="consultar_menu_y_horarios",
        description=("Busca info sobre platos, ingredientes, precios, opciones vegetarianas "
                     "y horarios del restaurante 'La Delicia'."),
    )
    print("  Herramientas definidas: consultar_menu_y_horarios, off_topic_tool, guardar_informe_en_notion.")
    return [retriever_tool, off_topic_tool, guardar_informe_en_notion]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def experto_menu_node(state: AgentState, llm):
    """Invoca al LLM con el rol de mozo para que decida el siguiente paso."""
    system_prompt = """
    Eres "Bruno", el mozo virtual del restaurante "La Delicia". Eres amable, servicial y eficiente.
    Tu objetivo es ayudar a los clientes a conocer el menú y responder sus preguntas.

    Instrucciones:
    1.  Si es un saludo, responde cordialmente SIN usar herramientas.
    2.  Utiliza la herramienta `consultar_menu_y_horarios` para responder CUALQUIER pregunta sobre platos, ingredientes, precios, recomendaciones y horarios.
    3.  Si el cliente te pide una recomendación (ej. "algo liviano", "un plato sin carne"), usa la herramienta para buscar opciones y luego preséntalas de forma atractiva.
    4.  Si la pregunta no tiene NADA que ver con el restaurante, el menú o la comida, DEBES usar la herramienta `off_topic_tool`.
    5.  Basa tus respuestas ÚNICAMENTE en la información que te proporcionan tus herramientas. No inventes platos, precios ni horarios.
    6.  Sé conciso pero completo en tus respuestas. Si das un precio, menciónalo claramente.
    """
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def capitan_pedidos_node(state: AgentState, llm_with_tools):

    # 2.1) ¿Hay al menos un mensaje humano no vacío?
    hay_humano = any(
        isinstance(m, HumanMessage) and (m.content or "").strip()
        for m in state["messages"]
    )
    if not hay_humano:
        # Modo seguro: no intentes tools; despide y listo
        resp = llm_with_tools.invoke(
            [SystemMessage(content="No hay mensajes del cliente. Despídete brevemente.")],
            tool_choice={"function_calling_config": {"mode": "NONE"}},
        )
        return {"messages": [resp]}

    # 2.2) Historial (solo texto no vacío)
    conversation_history = "\n".join(
        f"{'Cliente' if isinstance(m, HumanMessage) else 'Bruno'}: {(m.content or '').strip()}"
        for m in state["messages"]
        if (getattr(m, "content", None) or "").strip()
    )

    # 2.3) Primera consulta humana
    primera_consulta = "Interacción sin consulta inicial"
    for m in state["messages"]:
        if isinstance(m, HumanMessage) and (m.content or "").strip():
            primera_consulta = m.content.strip()
            break

    system_prompt = f"""
Eres el "Capitán", gerente de "La Delicia". Debes:
1) Leer la conversación entre Bruno y el cliente.
2) Crear un resumen muy conciso (máximo 2 frases) de lo que consultó el cliente.
3) Llamar a la herramienta `guardar_informe_en_notion` usando:
   - consulta = la primera pregunta del cliente
   - resumen = tu resumen
CONVERSACIÓN:
---
{conversation_history}
---
    """.strip()

    human_prompt = "Analiza y llama ahora a `guardar_informe_en_notion` con los argumentos solicitados."
    tool_choice = {
        "function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": ["guardar_informe_en_notion"],
        }
    }

    # 2.4) Intento con tools; si falla, despedida sin tools (no crashea)
    try:
        resp = llm_with_tools.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)],
            tool_choice=tool_choice,
        )
        return {"messages": [resp]}
    except Exception as e:
        print(f" Capitán: fallback por error: {e}")
        resp = llm_with_tools.invoke(
            [SystemMessage(content="Despídete cordialmente y agradece la visita.")],
            tool_choice={"function_calling_config": {"mode": "NONE"}},
        )
        return {"messages": [resp]}

def route(state):
    """Decide a qué agente enviar la conversación basándose en el ÚLTIMO mensaje HUMANO."""
    last_human = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage) and (m.content or "").strip():
            last_human = m
            break

    if not last_human:
        decision = "experto_menu"
        print(f"Router: no hay mensaje humano → {decision}")
        return decision

    text = (last_human.content or "").strip().lower()

    # PALABRAS CLAVE de salida: match por palabra completa (no “substrings”).
    despedidas = [
        r"\bgracias\b",
        r"\blisto\b",
        r"\beso es todo\b",
        r"\bchau\b",
        r"\bsalir\b",
        r"\bperfecto\b",
    ]
    es_despedida = any(re.search(pat, text) for pat in despedidas)

    decision = "capitan_pedidos" if es_despedida else "experto_menu"

    return decision


ALLOWED_MENU_TOOLS = {"consultar_menu_y_horarios", "off_topic_tool"}
ALLOWED_CAPTAIN_TOOLS = {"guardar_informe_en_notion"}

def _needs_tools_filtered(state, allowed_names: set[str]):
    msgs = state["messages"]
    if not msgs:
        return "__end__"

    last = msgs[-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        # Extrae los nombres de las herramientas que el modelo quiere usar
        names = [tc.get("name") for tc in last.tool_calls if isinstance(tc, dict)]
        # Solo ir a tools si hay alguna permitida
        if any(n in allowed_names for n in names):
            return "tools"

    return "__end__"


def build_graph(llm_with_tools, tools_list):
    graph = StateGraph(AgentState)

    # Nodos
    graph.add_node("experto_menu", lambda s: experto_menu_node(s, llm_with_tools))
    graph.add_node("capitan_pedidos", lambda s: capitan_pedidos_node(s, llm_with_tools))
    tools_node = ToolNode(tools_list)
    graph.add_node("tools", tools_node)

    # Nodo router (no-op)
    graph.add_node("router", lambda s: {})  # no modifica el estado

    # Entry point
    graph.set_entry_point("router")

    #  router decide hacia dónde va la conversación
    graph.add_conditional_edges(
        "router",
        route,
        {"experto_menu": "experto_menu", "capitan_pedidos": "capitan_pedidos"},
    )

    #  experto_menu: modelo → tool → modelo → END
    def _needs_tools(state):
        msgs = state["messages"]
        last = msgs[-1]
        print(f" _needs_tools: last={type(last).__name__}, "
            f"tool_calls={getattr(last, 'tool_calls', None)}")

        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            print("  Decisión: tools")
            return "tools"

        print(" Decisión: __end__")
        return "__end__"

    
    # experto_menu → tools solo si la tool pedida está permitida (retriever/off_topic)
    graph.add_conditional_edges(
        "experto_menu",
        lambda s: _needs_tools_filtered(s, ALLOWED_MENU_TOOLS),
        {"tools": "tools", "__end__": END},
    )
    graph.add_edge("tools", "experto_menu")

    # capitan_pedidos → tools solo si pide guardar_informe_en_notion
    graph.add_conditional_edges(
        "capitan_pedidos",
        lambda s: _needs_tools_filtered(s, ALLOWED_CAPTAIN_TOOLS),
        {"tools": "tools", "__end__": END},
    )

    print(" Grafo del sistema de agentes construido y compilado.")
    return graph.compile()

def main():
    setup_environment()

    # Desactivar LangSmith por defecto
    os.environ.pop("LANGCHAIN_TRACING_V2", None)

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    documents = load_documents()
    vectorstore = create_or_load_vectorstore(documents, embedding_model)
    tools = define_tools(vectorstore)
    llm_with_tools = llm.bind_tools(tools)

    rag_agent = build_graph(llm_with_tools, tools)

    print("\n" + "=" * 50)
    print("       BIENVENIDO AL RESTAURANTE 'LA DELICIA' 2.0 ")
    print("=" * 50)
    print("\nBruno, tu mozo virtual, está listo para atenderte.")
    print(" (Escribe 'gracias' o 'salir' para finalizar y guardar el informe)")

    state_messages: list[BaseMessage] = []

    exit_words = {"exit", "quit", "salir", "gracias", "chau", "perfecto"}

    while True:
        query = input("\n👤 Cliente: ").strip()
        state_messages.append(HumanMessage(content=query))

        # Salida inmediata sin LLM
        if query.lower() in exit_words:
            primera = next((m.content for m in state_messages if isinstance(m, HumanMessage) and m.content), "Interacción sin consulta inicial")
            resumen = "El cliente finalizó la conversación. Consultas previas: " + "; ".join(
                m.content for m in state_messages if isinstance(m, HumanMessage) and m.content
            )[:1800]
            # llamamos la tool python directamente
            res = guardar_informe_en_notion.invoke({"consulta": primera, "resumen": resumen})
            print("\n Bruno:", res)
            print(" Bruno: ¡Gracias por tu visita! ¡Vuelve pronto!")
            break


        result = rag_agent.invoke(
            {"messages": state_messages},
            config={"recursion_limit": 25}
        )



        # Tomar el último mensaje “de texto” seguro
        final = result["messages"][-1]
        text = getattr(final, "content", None)
        if not text:
            # Buscar el último AIMessage con texto
            for m in reversed(result["messages"]):
                if isinstance(m, AIMessage) and getattr(m, "content", None):
                    text = m.content
                    break
            if not text:
                text = "[Sin respuesta de texto del modelo]"

        print(f"\n Bruno: {text}")

        # Actualizar estado
        state_messages = result["messages"]

if __name__ == "__main__":
    main()
