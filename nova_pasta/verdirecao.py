import time
from datetime import datetime

class TradingAnalyzer:
    def __init__(self):
        # Armazena apenas as duas últimas leituras
        self.previous_data = None  # dados anteriores (há 10 segundos)
        self.current_data = None   # dados atuais
        
        # Estado atual da direção
        self.current_direction = None  # 'LONG' ou 'SHORT'
        
        # Status dos indicadores (se estão seguindo a direção)
        self.red_following = False
        self.yellow_following = False
        
        print("=== ANALISADOR DE TENDÊNCIAS INICIADO ===")
        print("📊 Monitorando direções: GREEN=LONG, BLUE=SHORT")
        print("📈 Analisando tendências a cada 10 segundos")
        print("💾 Salvando GREEN/BLUE junto com RED/YELLOW para análises")
        print("🔄 Lógica de persistência: mantém aprovação se não contrariar\n")
    
    def round_number(self, value_str):
        """
        Arredonda o número para o inteiro mais próximo.
        Exemplo: 15.67 -> 16, -14.34 -> -14
        """
        try:
            # Remove vírgula e converte para float
            clean_value = value_str.replace(',', '.')
            float_val = float(clean_value)
            return round(float_val)
        except:
            return None
    
    def process_screen_data(self, numbers_found, timestamp):
        """
        Processa os dados vindos do monitor da tela.
        numbers_found: lista com os dados detectados na tela
        timestamp: horário da captura
        """
        if not numbers_found:
            print(f"[{timestamp}] ⚠️  Nenhum dado recebido para análise")
            return
        
        # Processa os dados recebidos
        processed_data = {
            'timestamp': timestamp,
            'direction': None,  # 'LONG' ou 'SHORT'
            'green': None,      # valor GREEN (sempre salvo)
            'blue': None,       # valor BLUE (sempre salvo)
            'red': None,        # valor RED
            'yellow': None      # valor YELLOW
        }
        
        # Extrai e processa cada cor
        for item in numbers_found:
            color = item['color']
            raw_value = item['text']
            
            if not raw_value:
                continue
                
            # Arredonda o número
            rounded_value = self.round_number(raw_value)
            if rounded_value is None:
                continue
            
            # Processa baseado na cor
            if color == 'GREEN':
                processed_data['direction'] = 'LONG'
                processed_data['green'] = rounded_value
                print(f"[{timestamp}] 🟢 GREEN detectado: {raw_value} → {rounded_value} (LONG)")
                
            elif color == 'BLUE':
                processed_data['direction'] = 'SHORT'
                processed_data['blue'] = rounded_value
                print(f"[{timestamp}] 🔵 BLUE detectado: {raw_value} → {rounded_value} (SHORT)")
                
            elif color == 'RED':
                processed_data['red'] = rounded_value
                print(f"[{timestamp}] 🔴 RED detectado: {raw_value} → {rounded_value}")
                
            elif color == 'YELLOW':
                processed_data['yellow'] = rounded_value
                print(f"[{timestamp}] 🟡 YELLOW detectado: {raw_value} → {rounded_value}")
        
        # Atualiza o estado atual da direção
        if processed_data['direction']:
            # Se mudou de direção, reseta o status dos indicadores
            if self.current_direction != processed_data['direction']:
                self.red_following = False
                self.yellow_following = False
                print(f"[{timestamp}] 🔄 Direção mudou para {processed_data['direction']}, resetando status dos indicadores")
            
            self.current_direction = processed_data['direction']
        
        # Mostra dados completos salvos
        self.show_saved_data(processed_data)
        
        # Analisa a tendência
        self.analyze_trend(processed_data)
        
        # Atualiza os dados armazenados (move current para previous, novo vira current)
        self.previous_data = self.current_data
        self.current_data = processed_data
    
    def show_saved_data(self, data):
        """
        Mostra todos os dados que estão sendo salvos.
        """
        print(f"[{data['timestamp']}] 💾 DADOS SALVOS PARA ANÁLISE:")
        if data['green'] is not None:
            print(f"  🟢 GREEN: {data['green']}")
        if data['blue'] is not None:
            print(f"  🔵 BLUE: {data['blue']}")
        if data['red'] is not None:
            print(f"  🔴 RED: {data['red']}")
        if data['yellow'] is not None:
            print(f"  🟡 YELLOW: {data['yellow']}")
        if data['direction']:
            print(f"  🎯 DIREÇÃO: {data['direction']}")
        print()
    
    def analyze_trend(self, new_data):
        """
        Analisa se RED e YELLOW estão seguindo a direção definida por GREEN/BLUE.
        - GREEN (LONG): RED e YELLOW devem SUBIR para confirmar tendência
        - BLUE (SHORT): RED e YELLOW devem DESCER para confirmar tendência
        """
        if not self.current_data:
            print(f"[{new_data['timestamp']}] 📋 Primeira leitura armazenada")
            return
        
        if not self.current_direction:
            print(f"[{new_data['timestamp']}] ⚠️  Direção não identificada")
            return
        
        # Compara RED e YELLOW entre atual e anterior
        prev_red = self.current_data.get('red')
        prev_yellow = self.current_data.get('yellow')
        new_red = new_data.get('red')
        new_yellow = new_data.get('yellow')
        
        # Precisa ter RED e YELLOW em ambos os períodos
        if (prev_red is None or prev_yellow is None) or (new_red is None or new_yellow is None):
            print(f"[{new_data['timestamp']}] ⚠️  Necessário ter RED e YELLOW em ambos os períodos para análise")
            print(f"    Anterior: RED={prev_red}, YELLOW={prev_yellow}")
            print(f"    Atual: RED={new_red}, YELLOW={new_yellow}")
            return
        
        # Calcula a variação de cada cor
        red_change = new_red - prev_red
        yellow_change = new_yellow - prev_yellow
        
        # Determina se cada indicador seguiu a direção com lógica de persistência
        
        # Para RED
        if self.current_direction == 'LONG':
            # LONG: RED deve subir para ganhar aprovação, só perde se descer
            if red_change > 0:
                self.red_following = True  # Ganhou aprovação
            elif red_change < 0:
                self.red_following = False  # Perdeu aprovação (contrariou)
            # red_change == 0: mantém status anterior
        else:  # SHORT
            # SHORT: RED deve descer para ganhar aprovação, só perde se subir
            if red_change < 0:
                self.red_following = True  # Ganhou aprovação
            elif red_change > 0:
                self.red_following = False  # Perdeu aprovação (contrariou)
            # red_change == 0: mantém status anterior
        
        # Para YELLOW
        if self.current_direction == 'LONG':
            # LONG: YELLOW deve subir para ganhar aprovação, só perde se descer
            if yellow_change > 0:
                self.yellow_following = True  # Ganhou aprovação
            elif yellow_change < 0:
                self.yellow_following = False  # Perdeu aprovação (contrariou)
            # yellow_change == 0: mantém status anterior
        else:  # SHORT
            # SHORT: YELLOW deve descer para ganhar aprovação, só perde se subir
            if yellow_change < 0:
                self.yellow_following = True  # Ganhou aprovação
            elif yellow_change > 0:
                self.yellow_following = False  # Perdeu aprovação (contrariou)
            # yellow_change == 0: mantém status anterior
        
        # Conta quantos indicadores estão seguindo a direção
        indicators_confirming = sum([self.red_following, self.yellow_following])
        
        # Analisa o resultado
        if indicators_confirming == 2:
            # Ambos confirmam
            if self.current_direction == 'LONG':
                result = "📈 CONFIRMANDO LONG (ambos indicadores subiram)"
                emoji = "🟢⬆️"
            else:
                result = "📉 CONFIRMANDO SHORT (ambos indicadores desceram)"
                emoji = "🔵⬇️"
                
        elif indicators_confirming == 1:
            # Apenas 1 confirma
            if self.current_direction == 'LONG':
                result = "🔀 LONG PARCIAL (apenas 1 indicador subiu)"
                emoji = "🟢➡️"
            else:
                result = "🔀 SHORT PARCIAL (apenas 1 indicador desceu)"
                emoji = "🔵➡️"
                
        else:
            # Nenhum confirma
            if self.current_direction == 'LONG':
                result = "📉 CONTRADIZENDO LONG (nenhum indicador subiu)"
                emoji = "🟢⚠️"
            else:
                result = "📈 CONTRADIZENDO SHORT (nenhum indicador desceu)"
                emoji = "🔵⚠️"
        
        # Mostra os detalhes da comparação
        print(f"\n{'='*60}")
        print(f"[{new_data['timestamp']}] 🔍 ANÁLISE DE TENDÊNCIA")
        print(f"🎯 ESTRATÉGIA: {self.current_direction}")
        print(f"")
        print(f"DADOS ANTERIORES:")
        if prev_red is not None:
            print(f"  🔴 RED: {prev_red}")
        if prev_yellow is not None:
            print(f"  🟡 YELLOW: {prev_yellow}")
        if self.current_data.get('green') is not None:
            print(f"  🟢 GREEN: {self.current_data.get('green')}")
        if self.current_data.get('blue') is not None:
            print(f"  🔵 BLUE: {self.current_data.get('blue')}")
        
        print(f"")
        print(f"DADOS ATUAIS:")
        if new_red is not None:
            red_status = "✅" if self.red_following else "❌"
            red_action = ""
            if red_change > 0:
                red_action = " (subiu)"
            elif red_change < 0:
                red_action = " (desceu)"
            else:
                red_action = " (manteve)"
            print(f"  🔴 RED: {new_red} ({red_change:+d}){red_action} {red_status}")
        if new_yellow is not None:
            yellow_status = "✅" if self.yellow_following else "❌"
            yellow_action = ""
            if yellow_change > 0:
                yellow_action = " (subiu)"
            elif yellow_change < 0:
                yellow_action = " (desceu)"
            else:
                yellow_action = " (manteve)"
            print(f"  🟡 YELLOW: {new_yellow} ({yellow_change:+d}){yellow_action} {yellow_status}")
        if new_data.get('green') is not None:
            print(f"  🟢 GREEN: {new_data.get('green')}")
        if new_data.get('blue') is not None:
            print(f"  🔵 BLUE: {new_data.get('blue')}")
        
        print(f"")
        print(f"📊 RESUMO: {indicators_confirming}/2 indicadores seguindo a direção {self.current_direction}")
        print(f"{emoji} RESULTADO: {result}")
        print(f"{'='*60}\n")
    
    def get_current_status(self):
        """
        Retorna o status atual do analisador.
        """
        status = {
            'direction': self.current_direction,
            'has_data': self.current_data is not None,
            'can_analyze': self.previous_data is not None and self.current_data is not None,
            'current_data': self.current_data,
            'previous_data': self.previous_data
        }
        return status
    
    def get_all_saved_data(self):
        """
        Retorna todos os dados salvos (para futuras análises).
        """
        return {
            'previous': self.previous_data,
            'current': self.current_data,
            'direction': self.current_direction
        }


