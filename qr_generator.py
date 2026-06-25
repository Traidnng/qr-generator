import os
import sys
import json
import random
from datetime import datetime

try:
    import qrcode
except ImportError:
    print("Hata: 'qrcode' kütüphanesi bulunamadı.")
    print("Lütfen terminalde şu komutu çalıştırın: pip install qrcode[pil]")
    sys.exit(1)

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

HISTORY_FILE = "qr_history.json"
QR_DIR = "qr_output"
DEFAULT_FILENAME = "qrcode_output"

lang_tr = {
    "title": f"{BLUE}{BOLD}[ QR ÜRETİCİ ]{RESET}",
    "m_gen": f"  {YELLOW}1{RESET}  QR Oluştur",
    "m_hist": f"  {YELLOW}2{RESET}  Geçmişi Gör",
    "m_open": f"  {YELLOW}3{RESET}  Son QR'ı Aç",
    "m_lang": f"  {YELLOW}4{RESET}  Dili Değiştir (EN)",
    "m_exit": f"  {YELLOW}5{RESET}  Çıkış",
    "prompt": "Seçiminiz >> ",
    "p_data": "Metin veya URL girin: ",
    "p_file": "Dosya adı (boş bırakılabilir): ",
    "p_preview": "Terminalde ASCII önizleme yapılsın mı? (e/h): ",
    "p_color": "Renk seçin (1-6, varsayılan=1): ",
    "err_empty": f"{RED}Bu alan boş bırakılamaz!{RESET}",
    "saved": f"{GREEN}Başarıyla kaydedildi →{RESET} ",
    "err": f"{RED}Bir hata oluştu:{RESET} ",
    "bye": "Görüşmek üzere!",
    "bad": f"{RED}Geçersiz seçim, tekrar deneyin.{RESET}",
    "no_hist": f"{DIM}Henüz bir geçmiş kaydı bulunmuyor.{RESET}",
    "hist_hdr": f"{CYAN}-- OLUŞTURULAN QR KODLAR --{RESET}",
    "no_last": f"{DIM}Henüz bir QR kod oluşturulmamış veya dosya silinmiş.{RESET}",
    "opening": f"{DIM}Dosya açılıyor...{RESET}",
    "rand_clr": f"{DIM}Rastgele renk seçildi:{RESET} ",
    "clr_lbl": "Renk Seçenekleri:",
}

lang_en = {
    "title": f"{BLUE}{BOLD}[ QR GENERATOR ]{RESET}",
    "m_gen": f"  {YELLOW}1{RESET}  Generate QR",
    "m_hist": f"  {YELLOW}2{RESET}  View History",
    "m_open": f"  {YELLOW}3{RESET}  Open Last QR",
    "m_lang": f"  {YELLOW}4{RESET}  Switch Language (TR)",
    "m_exit": f"  {YELLOW}5{RESET}  Quit",
    "prompt": "Your choice >> ",
    "p_data": "Enter text or URL: ",
    "p_file": "Filename (can be empty): ",
    "p_preview": "Show ASCII preview in terminal? (y/n): ",
    "p_color": "Select color (1-6, default=1): ",
    "err_empty": f"{RED}This field cannot be empty!{RESET}",
    "saved": f"{GREEN}Successfully saved →{RESET} ",
    "err": f"{RED}An error occurred:{RESET} ",
    "bye": "See you later!",
    "bad": f"{RED}Invalid choice, try again.{RESET}",
    "no_hist": f"{DIM}No history records found.{RESET}",
    "hist_hdr": f"{CYAN}-- GENERATED QR CODES --{RESET}",
    "no_last": f"{DIM}No QR code generated yet or file is missing.{RESET}",
    "opening": f"{DIM}Opening file...{RESET}",
    "rand_clr": f"{DIM}Random color selected:{RESET} ",
    "clr_lbl": "Color Options:",
}

langs = {"tr": lang_tr, "en": lang_en}

color_opts = {
    "1": ("black", "white", "Klasik (Siyah/Beyaz)"),
    "2": ("darkblue", "white", "Lacivert/Beyaz"),
    "3": ("darkred", "white", "Kırmızı/Beyaz"),
    "4": ("black", "#f5f5dc", "Siyah/Krem"),
    "5": ("white", "black", "Negatif (Beyaz/Siyah)"),
    "6": ("random", "random", "Rastgele"),
}

rand_colors = [
    ("darkgreen", "white"),
    ("purple", "white"),
    ("darkorange", "white"),
    ("teal", "white"),
    ("black", "#e8f4f8"),
]


