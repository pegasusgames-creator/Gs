#!/usr/bin/env python3
"""
_emit_translations_v2.py — write Nonogram metadata translations across
all 12 non-English locales (the existing folders contained English
placeholder text), plus add zh-CN and ar to WaterSort. Validates
against per-field character limits and per-language banned phrases
before writing.

ANTHROPIC_API_KEY isn't set in this environment, so gen_translations.py
can't run. Translations were authored directly in:
- Nonogram: V8 (direct minimal) voice
- WaterSort: V5 (calm / zen) voice — matches the rest of the app

Run from the repo root:
    python3 scripts/_emit_translations_v2.py
"""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent

LIMITS = {
    "subtitle.txt":          30,
    "short_description.txt": 80,
    "full_description.txt":  4000,
    "keywords.txt":          100,
    "release_notes.txt":     500,
    "promotional_text.txt":  170,
}

# Substring banned-phrase checks (case-insensitive).
BANNED = {
    "de": ["nr. 1", "beste", "jetzt herunterladen", "jetzt installieren"],
    "es": ["#1", "el mejor", "descarga ahora", "instala ahora"],
    "fr": ["n°1", "le meilleur", "télécharge maintenant"],
    "pt": ["nº 1", "o melhor", "baixe agora", "instale agora"],
    "uk": ["№1", "найкращий", "завантажуйте зараз"],
    "en": ["#1", "best", "top rated", "download now", "install now", "% off"],
    "ar": ["#1", "الأفضل", "حمّل الآن", "ثبّت الآن"],
    "zh": ["#1", "最佳", "立即下载", "立即安装"],
    "hi": [], "id": [], "it": [], "ja": [], "tr": [],
}

LOCALE_LANG = {
    "ar": "ar", "de-DE": "de", "es-419": "es", "fr-FR": "fr",
    "hi-IN": "hi", "id": "id", "it-IT": "it", "ja-JP": "ja",
    "pt-BR": "pt", "tr-TR": "tr", "uk": "uk", "zh-CN": "zh",
}


# =============================================================================
# NONOGRAM TRANSLATIONS — all 12 non-English locales, all 6 fields
# Voice: V8 (direct, minimal — no fluff)
# =============================================================================

NONOGRAM_TITLE = "Nonogram"

