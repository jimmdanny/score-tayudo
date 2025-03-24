import streamlit as st

# Funciones de puntuación para cada grupo

def calcular_score_parcial(
    dias_ultima_compra,
    monto_compra,
    frecuencia_mensual,
    tipo_documento,
    direccion_valida,
    antiguedad_meses,
    referencia_vendedor
):
    if dias_ultima_compra < 15:
        score_recencia = 10
    elif dias_ultima_compra <= 30:
        score_recencia = 7
    elif dias_ultima_compra <= 60:
        score_recencia = 4
    else:
        score_recencia = 1

    if monto_compra > 2000:
        score_monto = 10
    elif monto_compra > 1000:
        score_monto = 7
    elif monto_compra > 300:
        score_monto = 4
    else:
        score_monto = 1

    if frecuencia_mensual >= 4:
        score_frecuencia = 10
    elif frecuencia_mensual >= 2:
        score_frecuencia = 6
    else:
        score_frecuencia = 2

    if tipo_documento == "RUC":
        score_datos = 5
    elif tipo_documento == "DNI":
        score_datos = 2
    else:
        score_datos = 0

    if direccion_valida:
        score_datos += 2

    if antiguedad_meses > 24:
        score_antiguedad = 10
    elif antiguedad_meses > 12:
        score_antiguedad = 7
    elif antiguedad_meses >= 6:
        score_antiguedad = 4
    else:
        score_antiguedad = 1

    if referencia_vendedor == 5:
        score_referencia = 10
    elif referencia_vendedor == 4:
        score_referencia = 8
    elif referencia_vendedor == 3:
        score_referencia = 5
    elif referencia_vendedor == 2:
        score_referencia = 2
    else:
        score_referencia = 0

    score_final = (
        0.15 * score_recencia +
        0.20 * score_monto +
        0.20 * score_frecuencia +
        0.10 * score_datos +
        0.15 * score_antiguedad +
        0.20 * score_referencia
    )

    return round(score_final * 10, 2)


def calcular_score_completo(score_parcial, entidades, calificacion, incremento):
    if entidades <= 2:
        score_entidades = 10
    elif entidades <= 4:
        score_entidades = 6
    else:
        score_entidades = 2

    mapa_calif = {"A": 10, "B": 6, "C": 3, "D": 0}
    score_calif = mapa_calif.get(calificacion.upper(), 0)

    if incremento < 0:
        score_deuda = 10
    elif incremento == 0:
        score_deuda = 6
    else:
        score_deuda = 0

    score_extra = (
        0.33 * score_entidades +
        0.34 * score_calif +
        0.33 * score_deuda
    ) * 10

    score_total = (score_parcial * 0.5) + (score_extra * 0.5)
    return round(score_total, 2)


def calcular_monto_otorgar(monto_compra, score_final):
    if score_final >= 80:
        porcentaje = 0.70
    elif score_final >= 60:
        porcentaje = 0.40
    else:
        porcentaje = 0.0

    monto_otorgar = min(monto_compra * porcentaje, 1000)
    return round(monto_otorgar, 2), porcentaje

# Interfaz visual
st.title("Calculadora de Score Financiero - Tayudo")
st.header("Paso 1: Datos del cliente (para ingresar por el vendedor)")

dias = st.number_input("Días desde la última compra", 0, 365)
monto = st.number_input("Monto de la compra (S/.)", 0.0)
frecuencia = st.slider("Frecuencia de compra mensual", 0, 10, 2)
doc = st.selectbox("Tipo de documento", ["RUC", "DNI"])
direccion = st.checkbox("Dirección válida", value=True)
antiguedad = st.number_input("Antigüedad como cliente (meses)", 0, 120)
referencia = st.slider("Puntaje del vendedor (1-5)", 1, 5)

st.header("Paso 2: Datos de análisis interno (solo para Tayudo)")
with st.expander("🔒 Ingresar si ya se validaron en centrales de riesgo"):
    entidades = st.number_input("Nro. entidades financieras", 0, 20)
    calificacion = st.selectbox("Calificación crediticia (6 meses)", ["A", "B", "C", "D"])
    incremento = st.number_input("% de incremento de deuda", -100.0, 300.0)

if st.button("Calcular Score"):
    score_parcial = calcular_score_parcial(
        dias, monto, frecuencia, doc, direccion, antiguedad, referencia
    )
    mostrar = f"✅ Score preliminar: {score_parcial}"

    if 'entidades' in locals() and entidades > 0:
        score_total = calcular_score_completo(score_parcial, entidades, calificacion, incremento)
        mostrar = f"💼 Score completo: {score_total}"

        monto_otorgar, porcentaje = calcular_monto_otorgar(monto, score_total)
        if porcentaje > 0:
            st.success(mostrar)
            st.info(f"💰 Monto máximo a otorgar: S/. {monto_otorgar:.2f} ({int(porcentaje*100)}% del monto de compra, con tope de S/. 1,000)")
            st.success("✅ Cliente aprobado. El monto se asigna en función de su score y nivel de compra.")
        else:
            st.error("❌ Cliente no califica para préstamo. Score insuficiente.")
    else:
        st.success(mostrar)
        st.warning("⚠️ Aún falta completar datos internos para obtener el score final.")
