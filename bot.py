import time
import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab, Image
import threading
import signal
import sys
import re

# ==============================
# CONFIGURAÇÕES
# ==============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
running = True

# ==============================
# FUNÇÃO MELHORADA PARA FORMATAR NÚMEROS
# ==============================
def format_number_with_point(text):
    """
    Melhorada para detectar melhor números negativos e formatação
    """
    if not text:
        return text
    
    # Remove espaços extras mas preserva sinais
    cleaned_text = text.strip()
    
    # Debug: mostra o texto original
    print(f"    📝 Texto original: '{text}' -> Limpo: '{cleaned_text}'")
    
    # Substitui vírgula por ponto
    if ',' in cleaned_text:
        cleaned_text = cleaned_text.replace(',', '.')
    
    # Regex mais robusta para capturar números com sinal
    # Busca padrões como: -27.2, +27.2, -27,2, 27.2, etc.
    number_pattern = r'[-+]?(?:\d+[.,]?\d*|\d*[.,]\d+)'
    matches = re.findall(number_pattern, cleaned_text)
    
    if not matches:
        # Tenta buscar apenas dígitos e reconstroir
        digits_only = re.findall(r'\d+', cleaned_text)
        if digits_only:
            # Se encontrou dígitos, verifica se há sinal negativo no texto original
            has_negative = '-' in text or '−' in text  # Verifica também o sinal menos unicode
            number_str = ''.join(digits_only)
            
            if len(number_str) >= 2:
                # Adiciona ponto entre penúltimo e último dígito
                formatted = number_str[:-1] + '.' + number_str[-1]
                if has_negative:
                    formatted = '-' + formatted
                print(f"    🔧 Reconstruído: '{formatted}'")
                return formatted
        return cleaned_text
    
    # Pega o primeiro match válido
    number_str = matches[0]
    
    # Se já tem ponto/vírgula, ajusta casas decimais
    if '.' in number_str or ',' in number_str:
        # Substitui vírgula por ponto
        number_str = number_str.replace(',', '.')
        parts = number_str.split('.')
        
        if len(parts) == 2 and len(parts[1]) > 1:
            # Se tem mais de 1 casa decimal, mantém apenas 1
            parts[1] = parts[1][:1]
        
        formatted = parts[0] + '.' + parts[1] if len(parts) == 2 else number_str
        print(f"    🔧 Formatado com ponto: '{formatted}'")
        return formatted
    
    # Se não tem ponto, adiciona entre penúltimo e último dígito
    # Separa sinal dos dígitos
    sign = ''
    digits = number_str
    if number_str.startswith(('-', '+')):
        sign = number_str[0]
        digits = number_str[1:]
    
    # Adiciona ponto se tiver pelo menos 2 dígitos
    if len(digits) >= 2:
        formatted = sign + digits[:-1] + '.' + digits[-1]
        print(f"    🔧 Formatado: '{formatted}'")
        return formatted
    
    print(f"    ➡️ Mantido original: '{number_str}'")
    return number_str

