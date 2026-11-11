"""Panel de Streamlit: clustering de las preguntas recibidas por WhatsApp."""
import os

import altair as alt
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

ARCHIVO = os.getenv("LOG_FILE", "preguntas.csv")
EJEMPLO = "preguntas_ejemplo.csv"

STOP_ES = ["de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "que", "es", "se", "por", "con",
           "para", "del", "al", "me", "mi", "lo", "como", "cómo", "cual", "cuál", "cuales", "cuáles",
           "hay", "son", "tiene", "tienen", "puedo", "quiero", "saber", "hola", "tengo", "si", "o",
           "su", "sus", "le", "ser", "esta", "está", "este", "mas", "más", "muy", "qué", "que"]

st.set_page_config(page_title="Panel del chatbot", page_icon="📊", layout="wide")
st.title("📊 Panel del chatbot de WhatsApp")

if os.path.exists(ARCHIVO) and os.path.getsize(ARCHIVO) > 0:
    df = pd.read_csv(ARCHIVO)
    st.caption(f"Datos reales de `{ARCHIVO}`")
else:
    df = pd.read_csv(EJEMPLO)
    st.info("Todavía no hay preguntas reales: mostrando datos de ejemplo para la demo.")

if len(df) < 3:
    st.warning("Se necesitan al menos 3 preguntas para agrupar.")
    st.stop()

df["fecha"] = pd.to_datetime(df["fecha"])
c1, c2, c3 = st.columns(3)
c1.metric("Preguntas recibidas", len(df))
c2.metric("Usuarios distintos", df["usuario"].nunique())
c3.metric("Sin respuesta en los documentos", f"{(1 - df['respondida'].mean()) * 100:.0f}%")

k = st.slider("Número de temas", 2, min(8, len(df)), min(4, len(df)))

# --- Clustering ---
vec = TfidfVectorizer(stop_words=STOP_ES, ngram_range=(1, 2), strip_accents="unicode")
X = vec.fit_transform(df["pregunta"])
km = KMeans(n_clusters=k, random_state=42, n_init=10)
df["cluster"] = km.fit_predict(X)

terminos = vec.get_feature_names_out()
nombres = {}
for i, centro in enumerate(km.cluster_centers_):
    top = centro.argsort()[-3:][::-1]
    nombres[i] = f"Tema {i + 1}: " + ", ".join(terminos[top])
df["tema"] = df["cluster"].map(nombres)

coords = PCA(n_components=2, random_state=42).fit_transform(X.toarray())
df["x"], df["y"] = coords[:, 0], coords[:, 1]

izq, der = st.columns([3, 2])
with izq:
    st.subheader("Mapa de preguntas por tema")
    st.altair_chart(
        alt.Chart(df).mark_circle(size=140, opacity=0.8).encode(
            x=alt.X("x", axis=None), y=alt.Y("y", axis=None),
            color=alt.Color("tema", legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["pregunta", "tema"],
        ).properties(height=420).interactive(),
        use_container_width=True,
    )
with der:
    st.subheader("Temas más consultados")
    conteo = df["tema"].value_counts().rename_axis("tema").reset_index(name="preguntas")
    st.altair_chart(
        alt.Chart(conteo).mark_bar().encode(
            x="preguntas:Q", y=alt.Y("tema:N", sort="-x", title=None), tooltip=["tema", "preguntas"]
        ).properties(height=420),
        use_container_width=True,
    )

st.subheader("❓ Preguntas que el bot no pudo responder")
st.caption("Pistas de qué información falta agregar a los documentos.")
st.dataframe(df[df["respondida"] == 0][["fecha", "pregunta", "tema"]], use_container_width=True)

with st.expander("Ver todas las preguntas"):
    st.dataframe(df[["fecha", "usuario", "pregunta", "tema", "respondida"]], use_container_width=True)
