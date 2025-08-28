# operacoes_data.py
# ========================================
# BANCO DE DADOS DAS OPERAÇÕES
# Apenas dados - sem lógica de negócio
# ========================================

# ========================================
# OPERAÇÕES LONG (1 até 50)
# ========================================

LONGS = {
    "long1": {
        "15m": {"yellow": 5.83, "green": 47.97, "red": 12.57},
        "3m": {"yellow": 5.07, "green": 1.50, "red": 3.80},
        "1m": {"yellow": 15.80, "green": -48.97, "red": -11.89}
    },
    "long2": {
        "15m": {"yellow": 9.86, "green": 39.72, "red": -7.24},
        "3m": {"yellow": 10.16, "green": 7.92, "red": 13.88},
        "1m": {"yellow": 14.63, "green": -14.63, "red": 7.18}
    },
    "long3": {
        "15m": {"yellow": 12.17, "green": -44.55, "red": 12.98},
        "3m": {"yellow": 18.12, "green": -66.37, "red": -21.23},
        "1m": {"yellow": 5.39, "green": 42.13, "red": -5.90}
    },
    "long4": {
        "15m": {"yellow": 10.45, "green": -17.16, "red": 4.32},
        "3m": {"yellow": 18.70, "green": -51.58, "red": -7.60},
        "1m": {"yellow": 8.41, "green": 43.48, "red": -5.80}
    },
    "long5": {
        "15m": {"yellow": 10.72, "green": -18.62, "red": -1.75},
        "3m": {"yellow": 4.85, "green": 3.39, "red": -6.88},
        "1m": {"yellow": 8.52, "green": -15.69, "red": -12.75}
    },
    "long6": {
        "15m": {"yellow": 11.77, "green": -11.53, "red": -12.03},
        "3m": {"yellow": 0.95, "green": 37.16, "red": 13.86},
        "1m": {"yellow": 14.48, "green": 4.70, "red": 0.33}
    },
    "long7": {
        "15m": {"yellow": 4.29, "green": -83.99, "red": -18.06},
        "3m": {"yellow": 18.08, "green": -21.04, "red": -41.53},
        "1m": {"yellow": 19.94, "green": -42.27, "red": -1.67}
    },
    "long8": {
        "15m": {"yellow": 11.53, "green": -49.79, "red": 16.11},
        "3m": {"yellow": 8.10, "green": -37.19, "red": 2.37},
        "1m": {"yellow": 9.57, "green": -0.57, "red": 10.39}
    },
    "long9": {
        "15m": {"yellow": 12.48, "green": 22.73, "red": 15.69},
        "3m": {"yellow": 2.99, "green": -42.31, "red": 17.83},
        "1m": {"yellow": 8.80, "green": 15.84, "red": 5.90}
    },
    "long10": {
        "15m": {"yellow": 4.20, "green": -60.57, "red": -15.93},
        "3m": {"yellow": 10.44, "green": 15.66, "red": -10.09},
        "1m": {"yellow": 13.28, "green": -0.97, "red": 0.71}
    },
    "long11": {
        "15m": {"yellow": 1.41, "green": -24.99, "red": -9.12},
        "3m": {"yellow": 7.34, "green": 6.84, "red": -4.52},
        "1m": {"yellow": 20.41, "green": -49.28, "red": 15.34}
    },
    # ========================================
    # CONTINUE ADICIONANDO SEUS DADOS AQUI
    # Copie e cole seguindo exatamente este formato:
    # "longX": {
    #     "15m": {"yellow": SEU_VALOR, "green": SEU_VALOR, "red": SEU_VALOR},
    #     "3m": {"yellow": SEU_VALOR, "green": SEU_VALOR, "red": SEU_VALOR},
    #     "1m": {"yellow": SEU_VALOR, "green": SEU_VALOR, "red": SEU_VALOR}
    # },
    # ========================================
    
    # Exemplo até long50 (substitua pelos seus dados)
    "long50": {
        "15m": {"yellow": 28, "green": 15, "red": -30},
        "3m": {"yellow": 26, "green": 17, "red": -28},
        "1m": {"yellow": 24, "green": 19, "red": -26}
    },
}

# ========================================
# OPERAÇÕES SHORT (1 até 50)
# ========================================

