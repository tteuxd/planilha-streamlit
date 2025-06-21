import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

CONFIG_FILE = "timers_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "timers" not in st.session_state:
    st.session_state.timers = load_config()

# Controle para evitar som repetido
if "played_sounds" not in st.session_state:
    st.session_state.played_sounds = {}

st_autorefresh(interval=1000, limit=None, key="timer_refresh")

st.title("Multi Timer Online com Streamlit com Som")

with st.form("novo_timer_form"):
    nome = st.text_input("Nome do Timer", value="Timer")
    minutos = st.number_input("Minutos", min_value=0, value=0)
    segundos = st.number_input("Segundos", min_value=0, max_value=59, value=10)
    loop = st.checkbox("Loop", value=False)
    add = st.form_submit_button("➕ Adicionar Timer")

if add:
    if minutos == 0 and segundos == 0:
        st.error("O tempo deve ser maior que zero!")
    else:
        total_segundos = minutos * 60 + segundos
        if nome in st.session_state.timers:
            st.warning(f"Timer com nome '{nome}' já existe. Escolha outro nome.")
        else:
            st.session_state.timers[nome] = {
                "total_seconds": total_segundos,
                "seconds_left": total_segundos,
                "loop": loop,
                "active": True,
            }
            st.session_state.played_sounds[nome] = False
            save_config(st.session_state.timers)
            st.success(f"Timer '{nome}' adicionado.")

to_remove = []
for nome, timer in st.session_state.timers.items():
    st.markdown("---")
    col1, col2, col3 = st.columns([4, 1, 1])

    if timer["active"]:
        if timer["seconds_left"] > 0:
            timer["seconds_left"] -= 1
            st.session_state.played_sounds[nome] = False  # reset flag se timer em contagem
        else:
            # Timer zerou
            if not st.session_state.played_sounds.get(nome, False):
                st.audio("https://www.soundjay.com/button/beep-07.wav")
                st.session_state.played_sounds[nome] = True
            st.warning(f"⏰ Timer '{nome}' terminou!")
            if timer["loop"]:
                timer["seconds_left"] = timer["total_seconds"]
                st.session_state.played_sounds[nome] = False  # reset flag para novo loop
            else:
                timer["active"] = False

    minutos = timer["seconds_left"] // 60
    segundos = timer["seconds_left"] % 60
    progresso = (timer["total_seconds"] - timer["seconds_left"]) / timer["total_seconds"] if timer["total_seconds"] > 0 else 1.0

    col1.write(f"**{nome}**: {minutos:02d}:{segundos:02d}")
    col1.progress(progresso)

    loop_checkbox = col2.checkbox("Loop", value=timer["loop"], key=f"loop_{nome}")
    if loop_checkbox != timer["loop"]:
        st.session_state.timers[nome]["loop"] = loop_checkbox
        save_config(st.session_state.timers)

    if col3.button("🛑 Parar", key=f"stop_{nome}"):
        to_remove.append(nome)
        st.success(f"Timer '{nome}' removido.")

for r in to_remove:
    if r in st.session_state.played_sounds:
        del st.session_state.played_sounds[r]
    del st.session_state.timers[r]
    save_config(st.session_state.timers)
