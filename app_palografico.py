import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image
import pypdf
import io

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
    "Envie a foto ou PDF do Palográfico", 
    type=["png", "jpg", "jpeg", "pdf"]
)

nome = st.sidebar.text_input("Nome do Candidato", "Candidato Exemplo")
idade = st.sidebar.number_input("Idade", min_value=6, max_value=100, value=35)
escolaridade = st.sidebar.selectbox(
    "Escolaridade", 
    ["Ensino Fundamental", "Ensino Médio", "Ensino Superior"]
)

# --- AJUSTE PRECISO DAS MARGENS ---
st.sidebar.markdown("---")
st.sidebar.header("🎯 Ajuste das Margens de Análise")
st.sidebar.caption("Defina a área exata do teste do candidato:")

corte_topo = st.sidebar.slider("Margem Superior - Início do Teste (%)", 0, 100, 48)
corte_base = st.sidebar.slider("Margem Inferior - Fim do Teste (%)", 0, 100, 100)
corte_esquerda = st.sidebar.slider("Margem Esquerda (%)", 0, 50, 0)
corte_direita = st.sidebar.slider("Margem Direita (%)", 50, 100, 100)

# --- MÓDULO DE PROCESSAMENTO DE IMAGEM E PDF ---
contagem_palos = 0
img_contours = None
image = None

if uploaded_file is not None:
    st.markdown("---")
    st.header("📸 Processamento de Arquivo e Detecção de Palos")
    
    try:
        # Processar PDF ou Imagem comum
        if uploaded_file.name.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(uploaded_file)
            page = reader.pages[0]
            
            if len(page.images) > 0:
                image_file = page.images[0]
                image = Image.open(io.BytesIO(image_file.data))
            else:
                st.error("Não foi possível extrair uma imagem válida deste PDF.")
        else:
            image = Image.open(uploaded_file)
        
        if image is not None:
            img_array = np.array(image.convert('RGB'))
            height_total, width_total, _ = img_array.shape
            
            # --- CÁLCULO DOS LIMITES REAIS DA MARGEM ---
            y_min = int(height_total * (corte_topo / 100))
            y_max = int(height_total * (corte_base / 100))
            x_min = int(width_total * (corte_esquerda / 100))
            x_max = int(width_total * (corte_direita / 100))
            
            # Validação para evitar cortes inválidos
            if y_max > y_min and x_max > x_min:
                # Extrai apenas a região delimitada pelas margens do candidato
                roi = img_array[y_min:y_max, x_min:x_max]
                gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                
                # --- PRÉ-PROCESSAMENTO DA ÁREA DO TESTE ---
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                gray_enhanced = clahe.apply(gray)
                blurred = cv2.GaussianBlur(gray_enhanced, (3, 3), 0)
                thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                
                # --- FILTRAGEM MORFOLÓGICA ---
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
                mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                img_contours = img_array.copy()
                
                # Desenha a caixa delimitadora da margem (Em Azul)
                cv2.rectangle(img_contours, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)
                
                contagem_palos = 0
                
                for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    # Converte coordenadas para a imagem global
                    x_real = x + x_min
                    y_real = y + y_min
                    
                    min_h = height_total * 0.015
                    aspect_ratio = h / max(w, 1)
                    max_w = height_total * 0.01

                    if h > min_h and h < (height_total * 0.1) and aspect_ratio > 1.8 and w < max_w:
                        contagem_palos += 1
                        cv2.rectangle(img_contours, (x_real, y_real), (x_real + w, y_real + h), (0, 255, 0), 2)
                        
                # Exibição dos Resultados
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.image(image, caption="Documento Enviado", use_column_width=True)
                with col_img2:
                    st.image(img_contours, caption="Área Útil do Teste (Caixa Azul = Margens do Candidato)", use_column_width=True)
                    
                st.info(f"💡 **Sugestão da Câmera:** Foram identificados aproximadamente **{contagem_palos} palos** dentro da margem delimitada.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.sidebar.markdown("---")
st.sidebar.header("2. Validação da Contagem por Tempo")

sugestao_por_tempo = contagem_palos // 5 if contagem_palos > 0 else 90

t1 = st.sidebar.number_input("Tempo 1 (1 min)", value=sugestao_por_tempo)
t2 = st.sidebar.number_input("Tempo 2 (1 min)", value=sugestao_por_tempo)
t3 = st.sidebar.number_input("Tempo 3 (1 min)", value=sugestao_por_tempo)
t4 = st.sidebar.number_input("Tempo 4 (1 min)", value=sugestao_por_tempo)
t5 = st.sidebar.number_input("Tempo 5 (1 min)", value=sugestao_por_tempo)

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
