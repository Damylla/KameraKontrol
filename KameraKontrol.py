import cv2
from ultralytics import YOLO
import numpy as np
import time
from datetime import datetime

print("🚀 Fabrika İzleme Paneli Başlatılıyor...")
print("📷 Atech USB Webcam kullanılıyor.")

# =============================================
# 1. YAPAY ZEKA MODELİNİ YÜKLE
# =============================================
model = YOLO("yolov8n.pt")

# =============================================
# 2. KAMERA BAĞLANTISI (Atech USB - Port 1)
# =============================================
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("❌ Atech kamera bulunamadı! Port 0 veya 2'yi dene.")
    exit()

# =============================================
# 3. TAKİP SİSTEMİ (İnsanlara ID atamak için)
# =============================================
takip_sozlugu = {}  # {ID: [son_görüldüğü_zaman, merkez_x, merkez_y]}
sonraki_id = 1
kayip_esigi = 30  # 30 kare görünmezse ID'yi sil

# =============================================
# 4. BELİRLENEN ALAN (Tezgah / Bölge) - Piksel cinsinden
# =============================================
# Ekranda yeşil dikdörtgen olarak görünecek
ALAN_X1, ALAN_Y1, ALAN_X2, ALAN_Y2 = 150, 150, 450, 400  

# =============================================
# 5. PALET SAYMA AYARLARI
# =============================================
PALET_MIN_ALAN = 8000  # Palet boyutundaki nesneleri yakalamak için

print("✅ Kamera bağlandı. Çıkmak için 'q' tuşuna bas.")

# =============================================
# 6. ANA DÖNGÜ
# =============================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Görüntü alınamıyor...")
        break

    # ---- A) YOLO ile İnsan Tespiti ----
    results = model(frame)
    
    # ---- B) İnsanları ve ID'leri işle ----
    mevcut_merkezler = []
    
    for r in results[0].boxes:
        if int(r.cls[0]) == 0:  # 0 = İnsan
            x1, y1, x2, y2 = map(int, r.xyxy[0])
            merkez_x = (x1 + x2) // 2
            merkez_y = (y1 + y2) // 2
            mevcut_merkezler.append((merkez_x, merkez_y, x1, y1, x2, y2))
    
    # ---- C) ID Atama / Güncelleme (Basit Takip) ----
    yeni_takip = {}
    for (mx, my, x1, y1, x2, y2) in mevcut_merkezler:
        eslesen_id = None
        en_kucuk_mesafe = 100  # Piksel cinsinden eşleşme mesafesi
        
        for pid, (_, px, py) in takip_sozlugu.items():
            mesafe = np.sqrt((mx - px)**2 + (my - py)**2)
            if mesafe < en_kucuk_mesafe:
                en_kucuk_mesafe = mesafe
                eslesen_id = pid
        
        if eslesen_id is not None:
            yeni_takip[eslesen_id] = [time.time(), mx, my]
        else:
            yeni_takip[sonraki_id] = [time.time(), mx, my]
            sonraki_id += 1
    
    takip_sozlugu = yeni_takip

    # ---- D) Görüntüyü İşaretle (Kutular + ID'ler) ----
    annotated = frame.copy()
    
    for pid, (_, mx, my) in takip_sozlugu.items():
        # Bu ID'ye ait insanı bul ve kutu çiz
        for (mx2, my2, x1, y1, x2, y2) in mevcut_merkezler:
            if abs(mx - mx2) < 10 and abs(my - my2) < 10:
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated, f"ID:{pid}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                break

    # ---- E) SENARYO 4: Tezgah Alanı ve Süre Takibi ----
    cv2.rectangle(annotated, (ALAN_X1, ALAN_Y1), (ALAN_X2, ALAN_Y2), (255, 0, 0), 3)
    cv2.putText(annotated, "TEZGAH ALANI", (ALAN_X1, ALAN_Y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    alandaki_kisi_sayisi = 0
    for pid, (zaman, mx, my) in takip_sozlugu.items():
        if ALAN_X1 < mx < ALAN_X2 and ALAN_Y1 < my < ALAN_Y2:
            alandaki_kisi_sayisi += 1
            gecen_sure = int(time.time() - zaman)
            cv2.putText(annotated, f"ID:{pid} {gecen_sure}sn", (mx-20, my-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # ---- F) SENARYO 2: Palet / Ürün Sayısı (Kontur ile) ----
    gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gri, (5, 5), 0)
    kenarlar = cv2.Canny(blur, 50, 150)
    konturlar, _ = cv2.findContours(kenarlar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    palet_sayisi = 0
    for cnt in konturlar:
        alan = cv2.contourArea(cnt)
        if alan > PALET_MIN_ALAN:
            x, y, w, h = cv2.boundingRect(cnt)
            # Sadece tezgah alanı içindeki paletleri say (isteğe bağlı)
            # if ALAN_X1 < x+w/2 < ALAN_X2 and ALAN_Y1 < y+h/2 < ALAN_Y2:
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 255), 2)
            palet_sayisi += 1

    # ---- G) EKRAN BİLGİLERİ (Tüm veriler tek ekranda) ----
    toplam_kisi = len(takip_sozlugu)
    
    cv2.putText(annotated, f"Toplam Kisi: {toplam_kisi}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    cv2.putText(annotated, f"Tezgahdaki Kisi: {alandaki_kisi_sayisi}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    cv2.putText(annotated, f"Tezgahdaki Palet: {palet_sayisi}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    
    # Zaman damgası
    cv2.putText(annotated, datetime.now().strftime("%H:%M:%S"), (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    # ---- H) GÖRÜNTÜYÜ GÖSTER ----
    cv2.imshow("Fabrika Izleme Paneli (Atech USB)", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# =============================================
# 7. TEMİZLİK
# =============================================
cap.release()
cv2.destroyAllWindows()
print("👋 Sistem durduruldu.")