def clear_screen():
    """Terminal ekranını temizler"""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_user():
    input(f"\n{DIM}Devam etmek için Enter'a basın...{RESET}")

def load_history():
    """Geçmiş dosyasını okur, yoksa boş liste döner"""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Geçmiş yüklenirken hata oluştu: {e}")
        return []

def show_history(texts):
    clear_screen()
    history = load_history()
    print(texts["hist_hdr"])
    
    if not history:
        print(texts["no_hist"])
        wait_for_user()
        return
        
    for index, record in enumerate(reversed(history[-15:]), 1):
        timestamp = record.get("time", "Bilinmiyor")
        data = record.get("data", "")[:55] # Çok uzun metinleri keselim
        filename = record.get("file", "")
        print(f"  {DIM}{index:02d}{RESET}  {timestamp}  {YELLOW}{data}{RESET}  → {filename}")
        
    wait_for_user()

def generate_qr(texts):
    print()
    data = input(texts["p_data"]).strip()
    
    if not data:
        print(texts["err_empty"])
        wait_for_user()
        return

    filename = input(texts["p_file"]).strip()
    if not filename:
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    elif not filename.endswith(".png"):
        filename += ".png"

    os.makedirs(QR_DIR, exist_ok=True)
    outfile = os.path.join(QR_DIR, filename)

    print(f"\n{DIM}{texts['clr_lbl']}{RESET}")
    for key, (fill, back, label) in color_opts.items():
        print(f"  {YELLOW}{key}{RESET}  {label}")

    color_choice = input(texts["p_color"]).strip() or "1"
    fill_color, back_color, _ = color_opts.get(color_choice, color_opts["1"])
    
    if fill_color == "random":
        fill_color, back_color = random.choice(rand_colors)
        print(f"{texts['rand_clr']}{fill_color} / {back_color}")

    preview_input = input(texts["p_preview"]).strip().lower()
    show_preview = preview_input in ("y", "e", "1", "evet", "yes")

    # QR Oluşturma aşaması
    try:
        qr = qrcode.QRCode(
            version=None, # Boyutu otomatik ayarla
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10, 
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)

        if show_preview:
            print()
            for row in qr.get_matrix():
                print("".join("██" if cell else "  " for cell in row))
            print()

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(outfile)
        print(f"\n{texts['saved']}{BOLD}{outfile}{RESET}")

        # Geçmişe ekle
        history = load_history()
        history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data": data, 
            "file": outfile, 
            "colors": f"{fill_color}/{back_color}"
        })
        
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history[-50:], file, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"\n{texts['err']}{e}")

    wait_for_user()

def open_last_qr(texts):
    history = load_history()
    
    if not history:
        print(texts["no_last"])
        wait_for_user()
        return

    last_file = history[-1].get("file", "")
    
    if not last_file or not os.path.exists(last_file):
        print(texts["no_last"])
        wait_for_user()
        return

    print(texts["opening"])
    
    if sys.platform == "win32":
        os.startfile(last_file)
    elif sys.platform == "darwin": # macOS
        os.system(f"open '{last_file}'")
    else: # Linux
        os.system(f"xdg-open '{last_file}'")
        
    wait_for_user()

def main():
    clear_screen()
    print(f"{BOLD}Dil Seçimi / Select Language{RESET}")
    print(f"  {YELLOW}1{RESET}  Türkçe")
    print(f"  {YELLOW}2{RESET}  English")
    
    user_lang = input(">> ").strip()
    current_lang = "en" if user_lang == "2" else "tr"

    while True:
        clear_screen()
        texts = langs[current_lang]
        
        print(texts["title"])
        print()
        print(texts["m_gen"])
        print(texts["m_hist"])
        print(texts["m_open"])
        print(texts["m_lang"])
        print(texts["m_exit"])
        print()

        choice = input(texts["prompt"]).strip()
        
        if choice == "1":
            generate_qr(texts)
        elif choice == "2":
            show_history(texts)
        elif choice == "3":
            open_last_qr(texts)
        elif choice == "4":
            current_lang = "en" if current_lang == "tr" else "tr"
        elif choice == "5":
            print(f"\n{DIM}{texts['bye']}{RESET}\n")
            sys.exit(0)
        else:
            print(texts["bad"])
            wait_for_user()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{DIM}Program sonlandırıldı (CTRL+C).{RESET}")
        sys.exit(0)
