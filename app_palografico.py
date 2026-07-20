import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image

# Configuração da Página
st.set_page_config(
    page_title="Sistema Palográfico - Lado Psicologia",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Sistema de Correção Automática - Teste Palográfico")
st.subheader("Lado Psicologia | Análise e Visão Computacional")

# --- BARRA LATERAL: INPUTS E UPLOAD ---
st.sidebar.header("1. Upload e Dados do Candidato")

# Upload do Teste
uploaded_file = st.sidebar.file_uploader(
    "Envie a foto/escaneamento do Palográfico", 
    type=["png", "jpg", "jpeg"]
)

nome = st.sidebar.text_input("Nome do Candidato", "Candidato Exemplo")
idade = st.sidebar.number_input("Idade", min_value=6, max_value=100, value=35)
escolaridade = st.sidebar.selectbox(
    "Escolaridade", 
    ["Ensino Fundamental", "Ensino Médio", "Ensino Superior"]
)

# --- MÓDULO DE VISÃO COMPUTACIONAL ---
palos_detectados_por_tempo = [0, 0, 0, 0, 0]

if uploaded_file is not None:
    st.markdown("---")
    st.header("📸 Processamento de Imagem e Detecção de Palos")
    
    # Converter arquivo carregado para imagem OpenCV
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Aplicação de Limiarização (Binarização em Preto e Branco)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Detecção de contornos para identificar os traços
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    img_contours = img_array.copy()
    contagem_palos = 0
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filtro de proporção: palos são mais altos do que largos
        if h > 15 and w < 15 and (h / max(w, 1)) > 1.5:
            contagem_palos += 1
            cv2.rectangle(img_contours, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image(image, caption="Imagem Original Enviada", use_column_width=True)
    with col_img2:
        st.image(img_contours, caption=f"Leitura Automática: ~{contagem_palos} traços identificados (em verde)", use_column_width=True)
        
    st.info(f"💡 **Sugestão da Câmera:** Foram identificados aproximadamente **{contagem_palos} palos** no total da folha.")

st.sidebar.markdown("---")
st.sidebar.header("2. Validação da Contagem por Tempo")

t1 = st.sidebar.number_input("Tempo 1 (1 min)", value=90)
t2 = st.sidebar.number_input("Tempo 2 (1 min)", value=95)
t3 = st.sidebar.number_input("Tempo 3 (1 min)", value=92)
t4 = st.sidebar.number_input("Tempo 4 (1 min)", value=94)
t5 = st.sidebar.number_input("Tempo 5 (1 min)", value=95)

tempos = [t1, t2, t3, t4, t5]
produtividade_total = sum(tempos)

# --- CÁLCULOS NORMATIVOS ---
media_tempos = np.mean(tempos)
desvio_padrao = np.std(tempos)
nor = (desvio_padrao / media_tempos) * 100 if media_tempos > 0 else 0

# --- PAINEL PRINCIPAL ---
col1, col2, col3 = st.columns(3)
col1.metric("Produtividade Total (N)", f"{produtividade_total} palos")
col2.metric("Oscilação Rítmica (NOR)", f"{nor:.2f}%")
col3.metric("Perfil Normativo", f"Sudeste - {escolaridade}")

st.markdown("---")
st.subheader("Resumo da Avaliação")
df_resumo = pd.DataFrame({
    'Tempo': ['1º Tempo', '2º Tempo', '3º Tempo', '4º Tempo', '5º Tempo', 'Total (N)'],
    'Quantidade de Palos': [t1, t2, t3, t4, t5, produtividade_total]
})
st.table(df_resumo)
