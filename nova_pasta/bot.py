import time
import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab
import threading
import signal
import sys
import re

# Importa o analisador (certifique-se de que o arquivo trading_analyzer.py esteja na mesma pasta)
try:
    from verdirecao import TradingAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    print("⚠️  Arquivo trading_analyzer.py não encontrado. Executando sem análise.")
    ANALYZER_AVAILABLE = False

# ==============================
# CONFIGURAÇÕES
# ==============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
running = True
DEBUG = False  # colocar True para ver janelas com detecções (cv2.imshow)

# Inicializa o analisador
if ANALYZER_AVAILABLE:
    analyzer = TradingAnalyzer()
else:
    analyzer = None

# ==============================
# UTILITÁRIOS
# ==============================
def format_number_with_point(text):
    if not text:
        return None
    cleaned_text = text.strip()
    cleaned_text = re.sub(r'[^-0123456789.,%]', '', cleaned_text)
    cleaned_text = cleaned_text.replace(',', '.')
    if cleaned_text.count('.') > 1:
        parts = cleaned_text.split('.')
        cleaned_text = '.'.join(parts[:-1]).replace('.', '') + '.' + parts[-1]
    if cleaned_text.count('-') > 1:
        if cleaned_text.startswith('-'):
            cleaned_text = '-' + cleaned_text[1:].replace('-', '')
        else:
            cleaned_text = cleaned_text.replace('-', '')
    if not cleaned_text or cleaned_text == '-' or cleaned_text == '.':
        return None
    number_pattern = r'^-?\d+(\.\d+)?%?$'
    if re.match(number_pattern, cleaned_text):
        try:
            test_num = cleaned_text.replace('%', '')
            float(test_num)
            return cleaned_text
        except:
            return None
    return None

def remove_centena(text):
    """
    Remove o primeiro dígito da parte inteira se a parte inteira tiver >=3 dígitos 
    E se o primeiro dígito for 7.
    Ex.: 734.45 -> 34.45  |  -743.87 -> -43.87  |  834.22 -> 834.22 (não remove)
    O texto deve usar '.' como separador decimal.
    """
    try:
        sign = '-' if text.startswith('-') else ''
        s = text.lstrip('+-')
        s = s.replace(',', '.')
        if '.' in s:
            inteiro, frac = s.split('.', 1)
            # Remove o primeiro dígito apenas se for 7 e tiver pelo menos 3 dígitos
            if len(inteiro) >= 3 and inteiro[0] == '7':
                inteiro = inteiro[1:]
            if inteiro == '':
                inteiro = '0'
            new = sign + inteiro + '.' + frac
            return new
        else:
            # sem casas decimais
            if len(s) >= 3 and s[0] == '7':
                s = s[1:]
            return sign + s
    except:
        return text

def remove_dezena_yellow_red(text):
    """
    Para cores YELLOW e RED apenas: Remove o primeiro dígito se for 7 e houver pelo menos 2 dígitos na parte inteira.
    Ex.: -74.22 -> -4.22  |  75.33 -> 5.33  |  7.45 -> 7.45 (não remove, só tem 1 dígito)
    """
    try:
        sign = '-' if text.startswith('-') else ''
        s = text.lstrip('+-')
        s = s.replace(',', '.')
        if '.' in s:
            inteiro, frac = s.split('.', 1)
            # Remove o primeiro dígito apenas se for 7 e tiver pelo menos 2 dígitos
            if len(inteiro) >= 2 and inteiro[0] == '7':
                inteiro = inteiro[1:]
            if inteiro == '':
                inteiro = '0'
            new = sign + inteiro + '.' + frac
            return new
        else:
            # sem casas decimais
            if len(s) >= 2 and s[0] == '7':
                s = s[1:]
            return sign + s
    except:
        return text

def has_decimal_places(numbers_found):
    """
    Verifica se todos os números encontrados têm casas decimais (vírgula).
    Retorna True se todos tiverem vírgula, False caso contrário.
    """
    if not numbers_found:
        return True  # Se não há números, considera como "ok"
    
    for item in numbers_found:
        if item['text'] and '.' not in item['text']:
            return False
    return True

