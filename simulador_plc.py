import streamlit as st
import schemdraw
schemdraw.use('matplotlib') 
import schemdraw.elements as elm
import schemdraw.logic as log
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Simulador HMI-PLC - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_GREEN}; border-radius: 4px; font-weight: bold; color: #333; font-family: 'serif';}}
    .alert-box-off {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; font-family: 'serif';}}
    
    /* Estilos para la Tabla de Verdad */
    .truth-table {{ width: 100%; border-collapse: collapse; font-family: 'serif'; text-align: center; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    .truth-table th {{ background-color: {TEC_GREEN}; color: white; padding: 10px; border: 1px solid #ddd; }}
    .truth-table td {{ padding: 10px; border: 1px solid #ddd; font-weight: bold; color: #333; }}
    .active-row {{ background-color: #e6f0eb; border: 2px solid {TEC_GREEN} !important; color: {TEC_GREEN} !important; font-size: 1.1em; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Laboratorio de Redes: Simulador Lógico y de Escalera</p>', unsafe_allow_html=True)

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def evaluar_logica(puerta, a, b):
    if puerta == "AND": return a and b
    elif puerta == "OR": return a or b
    elif puerta == "NOT": return not a
    elif puerta == "NAND": return not (a and b)
    elif puerta == "NOR": return not (a or b)
    elif puerta == "XOR": return a != b
    elif puerta == "XNOR": return a == b

# ==========================================
# BARRA LATERAL: CONFIGURACIÓN DEL RUNG
# ==========================================
st.sidebar.header("1. Configuración de Lógica")
st.sidebar.caption("Seleccione la función lógica a simular:")

gate_type = st.sidebar.selectbox("Compuerta Lógica:", 
                                 ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"])

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# LÓGICA DE CONTROL (EVALUACIÓN BOOLEANA)
# ==========================================
col_ctrl, col_vis = st.columns([1, 2])

with col_ctrl:
    st.markdown('<p class="section-header">Panel de Operador (Entradas)</p>', unsafe_allow_html=True)
    st.write("Active o desactive las señales físicas:")
    
    val_i0 = st.toggle("Activar Sensor I0.0 (Input 1)")
    
    if gate_type == "NOT":
        val_i1 = False
        st.caption("*(Input 2 deshabilitado para compuerta NOT)*")
    else:
        val_i1 = st.toggle("Activar Sensor I0.1 (Input 2)")
    
    # Evaluación del estado actual
    q0 = evaluar_logica(gate_type, val_i0, val_i1)

    st.markdown('<p class="section-header">Estado de Salida (Q0.0)</p>', unsafe_allow_html=True)
    if q0:
        st.markdown(f'<div class="alert-box">ENERGIZADA (1 Lógico)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box-off">DESENERGIZADA (0 Lógico)</div>', unsafe_allow_html=True)

# ==========================================
# INTERFAZ GRÁFICA (SCHEMDRAW Y TABLA)
# ==========================================
color_on = TEC_GREEN
color_off = 'gray'

with col_vis:
    # ---------------------------------------------------------
    # 1. DIAGRAMA ELÉCTRICO EQUIVALENTE (ESCALERA)
    # ---------------------------------------------------------
    st.markdown('<p class="section-header">1. Circuito Eléctrico Equivalente</p>', unsafe_allow_html=True)
    
    with schemdraw.Drawing(show=False) as d_elec:
        d_elec.config(fontsize=10, lw=2, font='serif')
        
        d_elec += elm.Line().down().length(1).color(color_on)
        d_elec += elm.Line().right().length(0.5).color(color_on)
        
        if gate_type == "AND":
            d_elec += elm.Switch(action='close' if val_i0 else 'open').right().length(3).label('I0.0 (NO)').color(color_on if val_i0 else color_off)
            d_elec += elm.Switch(action='close' if val_i1 else 'open').right().length(3).label('I0.1 (NO)').color(color_on if (val_i0 and val_i1) else color_off)
        
        elif gate_type == "OR":
            d_elec += elm.Line().right().length(0.5).color(color_on)
            d_elec.push()
            d_elec += elm.Line().up().length(1).color(color_on)
            d_elec += elm.Switch(action='close' if val_i0 else 'open').right().length(3).label('I0.0 (NO)').color(color_on if val_i0 else color_off)
            d_elec += elm.Line().down().length(1).color(color_on if val_i0 else color_off)
            d_elec.pop()
            d_elec += elm.Line().down().length(1).color(color_on)
            d_elec += elm.Switch(action='close' if val_i1 else 'open').right().length(3).label('I0.1 (NO)').color(color_on if val_i1 else color_off)
            d_elec += elm.Line().up().length(1).color(color_on if val_i1 else color_off)
            d_elec += elm.Line().right().length(0.5).color(color_on if q0 else color_off)

        elif gate_type == "NOT":
            d_elec += elm.Switch(action='open' if val_i0 else 'close').right().length(3).label('I0.0 (NC)').color(color_on if not val_i0 else color_off)

        elif gate_type == "NAND":
            d_elec += elm.Line().right().length(0.5).color(color_on)
            d_elec.push()
            d_elec += elm.Line().up().length(1).color(color_on)
            d_elec += elm.Switch(action='open' if val_i0 else 'close').right().length(3).label('I0.0 (NC)').color(color_on if not val_i0 else color_off)
            d_elec += elm.Line().down().length(1).color(color_on if not val_i0 else color_off)
            d_elec.pop()
            d_elec += elm.Line().down().length(1).color(color_on)
            d_elec += elm.Switch(action='open' if val_i1 else 'close').right().length(3).label('I0.1 (NC)').color(color_on if not val_i1 else color_off)
            d_elec += elm.Line().up().length(1).color(color_on if not val_i1 else color_off)
            d_elec += elm.Line().right().length(0.5).color(color_on if q0 else color_off)

        elif gate_type == "NOR":
            d_elec += elm.Switch(action='open' if val_i0 else 'close').right().length(3).label('I0.0 (NC)').color(color_on if not val_i0 else color_off)
            d_elec += elm.Switch(action='open' if val_i1 else 'close').right().length(3).label('I0.1 (NC)').color(color_on if (not val_i0 and not val_i1) else color_off)

        elif gate_type == "XOR":
            d_elec += elm.Line().right().length(0.5).color(color_on)
            d_elec.push()
            d_elec += elm.Line().up().length(1.2).color(color_on)
            d_elec += elm.Switch(action='close' if val_i0 else 'open').right().length(2).label('I0.0 (NO)').color(color_on if val_i0 else color_off)
            d_elec += elm.Switch(action='open' if val_i1 else 'close').right().length(2).label('I0.1 (NC)').color(color_on if (val_i0 and not val_i1) else color_off)
            d_elec += elm.Line().down().length(1.2).color(color_on if (val_i0 and not val_i1) else color_off)
            d_elec.pop()
            d_elec += elm.Line().down().length(1.2).color(color_on)
            d_elec += elm.Switch(action='open' if val_i0 else 'close').right().length(2).label('I0.0 (NC)').color(color_on if not val_i0 else color_off)
            d_elec += elm.Switch(action='close' if val_i1 else 'open').right().length(2).label('I0.1 (NO)').color(color_on if (not val_i0 and val_i1) else color_off)
            d_elec += elm.Line().up().length(1.2).color(color_on if (not val_i0 and val_i1) else color_off)
            d_elec += elm.Line().right().length(0.5).color(color_on if q0 else color_off)

        elif gate_type == "XNOR":
            d_elec += elm.Line().right().length(0.5).color(color_on)
            d_elec.push()
            d_elec += elm.Line().up().length(1.2).color(color_on)
            d_elec += elm.Switch(action='close' if val_i0 else 'open').right().length(2).label('I0.0 (NO)').color(color_on if val_i0 else color_off)
            d_elec += elm.Switch(action='close' if val_i1 else 'open').right().length(2).label('I0.1 (NO)').color(color_on if (val_i0 and val_i1) else color_off)
            d_elec += elm.Line().down().length(1.2).color(color_on if (val_i0 and val_i1) else color_off)
            d_elec.pop()
            d_elec += elm.Line().down().length(1.2).color(color_on)
            d_elec += elm.Switch(action='open' if val_i0 else 'close').right().length(2).label('I0.0 (NC)').color(color_on if not val_i0 else color_off)
            d_elec += elm.Switch(action='open' if val_i1 else 'close').right().length(2).label('I0.1 (NC)').color(color_on if (not val_i0 and not val_i1) else color_off)
            d_elec += elm.Line().up().length(1.2).color(color_on if (not val_i0 and not val_i1) else color_off)
            d_elec += elm.Line().right().length(0.5).color(color_on if q0 else color_off)

        d_elec += elm.Lamp().right().length(2).label('Q0.0').color(color_on if q0 else color_off)
        d_elec += elm.Line().right().length(0.5).color(color_off)
        d_elec += elm.Line().down().length(1).color(color_off)
    
    fig_elec = plt.gcf()
    fig_elec.patch.set_alpha(0.0) 
    st.pyplot(fig_elec)
    plt.close(fig_elec)

    # ---------------------------------------------------------
    # 2. DIAGRAMA DE COMPUERTA LÓGICA
    # ---------------------------------------------------------
    st.markdown('<p class="section-header">2. Símbolo Lógico Estándar</p>', unsafe_allow_html=True)
    
    with schemdraw.Drawing(show=False) as d_log:
        d_log.config(fontsize=14, lw=2, font='serif')
        
        c_in0 = color_on if val_i0 else color_off
        c_in1 = color_on if val_i1 else color_off
        c_out = color_on if q0 else color_off

        if gate_type == "AND": G = d_log.add(log.And().label('AND', 'center'))
        elif gate_type == "OR": G = d_log.add(log.Or().label('OR', 'center'))
        elif gate_type == "NOT": G = d_log.add(log.Not().label('NOT', 'center'))
        elif gate_type == "NAND": G = d_log.add(log.Nand().label('NAND', 'center'))
        elif gate_type == "NOR": G = d_log.add(log.Nor().label('NOR', 'center'))
        elif gate_type == "XOR": G = d_log.add(log.Xor().label('XOR', 'center'))
        elif gate_type == "XNOR": G = d_log.add(log.Xnor().label('XNOR', 'center'))
            
        if gate_type == "NOT":
            d_log.add(elm.Line().left().at(G.in1).length(1.5).color(c_in0).label('Input', 'left'))
        else:
            d_log.add(elm.Line().left().at(G.in1).length(1.5).color(c_in0).label('Input 1', 'left'))
            d_log.add(elm.Line().left().at(G.in2).length(1.5).color(c_in1).label('Input 2', 'left'))
            
        d_log.add(elm.Line().right().at(G.out).length(1.5).color(c_out).label('Output', 'right'))

    fig_log = plt.gcf()
    fig_log.patch.set_alpha(0.0)
    st.pyplot(fig_log)
    plt.close(fig_log)

    # ---------------------------------------------------------
    # 3. TABLA DE VERDAD DINÁMICA
    # ---------------------------------------------------------
    st.markdown('<p class="section-header">3. Tabla de Verdad Dinámica</p>', unsafe_allow_html=True)
    
    # Construcción dinámica del HTML de la tabla
    html_table = '<table class="truth-table">'
    
    if gate_type == "NOT":
        html_table += f"<tr><th>Input (I0.0)</th><th>Output (Q0.0)</th></tr>"
        for a in [False, True]:
            out = evaluar_logica(gate_type, a, False)
            is_active = (val_i0 == a)
            row_class = "active-row" if is_active else ""
            html_table += f"<tr class='{row_class}'><td>{int(a)}</td><td>{int(out)}</td></tr>"
    else:
        html_table += f"<tr><th>Input 1 (I0.0)</th><th>Input 2 (I0.1)</th><th>Output (Q0.0)</th></tr>"
        for a in [False, True]:
            for b in [False, True]:
                out = evaluar_logica(gate_type, a, b)
                is_active = (val_i0 == a and val_i1 == b)
                row_class = "active-row" if is_active else ""
                html_table += f"<tr class='{row_class}'><td>{int(a)}</td><td>{int(b)}</td><td>{int(out)}</td></tr>"
    
    html_table += "</table>"
    
    st.markdown(html_table, unsafe_allow_html=True)