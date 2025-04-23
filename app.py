import json
import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_keyfile_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)

client = gspread.authorize(creds)
spreadsheet = client.open("season_2025")
sheet_main = spreadsheet.worksheet("main")

@st.cache_data(ttl=3600)
def carregar_dados_jogadores():
    sheet = spreadsheet.worksheet("dados_jogadores")
    data = sheet.get_all_records()
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)
def carregar_escalacoes():
    sheet = spreadsheet.worksheet("escalacoes_rodadas")
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df_jogadores = carregar_dados_jogadores()
df_escalacoes = carregar_escalacoes()
jogadores_dict = dict(zip(df_jogadores["PLAYER"], df_jogadores["POSIÇÃO"]))

def get_jogadores_da_rodada(rodada, time):
    jogadores = df_escalacoes.query("RODADA == @rodada and TIME == @time")["JOGADOR"].tolist()
    return jogadores[:5]

st.markdown("""
<div style="text-align: center;">
    <h2>🏆 Registro de Partida</h2>
    <h1><strong>MR LEAGUE</strong></h1>
</div>
""", unsafe_allow_html=True)

data_partida = st.date_input("Data da Partida", value=datetime.today())
rodada = st.number_input("Rodada", min_value=1, step=1)

try:
    valores = sheet_main.col_values(4)[1:]
    valores_numericos = [int(v) for v in valores if v.isdigit()]
    ultimo_id = max(valores_numericos) if valores_numericos else 0
except:
    ultimo_id = 0
partida = st.number_input("ID da Partida", min_value=1, value=ultimo_id + 1, step=1)

col_team1, col_team2 = st.columns(2)
with col_team1:
    time1 = st.selectbox("Time 1", ["AMARELO", "BRANCO", "VERMELHO", "PRETO"], key="time1")
with col_team2:
    time2 = st.selectbox("Time 2", ["AMARELO", "BRANCO", "VERMELHO", "PRETO"], key="time2")

modo_mobile = st.checkbox("Modo Celular (colunas empilhadas)", value=False)

def render_time_inputs(time_nome, prefixo, jogadores_linha):
    dados_time = []
    st.markdown(f"### {time_nome} - GOLEIRO")
    jogador = st.selectbox("Goleiro", list(jogadores_dict.keys()), key=f"{prefixo}_goleiro")
    posicao = jogadores_dict.get(jogador, "GK")
    with st.expander(f"SCOUTS {jogador}"):
        st.text(f"Posição: {posicao}")
        gol = st.number_input("Gols", min_value=0, key=f"{prefixo}_goleiro_gol")
        ass = st.number_input("Assistências", min_value=0, key=f"{prefixo}_goleiro_ass")
        gc = st.number_input("Gol Contra", min_value=0, key=f"{prefixo}_goleiro_gc")
        ama = st.number_input("Cartão Amarelo", min_value=0, key=f"{prefixo}_goleiro_ama")
        azul = st.number_input("Cartão Azul", min_value=0, key=f"{prefixo}_goleiro_azul")
        ver = st.number_input("Cartão Vermelho", min_value=0, key=f"{prefixo}_goleiro_ver")
        pp = st.number_input("Pênalti Perdido", min_value=0, key=f"{prefixo}_goleiro_pp")
        falta = st.number_input("Faltas Cometidas", min_value=0, key=f"{prefixo}_goleiro_falta")
        dd = st.number_input("Defesas Difíceis", min_value=0, key=f"{prefixo}_goleiro_dd")
        dp = st.number_input("Defesas de Pênalti", min_value=0, key=f"{prefixo}_goleiro_dp")

    dados_time.append({
        "jogador": jogador, "posicao": posicao, "time": time_nome,
        "gol": gol, "ass": ass, "gc": gc, "ama": ama, "azul": azul,
        "ver": ver, "pp": pp, "falta": falta, "dd": dd, "dp": dp, "gs": None
    })

    st.markdown(f"### {time_nome} - JOGADORES DE LINHA")
    for i, jogador in enumerate(jogadores_linha):
        posicao = jogadores_dict.get(jogador, "N/A")
        with st.expander(f"SCOUTS {jogador}"):
            st.text(f"Posição: {posicao}")
            gol = st.number_input("Gols", min_value=0, key=f"{prefixo}_linha_gol_{i}")
            ass = st.number_input("Assistências", min_value=0, key=f"{prefixo}_linha_ass_{i}")
            gc = st.number_input("Gol Contra", min_value=0, key=f"{prefixo}_linha_gc_{i}")
            ama = st.number_input("Cartão Amarelo", min_value=0, key=f"{prefixo}_linha_ama_{i}")
            azul = st.number_input("Cartão Azul", min_value=0, key=f"{prefixo}_linha_azul_{i}")
            ver = st.number_input("Cartão Vermelho", min_value=0, key=f"{prefixo}_linha_ver_{i}")
            pp = st.number_input("Pênalti Perdido", min_value=0, key=f"{prefixo}_linha_pp_{i}")
            falta = st.number_input("Faltas Cometidas", min_value=0, key=f"{prefixo}_linha_falta_{i}")
        dados_time.append({
            "jogador": jogador, "posicao": posicao, "time": time_nome,
            "gol": gol, "ass": ass, "gc": gc, "ama": ama, "azul": azul,
            "ver": ver, "pp": pp, "falta": falta, "dd": None, "dp": None
        })
    return dados_time