SHORTS = {
    "short1": {
        "15m": {"yellow": -12.14, "blue": 7.10, "red": 18.81},
        "3m": {"yellow": -3.39, "blue": -56.49, "red": -22.23},
        "1m": {"yellow": -11.39, "blue": -38.68, "red": -29.32}
    },
    "short2": {
        "15m": {"yellow": -8.74, "blue": 17.38, "red": 8.19},
        "3m": {"yellow": -3.74, "blue": -47.75, "red": -9.70},
        "1m": {"yellow": -8.29, "blue": -2.29, "red": -18.17}
    },
    "short3": {
        "15m": {"yellow": -6.33, "blue": 68.05, "red": 22.17},
        "3m": {"yellow": -1.48, "blue": -34.83, "red": 9.06},
        "1m": {"yellow": -3.73, "blue": -2.59, "red": -2.91}
    },
    "short4": {
        "15m": {"yellow": -1.44, "blue": 56.94, "red": -6.74},
        "3m": {"yellow": -19.54, "blue": 66.62, "red": 22.29},
        "1m": {"yellow": -5.18, "blue": 59.44, "red": -3.31}
    },
    "short5": {
        "15m": {"yellow": -21.44, "blue": 30.21, "red": 0.27},
        "3m": {"yellow": -7.18, "blue": 37.81, "red": -15.37},
        "1m": {"yellow": -4.41, "blue": -54.19, "red": -21.62}
    },
    "short6": {
        "15m": {"yellow": -3.84, "blue": -32.43, "red": -7.33},
        "3m": {"yellow": -13.70, "blue": 27.57, "red": 11.77},
        "1m": {"yellow": -20.88, "blue": 45.40, "red": -2.47}
    },
    "short7": {
        "15m": {"yellow": -6.58, "blue": 59.15, "red": -13.35},
        "3m": {"yellow": -10.43, "blue": 14.47, "red": -1.50},
        "1m": {"yellow": -14.16, "blue": -33.17, "red": -21.29}
    },
    "short8": {
        "15m": {"yellow": -1.90, "blue": 22.50, "red": 19.55},
        "3m": {"yellow": -17.05, "blue": 45.95, "red": 6.51},
        "1m": {"yellow": -3.58, "blue": 69.48, "red": 16.19}
    },
    "short9": {
        "15m": {"yellow": -0.47, "blue": -38.93, "red": -19.91},
        "3m": {"yellow": -14.12, "blue": 56.18, "red": -14.53},
        "1m": {"yellow": -10.05, "blue": 11.89, "red": 7.99}
    },
    "short10": {
        "15m": {"yellow": -1.40, "blue": -66.92, "red": -9.58},
        "3m": {"yellow": 9.20, "blue": -20.51, "red": -33.58},
        "1m": {"yellow": -5.69, "blue": 39.54, "red": -25.88}
    },
    "short11": {
        "15m": {"yellow": -9.71, "blue": 29.01, "red": 0.88},
        "3m": {"yellow": -7.62, "blue": -22.25, "red": 16.34},
        "1m": {"yellow": -13.61, "blue": 4.50, "red": 3.10}
    },
    # ========================================
    # CONTINUE ADICIONANDO SEUS DADOS AQUI
    # Para SHORTs use "blue" ao invés de "green"
    # ========================================
    
    "short50": {
        "15m": {"yellow": 28, "blue": 15, "red": -30},
        "3m": {"yellow": 26, "blue": 17, "red": -28},
        "1m": {"yellow": 24, "blue": 19, "red": -26}
    },
}

# ========================================
# VALIDAÇÃO DOS DADOS (executada no import)
# ========================================

def _validar_estrutura():
    """Valida se os dados estão no formato correto"""
    timeframes_esperados = {"15m", "3m", "1m"}
    cores_long_esperadas = {"yellow", "green", "red"}
    cores_short_esperadas = {"yellow", "blue", "red"}
    
    # Valida LONGs
    for nome, dados in LONGS.items():
        assert set(dados.keys()) == timeframes_esperados, f"❌ {nome}: timeframes incorretos"
        for tf, cores in dados.items():
            assert set(cores.keys()) == cores_long_esperadas, f"❌ {nome}.{tf}: cores incorretas para LONG"
    
    # Valida SHORTs
    for nome, dados in SHORTS.items():
        assert set(dados.keys()) == timeframes_esperados, f"❌ {nome}: timeframes incorretos"
        for tf, cores in dados.items():
            assert set(cores.keys()) == cores_short_esperadas, f"❌ {nome}.{tf}: cores incorretas para SHORT"
    
    return True

# Executa validação no momento do import
try:
    _validar_estrutura()
    print(f"✅ Dados validados: {len(LONGS)} LONGs, {len(SHORTS)} SHORTs")
except AssertionError as e:
    print(f"❌ ERRO na estrutura dos dados: {e}")
    raise

# ========================================
# METADADOS (apenas para referência)
# ========================================

METADATA = {
    "total_longs": len(LONGS),
    "total_shorts": len(SHORTS),
    "total_operacoes": len(LONGS) + len(SHORTS),
    "timeframes": ["15m", "3m", "1m"],
    "cores_long": ["yellow", "green", "red"],
    "cores_short": ["yellow", "blue", "red"],
    "versao_dados": "1.0"
}