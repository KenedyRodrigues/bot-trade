# comparador_operacoes.py
# ========================================
# COMPARADOR DE OPERAÇÕES
# ========================================

from operasucesso import LONGS, SHORTS

# ========================================
# VALORES ATUAIS - PREENCHA AQUI
# ========================================

# Preencha com os valores atuais observados
VALORES_ATUAIS = {
    "15m": {
        "yellow": 5.20,      # Substitua pelo valor atual
        "cor_especial": "green",  # "green" para LONG ou "blue" para SHORT
        "valor_especial": -27.56,     # Valor da cor especial (green ou blue)
        "red": -13.54           # Valor do red
    },
    "3m": {
        "yellow": 11.24,       # Substitua pelo valor atual
        "cor_especial": "green",  # Deve ser a mesma cor do 15m
        "valor_especial": 9.54,     # Valor da cor especial
        "red": -3.58          # Valor do red
    },
    "1m": {
        "yellow": 23.45,      # Substitua pelo valor atual
        "cor_especial": "green",  # Deve ser a mesma cor do 15m
        "valor_especial": -52.45,    # Valor da cor especial
        "red": 18.45       # Valor do red
    }
}

# ========================================
# CONFIGURAÇÕES
# ========================================

MARGEM_ERRO = 5  # Margem de erro para cima e para baixo

# ========================================
# FUNÇÕES DE COMPARAÇÃO
# ========================================

def esta_dentro_margem(valor_atual, valor_salvo, margem=MARGEM_ERRO):
    """Verifica se o valor está dentro da margem de erro"""
    return abs(valor_atual - valor_salvo) <= margem

def calcular_distancia_total(atual, salvo):
    """Calcula a distância total entre dois conjuntos de valores"""
    distancia = 0
    for timeframe in ["15m", "3m", "1m"]:
        # Yellow sempre existe
        distancia += abs(atual[timeframe]["yellow"] - salvo[timeframe]["yellow"])
        
        # Cor especial (green ou blue)
        cor_especial = atual[timeframe]["cor_especial"]
        distancia += abs(atual[timeframe]["valor_especial"] - salvo[timeframe][cor_especial])
        
        # Red sempre existe
        distancia += abs(atual[timeframe]["red"] - salvo[timeframe]["red"])
    
    return distancia

def comparar_timeframe(atual_tf, salvo_tf, cor_especial):
    """Compara um timeframe específico"""
    # Verifica yellow
    if not esta_dentro_margem(atual_tf["yellow"], salvo_tf["yellow"]):
        return False
    
    # Verifica cor especial (green ou blue)
    if not esta_dentro_margem(atual_tf["valor_especial"], salvo_tf[cor_especial]):
        return False
    
    # Verifica red
    if not esta_dentro_margem(atual_tf["red"], salvo_tf["red"]):
        return False
    
    return True