# ==============================
# FUNÇÃO PARA DETECTAR RETÂNGULOS COLORIDOS (CORRIGIDA)
# ==============================
def detect_colored_rectangles(img):
    """
    Detecta retângulos coloridos com filtros anti-duplicação e lógica de exclusão
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    rectangles = []
    detected_positions = []  # Para evitar duplicatas próximas
    
    # Configuração das cores
    colors_config = {
        'GREEN': ([35, 50, 50], [85, 255, 255]),  # Verde mais restrito
        'PINK': ([136, 120, 150], [156, 255, 255]),
        'RED': [([0, 50, 50], [15, 255, 255]), ([165, 50, 50], [180, 255, 255])],  # Vermelho mais restrito
        'YELLOW': ([15, 50, 50], [35, 255, 255]),  # Amarelo mais restrito
        'BLUE': ([90, 50, 50], [135, 255, 255])   # Azul mais restrito
    }

    def is_too_close(new_pos, existing_positions, min_distance=20):
        """Verifica se uma posição está muito próxima de posições já detectadas"""
        new_x, new_y = new_pos
        for existing_x, existing_y, _ in existing_positions:
            distance = np.sqrt((new_x - existing_x)**2 + (new_y - existing_y)**2)
            if distance < min_distance:
                return True
        return False

    def is_valid_position(x, y, w, h, img_shape):
        """Verifica se a posição é válida (não é fantasma na borda)"""
        img_h, img_w = img_shape[:2]
        
        # Rejeita se está muito na borda (posições suspeitas como 0,0)
        if x <= 2 or y <= 2:
            return False
        
        # Rejeita se está muito próximo das bordas
        if x + w >= img_w - 2 or y + h >= img_h - 2:
            return False
            
        return True

    # Detecta cada cor
    for color_name, color_range in colors_config.items():
        color_rectangles = []
        
        if color_name == 'RED':
            # Vermelho tem dois ranges
            mask1 = cv2.inRange(hsv, np.array(color_range[0][0]), np.array(color_range[0][1]))
            mask2 = cv2.inRange(hsv, np.array(color_range[1][0]), np.array(color_range[1][1]))
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            # Outras cores têm um range
            lower, upper = color_range
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 20 < area < 8000:  # Área mais restritiva
                x, y, w, h = cv2.boundingRect(contour)
                
                # Verifica critérios de validade
                if (0.2 < w/h < 8 and w > 15 and h > 10 and  # Proporções mais restritivas
                    is_valid_position(x, y, w, h, img.shape) and  # Posição válida
                    not is_too_close((x, y), detected_positions)):  # Não está muito próximo de outro
                    
                    color_rectangles.append((x, y, w, h, color_name, area))
                    detected_positions.append((x, y, color_name))

        # Para RED, pega apenas o maior se houver múltiplos
        if color_name == 'RED' and len(color_rectangles) > 1:
            color_rectangles.sort(key=lambda x: x[5], reverse=True)
            color_rectangles = [color_rectangles[0]]

        # Adiciona os retângulos válidos desta cor
        for rect in color_rectangles:
            rectangles.append(rect[:5])  # Remove a área da tupla final

    # LÓGICA: GREEN e BLUE são mutuamente exclusivos
    has_green = any(rect[4] == 'GREEN' for rect in rectangles)
    has_blue = any(rect[4] == 'BLUE' for rect in rectangles)
    
    if has_green and has_blue:
        rectangles = [rect for rect in rectangles if rect[4] != 'BLUE']

    return rectangles

# ==============================
# FUNÇÃO MELHORADA PARA OCR
# ==============================
def process_rectangle_ocr(rect_roi):
    if rect_roi.size == 0:
        return None
        
    gray = cv2.cvtColor(rect_roi, cv2.COLOR_BGR2GRAY)
    
    if rect_roi.shape[0] < 25 or rect_roi.shape[1] < 35:
        scale_factor = 5
        gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    methods = []
    try:
        thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        methods.append(thresh1)
    except: pass
    try:
        _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        methods.append(thresh2)
    except: pass
    try:
        _, thresh3 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        methods.append(thresh3)
    except: pass
    try:
        _, thresh4 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        methods.append(thresh4)
    except: pass
    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        _, thresh5 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        methods.append(thresh5)
    except: pass
    
    configs = [
        r'--oem 3 --psm 8 -c tessedit_char_whitelist=-−+0123456789.,%',
        r'--oem 3 --psm 7 -c tessedit_char_whitelist=-−+0123456789.,%',
        r'--oem 3 --psm 13 -c tessedit_char_whitelist=-−+0123456789.,%',
        r'--oem 3 --psm 6 -c tessedit_char_whitelist=-−+0123456789.,%',
        r'--oem 3 --psm 8',
        r'--oem 3 --psm 7',
    ]
    
    best_text = ""
    best_confidence = 0
    
    for thresh in methods:
        for config in configs:
            try:
                try:
                    data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                except:
                    avg_confidence = 50
                
                text = pytesseract.image_to_string(thresh, config=config).strip()
                text = text.replace(' ', '').replace('\n', '').replace('\r', '')
                text = text.replace('−', '-')
                
                if text and len(text) <= 12 and any(c.isdigit() for c in text):
                    digit_count = sum(1 for c in text if c.isdigit())
                    score = digit_count * 10 + avg_confidence
                    
                    if score > best_confidence:
                        best_text = text
                        best_confidence = score
                        
            except: continue
    
    if best_text and any(c.isdigit() for c in best_text):
        formatted_text = format_number_with_point(best_text)
        return formatted_text
    
    return None

# ==============================
# FUNÇÃO PARA CAPTURAR E PROCESSAR (MELHORADA)
# ==============================
def capture_and_process():
    global running
    time.sleep(3)
    
    try:
        while running:
            screenshot = ImageGrab.grab()
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            h, w, _ = img_cv.shape
            roi = img_cv[0:h, int(w*0.85):w]
            
            timestamp = time.strftime("%H:%M:%S")
            
            rectangles = detect_colored_rectangles(roi)
            numbers_found = []
            
            for i, (x, y, w_rect, h_rect, color) in enumerate(rectangles):
                margin = 3
                y1 = max(0, y - margin)
                y2 = min(roi.shape[0], y + h_rect + margin)
                x1 = max(0, x - margin)
                x2 = min(roi.shape[1], x + w_rect + margin)
                
                rect_roi = roi[y1:y2, x1:x2]
                
                if rect_roi.size > 0:
                    text = process_rectangle_ocr(rect_roi)
                    
                    if text:
                        numbers_found.append({
                            'position': (x, y),
                            'size': (w_rect, h_rect),
                            'text': text,
                            'color': color,
                            'rectangle_id': i
                        })
            
            if numbers_found:
                print(f"\n[{timestamp}] RESULTADOS:")
                for item in numbers_found:
                    print(f"{item['color']}: {item['text']}")
            else:
                print(f"[{timestamp}] Nenhum número detectado")
            
            time.sleep(10)
            
    except Exception as e:
        print(f"Erro: {e}")

# ==============================
# FUNÇÃO PARA ENCERRAR GRACIOSAMENTE
# ==============================
def signal_handler(sig, frame):
    global running
    print("\n🛑 Encerrando aplicação...")
    running = False
    sys.exit(0)

# ==============================
# PROGRAMA PRINCIPAL
# ==============================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    print("TradingView Monitor - Análise a cada 10s")
    print("Pressione Ctrl+C para encerrar")
    
    input("Pressione ENTER quando TradingView estiver visível...")
    
    capture_thread = threading.Thread(target=capture_and_process)
    capture_thread.daemon = True
    capture_thread.start()
    
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)