import streamlit as st
import feedparser
from datetime import datetime, timedelta
from openai import OpenAI
import time

# Configuración
st.set_page_config(page_title="IA Weekly Digest", layout="wide")
st.title("📈 IA Weekly Digest")
st.markdown("### Resumen semanal automático de los avances más importantes en IA")
st.markdown("Fuentes: Hugging Face Daily Papers (curados), arXiv (ML, AI, CV), MarkTechPost e Interconnects.ai.")

# Sidebar: Donaciones y newsletter
with st.sidebar:
    st.header("🚀 Apóyame")
    st.markdown("Si te gusta esta app, ayúdame a seguir creando contenido:")
    st.markdown("- **Newsletter**: [Suscríbete aquí](TU_LINK_NEWSLETTER)")  # Cambia por tu link (Substack, Beehiiv, etc.)
    st.markdown("- **Ko-fi / Café**: [Comprarme un café ☕](TU_LINK_KO_FI)")
    st.markdown("- **Crypto (Venezuela friendly)**: ")
    st.code("TU_WALLET_ADDRESS (BTC/USDT/ETC)", language="text")
    st.markdown("¡Gracias! Todo ayuda a seguir construyendo herramientas como esta con Grok.")

# API Key de Grok (secreta)
api_key = st.text_input("🔑 Grok API Key (opcional para resúmenes inteligentes)", type="password", help="Obtén tu key en https://x.ai/api o console.grok.com")
client = None
if api_key:
    client = OpenAI(base_url="https://api.x.ai/v1", api_key=api_key)
    st.success("Grok API conectada → resúmenes inteligentes activados")

# Feeds mejorados (más técnicos)
feeds = [
    "https://huggingface.co/papers/rss",
    "https://papers.takara.ai/api/feed",
    "https://arxiv.org/rss/cs.LG",
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.CV",
    "https://www.marktechpost.com/feed/",
    "https://www.interconnects.ai/rss",
]

@st.cache_data(ttl=3600, show_spinner=True)  # Cache 1 hora para refrescar más rápido
def fetch_weekly_entries(days=7):
    entries = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                if pub_date and pub_date >= cutoff_date:
                    summary = entry.summary if hasattr(entry, "summary") else "Sin resumen disponible."
                    summary = summary.replace("<p>", "").replace("</p>", "").split("<")[0].strip()
                    
                    entries.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": pub_date,
                        "raw_summary": summary
                    })
        except Exception as e:
            st.warning(f"Error con feed {url}: {e}")
    
    entries.sort(key=lambda x: x["published"], reverse=True)
    return entries[:10]

entries = fetch_weekly_entries()

if not entries:
    st.info("No hay entradas recientes. Refresca en unas horas.")
else:
    st.success(f"{len(entries)} avances destacados de la última semana")

    for i, entry in enumerate(entries, 1):
        with st.expander(f"**{i}. {entry['title']}** • {entry['published'].strftime('%d/%m/%Y')}"):
            st.markdown(f"[🔗 Fuente original]({entry['link']})")
            
            why = entry['raw_summary']
            if len(why) > 400:
                why = why[:400] + "..."
            
            if client:
                with st.spinner("Grok está resumiendo..."):
                    try:
                        response = client.chat.completions.create(
                            model="grok-beta",  # o "grok-4" si ya existe
                            messages=[{"role": "user", "content": f"Resume en 1-2 frases claras y en español por qué este avance en IA es importante: {entry['title']}\n\n{entry['raw_summary']}"}],
                            max_tokens=100
                        )
                        why = response.choices[0].message.content.strip()
                        time.sleep(1)  # Para no saturar rate limits
                    except Exception as e:
                        why = f"Error con Grok: {e}. Usando resumen básico: {why}"
            
            st.markdown(f"**Por qué importa:** {why}")

st.caption("App creada con ❤️ y Grok desde un celular Android en Venezuela. ¡Refresca para actualizar!")
