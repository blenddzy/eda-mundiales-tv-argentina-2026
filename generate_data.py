"""
generate_data.py
Genera un CSV con datos sintéticos basados en los patrones reales
del INDEC — Intercambio Comercial Argentino (ICA).

Fuente de referencia:
https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40

Los valores son estimaciones realistas basadas en los informes
publicados mensualmente. Para reemplazar con datos reales,
descargá los Excel del INDEC y adaptá el script de carga al final.
"""

import pandas as pd
import numpy as np
from datetime import date

np.random.seed(42)

def generar_datos():
    fechas = pd.date_range("2013-01-01", "2026-05-01", freq="MS")
    
    records = []
    for fecha in fechas:
        año = fecha.year
        mes = fecha.month

        # ── Base electrónica de consumo (mill. USD) ───────────────────────────
        # Tendencia base: crecimiento gradual con crisis en 2018-2019, 2023
        if año <= 2015:
            base_elec = 180
        elif año <= 2017:
            base_elec = 160
        elif año == 2018:
            base_elec = 140
        elif año == 2019:
            base_elec = 90   # crisis cambiaria
        elif año == 2020:
            base_elec = 70   # pandemia
        elif año == 2021:
            base_elec = 130  # recuperación
        elif año == 2022:
            base_elec = 150
        elif año == 2023:
            base_elec = 80   # cepo importaciones
        elif año == 2024:
            base_elec = 110  # apertura Milei
        else:
            base_elec = 130  # 2025-2026

        # ── Efecto Mundial ────────────────────────────────────────────────────
        # Mundiales: Jun-Jul 2014, Jun-Jul 2018, Nov-Dic 2022, Jun-Jul 2026
        boost_mundial = 0

        # Pre-mundial (pico de importación: 2-4 meses antes)
        mundiales = {
            2014: (6, 7),   # Brasil
            2018: (6, 7),   # Rusia
            2022: (11, 12), # Qatar
            2026: (6, 7),   # USA/CAN/MEX
        }

        if año in mundiales:
            m_inicio, m_fin = mundiales[año]
            meses_pre = range(m_inicio - 4, m_inicio)
            meses_durante = range(m_inicio, m_fin + 1)

            if mes in meses_pre:
                # Pico en los 2 meses anteriores al mundial
                distancia = m_inicio - mes
                boost_mundial = base_elec * (0.35 if distancia <= 2 else 0.15)
            elif mes in meses_durante:
                boost_mundial = base_elec * 0.10  # durante el torneo baja un poco

        # ── Estacionalidad general ─────────────────────────────────────────────
        # Diciembre y enero tienen más importaciones de consumo
        boost_diciembre = base_elec * 0.12 if mes == 12 else 0
        boost_enero     = base_elec * 0.08 if mes == 1  else 0

        # ── Valor final con ruido ─────────────────────────────────────────────
        valor_elec = base_elec + boost_mundial + boost_diciembre + boost_enero
        valor_elec *= np.random.uniform(0.92, 1.08)

        # ── Bienes de capital (maquinaria y herramientas) ─────────────────────
        # Más estable, con caída en crisis y recuperación post-2024
        if año <= 2017:
            base_cap = 900
        elif año <= 2019:
            base_cap = 650
        elif año == 2020:
            base_cap = 500
        elif año <= 2022:
            base_cap = 750
        elif año == 2023:
            base_cap = 550
        else:
            base_cap = 700
        valor_cap = base_cap * np.random.uniform(0.88, 1.12)

        # ── Vehículos ─────────────────────────────────────────────────────────
        if año <= 2017:
            base_veh = 800
        elif año <= 2019:
            base_veh = 400
        elif año == 2020:
            base_veh = 200
        elif año <= 2022:
            base_veh = 600
        elif año == 2023:
            base_veh = 300
        else:
            base_veh = 500
        valor_veh = base_veh * np.random.uniform(0.85, 1.15)

        # ── Productos intermedios ──────────────────────────────────────────────
        base_int = 1800 if año >= 2021 else 1500
        if año in [2019, 2023]:
            base_int *= 0.7
        valor_int = base_int * np.random.uniform(0.90, 1.10)

        records.append({
            "fecha":                    fecha.strftime("%Y-%m"),
            "año":                      año,
            "mes":                      mes,
            "electronica_consumo_musd": round(valor_elec, 1),
            "bienes_capital_musd":      round(valor_cap, 1),
            "vehiculos_musd":           round(valor_veh, 1),
            "bienes_intermedios_musd":  round(valor_int, 1),
            "es_año_mundial":           1 if año in mundiales else 0,
        })

    df = pd.DataFrame(records)
    df["total_importaciones_musd"] = (
        df["electronica_consumo_musd"] +
        df["bienes_capital_musd"] +
        df["vehiculos_musd"] +
        df["bienes_intermedios_musd"]
    ).round(1)

    return df


if __name__ == "__main__":
    df = generar_datos()
    df.to_csv("data/importaciones_argentina_2013_2026.csv", index=False)
    print(f"Dataset generado: {len(df)} filas")
    print(df.tail())
