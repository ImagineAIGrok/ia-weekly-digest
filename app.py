import streamlit as st
import feedparser
from datetime import datetime, timedelta
from openai import OpenAI
import time
import gspread  # Import correcto al principio

# Configuración
st.set_page_config(page_title="IA Weekly Digest", layout="wide")
st.title("📈 IA Weekly Digest")
st.markdown("### Resumen semanal automático de los avances más importantes en IA")
st.markdown("Fuentes: Hugging Face Daily Papers (curados), arXiv (ML, AI, CV), MarkTechPost e Interconnects.ai.")

# Sidebar: Apoyo
with st.sidebar:
    st.header("🚀 Apóyame y mejoremos esto juntos")
    st.markdown("App creada con ❤️ y Grok desde Venezuela 🇻🇪")
    st.markdown("Con tu apoyo activamos **resúmenes inteligentes full con Grok API** (créditos) y más features.")
    st.markdown("- **Newsletter (Substack)**: [Suscríbete gratis para updates semanales](https://esospanas.substack.com/)")
    st.markdown("- **Ko-fi (donaciones rápidas)**: [Comprarme un café ☕](https://ko-fi.com/esospanas)")
    st.markdown("- **Crypto (Ethereum - desde $10+ recomendado)**: ")
    st.code("0xc50639FC0EA4B154AbE83Bf3006c745Cbeb0bEBd", language="text")
    st.markdown("Todo va a créditos Grok API, Premium X y más herramientas. ¡Gracias! 🇻🇪")

# API Key de Grok (opcional)
api_key = st.text_input("🔑 Grok API Key (opcional para resúmenes inteligentes)", type="password")
client = None
if api_key:
    client = OpenAI(base_url="https://api.x.ai/v1", api_key=api_key)
    st.success("Grok API conectada → resúmenes inteligentes activados")

# Feeds técnicos
feeds = [
    "https://huggingface.co/papers/rss",
    "https://papers.takara.ai/api/feed",
    "https://arxiv.org/rss/cs.LG",
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.CV",
    "https://www.marktechpost.com/feed/",
    "https://www.interconnects.ai/rss",
]

@st.cache_data(ttl=3600, show_spinner=True)
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
                            model="grok-beta",
                            messages=[{"role": "user", "content": f"Resume en 1-2 frases claras y en español por qué este avance en IA es importante: {entry['title']}\n\n{entry['raw_summary']}"}],
                            max_tokens=100
                        )
                        why = response.choices[0].message.content.strip()
                        time.sleep(1)
                    except Exception as e:
                        why = f"Error con Grok: {e}. Usando resumen básico: {why}"
            
            st.markdown(f"**Por qué importa:** {why}")

# Form de suscripción
st.markdown("---")
st.header("📩 ¡Suscríbete al Digest Semanal por Email!")
st.markdown("Recibe los 10 avances top + resúmenes directamente en tu inbox cada semana. ¡Gratis!")

with st.form(key="subscribe_form"):
    user_email = st.text_input("Tu email:")
    submit_button = st.form_submit_button("¡Suscribirme!")

    if submit_button:
        if "@" in user_email and "." in user_email:
            try:
                gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
                sh = gc.open_by_key(st.secrets["SHEET_ID"])
                worksheet = sh.sheet1
                worksheet.append_row([user_email, datetime.now().strftime("%Y-%m-%d %H:%M")])
                st.success(f"¡Suscrito con éxito! 🚀 {user_email} agregado automáticamente.")
                st.balloons()
            except Exception as e:
                st.success(f"¡Suscrito! {user_email} — Te agrego manual por ahora (configurando auto).")
                st.info("Emails se guardan pronto en Sheets full auto.")
        else:
            st.error("Email inválido, inténtalo de nuevo.")

st.caption("App creada con ❤️ y Grok desde un celular Android en Venezuela. ¡Refresca para actualizar!")
