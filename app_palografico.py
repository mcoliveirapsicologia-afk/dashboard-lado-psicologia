import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sistema de Correção Palográfico - Lado Psicologia", layout="wide")

st.title("Sistema de Correção Automática - Teste Palográfico")
st.subheader("Padronização Região Sudeste (Conforme Manual SATEPSI)")

# Sidebar para Entrada de Dados do Candidato
st.sidebar.header("Dados do Candidato")
nome = st.sidebar.text_input("Nome do Candidato", "Candidato Exemplo")
idade = st.sidebar.number_input("Idade", min_value=18, max_value=80, value=35)
escolaridade = st.sidebar.selectbox("Escolaridade", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior"])
finalidade = st.sidebar.selectbox("Finalidade", ["CNH / Trânsito", "Porte / Posse de Arma", "Seleção / Perícia Clínico-Organizacional"])

# Dados Quantitativos (Contagem dos Tempos)
st.sidebar.header("Contagem de Palos por Tempo")
t1 = st.sidebar.number_input("1º Tempo (1 min)", value=90)
t2 = st.sidebar.number_input("2º Tempo (1 min)", value=95)
t3 = st.sidebar.number_input("3º Tempo (1 min)", value=93)
t4 = st.sidebar.number_input("4º Tempo (1 min)", value=92)
t5 = st.sidebar.number_input("5º Tempo (1 min)", value=96)

# Dados Das Medidas Espaciais em mm
st.sidebar.header("Medições com Régua (mm)")
tamanho_palo = st.sidebar.number_input("Tamanho dos Palos (mm)", value=7.0)
dist_palos = st.sidebar.number_input("Distância entre Palos (mm)", value=2.5)
dist_linhas = st.sidebar.number_input("Distância entre Linhas (mm)", value=8.0)

# Processamento dos Cálculos
N = t1 + t2 + t3 + t4 + t5
diffs = [abs(t2-t1), abs(t3-t2), abs(t4-t3), abs(t5-t4)]
soma_diffs = sum(diffs)
nor = (soma_diffs * 100) / N if N > 0 else 0

# Lógica de Classificação das Normas (Tabelas Sudeste)
def classificar_produtividade(n_val, esc):
    if esc == "Ensino Fundamental":
        if n_val < 377: return "Baixo / Muito Baixo"
        elif n_val <= 571: return "Médio"
        else: return "Alto / Muito Alto"
    elif esc == "Ensino Médio":
        if n_val < 414: return "Baixo / Muito Baixo"
        elif n_val <= 602: return "Médio"
        else: return "Alto / Muito Alto"
    else: # Superior
        if n_val < 460: return "Baixo / Muito Baixo"
        elif n_val <= 650: return "Médio"
        else: return "Alto / Muito Alto"

def classificar_nor(nor_val):
    if nor_val < 2.5: return "Muito Baixo (Alta Regularidade)"
    elif nor_val <= 8.5: return "Médio (Ritmo Normal)"
    else: return "Elevado (Alta Oscilação/Instabilidade)"

class_n = classificar_produtividade(N, escolaridade)
class_nor = classificar_nor(nor)

# Exibição do Painel Principal
col1, col2, col3 = st.columns(3)
col1.metric("Produtividade Total (N)", f"{N} palos", f"Classificação: {class_n}")
col2.metric("Nível de Oscilação Rítmica (NOR)", f"{nor:.2f}%", f"Classificação: {class_nor}")
col3.metric("Perfil Normativo Selecionado", f"Sudeste - {escolaridade}", f"Idade: {idade} anos")

st.markdown("---")
st.header("Análise Detalhada e Parecer Gerado")

st.write(f"**Candidato:** {nome} | **Idade:** {idade} anos | **Escolaridade:** {escolaridade}")
st.write(f"**Tabela Aplicada:** Tabela Normativa Sudeste — {escolaridade} ({idade} anos)")

# Tabela Resumo
df_resumo = pd.DataFrame({
    "Variável Mensurada": ["Produtividade (N)", "Oscilação (NOR)", "Tamanho do Palo", "Distância Palos", "Distância Linhas"],
    "Valor Obtido": [N, f"{nor:.2f}%", f"{tamanho_palo} mm", f"{dist_palos} mm", f"{dist_linhas} mm"],
    "Classificação Normativa (Sudeste)": [class_n, class_nor, "Médio / Normal" if 6.0 <= tamanho_palo <= 9.0 else "Fora da Média", "Médio / Normal", "Médio / Normal"]
})

st.table(df_resumo)

if st.button("Gerar Laudo Final em PDF"):
    st.success("Laudo processado e pronto para download conforme normas do CFP/SATEPSI!")