jogadores_time1 = get_jogadores_da_rodada(rodada, time1)
jogadores_time2 = get_jogadores_da_rodada(rodada, time2)

if modo_mobile:
    time1_data = render_time_inputs(time1, "t1", jogadores_time1)
    st.markdown("---")
    time2_data = render_time_inputs(time2, "t2", jogadores_time2)
else:
    col_time1, col_time2 = st.columns(2)
    with col_time1:
        time1_data = render_time_inputs(time1, "t1", jogadores_time1)
    with col_time2:
        time2_data = render_time_inputs(time2, "t2", jogadores_time2)

# Placar automático calculado com base nos scouts
placar_time1 = sum(j["gol"] for j in time1_data) + sum(j["gc"] for j in time2_data)
placar_time2 = sum(j["gol"] for j in time2_data) + sum(j["gc"] for j in time1_data)

# Exibição visual do placar entre os times
st.markdown(f"""
<div style='text-align: center; font-size: 32px; margin-top: 10px; margin-bottom: 20px;'>
    <strong>{time1}</strong> {placar_time1} x {placar_time2} <strong>{time2}</strong>
</div>
""", unsafe_allow_html=True)

def calcular_resultado(p1, p2):
    if p1 > p2:
        return "V", "D", p2 == 0
    elif p1 < p2:
        return "D", "V", False
    else:
        return "E", "E", False

status_time1, status_time2, stg_time1 = calcular_resultado(placar_time1, placar_time2)
stg_time2 = placar_time1 == 0

for data, placar_adversario in zip([time1_data, time2_data], [placar_time2, placar_time1]):
    for jogador in data:
        if jogador["posicao"] == "GK":
            jogador["gs"] = placar_adversario

if st.button("✅ Registrar Partida"):
    all_data = []
    for data, status, stg, placar_adversario in zip(
        [time1_data, time2_data],
        [status_time1, status_time2],
        [stg_time1, stg_time2],
        [placar_time2, placar_time1]
    ):
        for jogador in data:
            linha = [
                data_partida.strftime("%Y-%m-%d"),
                "LIGA",
                rodada,
                partida,
                jogador["jogador"],
                jogador["posicao"],
                jogador["time"],
                1 if status == "V" else 0,
                1 if status == "E" else 0,
                1 if status == "D" else 0,
                jogador["gol"],
                jogador["ass"],
                1 if stg and status == "V" else 0,
                jogador["gc"],
                jogador["ama"],
                jogador["azul"],
                jogador["ver"],
                jogador["pp"],
                jogador["gs"] if jogador["posicao"] == "GK" else None,
                jogador["dd"] if jogador["posicao"] == "GK" else None,
                jogador["dp"] if jogador["posicao"] == "GK" else None,
                jogador["falta"],
            ]
            all_data.append(linha)

    for row in all_data:
        sheet_main.append_row(row)

    st.success("✅ Todos os jogadores da partida foram registrados com sucesso!")
