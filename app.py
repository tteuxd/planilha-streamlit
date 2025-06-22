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

def play_beep():
    beep_html = """
    <audio autoplay>
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
        Seu navegador não suporta áudio.
    </audio>
    """
    st.markdown(beep_html, unsafe_allow_html=True)

# Atualiza automaticamente a cada 1 segundo
st_autorefresh(interval=1000, limit=None, key="timer_refresh")

st.title("⏲️ Multi Timer Online (Sincronizado)")

# Carrega timers do JSON a cada atualização
timers = load_config()

# Formulário para novo timer
with st.form("novo_timer_form"):
    nome = st.text_input("Nome do Timer", value="Timer")
    minutos = st.number_input("Minutos", min_value=0, value=0)
    segundos = st.number_input("Segundos", min_value=0, max_value=59, value=10)
    loop = st.checkbox("Loop", value=False)
    add = st.form_submit_button("➕ Adicionar Timer")

if add:
    if minutos == 0 and segundos == 0:
        st.error("O tempo deve ser maior que zero!")
    elif nome in timers:
        st.warning(f"Timer com nome '{nome}' já existe.")
    else:
        total_segundos = minutos * 60 + segundos
        timers[nome] = {
            "total_seconds": total_segundos,
            "seconds_left": total_segundos,
            "loop": loop,
            "active": True,
            "played": False
        }
        save_config(timers)
        st.success(f"Timer '{nome}' adicionado.")

# Gerenciar timers
to_remove = []
for nome, timer in timers.items():
    st.markdown("---")
    col1, col2, col3 = st.columns([4, 1, 1])

    # Atualiza timer
    if timer["active"]:
        if timer["seconds_left"] > 0:
            timer["seconds_left"] -= 1
            timer["played"] = False
        else:
            if not timer.get("played", False):
                play_beep()
                timer["played"] = True
            st.warning(f"⏰ Timer '{nome}' terminou!")
            if timer["loop"]:
                timer["seconds_left"] = timer["total_seconds"]
                timer["played"] = False
            else:
                timer["active"] = False

    minutos = timer["seconds_left"] // 60
    segundos = timer["seconds_left"] % 60
    progresso = (timer["total_seconds"] - timer["seconds_left"]) / timer["total_seconds"] if timer["total_seconds"] > 0 else 1.0

    col1.write(f"**{nome}**: {minutos:02d}:{segundos:02d}")
    col1.progress(progresso)

    loop_checkbox = col2.checkbox("Loop", value=timer["loop"], key=f"loop_{nome}")
    if loop_checkbox != timer["loop"]:
        timers[nome]["loop"] = loop_checkbox

    if col3.button("🛑 Parar", key=f"stop_{nome}"):
        to_remove.append(nome)
        st.success(f"Timer '{nome}' removido.")

# Remove timers
for r in to_remove:
    if r in timers:
        del timers[r]

# Salva as alterações
save_config(timers)