NN = {
    # --------------------------------------------------------------- ar
    "ar": {
        "subtitle.txt": "ارسم بالأرقام. يومياً.",
        "short_description.txt":
            "أدلة رقمية، صور خفية. منطق هادئ. بدون مؤقت. بيكروس يومي.",
        "promotional_text.txt":
            "لغز اليوم صورة صغيرة مخبأة خلف عمود من الأرقام. حلّها.",
        "keywords.txt":
            "نونوغرام,بيكروس,لغز أرقام,لغز منطقي,بيكسل آرت,لعبة دماغ,استرخاء",
        "release_notes.txt":
            "تصميم ورق دافئ — كل شاشة أُعيد بناؤها حول جمالية لغز جريدة هادئة. لحظة الحل المُحدثة. 500 مستوى، تحدٍّ يومي، تتبع السلاسل. يعمل بالكامل دون اتصال.",
        "full_description.txt":
            """ضع علامة على صف، اعدّ العمود، وشاهد صورة بكسل آرت صغيرة تنبثق من شبكة فارغة — اللغز للجزء من يومك حين تريد التفكير، لا السباق.

500 لوحة مصنوعة يدوياً من إحماء صباحي 5×5 إلى ماراثون 20×20. بدون مؤقت. بدون سلسلة قد تكسرها بتفويت يوم. فقط الرضا البطيء للمنطق المدفوع بالأدلة.

✨ الإحساس
• جمالية الورق الدافئ — مريحة للعينين بعد يوم طويل أمام الشاشة
• ردود فعل بمستوى ASMR — نغمات تعبئة ناعمة، أربيجيو فوز لطيف، مرئيات حبر على ورق
• هادئة، بطيئة، مُرضية — بلا ضغط، بلا تسرّع
• لحظة كشف الصورة عندما تستقر الخلية الأخيرة في مكانها

🧠 منطق يحرك الدماغ
500 لغز محبوك يدوياً يتدرج من إحماء 5×5 إلى 20×20 ستعود إليه أياماً. كل قائمة أدلة تُحلّ إلى صورة واحدة صحيحة فقط — استنتاج خالص، بلا تخمين.

🎯 ما الموجود فيه
• مجاني للعب — كل من اللوحات الـ500 مُضمّن، بلا جدار دفع
• أربعة أحجام شبكات: 5×5 مبتدئ → 20×20 خبير
• بيكروس يومي — نونوغرام جديد كل صباح، قابل للحل دائماً
• ألوان مظهر تُفتح بالعب
• مهام يومية — ثلاثة أهداف جديدة كل 24 ساعة
• إحصائيات وترتيب عالمي — انظر كيف تقارن نفسك
• يعمل بالكامل دون اتصال — حلّ في القطار، على الطائرة، في أي مكان

🎮 كيفية اللعب
• الأرقام فوق كل عمود تُظهر كم خلية تمتلئ بالتتابع
• الأرقام بجانب كل صف تفعل المثل
• اضغط للتعبئة، اضغط مطولاً لوضع علامة فارغة على خلية
• عندما تتطابق كل الأدلة، تُكشف الصورة

يُسمى أيضاً بيكروس، هانجي، أو الرسم بالأرقام. مهما كان اسمه عندك، فهو أهدأ عشرين دقيقة ستقضيها مع هاتفك اليوم.
""",
    },

    # --------------------------------------------------------------- de-DE
    "de-DE": {
        "subtitle.txt": "Malen nach Zahlen. Täglich.",
        "short_description.txt":
            "Zahlenrätsel, versteckte Bilder. Langsame Logik. Kein Timer. Täglicher Picross.",
        "promotional_text.txt":
            "Das heutige Rätsel ist ein kleines Bild hinter einer Zahlenspalte. Löse es.",
        "keywords.txt":
            "nonogramm,picross,hanjie,pixelkunst,zahlenrätsel,logikrätsel,denkspiel,malen nach zahlen,entspannen",
        "release_notes.txt":
            "Warmes Papier-Redesign — jeder Bildschirm um eine ruhige Zeitungsrätsel-Ästhetik herum neu gebaut. Auflösungsmoment aufgefrischt. 500 Level, tägliche Herausforderung, Streak-Tracking. Spielt vollständig offline.",
        "full_description.txt":
            """Markiere eine Zeile, zähle die Spalte und beobachte, wie ein winziges Pixelkunst-Bild aus einem Raster aus Nichts entsteht — das Rätsel für den Teil deines Tages, an dem du denken willst, nicht rennen.

500 handgefertigte Bretter von einer 5×5 Morgenaufwärmung bis zu einem 20×20 Marathon. Kein Timer. Keine Streak, die du durch das Auslassen eines Tages brechen kannst. Nur die langsame Zufriedenheit hinweisgesteuerter Logik.

✨ DAS GEFÜHL
• Warme Papier-Ästhetik — entspannend für die Augen nach einem langen Bildschirmtag
• ASMR-Niveau-Feedback — sanfte Fülltöne, leichtes Sieg-Arpeggio, Tinte-auf-Papier-Optik
• Ruhig, langsam, befriedigend — kein Druck, keine Eile
• Bildenthüllungs-Moment, wenn die letzte Zelle an ihren Platz fällt

🧠 GEHIRN-BIEGENDE LOGIK
500 handgefertigte Knobel-Rätsel, die von einer 5×5-Aufwärmung zu einem 20×20 ansteigen, zu dem du tagelang zurückkehren wirst. Jede Hinweisliste löst sich zu genau einem gültigen Bild auf — reine Deduktion, kein Raten.

🎯 WAS DRIN IST
• Kostenlos zu spielen — jedes der 500 Bretter enthalten, keine Bezahlschranke
• Vier Rastergrößen: 5×5 ANFÄNGER → 20×20 EXPERTE
• Täglicher Picross — ein frisches Nonogramm jeden Morgen, immer lösbar
• Farbthemen, die durch Spielen freigeschaltet werden
• Tägliche Missionen — drei frische Ziele alle 24 Stunden
• Statistiken und globaler Rang — sieh, wie du abschneidest
• Funktioniert vollständig offline — löse im Zug, im Flugzeug, überall

🎮 SO SPIELST DU
• Zahlen über jeder Spalte zeigen, wie viele Zellen aufeinanderfolgend gefüllt werden
• Zahlen neben jeder Reihe tun dasselbe
• Tippe zum Füllen, halte lange für eine leere Zelle
• Wenn alle Hinweise passen, wird das Bild enthüllt

Auch genannt Picross, Hanjie oder Malen nach Zahlen. Wie auch immer du es nennst, es sind die ruhigsten zwanzig Minuten, die du heute mit deinem Telefon verbringst.
""",
    },

    # --------------------------------------------------------------- es-419
    "es-419": {
        "subtitle.txt": "Pinta por números. Diario.",
        "short_description.txt":
            "Pistas numéricas, imágenes ocultas. Lógica lenta. Sin reloj. Picross diario.",
        "promotional_text.txt":
            "El acertijo de hoy es una pequeña imagen escondida tras una columna de números. Resuélvelo.",
        "keywords.txt":
            "nonograma,picross,hanjie,pixel art,acertijo,logica,juego mental,pintar por numeros,relajante",
        "release_notes.txt":
            "Rediseño en papel cálido — cada pantalla reconstruida en torno a una estética serena de acertijo de periódico. Momento de resolución renovado. 500 niveles, desafío diario, seguimiento de rachas. Juega totalmente sin conexión.",
        "full_description.txt":
            """Marca una fila, cuenta la columna y observa cómo una pequeña imagen de pixel art emerge de una cuadrícula vacía — el acertijo para esa parte de tu día en que quieres pensar, no correr.

500 tableros hechos a mano desde un calentamiento matutino de 5×5 hasta un maratón de 20×20. Sin temporizador. Sin racha que puedas romper saltándote un día. Solo la lenta satisfacción de la lógica guiada por pistas.

✨ LA SENSACIÓN
• Estética de papel cálido — relajante para los ojos tras un largo día de pantalla
• Retroalimentación nivel ASMR — tonos suaves de relleno, gentil arpegio de victoria, visuales de tinta sobre papel
• Tranquilo, lento, satisfactorio — sin presión, sin prisa
• Momento de revelación de la imagen cuando la última celda cae en su lugar

🧠 LÓGICA QUE DOBLA EL CEREBRO
500 acertijos hechos a mano que escalan desde un calentamiento de 5×5 hasta un 20×20 al que volverás durante días. Cada lista de pistas se resuelve en exactamente una imagen válida — deducción pura, sin adivinar.

🎯 LO QUE INCLUYE
• Gratis para jugar — los 500 tableros incluidos, sin muro de pago
• Cuatro tamaños de cuadrícula: 5×5 PRINCIPIANTE → 20×20 EXPERTO
• Picross Diario — un nonograma fresco cada mañana, siempre resoluble
• Temas de color desbloqueables jugando
• Misiones diarias — tres objetivos frescos cada 24 horas
• Estadísticas y ranking global — ve cómo te comparas
• Funciona totalmente sin conexión — resuelve en el tren, en un vuelo, donde sea

🎮 CÓMO JUGAR
• Los números arriba de cada columna muestran cuántas celdas se llenan consecutivamente
• Los números al lado de cada fila hacen lo mismo
• Toca para llenar, mantén presionado para marcar una celda vacía
• Cuando todas las pistas coinciden, se revela la imagen

También llamado picross, hanjie o pintar por números. Como sea que lo llames, son los veinte minutos más tranquilos que pasarás con tu teléfono hoy.
""",
    },

    # --------------------------------------------------------------- fr-FR
    "fr-FR": {
        "subtitle.txt": "Peindre par numéros.",
        "short_description.txt":
            "Indices, images cachées. Logique lente. Sans minuteur. Picross du jour.",
        "promotional_text.txt":
            "L'énigme du jour est une petite image cachée derrière une colonne de chiffres. Résous-la.",
        "keywords.txt":
            "nonogramme,picross,hanjie,pixel art,enigme numerique,logique,jeu cerebral,peindre numeros,relaxant",
        "release_notes.txt":
            "Refonte papier chaleureux — chaque écran reconstruit autour d'une esthétique calme d'énigme de journal. Moment de résolution rafraîchi. 500 niveaux, défi quotidien, suivi de séries. Joue entièrement hors ligne.",
        "full_description.txt":
            """Marque une ligne, compte la colonne, et regarde une petite image en pixel art émerger d'une grille vide — l'énigme pour la partie de ta journée où tu veux penser, pas courir.

500 plateaux faits main d'un échauffement matinal 5×5 à un marathon 20×20. Pas de minuteur. Pas de série que tu peux briser en sautant un jour. Juste la satisfaction lente d'une logique guidée par des indices.

✨ LA SENSATION
• Esthétique papier chaleureux — reposante pour les yeux après une longue journée d'écran
• Retours niveau ASMR — tons de remplissage doux, arpège de victoire léger, visuels encre-sur-papier
• Calme, lent, satisfaisant — sans pression, sans précipitation
• Moment de révélation de l'image quand la dernière cellule trouve sa place

🧠 LOGIQUE QUI TORD LE CERVEAU
500 énigmes faites main qui s'échelonnent d'un échauffement 5×5 à un 20×20 sur lequel tu reviendras pendant des jours. Chaque liste d'indices se résout en exactement une image valide — déduction pure, pas de devinette.

🎯 CE QU'IL Y A DEDANS
• Gratuit à jouer — chacun des 500 plateaux inclus, pas de mur payant
• Quatre tailles de grille : 5×5 DÉBUTANT → 20×20 EXPERT
• Picross Quotidien — un nouveau nonogramme chaque matin, toujours résoluble
• Thèmes de couleur déblocables en jouant
• Missions quotidiennes — trois objectifs frais toutes les 24 heures
• Stats et classement mondial — vois comment tu te compares
• Fonctionne entièrement hors ligne — résous dans le train, en avion, partout

🎮 COMMENT JOUER
• Les chiffres au-dessus de chaque colonne montrent combien de cellules se remplissent consécutivement
• Les chiffres à côté de chaque ligne font de même
• Touche pour remplir, maintiens pour marquer une cellule vide
• Quand tous les indices correspondent, l'image est révélée

Aussi appelé picross, hanjie, ou peindre par numéros. Quel que soit le nom, ce sont les vingt minutes les plus calmes que tu passeras avec ton téléphone aujourd'hui.
""",
    },

    # --------------------------------------------------------------- hi-IN
    "hi-IN": {
        "subtitle.txt": "नंबर से रंगें। रोज़।",
        "short_description.txt":
            "संख्या संकेत, छिपी तस्वीरें। धीमा तर्क। कोई टाइमर नहीं। दैनिक पिक्रॉस।",
        "promotional_text.txt":
            "आज की पहेली संख्याओं के स्तंभ के पीछे छिपी एक छोटी तस्वीर है। इसे हल करें।",
        "keywords.txt":
            "नॉनोग्राम,पिक्रॉस,पिक्सेल आर्ट,संख्या पहेली,तर्क पहेली,दिमागी खेल,नंबर से रंगें,आरामदायक",
        "release_notes.txt":
            "गर्म कागज़ पुनः डिज़ाइन — हर स्क्रीन शांत अख़बार-पहेली सौंदर्य के आसपास फिर से बनाई गई। हल किए गए क्षण को ताज़ा किया गया। 500 स्तर, दैनिक चुनौती, स्ट्रीक ट्रैकिंग। पूरी तरह ऑफ़लाइन खेलें।",
        "full_description.txt":
            """एक पंक्ति को चिह्नित करें, स्तंभ की गिनती करें, और एक खाली ग्रिड से एक छोटी पिक्सेल आर्ट तस्वीर उभरती देखें — आपके दिन के उस हिस्से के लिए पहेली जब आप सोचना चाहते हैं, दौड़ना नहीं।

500 हस्तनिर्मित बोर्ड एक 5×5 सुबह की वार्म-अप से 20×20 मैराथन तक। कोई टाइमर नहीं। कोई स्ट्रीक नहीं जो एक दिन छोड़ने से टूटे। बस संकेत-संचालित तर्क की धीमी संतुष्टि।

✨ अनुभव
• गर्म कागज़ का सौंदर्य — लंबे स्क्रीन दिन के बाद आँखों के लिए आरामदायक
• ASMR-स्तर की प्रतिक्रिया — कोमल भराव स्वर, सौम्य जीत आर्पेजियो, कागज़ पर स्याही दृश्य
• शांत, धीमा, संतोषजनक — कोई दबाव नहीं, कोई जल्दी नहीं
• तस्वीर-प्रकटीकरण क्षण जब अंतिम सेल अपनी जगह पर गिरती है

🧠 दिमाग-मोड़ने वाला तर्क
500 हस्तनिर्मित दिमागी पहेलियाँ जो 5×5 वार्म-अप से 20×20 तक बढ़ती हैं जिस पर आप दिनों तक लौटेंगे। हर संकेत सूची ठीक एक मान्य तस्वीर तक पहुँचती है — शुद्ध निगमन, कोई अनुमान नहीं।

🎯 इसमें क्या है
• खेलने के लिए मुफ़्त — सभी 500 बोर्ड शामिल, कोई पेवॉल नहीं
• चार ग्रिड आकार: 5×5 शुरुआती → 20×20 विशेषज्ञ
• दैनिक पिक्रॉस — हर सुबह एक ताज़ा नॉनोग्राम, हमेशा हल करने योग्य
• खेलकर अनलॉक होने वाले रंग थीम
• दैनिक मिशन — हर 24 घंटे में तीन ताज़ा लक्ष्य
• आँकड़े और वैश्विक रैंक — देखें आप कैसे तुलना करते हैं
• पूरी तरह ऑफ़लाइन काम करता है — ट्रेन में, उड़ान में, कहीं भी हल करें

🎮 कैसे खेलें
• हर स्तंभ के ऊपर की संख्याएँ दिखाती हैं कि कितनी सेल लगातार भरती हैं
• हर पंक्ति के पास की संख्याएँ वही करती हैं
• भरने के लिए टैप करें, खाली के रूप में चिह्नित करने के लिए लंबे समय तक दबाएँ
• जब सभी संकेत मेल खाते हैं, तस्वीर प्रकट होती है

इसे पिक्रॉस, हानजी, या नंबर से रंगें भी कहा जाता है। आप जो भी कहें, यह आज आपके फ़ोन के साथ बिताए सबसे शांत बीस मिनट हैं।
""",
    },

    # --------------------------------------------------------------- id (Indonesian)
    "id": {
        "subtitle.txt": "Lukis pakai angka. Harian.",
        "short_description.txt":
            "Petunjuk angka, gambar tersembunyi. Logika lambat. Tanpa timer. Picross harian.",
        "promotional_text.txt":
            "Teka-teki hari ini adalah gambar kecil tersembunyi di balik kolom angka. Pecahkan.",
        "keywords.txt":
            "nonogram,picross,hanjie,pixel art,teka teki angka,logika,asah otak,lukis pakai angka,santai",
        "release_notes.txt":
            "Desain ulang kertas hangat — setiap layar dibangun ulang dengan estetika teka-teki koran yang tenang. Momen penyelesaian diperbarui. 500 level, tantangan harian, pelacakan streak. Bermain sepenuhnya offline.",
        "full_description.txt":
            """Tandai baris, hitung kolom, dan saksikan gambar pixel art kecil muncul dari kotak kosong — teka-teki untuk bagian harimu saat kamu ingin berpikir, bukan berlari.

500 papan buatan tangan dari pemanasan pagi 5×5 hingga maraton 20×20. Tanpa timer. Tanpa streak yang bisa kamu putuskan dengan melewatkan satu hari. Hanya kepuasan lambat dari logika yang dipandu petunjuk.

✨ NUANSA
• Estetika kertas hangat — menenangkan mata setelah hari layar yang panjang
• Umpan balik tingkat ASMR — nada isi lembut, arpeggio kemenangan halus, visual tinta-di-kertas
• Tenang, lambat, memuaskan — tanpa tekanan, tanpa terburu-buru
• Momen pengungkapan gambar saat sel terakhir jatuh ke tempatnya

🧠 LOGIKA YANG MEMBENGKOKKAN OTAK
500 teka-teki buatan tangan yang meningkat dari pemanasan 5×5 ke 20×20 yang akan kamu kunjungi berhari-hari. Setiap daftar petunjuk diselesaikan menjadi tepat satu gambar valid — deduksi murni, tanpa menebak.

🎯 APA SAJA DI DALAMNYA
• Gratis dimainkan — semua 500 papan termasuk, tanpa paywall
• Empat ukuran kotak: 5×5 PEMULA → 20×20 AHLI
• Picross Harian — nonogram baru setiap pagi, selalu bisa diselesaikan
• Tema warna terbuka dengan bermain
• Misi harian — tiga tujuan baru setiap 24 jam
• Statistik dan peringkat global — lihat bagaimana kamu dibandingkan
• Bekerja sepenuhnya offline — selesaikan di kereta, di pesawat, di mana saja

🎮 CARA BERMAIN
• Angka di atas setiap kolom menunjukkan berapa sel terisi berurutan
• Angka di samping setiap baris melakukan hal sama
• Ketuk untuk mengisi, tekan lama untuk menandai sel sebagai kosong
• Saat semua petunjuk cocok, gambar terungkap

Juga disebut picross, hanjie, atau lukis pakai angka. Apapun namanya, ini dua puluh menit paling tenang yang akan kamu habiskan dengan ponselmu hari ini.
""",
    },

    # --------------------------------------------------------------- it-IT
    "it-IT": {
        "subtitle.txt": "Dipingi coi numeri. Ogni dì.",
        "short_description.txt":
            "Indizi, immagini nascoste. Logica lenta. Niente timer. Picross del giorno.",
        "promotional_text.txt":
            "L'enigma di oggi è una piccola immagine nascosta dietro una colonna di numeri. Risolvilo.",
        "keywords.txt":
            "nonogramma,picross,hanjie,pixel art,enigma numerico,logica,gioco mentale,dipingere numeri,rilassante",
        "release_notes.txt":
            "Riprogettazione carta calda — ogni schermata ricostruita attorno a un'estetica calma di enigma da giornale. Momento di risoluzione rinfrescato. 500 livelli, sfida quotidiana, tracciamento streak. Si gioca completamente offline.",
        "full_description.txt":
            """Segna una riga, conta la colonna, e guarda una piccola immagine in pixel art emergere da una griglia di nulla — l'enigma per quella parte della tua giornata in cui vuoi pensare, non correre.

500 tabelloni fatti a mano da un riscaldamento mattutino 5×5 a una maratona 20×20. Nessun timer. Nessuno streak che puoi rompere saltando un giorno. Solo la lenta soddisfazione della logica guidata dagli indizi.

✨ LA SENSAZIONE
• Estetica carta calda — rilassante per gli occhi dopo una lunga giornata davanti allo schermo
• Feedback livello ASMR — toni di riempimento morbidi, gentile arpeggio di vittoria, visuali inchiostro-su-carta
• Tranquillo, lento, soddisfacente — senza pressione, senza fretta
• Momento di rivelazione dell'immagine quando l'ultima cella va al suo posto

🧠 LOGICA CHE PIEGA IL CERVELLO
500 enigmi fatti a mano che salgono da un riscaldamento 5×5 a un 20×20 a cui tornerai per giorni. Ogni lista di indizi si risolve in esattamente un'immagine valida — pura deduzione, niente indovinare.

🎯 COSA C'È DENTRO
• Gratis da giocare — tutti i 500 tabelloni inclusi, nessun paywall
• Quattro dimensioni di griglia: 5×5 PRINCIPIANTE → 20×20 ESPERTO
• Picross Quotidiano — un nuovo nonogramma ogni mattina, sempre risolvibile
• Temi colore sbloccabili giocando
• Missioni quotidiane — tre obiettivi freschi ogni 24 ore
• Statistiche e classifica globale — vedi come ti confronti
• Funziona completamente offline — risolvi in treno, in aereo, ovunque

🎮 COME GIOCARE
• I numeri sopra ogni colonna mostrano quante celle si riempiono consecutivamente
• I numeri accanto a ogni riga fanno lo stesso
• Tocca per riempire, tieni premuto per segnare una cella come vuota
• Quando tutti gli indizi corrispondono, l'immagine è rivelata

Chiamato anche picross, hanjie, o dipingere con i numeri. Qualunque nome usi, sono i venti minuti più tranquilli che passerai con il tuo telefono oggi.
""",
    },

    # --------------------------------------------------------------- ja-JP
    "ja-JP": {
        "subtitle.txt": "数字で塗り絵。毎日。",
        "short_description.txt":
            "数字のヒント、隠された絵。ゆっくりロジック。タイマーなし。デイリーピクロス。",
        "promotional_text.txt":
            "今日のパズルは数字の列の後ろに隠れた小さな絵。解いてください。",
        "keywords.txt":
            "ノノグラム,ピクロス,ハンジー,ピクセルアート,数字パズル,ロジックパズル,脳トレ,塗り絵,リラックス",
        "release_notes.txt":
            "暖かな紙のリデザイン — すべての画面を静かな新聞パズルの美学で再構築。クリア時の演出を一新。500レベル、デイリーチャレンジ、ストリーク追跡。完全オフライン対応。",
        "full_description.txt":
            """行に印を付け、列を数え、何もないグリッドから小さなピクセルアートが現れるのを見守る — 走るのではなく考えたい時間のためのパズル。

5×5の朝のウォームアップから20×20のマラソンまで、500の手作りボード。タイマーなし。1日休んで途切れるストリークなし。ヒント主導のロジックがもたらすゆっくりとした満足だけ。

✨ 雰囲気
• 暖かな紙の美学 — 長い画面の日々の後、目に優しい
• ASMR級のフィードバック — 柔らかな塗りトーン、優しい勝利アルペジオ、紙とインクのビジュアル
• 静かで、ゆっくり、満足感がある — プレッシャーなし、急ぎなし
• 最後のセルが収まった時の絵の現出の瞬間

🧠 脳をひねるロジック
5×5のウォームアップから何日も戻りたくなる20×20まで、難易度が上がる500の手作り脳トレパズル。すべてのヒントリストは正確に1つの有効な絵に解決 — 純粋な演繹、推測なし。

🎯 何が含まれているか
• 無料プレイ — 500ボードすべて収録、有料の壁なし
• 4つのグリッドサイズ: 5×5 初心者 → 20×20 エキスパート
• デイリーピクロス — 毎朝新しいノノグラム、常に解ける
• プレイで解放されるカラーテーマ
• デイリーミッション — 24時間ごとに3つの新しい目標
• 統計と世界ランキング — あなたの位置を確認
• 完全オフライン動作 — 電車で、飛行機で、どこでも解ける

🎮 遊び方
• 各列の上の数字は連続して塗られるセル数を示す
• 各行の隣の数字も同様
• タップで塗る、長押しで空マスとしてマーク
• すべてのヒントが一致すると、絵が現れる

ピクロス、ハンジー、塗り絵とも呼ばれる。何と呼んでも、今日あなたが携帯と過ごす最も穏やかな20分間。
""",
    },

    # --------------------------------------------------------------- pt-BR
    "pt-BR": {
        "subtitle.txt": "Pinte por números. Diário.",
        "short_description.txt":
            "Pistas numéricas, imagens ocultas. Lógica lenta. Sem cronômetro. Picross diário.",
        "promotional_text.txt":
            "O quebra-cabeça de hoje é uma pequena imagem escondida atrás de uma coluna de números. Resolva-o.",
        "keywords.txt":
            "nonograma,picross,hanjie,pixel art,quebra cabeca,logica,jogo mental,pintar numeros,relaxante",
        "release_notes.txt":
            "Redesign em papel quente — cada tela reconstruída em torno de uma estética calma de quebra-cabeça de jornal. Momento de resolução renovado. 500 níveis, desafio diário, rastreamento de sequências. Joga totalmente offline.",
        "full_description.txt":
            """Marque uma linha, conte a coluna e veja uma pequena imagem em pixel art emergir de uma grade vazia — o quebra-cabeça para aquela parte do seu dia em que você quer pensar, não correr.

500 tabuleiros feitos à mão de um aquecimento matinal 5×5 até uma maratona 20×20. Sem cronômetro. Sem sequência que você possa quebrar pulando um dia. Apenas a satisfação lenta da lógica guiada por pistas.

✨ A SENSAÇÃO
• Estética de papel quente — relaxante para os olhos após um longo dia de tela
• Retorno nível ASMR — tons de preenchimento suaves, gentil arpejo de vitória, visuais de tinta no papel
• Tranquilo, lento, satisfatório — sem pressão, sem pressa
• Momento de revelação da imagem quando a última célula se encaixa

🧠 LÓGICA QUE DOBRA O CÉREBRO
500 quebra-cabeças feitos à mão escalando de um aquecimento 5×5 a um 20×20 ao qual você voltará por dias. Cada lista de pistas resolve em exatamente uma imagem válida — dedução pura, sem adivinhar.

🎯 O QUE TEM AÍ DENTRO
• Grátis para jogar — todos os 500 tabuleiros incluídos, sem paywall
• Quatro tamanhos de grade: 5×5 INICIANTE → 20×20 ESPECIALISTA
• Picross Diário — um nonograma fresco toda manhã, sempre resolvível
• Temas de cores desbloqueáveis jogando
• Missões diárias — três objetivos frescos a cada 24 horas
• Estatísticas e ranking global — veja como você se compara
• Funciona totalmente offline — resolva no trem, no avião, em qualquer lugar

🎮 COMO JOGAR
• Os números acima de cada coluna mostram quantas células se preenchem consecutivamente
• Os números ao lado de cada linha fazem o mesmo
• Toque para preencher, segure para marcar uma célula como vazia
• Quando todas as pistas combinam, a imagem é revelada

Também chamado de picross, hanjie ou pintar por números. Como você o chamar, são os vinte minutos mais tranquilos que você passará com seu telefone hoje.
""",
    },

    # --------------------------------------------------------------- tr-TR
    "tr-TR": {
        "subtitle.txt": "Sayılarla boya. Her gün.",
        "short_description.txt":
            "Sayı ipuçları, gizli resimler. Yavaş mantık. Zamanlayıcı yok. Günlük picross.",
        "promotional_text.txt":
            "Bugünün bulmacası bir sayı sütununun arkasına saklanmış küçük bir resim. Çöz.",
        "keywords.txt":
            "nonogram,picross,hanjie,piksel sanat,sayı bulmaca,mantık,zeka oyunu,sayı boyama,rahatlatıcı",
        "release_notes.txt":
            "Sıcak kâğıt yeniden tasarımı — her ekran sakin bir gazete bulmacası estetiği etrafında yeniden inşa edildi. Çözüm anı yenilendi. 500 seviye, günlük meydan okuma, seri takibi. Tamamen çevrimdışı oynanır.",
        "full_description.txt":
            """Bir satırı işaretle, sütunu say ve boş bir ızgaradan küçük bir piksel sanatı resminin ortaya çıkışını izle — koşmak değil düşünmek istediğin günün o bölümü için bulmaca.

5×5 sabah ısınmasından 20×20 maratona kadar 500 el yapımı tahta. Zamanlayıcı yok. Bir günü atlayarak kırabileceğin seri yok. Sadece ipucu güdümlü mantığın yavaş tatmini.

✨ HİS
• Sıcak kâğıt estetiği — uzun bir ekran gününün ardından gözleri rahatlatıcı
• ASMR seviyesinde geri bildirim — yumuşak doldurma tonları, hafif zafer arpejisi, kâğıt üstü mürekkep görselleri
• Sakin, yavaş, tatmin edici — baskı yok, acele yok
• Son hücre yerine düştüğünde resim açığa çıkma anı

🧠 BEYNİ BÜKEN MANTIK
5×5 ısınmadan günlerce geri döneceğin 20×20'ye yükselen 500 el yapımı zeka bulmacası. Her ipucu listesi tam olarak bir geçerli resme çözülür — saf çıkarım, tahmin yok.

🎯 İÇİNDE NE VAR
• Oynamak ücretsiz — 500 tahtanın hepsi dahil, paywall yok
• Dört ızgara boyutu: 5×5 BAŞLANGIÇ → 20×20 UZMAN
• Günlük Picross — her sabah yeni bir nonogram, daima çözülebilir
• Oyunla açılan renk temaları
• Günlük görevler — her 24 saatte üç yeni hedef
• İstatistikler ve global sıralama — nasıl karşılaştırıldığını gör
• Tamamen çevrimdışı çalışır — trende, uçakta, herhangi bir yerde çöz

🎮 NASIL OYNANIR
• Her sütunun üstündeki sayılar art arda doldurulan hücre sayısını gösterir
• Her satırın yanındaki sayılar aynısını yapar
• Doldurmak için dokun, boş olarak işaretlemek için uzun bas
• Tüm ipuçları eşleştiğinde resim açığa çıkar

Picross, hanjie veya sayılarla boyama olarak da bilinir. Adı ne olursa olsun, bugün telefonunla geçireceğin en sakin yirmi dakika.
""",
    },

    # --------------------------------------------------------------- uk (Ukrainian)
    "uk": {
        "subtitle.txt": "Малюй за номерами. Щодня.",
        "short_description.txt":
            "Числові підказки, приховані картини. Логіка. Без таймера. Щоденний пікрос",
        "promotional_text.txt":
            "Сьогоднішня головоломка — маленька картинка, схована за стовпцем чисел. Розв'яжи її.",
        "keywords.txt":
            "нонограма,пікрос,піксель арт,логіка,головоломка,для мозку,малювання,розслабляюча",
        "release_notes.txt":
            "Редизайн у теплому папері — кожен екран перебудовано навколо спокійної естетики газетної головоломки. Оновлено момент розв'язання. 500 рівнів, щоденне випробування, відстеження серій. Грається повністю офлайн.",
        "full_description.txt":
            """Познач рядок, порахуй стовпець, і спостерігай, як крихітна картинка піксельного мистецтва з'являється з порожньої сітки — головоломка для тієї частини твого дня, коли хочеш думати, а не бігти.

500 ручних дошок від ранкової розминки 5×5 до марафону 20×20. Без таймера. Без серії, яку можна перервати, пропустивши один день. Лише повільне задоволення від логіки, керованої підказками.

✨ ВІДЧУТТЯ
• Тепла паперова естетика — заспокоює очі після довгого дня перед екраном
• Зворотний зв'язок рівня ASMR — м'які тони заповнення, лагідне арпеджіо перемоги, візуал чорнила на папері
• Тихо, повільно, задовільно — без тиску, без поспіху
• Момент розкриття картини, коли остання клітинка стає на місце

🧠 ЛОГІКА, ЩО ВИГИНАЄ МОЗОК
500 ручних головоломок для мозку, що зростають від розминки 5×5 до 20×20, до якої повертатимешся днями. Кожен список підказок розв'язується рівно в одну дійсну картину — чистий висновок, без вгадування.

🎯 ЩО ВСЕРЕДИНІ
• Безкоштовна гра — усі 500 дошок включені, без платних стін
• Чотири розміри сітки: 5×5 ПОЧАТКІВЕЦЬ → 20×20 ЕКСПЕРТ
• Щоденний Пікрос — свіжа нонограма щоранку, завжди розв'язна
• Кольорові теми, що відкриваються грою
• Щоденні місії — три свіжі цілі кожні 24 години
• Статистика та глобальний рейтинг — побач, як ти порівнюєшся
• Працює повністю офлайн — розв'язуй у потязі, в літаку, будь-де

🎮 ЯК ГРАТИ
• Числа над кожним стовпцем показують, скільки клітинок заповнюються підряд
• Числа поряд з кожним рядком роблять те саме
• Торкнись, щоб заповнити, утримуй, щоб позначити порожню клітинку
• Коли всі підказки збігаються, картина розкривається

Також відома як пікрос, ханджі, або малювання за номерами. Як би ти її не називав, це найспокійніші двадцять хвилин, які проведеш зі своїм телефоном сьогодні.
""",
    },

    # --------------------------------------------------------------- zh-CN
    "zh-CN": {
        "subtitle.txt": "数字填色。每日。",
        "short_description.txt":
            "数字提示，隐藏图画。慢逻辑。无计时器。每日数图。",
        "promotional_text.txt":
            "今日谜题是一张藏在数字列后的小图。解开它。",
        "keywords.txt":
            "数织,数图,picross,像素艺术,数字谜题,逻辑谜题,益智游戏,数字填色,放松",
        "release_notes.txt":
            "温暖纸张重设计 — 每个界面围绕一份安静的报纸谜题美学重建。解题瞬间焕新。500关、每日挑战、连胜追踪。完全离线游玩。",
        "full_description.txt":
            """标记一行，数一列，看一幅小小的像素艺术从一片空白格中浮现 — 这是为你想思考而非奔跑的那段时光准备的谜题。

500个手工制作的盘面，从5×5的晨间热身到20×20的马拉松。无计时器。没有跳过一天就会断的连胜。只有线索驱动逻辑带来的慢节奏满足。

✨ 感受
• 温暖纸张美学 — 在长时间盯屏后让眼睛放松
• ASMR级别的反馈 — 柔和填充音、轻盈胜利琶音、墨水纸张视觉
• 安静、缓慢、令人满足 — 没有压力、没有催促
• 最后一格落位时的图画揭晓瞬间

🧠 折弯大脑的逻辑
500个手工脑力谜题，从5×5热身一路升级到值得反复回味数日的20×20。每组提示恰好对应一幅有效图画 — 纯演绎，不靠猜。

🎯 内含什么
• 免费游玩 — 全部500个盘面在内，无付费墙
• 四种网格尺寸：5×5 入门 → 20×20 高手
• 每日数图 — 每天早晨一张新数图，始终可解
• 通过游玩解锁的配色主题
• 每日任务 — 每24小时三个新目标
• 统计与全球排名 — 看你的水平如何
• 完全离线工作 — 在火车上、飞机上、任何地方都能解

🎮 怎么玩
• 每列上方的数字表示连续填充的格数
• 每行旁的数字含义相同
• 点击填充，长按标记为空格
• 所有提示匹配时，图画揭晓

也叫数图、picross、汉吉，或数字填色。无论怎么称呼，这都是你今天与手机相处的最安静二十分钟。
""",
    },
}