def encontrar_operacao_similar():
    """Encontra a operação mais similar aos valores atuais"""
    
    # Determina se é LONG ou SHORT baseado na cor especial
    cor_especial = VALORES_ATUAIS["15m"]["cor_especial"]
    
    if cor_especial == "green":
        operacoes = LONGS
        tipo_operacao = "LONG"
    elif cor_especial == "blue":
        operacoes = SHORTS
        tipo_operacao = "SHORT"
    else:
        raise ValueError("cor_especial deve ser 'green' ou 'blue'")
    
    print(f"🔍 Procurando operações do tipo: {tipo_operacao}")
    print(f"📊 Valores atuais:")
    for tf in ["15m", "3m", "1m"]:
        valores = VALORES_ATUAIS[tf]
        print(f"   {tf}: Yellow={valores['yellow']}, {cor_especial.title()}={valores['valor_especial']}, Red={valores['red']}")
    
    print(f"🎯 Margem de erro: ±{MARGEM_ERRO}")
    
    # Primeira fase: filtrar por 15m - PASSAR TODAS QUE COMBINAREM
    candidatos_15m = []
    print(f"\n🔎 Fase 1 - Comparando 15m (margem ±{MARGEM_ERRO}):")
    
    for nome, dados in operacoes.items():
        if comparar_timeframe(VALORES_ATUAIS["15m"], dados["15m"], cor_especial):
            candidatos_15m.append(nome)
            # Mostra os valores para comparação
            valores_15m = dados["15m"]
            print(f"   ✅ {nome} passou no 15m -> Y:{valores_15m['yellow']}, {cor_especial.title()}:{valores_15m[cor_especial]}, R:{valores_15m['red']}")
        else:
            valores_15m = dados["15m"]
            print(f"   ❌ {nome} não passou no 15m -> Y:{valores_15m['yellow']}, {cor_especial.title()}:{valores_15m[cor_especial]}, R:{valores_15m['red']}")
    
    print(f"\n✨ Resultado Fase 1: {len(candidatos_15m)} operações passaram -> {candidatos_15m}")
    
    if not candidatos_15m:
        print("⚠️  Nenhuma operação passou no filtro de 15m")
        return None
    
    # Segunda fase: filtrar por 3m - PASSAR TODAS QUE COMBINAREM
    candidatos_3m = []
    print(f"\n🔎 Fase 2 - Comparando 3m nos {len(candidatos_15m)} candidatos do 15m:")
    
    for nome in candidatos_15m:
        dados = operacoes[nome]
        if comparar_timeframe(VALORES_ATUAIS["3m"], dados["3m"], cor_especial):
            candidatos_3m.append(nome)
            valores_3m = dados["3m"]
            print(f"   ✅ {nome} passou no 3m -> Y:{valores_3m['yellow']}, {cor_especial.title()}:{valores_3m[cor_especial]}, R:{valores_3m['red']}")
        else:
            valores_3m = dados["3m"]
            print(f"   ❌ {nome} não passou no 3m -> Y:{valores_3m['yellow']}, {cor_especial.title()}:{valores_3m[cor_especial]}, R:{valores_3m['red']}")
    
    print(f"\n✨ Resultado Fase 2: {len(candidatos_3m)} operações passaram -> {candidatos_3m}")
    
    if not candidatos_3m:
        print("⚠️  Nenhuma operação passou no filtro de 3m")
        # Retorna a melhor do 15m como fallback
        print(f"📋 Analisando as {len(candidatos_15m)} que passaram no 15m como fallback:")
        return encontrar_melhor_candidato(candidatos_15m, operacoes, "15m")
    
    # Terceira fase: filtrar por 1m - PASSAR TODAS QUE COMBINAREM
    candidatos_1m = []
    print(f"\n🔎 Fase 3 - Comparando 1m nos {len(candidatos_3m)} candidatos do 3m:")
    
    for nome in candidatos_3m:
        dados = operacoes[nome]
        if comparar_timeframe(VALORES_ATUAIS["1m"], dados["1m"], cor_especial):
            candidatos_1m.append(nome)
            valores_1m = dados["1m"]
            print(f"   ✅ {nome} passou no 1m -> Y:{valores_1m['yellow']}, {cor_especial.title()}:{valores_1m[cor_especial]}, R:{valores_1m['red']}")
        else:
            valores_1m = dados["1m"]
            print(f"   ❌ {nome} não passou no 1m -> Y:{valores_1m['yellow']}, {cor_especial.title()}:{valores_1m[cor_especial]}, R:{valores_1m['red']}")
    
    print(f"\n✨ Resultado Fase 3: {len(candidatos_1m)} operações passaram -> {candidatos_1m}")
    
    # Se houver candidatos que passaram em todos os timeframes
    if candidatos_1m:
        print(f"\n🎯 {len(candidatos_1m)} operações passaram em TODOS os timeframes!")
        return encontrar_melhor_candidato(candidatos_1m, operacoes, "todos")
    
    # Se não houver candidatos no 1m, pegar o melhor dos candidatos do 3m
    else:
        print(f"\n📋 Nenhuma passou no 1m, analisando as {len(candidatos_3m)} que passaram até o 3m:")
        return encontrar_melhor_candidato(candidatos_3m, operacoes, "3m")

def encontrar_melhor_candidato(candidatos, operacoes, fase):
    """Encontra o melhor candidato entre uma lista calculando a menor distância"""
    melhor_operacao = None
    menor_distancia = float('inf')
    todas_distancias = []
    
    print(f"   📏 Calculando distâncias para {len(candidatos)} candidatos:")
    
    for nome in candidatos:
        dados = operacoes[nome]
        distancia = calcular_distancia_total(VALORES_ATUAIS, dados)
        todas_distancias.append((nome, distancia))
        print(f"      {nome}: distância = {distancia:.2f}")
        
        if distancia < menor_distancia:
            menor_distancia = distancia
            melhor_operacao = nome
    
    # Ordena por distância para mostrar ranking
    todas_distancias.sort(key=lambda x: x[1])
    
    print(f"\n🏆 Ranking final (fase {fase}):")
    for i, (nome, dist) in enumerate(todas_distancias, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
        print(f"      {emoji} {nome}: {dist:.2f}")
    
    return melhor_operacao, operacoes[melhor_operacao], menor_distancia

# ========================================
# EXECUÇÃO PRINCIPAL
# ========================================

def main():
    """Executa a comparação principal"""
    print("="*50)
    print("🚀 COMPARADOR DE OPERAÇÕES")
    print("="*50)
    
    try:
        resultado = encontrar_operacao_similar()
        
        if resultado:
            nome, dados, distancia = resultado
            cor_especial = VALORES_ATUAIS["15m"]["cor_especial"]
            
            print(f"\n🏆 RESULTADO FINAL:")
            print(f"   Operação mais similar: {nome}")
            print(f"   Distância total: {distancia:.2f}")
            print(f"\n📊 Comparação detalhada:")
            
            for tf in ["15m", "3m", "1m"]:
                atual = VALORES_ATUAIS[tf]
                salvo = dados[tf]
                print(f"\n   {tf}:")
                print(f"      Yellow: {atual['yellow']} vs {salvo['yellow']} (diff: {abs(atual['yellow'] - salvo['yellow']):.2f})")
                print(f"      {cor_especial.title()}: {atual['valor_especial']} vs {salvo[cor_especial]} (diff: {abs(atual['valor_especial'] - salvo[cor_especial]):.2f})")
                print(f"      Red: {atual['red']} vs {salvo['red']} (diff: {abs(atual['red'] - salvo['red']):.2f})")
        
        else:
            print("\n❌ NENHUMA OPERAÇÃO SIMILAR ENCONTRADA")
            print("   Sugestões:")
            print("   - Aumente a MARGEM_ERRO")
            print("   - Verifique se os valores estão corretos")
            print("   - Verifique se a cor_especial está correta")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

# ========================================
# EXECUTAR AUTOMATICAMENTE
# ========================================

if __name__ == "__main__":
    main()