import streamlit as st
import feedparser
from datetime import datetime, timedelta

# Configuración de la app
st.set_page_config(page_title="IA Weekly Digest", layout="wide")
st.title("📈 IA Weekly Digest")
st.markdown("### Resumen semanal automático de los avances más importantes en IA")
st.markdown("Fuentes: Hugging Face Daily Papers (curados), arXiv (ML, AI, CV) y Reddit r/MachineLearning. "
            "Se muestran los 10 más recientes de la última semana.")

# Fuentes RSS confiables (incluye HF Daily Papers curados)
feeds = [
    "https://papers.takara.ai/api/feed",                               # Hugging Face Daily Papers (curados)
    "https://arxiv.org/rss/cs.LG",                                     # arXiv Machine Learning
    "https://arxiv.org/rss/cs.AI",                                     # arXiv Artificial Intelligence
    "https://arxiv.org/rss/cs.CV",                                     # arXiv Computer Vision
    "https://www.reddit.com/r/MachineLearning/.rss",                   # Reddit r/MachineLearning
    "https://medium.com/feed/tag/artificial-intelligence",             # Medium AI tag (opcional, buenos artículos)
]

@st.cache_data(ttl=86400, show_spinner=False)  # Cache de 24 horas para no recargar cada vez
def fetch_weekly_entries(days=7):
    entries = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Obtener fecha de publicación
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Filtrar por fecha (últimos 7 días)
                if pub_date and pub_date >= cutoff_date:
                    summary = entry.summary if hasattr(entry, "summary") else entry.get("description", "Sin resumen disponible.")
                    # Limpiar HTML básico si existe
                    summary = summary.replace("<p>", "").replace("</p>", "").split("<")[0]
                    
                    entries.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": pub_date,
                        "summary": summary.strip()
                    })
        except Exception as e:
            st.warning(f"Error cargando feed {url}: {e}")
    
    # Ordenar por fecha descendente y tomar los 10 más recientes
    entries.sort(key=lambda x: x["published"], reverse=True)
    return entries[:10]

# Cargar datos
entries = fetch_weekly_entries()

if not entries:
    st.info("No se encontraron entradas recientes. Intenta más tarde o amplía el rango de días.")
else:
    st.success(f"Se encontraron {len(entries)} avances destacados de la última semana.")
    
    for i, entry in enumerate(entries, 1):
        with st.expander(f"**{i}. {entry['title']}** • {entry['published'].strftime('%d/%m/%Y')}"):
            st.markdown(f"[🔗 Abrir fuente original]({entry['link']})")
            
            # Frase corta de por qué importa (primeras 2-3 oraciones del summary/abstract)
            short_why = entry['summary']
            if len(short_why) > 400:
                short_why = short_why[:400].rsplit(".", 1)[0] + "..."
            elif "." in short_why:
                short_why = short_why.split(".", 2)[:2]
                short_why = ".".join(short_why) + "."
            
            st.markdown(f"**Por qué importa:** {short_why}")

st.caption("App creada con Streamlit + feedparser. Actualiza la página para refrescar los datos. "
           "Puedes personalizar las fuentes o añadir más feeds fácilmente.")