# =============================================================================
# WATERSORT NEW LOCALES — only zh-CN and ar (existing 10 already done)
# Voice: V5 (calm / zen)
# =============================================================================

WS_TITLE = "Water Sort Puzzle"

WS = {
    # --------------------------------------------------------------- ar
    "ar": {
        "subtitle.txt": "اسكب وافرز الماء",
        "short_description.txt":
            "اسكب وافرز ماءً ملوناً. 500 مستوى ومهام يومية وراحة!",
        "promotional_text.txt":
            "اسكب، افرز، وتنفّس. 500 مستوى مصنوع يدوياً مع تحدٍّ يومي ومهام.",
        "keywords.txt":
            "فرز الماء,لغز ألوان,سائل,لغز أنابيب,سكب,استرخاء,لغز",
        "release_notes.txt":
            "• ترويسة إعدادات مصقولة بأيقونة ترس مناسبة\n• زرّ اللعب يقرأ الآن «متابعة · المستوى N» عند وجود تقدّم غير منتهٍ\n• لوحة ألعاب أخرى أنظف\n• تحسينات استقرار صغيرة\n",
        "full_description.txt":
            """💧 Water Sort Puzzle — اسكب، افرز، تنفّس.

افرز السوائل الملوّنة في الأنابيب وأعد النظام إلى الفوضى. لغز مهدّئ بعمق يكافئ الصبر والاستراتيجية ولحظة «آها!» المثالية.

🌊 كيفية اللعب
• اضغط على أنبوب لالتقاط الطبقة العليا من السائل
• اسكبها على لون مطابق أو في أنبوب فارغ
• املأ كل أنبوب بلون واحد لإكمال المستوى
• بلا ضغط زمني — العب بإيقاعك الخاص

✨ الميزات
• 500 مستوى مصنوع يدوياً — من ألغاز مبتدئة لطيفة إلى تحديات خبراء صعبة
• حركات سكب ناعمة وانسيابية — راقب الماء يتدفق
• تحدٍّ يومي — لغز جديد كل يوم مع مكافآت السلسلة
• مهام يومية — 3 أهداف جديدة في اليوم، اربح عملات إضافية
• مقارنة الحركات — انظر عدد حركاتك مقابل البار وتصنيفك (10% / 25% / 50%)
• شاشة إحصائيات — تتبع المستويات المكتملة، إجمالي السكبات، السلسلة اليومية والمزيد
• سلسلة دخول يومية — كافآت أكبر كلما لعبت أكثر متتالياً
• حافظ السلسلة — غبت أياماً عديدة؟ اصرف عملات لحماية سلسلتك
• مؤثرات صوتية مائية جميلة وموسيقى بيئة إجرائية
• بلا مؤقت، بلا توتر — لعب مريح بالكامل
• اربح عملات وافتح تعزيزات
• نظام أرواح مع تجدد سخي خلال 30 دقيقة
• أزرار التلميح والتراجع عند توقفك
• يعمل بالكامل دون اتصال
• يدعم 20+ لغة

🏆 تقدم المستويات
المستويات تزداد صعوبة تدريجياً — أبداً قفزة مفاجئة:
• تعليمي (1–10):    3 ألوان — تعلّم الأساسيات
• سهل (11–30):      4 ألوان — اكسب الثقة
• متوسط (31–130):   5 ألوان — يبدأ التحدي الحقيقي
• صعب (131–300):    6–7 ألوان — إتقان حقيقي للألغاز
• خبير (301–500):   8 ألوان — التحدي الأقصى

📅 تحدٍّ يومي
لغز جديد كل يوم. ابنِ سلسلتك للحصول على عملات مكافأة متزايدة. فاتك يوم؟ اصرف عملات لإنقاذ سلسلتك وإبقاء اللهب مشتعلاً.

🎯 المهام اليومية
ثلاثة أهداف جديدة كل منتصف ليل:
• أكمل أي مستوى · اسكب 30 مرة · أنهِ 3 مستويات
• حلّ مثالي (بدون تراجع) · أكمل التحدي اليومي
اربح حتى 75 عملة مكافأة في اليوم بمجرد اللعب.

📊 إحصائيات وتقدم
• إجمالي المستويات المكتملة والحلول المثالية
• السكبات التراكمية — كم من الماء فرزت؟
• سلسلة الدخول اليومية والرقم القياسي الشخصي
• المستوى الحالي ورصيد العملات

⚡ مقارنة الحركات
بعد كل مستوى، انظر بالضبط كيف تقف:
• عدد حركاتك مقابل البار الأمثل
• أداء مصنّف: شرائح 10% / 25% / 50%
حسّن نتيجتك مع كل إعادة لعب.

🛒 المتجر
• إزالة الإعلانات — استمتع بتجربة بلا انقطاع للأبد
• حزمة عملات S — 50 عملة للتلميحات والتراجع
• حزمة عملات L — 200 عملة، الحزمة الأكبر
• تراجع غير محدود — لا تعلق مرة أخرى
• أرواح إضافية — استعد 5 أرواح فوراً
• أرواح غير محدودة (1س) — العب بحرية لساعة كاملة
• أرواح غير محدودة (∞) — لا تخسر روحاً مرة أخرى
""",
    },

    # --------------------------------------------------------------- zh-CN
    "zh-CN": {
        "subtitle.txt": "倒水、归类",
        "short_description.txt":
            "倒入并归类彩色液体。500关，每日任务，宁静感！",
        "promotional_text.txt":
            "倒入、归类、深呼吸。500个手工关卡，每日挑战与任务。",
        "keywords.txt":
            "水排序,颜色排序,液体谜题,试管谜题,倒水,放松,益智",
        "release_notes.txt":
            "• 设置标题栏抛光，换上正经的齿轮图标\n• 当存在未完成进度时，开始按钮显示「继续 · 第N关」\n• 更整洁的更多游戏面板\n• 细节稳定性改进\n",
        "full_description.txt":
            """💧 Water Sort Puzzle — 倒入、归类、深呼吸。

将彩色液体归类到试管中，从混乱中恢复秩序。一款深度宁静的益智游戏，奖励耐心、策略和那个完美的「啊哈！」瞬间。

🌊 玩法
• 点击试管以拿起最上层的液体
• 倒入颜色相同的试管或空试管
• 将每根试管装满单一颜色即可通关
• 没有时间压力 — 按你自己的节奏玩

✨ 功能
• 500个手工关卡 — 从温和的入门谜题到刁钻的高手挑战
• 顺滑流畅的倒水动画 — 看着水缓缓流动
• 每日挑战 — 每天一道全新谜题，附带连胜奖励
• 每日任务 — 每天3个新目标，赢得奖励金币
• 步数对比 — 看到你的步数与标准步数和你的排名（10% / 25% / 50%）
• 统计界面 — 跟踪通关数、总倒水次数、每日连胜等
• 每日登录连胜 — 连续游玩越久奖励越大
• 连胜守护 — 离开太久？花金币保护你的连胜
• 优美的水声效与程序生成的氛围音乐
• 无计时器、无压力 — 完全放松的游玩
• 赚取金币并解锁加成道具
• 慷慨的30分钟体力恢复系统
• 卡关时有提示和撤回按钮
• 完全离线工作
• 支持20+种语言

🏆 关卡进度
关卡难度逐渐提升 — 不会突然飙升：
• 教学 (1–10)：     3种颜色 — 学习基础
• 简单 (11–30)：    4种颜色 — 建立信心
• 中等 (31–130)：   5种颜色 — 真正的挑战开始
• 困难 (131–300)：  6–7种颜色 — 真正的谜题精通
• 专家 (301–500)：  8种颜色 — 终极挑战

📅 每日挑战
每天一道全新谜题。建立连胜以获得不断增长的奖励金币。错过一天？花金币救回连胜，让火焰持续燃烧。

🎯 每日任务
每个午夜三个新目标：
• 完成任意关卡 · 倒水30次 · 完成3关
• 完美解题（无撤回）· 完成每日挑战
仅靠游玩每天可获得最多75枚奖励金币。

📊 统计与进度
• 总通关数与完美解题数
• 累计倒水次数 — 你已经分类了多少水？
• 每日登录连胜与个人记录
• 当前关卡与金币余额

⚡ 步数对比
每关之后，准确看到你的位置：
• 你的步数 vs. 理想步数
• 排名表现：10% / 25% / 50% 区间
每次重玩都改进你的得分。

🛒 商店
• 移除广告 — 永久享受无打断的体验
• 金币包 S — 50金币用于提示与撤回
• 金币包 L — 200金币，最大的一包
• 无限撤回 — 再也不会卡关
• 额外生命 — 立即恢复5条生命
• 无限生命（1小时）— 自由游玩整整一小时
• 无限生命（∞）— 再也不会丢失生命
""",
    },
}