# Exemplo de uso e teste
if __name__ == "__main__":
    analyzer = TradingAnalyzer()
    
    print("TESTE DO ANALISADOR:")
    print("-" * 30)
    
    # Simula dados vindos da tela (formato igual ao do monitor)
    test_data_1 = [
        {'color': 'GREEN', 'text': '30.45'},  # LONG
        {'color': 'RED', 'text': '20.00'},    # Indicador
        {'color': 'YELLOW', 'text': '30.00'}  # Indicador
    ]
    
    test_data_2 = [
        {'color': 'GREEN', 'text': '31.22'},  # LONG (continua)
        {'color': 'RED', 'text': '22.00'},    # Subiu: 20 → 22 ✅
        {'color': 'YELLOW', 'text': '32.00'}  # Subiu: 30 → 32 ✅
    ]
    
    test_data_3 = [
        {'color': 'BLUE', 'text': '30.44'},   # SHORT (mudou direção)
        {'color': 'RED', 'text': '25.00'},    # Indicador
        {'color': 'YELLOW', 'text': '35.00'}  # Indicador
    ]
    
    test_data_4 = [
        {'color': 'BLUE', 'text': '29.67'},   # SHORT (continua)
        {'color': 'RED', 'text': '23.00'},    # Desceu: 25 → 23 ✅
        {'color': 'YELLOW', 'text': '33.00'}  # Desceu: 35 → 33 ✅
    ]
    
    # Simula a chegada dos dados
    print("1ª Leitura (GREEN = LONG):")
    analyzer.process_screen_data(test_data_1, "13:00:00")
    
    time.sleep(1)
    print("\n2ª Leitura (LONG confirmado - RED e YELLOW subiram):")
    analyzer.process_screen_data(test_data_2, "13:00:10")
    
    time.sleep(1)
    print("\n3ª Leitura (BLUE = SHORT):")
    analyzer.process_screen_data(test_data_3, "13:00:20")
    
    time.sleep(1)
    print("\n4ª Leitura (SHORT confirmado - RED e YELLOW desceram):")
    analyzer.process_screen_data(test_data_4, "13:00:30")
    
    # Mostra todos os dados salvos
    print("\n" + "="*50)
    print("📊 TODOS OS DADOS SALVOS PARA FUTURAS ANÁLISES:")
    all_data = analyzer.get_all_saved_data()
    print("Dados anteriores:", all_data['previous'])
    print("Dados atuais:", all_data['current'])
    print("Direção atual:", all_data['direction'])