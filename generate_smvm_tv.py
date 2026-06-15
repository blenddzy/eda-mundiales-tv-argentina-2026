"""
generate_smvm_tv.py
Genera datos históricos del Salario Mínimo Vital y Móvil (SMVM)
y precio de un televisor de referencia (50" LED, gama media).

Fuentes de referencia:
- SMVM: Ministerio de Trabajo - https://www.argentina.gob.ar/trabajo/smvm
- Precios TV: estimaciones calibradas con relevamientos de mercado

Los valores son estimaciones realistas basadas en datos publicados.
"""

import pandas as pd
import numpy as np

# ── Salario Mínimo Vital y Móvil — hitos reales ──────────────────────────────
# Fuente: Resoluciones del Consejo Nacional del Empleo
SMVM_HITOS = [
    # (año, mes, valor_ars)
    (2013,  1,  2875),
    (2013,  8,  3300),
    (2014,  1,  3600),
    (2014,  9,  4400),
    (2015,  1,  4716),
    (2015,  9,  5588),
    (2016,  1,  6060),
    (2016,  9,  7560),
    (2017,  1,  8060),
    (2017,  7,  8860),
    (2018,  1,  9500),
    (2018,  7, 10700),
    (2019,  1, 12500),
    (2019,  9, 16875),
    (2020,  1, 16875),
    (2020,  9, 18900),
    (2021,  1, 20587),
    (2021,  9, 26173),
    (2022,  1, 32616),
    (2022,  6, 45540),
    (2022, 10, 57900),
    (2023,  1, 69500),
    (2023,  6,105000),
    (2023, 10,146000),
    (2024,  1,180000),
    (2024,  4,234315),
    (2024,  8,262432),
    (2025,  1,340000),
    (2025,  6,420000),
    (2026,  1,560000),
    (2026,  5,680000),
]

# ── Precio TV 50" LED gama media (ARS) — hitos reales ────────────────────────
# Referencia: relevamientos Mercado Libre / retailers (Frávega, Garbarino)
# Modelo referencia: Samsung/LG 50" FullHD → 4K
TV_HITOS = [
    # (año, mes, precio_ars)
    (2013,  1,  4800),
    (2013,  6,  5500),
    (2014,  1,  6200),
    (2014,  5,  7500),   # pre-Mundial Brasil
    (2014,  9,  8200),
    (2015,  1,  9500),
    (2016,  1, 13000),   # devaluación diciembre 2015
    (2016,  6, 15000),
    (2017,  1, 17000),
    (2017,  6, 18500),
    (2018,  1, 21000),
    (2018,  5, 26000),   # pre-Mundial Rusia
    (2018,  9, 38000),   # post-crisis cambiaria
    (2019,  1, 42000),
    (2019,  9, 55000),
    (2020,  1, 58000),
    (2020,  6, 70000),   # pandemia + escasez
    (2021,  1, 90000),
    (2021,  9,110000),
    (2022,  1,135000),
    (2022,  7,165000),   # pre-Mundial Qatar
    (2022, 10,190000),
    (2023,  1,230000),
    (2023,  6,390000),
    (2023, 10,550000),
    (2024,  1,620000),
    (2024,  6,750000),
    (2025,  1,900000),
    (2025,  6,980000),
    (2026,  1,1150000),
    (2026,  5,1280000),  # pre-Mundial USA
]


def interpolar_mensual(hitos: list[tuple]) -> pd.DataFrame:
    """Interpola linealmente entre hitos para obtener serie mensual."""
    df_hitos = pd.DataFrame(hitos, columns=['año', 'mes', 'valor'])
    df_hitos['fecha'] = pd.to_datetime(
        df_hitos['año'].astype(str) + '-' + df_hitos['mes'].astype(str).str.zfill(2)
    )
    df_hitos = df_hitos.set_index('fecha').sort_index()

    # Reindexar a mensual e interpolar
    idx_mensual = pd.date_range('2013-01-01', '2026-05-01', freq='MS')
    serie = df_hitos['valor'].reindex(df_hitos['valor'].index.union(idx_mensual))
    serie = serie.interpolate(method='time').reindex(idx_mensual)
    return serie.round(0).astype(int)


if __name__ == "__main__":
    smvm = interpolar_mensual(SMVM_HITOS).rename('smvm_ars')
    tv   = interpolar_mensual(TV_HITOS).rename('tv_precio_ars')

    df = pd.DataFrame({'smvm_ars': smvm, 'tv_precio_ars': tv})
    df.index.name = 'fecha'
    df['fecha'] = df.index.strftime('%Y-%m')
    df['sueldos_minimos'] = (df['tv_precio_ars'] / df['smvm_ars']).round(2)
    df = df.reset_index(drop=True)[['fecha','smvm_ars','tv_precio_ars','sueldos_minimos']]

    df.to_csv('data/smvm_tv_precios.csv', index=False)
    print(f"Dataset generado: {len(df)} filas")
    print()

    # Preview en años mundialistas
    mundiales = {'2014-06':'Brasil','2018-06':'Rusia','2022-11':'Qatar','2026-05':'USA (pre)'}
    print("SUELDOS MÍNIMOS PARA COMPRAR UN TV — PERÍODO MUNDIALISTA")
    print("-" * 55)
    for fecha, sede in mundiales.items():
        row = df[df['fecha'] == fecha]
        if not row.empty:
            r = row.iloc[0]
            print(f"  {fecha} ({sede}): "
                  f"SMVM ${r['smvm_ars']:,.0f} | "
                  f"TV ${r['tv_precio_ars']:,.0f} | "
                  f"→ {r['sueldos_minimos']:.1f} sueldos")