def write_translations(app_name, title_text, locale_data):
    """Returns (written, failures)."""
    md_dir = REPO / app_name / "metadata"
    written = 0
    failures = []
    for locale, fields in locale_data.items():
        short = LOCALE_LANG.get(locale, locale.split("-")[0])
        out = md_dir / locale
        out.mkdir(parents=True, exist_ok=True)
        # title.txt — kept English globally
        (out / "title.txt").write_text(title_text + "\n")
        written += 1

        for field, content in fields.items():
            text = content if content.endswith("\n") else content + "\n"
            measured = text.strip()
            limit = LIMITS[field]
            if len(measured) > limit:
                failures.append(f"{app_name}/{locale}/{field}: {len(measured)} > {limit}")
                continue
            lower = measured.lower()
            for phrase in BANNED.get(short, []):
                if phrase.lower() in lower:
                    failures.append(f"{app_name}/{locale}/{field}: banned {phrase!r}")
                    break
            else:
                (out / field).write_text(text)
                written += 1
    return written, failures


def main():
    print("== NONOGRAM ==")
    n_w, n_f = write_translations("Nonogram", NONOGRAM_TITLE, NN)
    print(f"  wrote {n_w} files, failures: {len(n_f)}")
    for f in n_f:
        print(f"  - {f}")

    print()
    print("== WATERSORT (new locales only) ==")
    w_w, w_f = write_translations("WaterSortPuzzle", WS_TITLE, WS)
    print(f"  wrote {w_w} files, failures: {len(w_f)}")
    for f in w_f:
        print(f"  - {f}")

    if n_f or w_f:
        sys.exit(1)


if __name__ == "__main__":
    main()