# ==============================
# DETECTA RETÂNGULOS COLORIDOS
# ==============================
def detect_colored_rectangles(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    colors_config = {
        'RED': [([0, 40, 40], [20, 255, 255]), ([160, 40, 40], [180, 255, 255])],
        'GREEN': ([30, 40, 40], [90, 255, 255]),
        'YELLOW': ([10, 40, 40], [40, 255, 255]),
        'BLUE': ([85, 40, 40], [140, 255, 255]),
        'ORANGE': ([5, 40, 40], [25, 255, 255]),
        'CYAN': ([80, 40, 40], [100, 255, 255]),
    }

    all_rectangles = []
    def is_valid_position(x, y, w, h, img_shape):
        img_h, img_w = img_shape[:2]
        if x <= 1 or y <= 1:
            return False
        if x + w >= img_w - 1 or y + h >= img_h - 1:
            return False
        return True

    for color_name, color_range in colors_config.items():
        if color_name == 'RED':
            mask1 = cv2.inRange(hsv, np.array(color_range[0][0]), np.array(color_range[0][1]))
            mask2 = cv2.inRange(hsv, np.array(color_range[1][0]), np.array(color_range[1][1]))
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower, upper = color_range
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for contour in contours:
            area = cv2.contourArea(contour)
            if 80 < area < 8000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                if (0.2 < aspect_ratio < 8 and w > 12 and h > 8 and is_valid_position(x, y, w, h, img.shape)):
                    all_rectangles.append((x, y, w, h, color_name, area))

    # remove sobreposições (prioriza maiores)
    final_rectangles = []
    def rects_overlap(r1, r2, threshold=0.25):
        x1,y1,w1,h1 = r1[:4]; x2,y2,w2,h2 = r2[:4]
        xl = max(x1,x2); yt = max(y1,y2); xr = min(x1+w1, x2+w2); yb = min(y1+h1, y2+h2)
        if xr <= xl or yb <= yt:
            return False
        inter = (xr-xl)*(yb-yt)
        return (inter / (w1*h1) > threshold or inter / (w2*h2) > threshold)

    all_rectangles.sort(key=lambda x: x[5], reverse=True)
    for r in all_rectangles:
        overlap = False
        for fr in final_rectangles:
            if rects_overlap(r, fr, threshold=0.2):
                overlap = True; break
        if not overlap:
            final_rectangles.append(r)

    return [r[:5] for r in final_rectangles]

# ==============================
# DETECTA CANDIDATOS BRANCOS (QUADRADO 0.00)
# ==============================
def detect_white_candidates(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 150])   # reduzido para pegar brancos menos brilhantes
    upper = np.array([180, 60, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    rects = []
    h_img, w_img = img.shape[:2]
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        area = w*h
        # filtro amplo, damos preferência aos que estão mais à direita (no score)
        if 40 < area < 10000 and w > 6 and h > 6 and w < w_img and h < h_img:
            rects.append((x,y,w,h,area))
    # ordena por área decrescente
    rects.sort(key=lambda r: r[4], reverse=True)
    return rects

def detect_zero_by_white(roi, start_y):
    """
    Encontra o melhor candidato branco e retorna a posição Y absoluta (start_y + centro).
    Preferência: área grande e mais à direita.
    Retorna (zero_y_abs, best_rect) ou (None, None)
    """
    candidates = detect_white_candidates(roi)
    if not candidates:
        return None, None

    roi_w = roi.shape[1]
    # score = area * normalized_x_center (prioriza à direita)
    best = max(candidates, key=lambda r: r[4] * ((r[0] + r[2]/2) / max(1, roi_w)))
    x,y,w,h,area = best
    zero_y_abs = start_y + y + (h // 2)
    return zero_y_abs, best

# ==============================
# OCR PARA UMA REGIÃO
# ==============================
def process_rectangle_ocr(rect_roi):
    if rect_roi.size == 0:
        return None
    original_height, original_width = rect_roi.shape[:2]
    if original_height < 20 or original_width < 20:
        scale_factor = 5
    elif original_height < 35 or original_width < 35:
        scale_factor = 3
    else:
        scale_factor = 2
    rect_roi_resized = cv2.resize(rect_roi, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(rect_roi_resized, cv2.COLOR_BGR2GRAY)
    processed_images = []
    try:
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(otsu)
        processed_images.append(cv2.bitwise_not(otsu))
    except:
        processed_images.append(gray)
    configs = [
        r'--oem 3 --psm 8 -c tessedit_char_whitelist=-0123456789.,%',
        r'--oem 3 --psm 7 -c tessedit_char_whitelist=-0123456789.,%',
        r'--oem 3 --psm 6 -c tessedit_char_whitelist=-0123456789.,%'
    ]
    for img_processed in processed_images:
        for config in configs:
            try:
                text = pytesseract.image_to_string(img_processed, config=config).strip()
                text = re.sub(r'[^-0123456789.,%]', '', text)
                text = text.replace(',', '.')
                if text and 1 <= len(text) <= 12 and any(c.isdigit() for c in text):
                    formatted = format_number_with_point(text)
                    if formatted:
                        return formatted
            except:
                continue
    return None

# ==============================
# AJUSTA SINAL COM BASE NO ZERO
# ==============================
def adjust_sign_based_on_zero(numbers_found, zero_y_abs):
    """
    Se zero_y_abs existir, força o sinal com base em posição vertical.
    Se não existir, tenta fallback procurando OCR de valor próximo de zero (tolerância maior).
    Aplica as regras de remoção de dígitos baseadas na cor.
    """
    if zero_y_abs is None:
        # fallback: procura um item cujo valor OCR seja ~0 (tolerância 1.0)
        for it in numbers_found:
            try:
                v = float(it['text'].replace('%', ''))
                if abs(v) < 1.0:
                    zero_y_abs = it['position'][1]
                    if DEBUG:
                        print("Fallback encontrou zero por OCR em y=", zero_y_abs, "valor:", v)
                    break
            except:
                continue
        if zero_y_abs is None:
            # sem referência de zero: não altera sinais (mantém OCR)
            return numbers_found

    # aplica sinal e regras de remoção de dígitos
    for item in numbers_found:
        if item['text'] is None:
            continue
        y_center_abs = item['position'][1] + (item['size'][1] // 2)
        text = item['text']
        color = item['color']
        
        # decide sinal
        if y_center_abs > zero_y_abs:  # abaixo do zero -> negativo
            if not text.startswith('-'):
                item['text'] = '-' + text.lstrip('+-')
        else:
            item['text'] = item['text'].lstrip('-').lstrip('+')
        
        # aplica remoção de centena (para todas as cores se o primeiro dígito for 7)
        item['text'] = remove_centena(item['text'])
        
        # aplica remoção de dezena apenas para YELLOW e RED
        if color in ['YELLOW', 'RED']:
            item['text'] = remove_dezena_yellow_red(item['text'])
            
    return numbers_found

def wait_for_next_10s_interval():
    """
    Aguarda até o próximo momento em que os segundos sejam múltiplos de 10 (0, 10, 20, 30, 40, 50).
    """
    while True:
        current_time = time.time()
        seconds = int(current_time) % 60
        
        # Calcula quantos segundos faltam para o próximo múltiplo de 10
        next_interval_seconds = ((seconds // 10) + 1) * 10
        if next_interval_seconds >= 60:
            next_interval_seconds = 0
            # Se vai passar para o próximo minuto, aguarda até lá
            sleep_time = 60 - seconds
        else:
            sleep_time = next_interval_seconds - seconds
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        # Verifica se realmente chegou no momento certo
        current_seconds = int(time.time()) % 60
        if current_seconds % 10 == 0:
            return

def capture_screen_and_process():
    """
    Captura uma única vez e processa a imagem.
    Retorna (numbers_found, timestamp, has_decimals)
    """
    screen = ImageGrab.grab()
    img_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    h, w, _ = img_cv.shape

    # área de captura: ajuste conforme sua tela (direita)
    start_x = int(w * 0.90)
    end_x = w
    start_y = int(h * 0.14)
    end_y = int(h * 0.90)
    roi = img_cv[start_y:end_y, start_x:end_x]
    timestamp = time.strftime("%H:%M:%S")

    # 1) detecta melhor quadrado branco (PRIORITÁRIO)
    zero_y_abs, best_white = detect_zero_by_white(roi, start_y)

    # 2) detecta retângulos coloridos e faz OCR
    rectangles = detect_colored_rectangles(roi)
    numbers_found = []
    for i, (x, y, w_rect, h_rect, color) in enumerate(rectangles):
        margin = 2
        y1 = max(0, y - margin); y2 = min(roi.shape[0], y + h_rect + margin)
        x1 = max(0, x - margin); x2 = min(roi.shape[1], x + w_rect + margin)
        rect_roi = roi[y1:y2, x1:x2]
        if rect_roi.size > 0:
            text = process_rectangle_ocr(rect_roi)
            if text:
                numbers_found.append({
                    'position': (x + start_x, y + start_y),
                    'size': (w_rect, h_rect),
                    'text': text,
                    'color': color,
                    'rectangle_id': i
                })

    # se não achou o quadrado branco, tenta fallback procurando 0.00 entre OCRs (tolerância 1.0)
    if zero_y_abs is None:
        for it in numbers_found:
            try:
                v = float(it['text'].replace('%', ''))
                if abs(v) < 1.0:
                    zero_y_abs = it['position'][1]
                    print(f"[{timestamp}] Fallback: OCR achou ~0 em posição {zero_y_abs} (valor {v})")
                    break
            except:
                continue

    # ordena e ajusta sinais
    numbers_found.sort(key=lambda x: x['position'][1])
    numbers_found = adjust_sign_based_on_zero(numbers_found, zero_y_abs)
    
    # verifica se todos têm casas decimais
    has_decimals = has_decimal_places(numbers_found)

    # DEBUG: desenhar retângulos detectados
    if DEBUG:
        vis = roi.copy()
        # desenha coloridos
        for (x,y,w_rect,h_rect,color) in rectangles:
            cv2.rectangle(vis, (x,y), (x+w_rect, y+h_rect), (0,255,0), 1)
        # desenha branco escolhido
        if best_white is not None:
            bx,by,bw,bh,_ = best_white
            cv2.rectangle(vis, (bx,by), (bx+bw, by+bh), (0,0,255), 2)
        cv2.imshow("ROI debug", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

    return numbers_found, timestamp, has_decimals

def print_results(numbers_found, timestamp):
    """
    Imprime os resultados encontrados.
    """
    if numbers_found:
        print(f"\n[{timestamp}] VALORES DETECTADOS:")
        for item in numbers_found:
            disp = item['text'] if item['text'] is not None else ''
            disp = disp.replace('.', ',')
            print(f"  {item['color']}: {disp}")
    else:
        print(f"[{timestamp}] Nenhum valor detectado na área monitorada")

# ==============================
# LOOP PRINCIPAL MODIFICADO
# ==============================
def capture_and_process():
    global running, analyzer
    time.sleep(1)
    try:
        print("Aguardando o próximo intervalo de 10 segundos...")
        
        while running:
            # Aguarda até o próximo intervalo de 10 segundos
            wait_for_next_10s_interval()
            
            if not running:
                break
                
            # Captura e processa
            numbers_found, timestamp, has_decimals = capture_screen_and_process()
            
            # Mostra os resultados na tela
            print_results(numbers_found, timestamp)
            
            # Envia dados para o analisador (se disponível)
            if analyzer and numbers_found:
                try:
                    analyzer.process_screen_data(numbers_found, timestamp)
                except Exception as e:
                    print(f"[{timestamp}] ⚠️  Erro no analisador: {e}")
            
            # Se algum número veio sem vírgula, recaptura imediatamente
            if not has_decimals and numbers_found:
                print(f"[{timestamp}] ⚠️  Detectado número sem vírgula - recapturando...")
                time.sleep(0.2)  # pequena pausa antes de recapturar
                
                numbers_found, timestamp, _ = capture_screen_and_process()
                print_results(numbers_found, timestamp)
                
                # Envia os dados recapturados para o analisador também
                if analyzer and numbers_found:
                    try:
                        analyzer.process_screen_data(numbers_found, timestamp)
                    except Exception as e:
                        print(f"[{timestamp}] ⚠️  Erro no analisador (recaptura): {e}")

    except Exception as e:
        print("Erro durante captura:", e)
        import traceback; traceback.print_exc()
        running = False

# ==============================
# ENCERRAMENTO GRACIOSO
# ==============================
def signal_handler(sig, frame):
    global running
    print("\n🛑 Encerrando aplicação...")
    running = False
    try:
        cv2.destroyAllWindows()
    except:
        pass
    sys.exit(0)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("=== TradingView Monitor + Analisador de Tendências ===")
    print("🕐 Horários de captura: XX:XX:00, XX:XX:10, XX:XX:20, XX:XX:30, XX:XX:40, XX:XX:50")
    print("🔄 Recaptura imediata se algum número vier sem vírgula")
    if ANALYZER_AVAILABLE:
        print("📊 Analisador de tendências: ATIVO")
        print("🟢 GREEN = LONG | 🔵 BLUE = SHORT")
        print("💾 Salvando GREEN/BLUE/RED/YELLOW para futuras análises")
    else:
        print("⚠️  Analisador de tendências: INATIVO (arquivo trading_analyzer.py não encontrado)")
    print("DEBUG =", DEBUG)
    input("Posicione o TradingView e pressione ENTER...")
    capture_thread = threading.Thread(target=capture_and_process)
    capture_thread.daemon = True
    capture_thread.start()
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
