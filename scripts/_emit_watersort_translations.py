#!/usr/bin/env python3
"""
_emit_watersort_translations.py — one-shot translation writer for WaterSortPuzzle.

ANTHROPIC_API_KEY is not set in this environment, so gen_translations.py
cannot run. Instead, the translations below were authored directly in the
calm / zen voice (V5 — see app_themes.py change in this same task) and
written to disk by this script. Validates against character limits and
banned-phrase rules from gen_translations.py before writing each file.

Run once from the repo root:
    python3 scripts/_emit_watersort_translations.py
"""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
APP = "WaterSortPuzzle"

LIMITS = {
    "subtitle.txt":          30,
    "short_description.txt": 80,
    "full_description.txt":  4000,
    "keywords.txt":          100,
    "release_notes.txt":     500,
    "promotional_text.txt":  170,
}

# Substring banned-phrase checks (case-insensitive). Pulled from
# gen_translations.py BANNED_PHRASES_BY_LANG.
BANNED = {
    "de": ["nr. 1", "beste", "jetzt herunterladen", "jetzt installieren"],
    "es": ["#1", "el mejor", "descarga ahora", "instala ahora"],
    "fr": ["n°1", "le meilleur", "télécharge maintenant"],
    "pt": ["nº 1", "o melhor", "baixe agora", "instale agora"],
    "uk": ["№1", "найкращий", "завантажуйте зараз"],
    "en": ["#1", "best", "top rated", "download now", "install now", "% off"],
}

# Locale → short language code (matches BANNED keys).
LOCALES = {
    "de-DE": "de",
    "es-419": "es",
    "fr-FR": "fr",
    "hi-IN": "hi",
    "id":    "id",
    "it-IT": "it",
    "ja-JP": "ja",
    "pt-BR": "pt",
    "tr-TR": "tr",
    "uk":    "uk",
}

TITLE = "Water Sort Puzzle"

T = {}  # T[locale][field] = string

# ============================================================================
# de-DE — German
# ============================================================================
T["de-DE"] = {
    "subtitle.txt":
        "Wasser gießen & sortieren",
    "short_description.txt":
        "Gieße & sortiere buntes Wasser. 500 Level mit täglichen Missionen!",
    "promotional_text.txt":
        "Gieße, sortiere und atme durch. 500 handgefertigte Level mit täglicher Herausforderung und Missionen.",
    "keywords.txt":
        "wasser sortieren,farb sortier,flüssigkeit,röhrenrätsel,gießen,entspannen,knobeln",
    "release_notes.txt":
        "• Aufgeräumtes Hauptmenü — Level, Shop und Mehr Spiele in eine kompakte Symbolleiste verlegt\n• Kleine Stabilitätsverbesserungen\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Gießen, sortieren, durchatmen.

Sortiere die bunten Flüssigkeiten in Reagenzgläser und bringe Ordnung ins Chaos. Ein zutiefst beruhigendes Puzzlespiel, das Geduld, Strategie und den perfekten "Aha!"-Moment belohnt.

🌊 SO SPIELST DU
• Tippe auf ein Glas, um die oberste Flüssigkeitsschicht aufzunehmen
• Gieße sie auf eine passende Farbe oder in ein leeres Glas
• Fülle jedes Glas mit einer einzigen Farbe, um den Level zu lösen
• Kein Zeitdruck — spiele in deinem eigenen Tempo

✨ FUNKTIONEN
• 500 handgefertigte Level — von sanften Anfängerrätseln bis zu kniffligen Expertenherausforderungen
• Sanfte, flüssige Gießanimationen — beobachte das Wasser strömen
• Tägliche Herausforderung — jeden Tag ein neues Rätsel mit Streak-Belohnungen
• Tägliche Missionen — 3 frische Ziele pro Tag, verdiene Bonus-Münzen
• Zugvergleich — sieh deine Zugzahl im Vergleich zum Par-Wert und deine Platzierung (10% / 25% / 50%)
• Statistik — verfolge gelöste Level, Gesamt-Gießvorgänge, tägliche Streak und mehr
• Tägliche Login-Streak — größere Belohnungen, je länger du am Stück spielst
• Streak-Schutz — zu lange weg? Gib Münzen aus, um deine Streak zu schützen
• Sanfte Wasser-Soundeffekte und prozedurale Ambient-Musik
• Kein Timer, kein Stress — vollständig entspannendes Spielerlebnis
• Verdiene Münzen und schalte Power-ups frei
• Lebenssystem mit großzügiger 30-Minuten-Regeneration
• Tipp- und Rückgängig-Tasten, wenn du nicht weiterkommst
• Funktioniert vollständig offline
• 20+ Sprachen unterstützt

🏆 LEVEL-FORTSCHRITT
Die Level werden allmählich schwieriger — niemals ein plötzlicher Sprung:
• Tutorial (1–10):    3 Farben — lerne die Grundlagen
• Einfach (11–30):    4 Farben — gewinne Selbstvertrauen
• Mittel (31–130):    5 Farben — die echte Herausforderung beginnt
• Schwer (131–300):   6–7 Farben — wahre Rätselmeisterschaft
• Experte (301–500):  8 Farben — die ultimative Herausforderung

📅 TÄGLICHE HERAUSFORDERUNG
Jeden Tag ein frisches Rätsel. Baue deine Streak für stetig wachsende Bonus-Münzen auf. Einen Tag verpasst? Gib Münzen aus, um die Streak zu retten und das Feuer am Brennen zu halten.

🎯 TÄGLICHE MISSIONEN
Drei frische Ziele jede Mitternacht:
• Beliebigen Level lösen · 30 Mal gießen · 3 Level abschließen
• Perfekt lösen (ohne Rückgängig) · Tägliche Herausforderung beenden
Verdiene bis zu 75 Bonus-Münzen pro Tag, einfach durchs Spielen.

📊 STATISTIK & FORTSCHRITT
• Insgesamt gelöste Level und perfekte Lösungen
• Kumulierte Gießvorgänge — wie viel Wasser hast du sortiert?
• Tägliche Login-Streak und persönlicher Rekord
• Aktuelles Level und Münzguthaben

⚡ ZUGVERGLEICH
Nach jedem Level siehst du genau, wie du abschneidest:
• Deine Zugzahl im Vergleich zum Par-Wert
• Bewertete Leistung: 10% / 25% / 50% Stufen
Verfeinere deine Punktzahl bei jedem erneuten Versuch.

🛒 SHOP
• Werbung entfernen — genieße ein ungestörtes Spielerlebnis für immer
• Münzpaket S — 50 Münzen für Tipps und Rückgängig-Aktionen
• Münzpaket L — 200 Münzen, größtes Bündel
• Unbegrenzte Rückgängig-Aktionen — bleib nie wieder stecken
• Extra Leben — stelle 5 Leben sofort wieder her
• Unbegrenzte Leben (1h) — spiele eine ganze Stunde frei
• Unbegrenzte Leben (∞) — verliere nie wieder ein Leben
""",
}

# ============================================================================
# es-419 — Spanish (Latin America)
# ============================================================================
T["es-419"] = {
    "subtitle.txt":
        "Vierte y ordena agua",
    "short_description.txt":
        "Vierte y ordena agua de colores. ¡500 niveles, misiones diarias y calma!",
    "promotional_text.txt":
        "Vierte, ordena y respira. 500 niveles hechos a mano con desafío diario y misiones.",
    "keywords.txt":
        "ordenar agua,clasificar colores,liquido,puzzle de tubos,verter,relajante,rompecabezas",
    "release_notes.txt":
        "• Menú principal más limpio — Niveles, Tienda y Más Juegos movidos a una fila compacta de íconos\n• Pequeñas mejoras de estabilidad\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — ¡Vierte, ordena y relájate!

Ordena los líquidos de colores en los tubos y restaura la calma del caos. Un rompecabezas profundamente relajante que premia la paciencia, la estrategia y ese momento perfecto de "¡aha!".

🌊 CÓMO JUGAR
• Toca un tubo para tomar la capa superior de líquido
• Viértela sobre un color que coincida o en un tubo vacío
• Llena cada tubo con un solo color para completar el nivel
• Sin presión de tiempo — juega a tu propio ritmo

✨ CARACTERÍSTICAS
• 500 niveles hechos a mano — desde acertijos suaves para principiantes hasta retos expertos
• Animaciones de vertido suaves y fluidas — mira fluir el agua
• Desafío Diario — un acertijo nuevo cada día con recompensas por racha
• Misiones Diarias — 3 objetivos frescos al día, gana monedas extra
• Comparación de movimientos — ve tu conteo vs. el par y tu rango (10% / 25% / 50%)
• Pantalla de Estadísticas — rastrea niveles completados, vertidos totales, racha diaria y más
• Racha de Inicio de Sesión — reclama recompensas mayores cuanto más juegues seguido
• Protector de Racha — ¿muchos días fuera? Gasta monedas para proteger tu racha
• Hermosos efectos de sonido de agua y música ambiental procedural
• Sin temporizador, sin estrés — jugabilidad totalmente relajante
• Gana monedas y desbloquea potenciadores
• Sistema de vidas con generosa regeneración de 30 minutos
• Botones de Pista y Deshacer cuando te atascas
• Funciona completamente sin conexión
• Más de 20 idiomas

🏆 PROGRESIÓN DE NIVELES
Los niveles aumentan gradualmente en dificultad — nunca un salto repentino:
• Tutorial (1–10):     3 colores — aprende lo básico
• Fácil (11–30):       4 colores — gana confianza
• Medio (31–130):      5 colores — comienza el reto real
• Difícil (131–300):   6–7 colores — verdadera maestría
• Experto (301–500):   8 colores — el desafío definitivo

📅 DESAFÍO DIARIO
Un acertijo nuevo cada día. Construye tu racha para monedas extra crecientes. ¿Perdiste un día? Gasta monedas para salvar tu racha y mantener viva la llama.

🎯 MISIONES DIARIAS
Tres objetivos frescos cada medianoche:
• Completa cualquier nivel · Vierte 30 veces · Termina 3 niveles
• Solución perfecta (sin deshacer) · Completa el Desafío Diario
¡Gana hasta 75 monedas extra al día solo por jugar!

📊 ESTADÍSTICAS Y PROGRESO
• Total de niveles completados y soluciones perfectas
• Vertidos acumulados — ¿cuánta agua has ordenado?
• Racha diaria de inicio de sesión y récord personal
• Nivel actual y saldo de monedas

⚡ COMPARACIÓN DE MOVIMIENTOS
Después de cada nivel, ve exactamente cómo te comparas:
• Tu conteo de movimientos vs. el par óptimo
• Rendimiento clasificado: niveles 10% / 25% / 50%
¡Mejora tu puntaje cada vez que repitas!

🛒 TIENDA
• Quitar Anuncios — disfruta una experiencia ininterrumpida para siempre
• Paquete de Monedas S — 50 monedas para pistas y deshacer
• Paquete de Monedas L — 200 monedas, el paquete más grande
• Deshacer Ilimitado — nunca más te atasques
• Vidas Extra — restaura 5 vidas al instante
• Vidas Ilimitadas (1h) — juega libre por una hora completa
• Vidas Ilimitadas (∞) — nunca pierdas otra vida
""",
}

# ============================================================================
# fr-FR — French
# ============================================================================
T["fr-FR"] = {
    "subtitle.txt":
        "Verse et trie l'eau",
    "short_description.txt":
        "Verse et trie l'eau colorée. 500 niveaux, missions quotidiennes et calme !",
    "promotional_text.txt":
        "Verse, trie et respire. 500 niveaux façonnés à la main avec défi quotidien et missions.",
    "keywords.txt":
        "trier eau,tri couleurs,liquide,casse-tete tubes,verser,relaxant,puzzle",
    "release_notes.txt":
        "• Menu principal épuré — Niveaux, Boutique et Plus de Jeux déplacés vers une rangée d'icônes compacte\n• Petites améliorations de stabilité\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Verse, trie, respire.

Trie les liquides colorés dans les tubes et ramène le calme dans le chaos. Un puzzle profondément apaisant qui récompense la patience, la stratégie et ce parfait moment « aha ! ».

🌊 COMMENT JOUER
• Touche un tube pour prendre la couche supérieure de liquide
• Verse-la sur une couleur correspondante ou dans un tube vide
• Remplis chaque tube d'une seule couleur pour terminer le niveau
• Aucune pression du temps — joue à ton propre rythme

✨ FONCTIONNALITÉS
• 500 niveaux faits main — des énigmes douces pour débutants aux défis d'experts
• Animations de versement fluides et soyeuses — regarde l'eau couler
• Défi Quotidien — une nouvelle énigme chaque jour avec des récompenses de série
• Missions Quotidiennes — 3 objectifs frais par jour, gagne des pièces bonus
• Comparaison de coups — vois ton nombre de coups face au par et ton classement (10% / 25% / 50%)
• Écran de Statistiques — suis les niveaux terminés, versements totaux, série quotidienne et plus
• Série de Connexion Quotidienne — réclame des récompenses plus grandes à mesure que tu joues
• Protecteur de Série — trop de jours d'absence ? Dépense des pièces pour protéger ta série
• Beaux effets sonores d'eau et musique d'ambiance procédurale
• Pas de minuteur, pas de stress — jeu entièrement relaxant
• Gagne des pièces et débloque des bonus
• Système de vies avec régénération généreuse de 30 minutes
• Boutons d'Indice et Annuler quand tu es bloqué
• Fonctionne entièrement hors ligne
• Plus de 20 langues prises en charge

🏆 PROGRESSION DES NIVEAUX
Les niveaux augmentent en difficulté progressivement — jamais de pic soudain :
• Tutoriel (1–10) :    3 couleurs — apprends les bases
• Facile (11–30) :     4 couleurs — gagne en confiance
• Moyen (31–130) :     5 couleurs — le vrai défi commence
• Difficile (131–300) : 6–7 couleurs — vraie maîtrise des énigmes
• Expert (301–500) :   8 couleurs — le défi ultime

📅 DÉFI QUOTIDIEN
Une nouvelle énigme chaque jour. Construis ta série pour des pièces bonus croissantes. Manqué un jour ? Dépense des pièces pour sauver ta série et garder la flamme vivante.

🎯 MISSIONS QUOTIDIENNES
Trois objectifs frais à chaque minuit :
• Terminer un niveau · Verser 30 fois · Finir 3 niveaux
• Résolution parfaite (sans annulation) · Terminer le Défi Quotidien
Gagne jusqu'à 75 pièces bonus par jour rien qu'en jouant !

📊 STATS & PROGRÈS
• Total de niveaux terminés et solutions parfaites
• Versements cumulés — combien d'eau as-tu triée ?
• Série de connexion quotidienne et record personnel
• Niveau actuel et solde de pièces

⚡ COMPARAISON DE COUPS
Après chaque niveau, vois exactement où tu te situes :
• Ton nombre de coups face au par optimal
• Performance classée : tranches 10% / 25% / 50%
Améliore ton score à chaque rejouage !

🛒 BOUTIQUE
• Retirer les Pubs — profite d'une expérience ininterrompue pour toujours
• Pack de Pièces S — 50 pièces pour indices et annulations
• Pack de Pièces L — 200 pièces, le plus gros paquet
• Annulations Illimitées — ne reste plus jamais bloqué
• Vies Supplémentaires — restaure 5 vies instantanément
• Vies Illimitées (1h) — joue librement pendant une heure entière
• Vies Illimitées (∞) — ne perds plus jamais une vie
""",
}

# ============================================================================
# hi-IN — Hindi
# ============================================================================
T["hi-IN"] = {
    "subtitle.txt":
        "रंगीन पानी छाँटें",
    "short_description.txt":
        "रंगीन पानी डालें और छाँटें। 500 स्तर, दैनिक मिशन और शांति!",
    "promotional_text.txt":
        "डालें, छाँटें और आराम करें। 500 हस्तनिर्मित स्तर, दैनिक चुनौती और मिशन के साथ।",
    "keywords.txt":
        "वाटर सॉर्ट,रंग पहेली,तरल पहेली,ट्यूब पहेली,आरामदायक,दिमागी खेल",
    "release_notes.txt":
        "• साफ-सुथरा मुख्य मेनू — स्तर, दुकान और अधिक खेल कॉम्पैक्ट आइकन पंक्ति में स्थानांतरित\n• छोटे स्थिरता सुधार\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — डालें, छाँटें और आराम करें!

रंगीन तरल पदार्थों को ट्यूबों में छाँटें और अराजकता में व्यवस्था लाएँ। एक गहराई से शांत करने वाली पहेली जो धैर्य, रणनीति और उस सही "अहा!" क्षण को पुरस्कृत करती है।

🌊 कैसे खेलें
• ऊपरी तरल परत उठाने के लिए एक ट्यूब पर टैप करें
• इसे मेल खाते रंग पर या खाली ट्यूब में डालें
• स्तर पूरा करने के लिए प्रत्येक ट्यूब को एक ही रंग से भरें
• कोई समय का दबाव नहीं — अपनी गति से खेलें

✨ विशेषताएँ
• 500 हस्तनिर्मित स्तर — सरल शुरुआती पहेलियों से कठिन विशेषज्ञ चुनौतियों तक
• मक्खन-सी चिकनी तरल डालने की एनिमेशन — पानी का प्रवाह देखें
• दैनिक चुनौती — हर दिन एक बिल्कुल नई पहेली, स्ट्रीक पुरस्कारों के साथ
• दैनिक मिशन — हर दिन 3 ताज़ा लक्ष्य, बोनस सिक्के कमाएँ
• चाल तुलना — अपनी चाल गिनती बनाम पार और आपकी रैंकिंग देखें (10% / 25% / 50%)
• आँकड़े स्क्रीन — पूरे किए गए स्तर, कुल डालने, दैनिक स्ट्रीक और अधिक ट्रैक करें
• दैनिक लॉगिन स्ट्रीक — जितना लंबा खेलेंगे, उतने बड़े पुरस्कार
• स्ट्रीक सेवर — बहुत दिन दूर रहे? सिक्के खर्च करके अपनी स्ट्रीक की रक्षा करें
• सुंदर पानी की ध्वनि और परिवेश संगीत
• कोई टाइमर नहीं, कोई तनाव नहीं — पूरी तरह से आरामदायक खेल
• सिक्के कमाएँ और पावर-अप अनलॉक करें
• 30 मिनट के पुनर्जनन के साथ जीवन प्रणाली
• अटक जाने पर संकेत और पूर्ववत बटन
• पूरी तरह से ऑफ़लाइन काम करता है
• 20+ भाषाएँ समर्थित

🏆 स्तर प्रगति
स्तर धीरे-धीरे कठिन होते जाते हैं — कभी अचानक उछाल नहीं:
• ट्यूटोरियल (1–10):     3 रंग — मूल बातें सीखें
• आसान (11–30):          4 रंग — आत्मविश्वास बनाएँ
• मध्यम (31–130):        5 रंग — असली चुनौती शुरू होती है
• कठिन (131–300):        6–7 रंग — सच्ची पहेली निपुणता
• विशेषज्ञ (301–500):    8 रंग — परम चुनौती

📅 दैनिक चुनौती
हर दिन एक ताज़ा पहेली! बढ़ते बोनस सिक्कों के लिए अपनी स्ट्रीक बनाएँ। एक दिन छूट गया? सिक्के खर्च करें और अपनी स्ट्रीक बचाएँ।

🎯 दैनिक मिशन
हर मध्यरात्रि तीन ताज़ा लक्ष्य:
• कोई भी स्तर पूरा करें · 30 बार डालें · 3 स्तर समाप्त करें
• पूर्ण समाधान (बिना पूर्ववत) · दैनिक चुनौती पूरी करें
केवल खेलने से प्रतिदिन 75 बोनस सिक्के तक कमाएँ!

📊 आँकड़े और प्रगति
• कुल पूरे किए गए स्तर और पूर्ण समाधान
• संचयी डालने — आपने कितना पानी छाँटा है?
• दैनिक लॉगिन स्ट्रीक और व्यक्तिगत रिकॉर्ड
• वर्तमान स्तर और सिक्का शेष

⚡ चाल तुलना
हर स्तर के बाद, देखें कि आप ठीक कैसे खड़े हैं:
• आपकी चाल गिनती बनाम इष्टतम पार
• रैंक प्रदर्शन: 10% / 25% / 50% ब्रैकेट
हर बार दोबारा खेलने पर अपना स्कोर सुधारें!

🛒 दुकान
• विज्ञापन हटाएँ — हमेशा के लिए निर्बाध अनुभव का आनंद लें
• सिक्का पैक S — संकेत और पूर्ववत के लिए 50 सिक्के
• सिक्का पैक L — 200 सिक्के, सबसे बड़ा बंडल
• असीमित पूर्ववत — फिर कभी न अटकें
• अतिरिक्त जीवन — तुरंत 5 जीवन पुनर्स्थापित करें
• असीमित जीवन (1 घंटा) — पूरे एक घंटे के लिए स्वतंत्र खेलें
• असीमित जीवन (∞) — फिर कभी जीवन न खोएँ
""",
}

# ============================================================================
# id — Indonesian (Play Console code is `id`, not `id-ID`)
# ============================================================================
T["id"] = {
    "subtitle.txt":
        "Tuang & sortir air warna",
    "short_description.txt":
        "Tuang & sortir air berwarna. 500 level, misi harian, dan ketenangan!",
    "promotional_text.txt":
        "Tuang, sortir, dan tenangkan diri. 500 level buatan tangan dengan tantangan harian dan misi.",
    "keywords.txt":
        "sortir air,puzzle warna,cairan,puzzle tabung,menuang,santai,asah otak",
    "release_notes.txt":
        "• Menu utama lebih rapi — Level, Toko, dan Game Lainnya dipindahkan ke baris ikon yang ringkas\n• Perbaikan stabilitas kecil\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Tuang, sortir, tenangkan diri!

Sortir cairan berwarna ke dalam tabung dan kembalikan ketenangan dari kekacauan. Permainan teka-teki yang sangat menenangkan, memberi penghargaan pada kesabaran, strategi, dan momen "aha!" yang sempurna.

🌊 CARA BERMAIN
• Ketuk tabung untuk mengambil lapisan cairan paling atas
• Tuangkan ke warna yang cocok atau ke tabung kosong
• Isi setiap tabung dengan satu warna untuk menyelesaikan level
• Tanpa tekanan waktu — bermain dengan ritmemu sendiri

✨ FITUR
• 500 level buatan tangan — dari teka-teki pemula yang lembut hingga tantangan ahli yang menantang
• Animasi tuang yang mulus — saksikan air mengalir
• Tantangan Harian — teka-teki baru setiap hari dengan hadiah streak
• Misi Harian — 3 tujuan baru setiap hari, dapatkan koin bonus
• Perbandingan Langkah — lihat jumlah langkahmu vs. par dan peringkatmu (10% / 25% / 50%)
• Layar Statistik — lacak level selesai, total tuangan, streak harian, dan lainnya
• Streak Login Harian — klaim hadiah lebih besar semakin lama bermain berturut-turut
• Penyelamat Streak — terlalu lama absen? Gunakan koin untuk melindungi streak
• Efek suara air yang indah dan musik ambient prosedural
• Tanpa timer, tanpa stres — gameplay yang sepenuhnya santai
• Dapatkan koin dan buka power-up
• Sistem nyawa dengan regenerasi 30 menit yang murah hati
• Tombol Petunjuk & Undo saat kamu buntu
• Bekerja sepenuhnya offline
• 20+ bahasa didukung

🏆 PROGRESI LEVEL
Level meningkat secara bertahap — tidak pernah lonjakan tiba-tiba:
• Tutorial (1–10):     3 warna — pelajari dasarnya
• Mudah (11–30):       4 warna — bangun kepercayaan diri
• Sedang (31–130):     5 warna — tantangan sebenarnya dimulai
• Sulit (131–300):     6–7 warna — penguasaan teka-teki sejati
• Ahli (301–500):      8 warna — tantangan tertinggi

📅 TANTANGAN HARIAN
Teka-teki baru setiap hari! Bangun streak-mu untuk koin bonus yang terus meningkat. Lewat satu hari? Gunakan koin untuk menyelamatkan streak dan menjaga api tetap menyala.

🎯 MISI HARIAN
Tiga tujuan baru setiap tengah malam:
• Selesaikan level apa saja · Tuang 30 kali · Selesaikan 3 level
• Solusi sempurna (tanpa undo) · Selesaikan Tantangan Harian
Dapatkan hingga 75 koin bonus per hari hanya dengan bermain!

📊 STATISTIK & PROGRES
• Total level selesai dan solusi sempurna
• Tuangan kumulatif — berapa banyak air yang sudah kamu sortir?
• Streak login harian dan rekor pribadi
• Level saat ini dan saldo koin

⚡ PERBANDINGAN LANGKAH
Setelah setiap level, lihat persis bagaimana kamu berdiri:
• Jumlah langkahmu vs. par optimal
• Performa berperingkat: bracket 10% / 25% / 50%
Tingkatkan skormu setiap kali main ulang!

🛒 TOKO
• Hapus Iklan — nikmati pengalaman tanpa gangguan selamanya
• Paket Koin S — 50 koin untuk petunjuk dan undo
• Paket Koin L — 200 koin, paket terbesar
• Undo Tak Terbatas — tidak akan pernah buntu lagi
• Nyawa Ekstra — pulihkan 5 nyawa seketika
• Nyawa Tak Terbatas (1j) — main bebas selama satu jam penuh
• Nyawa Tak Terbatas (∞) — jangan pernah kehilangan nyawa lagi
""",
}

# ============================================================================
# it-IT — Italian
# ============================================================================
T["it-IT"] = {
    "subtitle.txt":
        "Versa e ordina l'acqua",
    "short_description.txt":
        "Versa e ordina acqua colorata. 500 livelli, missioni quotidiane e calma!",
    "promotional_text.txt":
        "Versa, ordina e respira. 500 livelli realizzati a mano con sfida quotidiana e missioni.",
    "keywords.txt":
        "ordina acqua,puzzle colori,liquido,puzzle provette,versare,rilassante,rompicapo",
    "release_notes.txt":
        "• Menu principale più pulito — Livelli, Negozio e Altri Giochi spostati in una riga compatta di icone\n• Piccoli miglioramenti di stabilità\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Versa, ordina, respira.

Ordina i liquidi colorati nelle provette e riporta la calma nel caos. Un puzzle profondamente rilassante che premia la pazienza, la strategia e quel perfetto momento "aha!".

🌊 COME GIOCARE
• Tocca una provetta per prendere lo strato superiore di liquido
• Versalo su un colore corrispondente o in una provetta vuota
• Riempi ogni provetta con un solo colore per completare il livello
• Nessuna pressione del tempo — gioca al tuo ritmo

✨ CARATTERISTICHE
• 500 livelli realizzati a mano — da rompicapi gentili per principianti a sfide esperte
• Animazioni di versamento morbide e fluide — guarda l'acqua scorrere
• Sfida Quotidiana — un nuovo rompicapo ogni giorno con ricompense streak
• Missioni Quotidiane — 3 obiettivi freschi al giorno, guadagna monete bonus
• Confronto Mosse — vedi le tue mosse vs. il par e la tua classifica (10% / 25% / 50%)
• Schermata Statistiche — traccia livelli completati, versamenti totali, streak quotidiano e altro
• Streak Login Giornaliero — riscatta ricompense più grandi quanto più giochi consecutivamente
• Salva Streak — troppi giorni di assenza? Spendi monete per proteggere il tuo streak
• Bellissimi effetti sonori d'acqua e musica ambient procedurale
• Nessun timer, nessuno stress — gameplay completamente rilassante
• Guadagna monete e sblocca potenziamenti
• Sistema di vite con generosa rigenerazione di 30 minuti
• Pulsanti Suggerimento e Annulla quando sei bloccato
• Funziona completamente offline
• Più di 20 lingue supportate

🏆 PROGRESSIONE LIVELLI
I livelli aumentano gradualmente di difficoltà — mai un picco improvviso:
• Tutorial (1–10):     3 colori — impara le basi
• Facile (11–30):      4 colori — costruisci fiducia
• Medio (31–130):      5 colori — la vera sfida inizia
• Difficile (131–300): 6–7 colori — vera maestria nei rompicapi
• Esperto (301–500):   8 colori — la sfida definitiva

📅 SFIDA QUOTIDIANA
Un nuovo rompicapo ogni giorno. Costruisci il tuo streak per monete bonus crescenti. Saltato un giorno? Spendi monete per salvare il tuo streak e mantenere viva la fiamma.

🎯 MISSIONI QUOTIDIANE
Tre obiettivi freschi a ogni mezzanotte:
• Completa qualsiasi livello · Versa 30 volte · Finisci 3 livelli
• Soluzione perfetta (senza annullamenti) · Completa la Sfida Quotidiana
Guadagna fino a 75 monete bonus al giorno solo giocando!

📊 STATISTICHE & PROGRESSO
• Totale livelli completati e soluzioni perfette
• Versamenti cumulativi — quanta acqua hai ordinato?
• Streak login quotidiano e record personale
• Livello attuale e saldo monete

⚡ CONFRONTO MOSSE
Dopo ogni livello, vedi esattamente come ti posizioni:
• Il tuo numero di mosse vs. il par ottimale
• Performance classificata: fasce 10% / 25% / 50%
Migliora il tuo punteggio ogni volta che rigiochi!

🛒 NEGOZIO
• Rimuovi Annunci — goditi un'esperienza ininterrotta per sempre
• Pacchetto Monete S — 50 monete per suggerimenti e annulla
• Pacchetto Monete L — 200 monete, il bundle più grande
• Annulla Illimitato — non rimanere mai più bloccato
• Vite Extra — ripristina 5 vite all'istante
• Vite Illimitate (1h) — gioca liberamente per un'ora intera
• Vite Illimitate (∞) — non perdere mai più una vita
""",
}

# ============================================================================
# ja-JP — Japanese
# ============================================================================
T["ja-JP"] = {
    "subtitle.txt":
        "色水を注いで仕分け",
    "short_description.txt":
        "色水を注いで仕分け。500レベル、デイリーミッション、心穏やかに！",
    "promotional_text.txt":
        "注ぎ、仕分け、ひと息。500の手作りレベルとデイリーチャレンジ、ミッション付き。",
    "keywords.txt":
        "水仕分け,色合わせ,液体パズル,試験管パズル,注ぐ,リラックス,脳トレ",
    "release_notes.txt":
        "• メインメニューを整理 — レベル、ショップ、その他のゲームをコンパクトなアイコン行に移動\n• 細かな安定性の改善\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — 注いで、仕分けて、ひと息。

カラフルな液体を試験管に仕分けて、混沌から秩序を取り戻そう。深く心を落ち着かせるパズルゲームで、忍耐、戦略、そして完璧な「ひらめき」の瞬間を味わえます。

🌊 遊び方
• 試験管をタップして一番上の液体層を持ち上げる
• 同じ色の上か空の試験管に注ぐ
• 各試験管を一色で満たしてレベルクリア
• 時間制限なし — 自分のペースで遊べます

✨ 特長
• 500の手作りレベル — 優しい初心者パズルから手強いエキスパート挑戦まで
• なめらかな液体アニメーション — 水の流れを眺める
• デイリーチャレンジ — 毎日新しいパズルとストリーク報酬
• デイリーミッション — 毎日3つの新しい目標、ボーナスコイン獲得
• 手数比較 — あなたの手数とパー、ランク (10% / 25% / 50%) を確認
• 統計画面 — 完了レベル、総注ぎ回数、デイリーストリークなどを記録
• デイリーログインストリーク — 連続プレイでより大きな報酬
• ストリークセーバー — 数日離れた? コインでストリークを保護
• 美しい水の効果音とアンビエント音楽
• タイマーなし、ストレスなし — 完全にリラックスできるプレイ
• コインを稼いでパワーアップを解放
• 30分で回復する寛大なライフシステム
• 行き詰まったときのヒント＆元に戻すボタン
• 完全オフライン対応
• 20以上の言語に対応

🏆 レベル進行
レベルは徐々に難しくなります — 急な難易度上昇はありません:
• チュートリアル (1–10): 3色 — 基本を学ぶ
• イージー (11–30):     4色 — 自信をつける
• ミディアム (31–130):  5色 — 本当の挑戦が始まる
• ハード (131–300):     6–7色 — 真のパズルマスタリー
• エキスパート (301–500): 8色 — 究極の挑戦

📅 デイリーチャレンジ
毎日新しいパズル！ ストリークを積み上げてボーナスコインを増やそう。1日逃した? コインでストリークを救って炎を絶やさないで。

🎯 デイリーミッション
毎日深夜に3つの新しい目標:
• どのレベルでもクリア · 30回注ぐ · 3レベル完了
• 完璧な解決 (元に戻すなし) · デイリーチャレンジ完了
プレイするだけで1日最大75ボーナスコイン！

📊 統計と進行状況
• 総完了レベルと完璧な解決数
• 累積注ぎ回数 — どれだけの水を仕分けた?
• デイリーログインストリークと自己記録
• 現在のレベルとコイン残高

⚡ 手数比較
各レベル後、自分の立ち位置が正確に分かります:
• あなたの手数 vs. 最適パー
• ランク評価: 10% / 25% / 50% の階層
リプレイのたびにスコアを向上させよう！

🛒 ショップ
• 広告削除 — 中断のない体験を永遠に
• コインパックS — ヒントと元に戻す用の50コイン
• コインパックL — 200コイン、最大バンドル
• 無制限の元に戻す — もう行き詰まらない
• 追加ライフ — 5ライフを即座に回復
• 無制限ライフ (1時間) — まるまる1時間自由にプレイ
• 無制限ライフ (∞) — もうライフを失わない
""",
}

# ============================================================================
# pt-BR — Portuguese (Brazil)
# ============================================================================
T["pt-BR"] = {
    "subtitle.txt":
        "Despeje e classifique água",
    "short_description.txt":
        "Despeje e classifique água colorida. 500 níveis, missões diárias e calma!",
    "promotional_text.txt":
        "Despeje, classifique e respire. 500 níveis feitos à mão com desafio diário e missões.",
    "keywords.txt":
        "classificar agua,puzzle cores,liquido,quebra cabeca tubos,despejar,relaxante,raciocinio",
    "release_notes.txt":
        "• Menu principal mais limpo — Níveis, Loja e Mais Jogos movidos para uma linha compacta de ícones\n• Pequenas melhorias de estabilidade\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Despeje, classifique, respire.

Classifique os líquidos coloridos nos tubos e traga ordem ao caos. Um quebra-cabeça profundamente calmante que recompensa paciência, estratégia e aquele momento perfeito de "aha!".

🌊 COMO JOGAR
• Toque em um tubo para pegar a camada superior de líquido
• Despeje sobre uma cor correspondente ou em um tubo vazio
• Encha cada tubo com uma única cor para completar o nível
• Sem pressão de tempo — jogue no seu próprio ritmo

✨ RECURSOS
• 500 níveis feitos à mão — de quebra-cabeças suaves para iniciantes a desafios experientes
• Animações de despejo suaves e fluidas — assista a água fluir
• Desafio Diário — um novo quebra-cabeça todo dia com recompensas de sequência
• Missões Diárias — 3 objetivos frescos por dia, ganhe moedas bônus
• Comparação de Movimentos — veja sua contagem vs. o par e seu ranking (10% / 25% / 50%)
• Tela de Estatísticas — acompanhe níveis completos, despejos totais, sequência diária e mais
• Sequência de Login Diária — receba recompensas maiores quanto mais jogar consecutivamente
• Protetor de Sequência — muitos dias longe? Gaste moedas para proteger sua sequência
• Lindos efeitos sonoros de água e música ambiente procedural
• Sem cronômetro, sem estresse — jogabilidade totalmente relaxante
• Ganhe moedas e desbloqueie aprimoramentos
• Sistema de vidas com generosa regeneração de 30 minutos
• Botões de Dica e Desfazer quando você travar
• Funciona totalmente offline
• Mais de 20 idiomas suportados

🏆 PROGRESSÃO DE NÍVEIS
Os níveis aumentam de dificuldade gradualmente — nunca um salto repentino:
• Tutorial (1–10):     3 cores — aprenda o básico
• Fácil (11–30):       4 cores — ganhe confiança
• Médio (31–130):      5 cores — o desafio real começa
• Difícil (131–300):   6–7 cores — verdadeira maestria
• Especialista (301–500): 8 cores — o desafio definitivo

📅 DESAFIO DIÁRIO
Um novo quebra-cabeça todo dia. Construa sua sequência para moedas bônus crescentes. Perdeu um dia? Gaste moedas para salvar sua sequência e manter a chama viva.

🎯 MISSÕES DIÁRIAS
Três objetivos frescos a cada meia-noite:
• Complete qualquer nível · Despeje 30 vezes · Termine 3 níveis
• Solução perfeita (sem desfazer) · Complete o Desafio Diário
Ganhe até 75 moedas bônus por dia apenas jogando!

📊 ESTATÍSTICAS E PROGRESSO
• Total de níveis completos e soluções perfeitas
• Despejos cumulativos — quanta água você classificou?
• Sequência de login diária e recorde pessoal
• Nível atual e saldo de moedas

⚡ COMPARAÇÃO DE MOVIMENTOS
Após cada nível, veja exatamente como você se sai:
• Sua contagem de movimentos vs. o par ótimo
• Desempenho classificado: faixas 10% / 25% / 50%
Melhore sua pontuação cada vez que rejogar!

🛒 LOJA
• Remover Anúncios — desfrute de uma experiência ininterrupta para sempre
• Pacote de Moedas P — 50 moedas para dicas e desfazer
• Pacote de Moedas G — 200 moedas, o maior pacote
• Desfazer Ilimitado — nunca mais fique travado
• Vidas Extras — restaure 5 vidas instantaneamente
• Vidas Ilimitadas (1h) — jogue livremente por uma hora inteira
• Vidas Ilimitadas (∞) — nunca mais perca uma vida
""",
}

# ============================================================================
# tr-TR — Turkish
# ============================================================================
T["tr-TR"] = {
    "subtitle.txt":
        "Renkli su dök & ayır",
    "short_description.txt":
        "Renkli suyu dök ve ayır. 500 seviye, günlük görevler ve huzur!",
    "promotional_text.txt":
        "Dök, ayır ve nefes al. 500 el yapımı seviye, günlük meydan okuma ve görevlerle.",
    "keywords.txt":
        "su ayırma,renk bulmaca,sıvı bulmaca,tüp bulmaca,dökme,rahatlatıcı,zeka oyunu",
    "release_notes.txt":
        "• Daha temiz ana menü — Seviyeler, Mağaza ve Diğer Oyunlar kompakt bir simge satırına taşındı\n• Küçük kararlılık iyileştirmeleri\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Dök, ayır, nefes al.

Renkli sıvıları tüplere ayır ve kaostan düzeni geri getir. Sabrı, stratejiyi ve o mükemmel "aha!" anını ödüllendiren, derinden rahatlatıcı bir bulmaca oyunu.

🌊 NASIL OYNANIR
• En üstteki sıvı katmanını almak için bir tüpe dokun
• Eşleşen bir renge veya boş bir tüpe dök
• Seviyeyi tamamlamak için her tüpü tek bir renkle doldur
• Zaman baskısı yok — kendi tempoyla oyna

✨ ÖZELLİKLER
• 500 el yapımı seviye — yumuşak başlangıç bulmacalarından zorlu uzman meydan okumalarına kadar
• Pürüzsüz, akıcı dökme animasyonları — suyun akışını izle
• Günlük Meydan Okuma — her gün yepyeni bir bulmaca, seri ödülleriyle
• Günlük Görevler — günde 3 taze hedef, bonus altın kazan
• Hamle Karşılaştırması — hamle sayını par ile ve sıralamanı (10% / 25% / 50%) gör
• İstatistik Ekranı — tamamlanan seviyeleri, toplam dökmeleri, günlük seriyi ve daha fazlasını izle
• Günlük Giriş Serisi — art arda oynadıkça daha büyük ödüller
• Seri Koruyucu — uzun gün uzakta mı? Serini korumak için altın harca
• Güzel su ses efektleri ve prosedürel ortam müziği
• Zamanlayıcı yok, stres yok — tamamen rahatlatıcı oynanış
• Altın kazan ve güçlendirmeleri aç
• Cömert 30 dakika yenilemeli can sistemi
• Tıkandığında İpucu ve Geri Al düğmeleri
• Tamamen çevrimdışı çalışır
• 20+ dil destekleniyor

🏆 SEVİYE İLERLEMESİ
Seviyeler kademeli olarak zorlaşır — asla ani bir sıçrama olmaz:
• Eğitim (1–10):       3 renk — temelleri öğren
• Kolay (11–30):       4 renk — özgüven kazan
• Orta (31–130):       5 renk — gerçek meydan okuma başlar
• Zor (131–300):       6–7 renk — gerçek bulmaca ustalığı
• Uzman (301–500):     8 renk — nihai meydan okuma

📅 GÜNLÜK MEYDAN OKUMA
Her gün taze bir bulmaca! Artan bonus altınlar için serini oluştur. Bir günü kaçırdın mı? Altın harcayarak serini kurtar ve ateşi canlı tut.

🎯 GÜNLÜK GÖREVLER
Her gece yarısı üç taze hedef:
• Herhangi bir seviyeyi tamamla · 30 kez dök · 3 seviye bitir
• Mükemmel çözüm (geri alma yok) · Günlük Meydan Okumayı bitir
Sadece oynayarak günde 75'e kadar bonus altın kazan!

📊 İSTATİSTİK & İLERLEME
• Toplam tamamlanan seviye ve mükemmel çözümler
• Birikmiş dökmeler — ne kadar su ayırdın?
• Günlük giriş serisi ve kişisel rekor
• Mevcut seviye ve altın bakiyesi

⚡ HAMLE KARŞILAŞTIRMASI
Her seviyeden sonra, tam olarak nerede olduğunu gör:
• Hamle sayın vs. optimum par
• Sıralanmış performans: 10% / 25% / 50% dilimleri
Her tekrar oynadığında skorunu iyileştir!

🛒 MAĞAZA
• Reklamları Kaldır — sonsuza dek kesintisiz bir deneyimin tadını çıkar
• Altın Paketi S — ipuçları ve geri al için 50 altın
• Altın Paketi L — 200 altın, en büyük paket
• Sınırsız Geri Al — bir daha asla tıkanma
• Ekstra Can — anında 5 can geri yükle
• Sınırsız Can (1s) — bir saat boyunca özgürce oyna
• Sınırsız Can (∞) — bir daha asla can kaybetme
""",
}

# ============================================================================
# uk — Ukrainian (Play Console code is `uk`, not `uk-UA`)
# ============================================================================
T["uk"] = {
    "subtitle.txt":
        "Налий і сортуй воду",
    "short_description.txt":
        "Наливай і сортуй кольорову воду. 500 рівнів, щоденні місії та спокій!",
    "promotional_text.txt":
        "Наливай, сортуй і видихни. 500 ручних рівнів зі щоденним викликом і місіями.",
    "keywords.txt":
        "сортування води,кольорова головоломка,рідина,пробірки,наливати,розслаблююча,логіка",
    "release_notes.txt":
        "• Чистіше головне меню — Рівні, Магазин і Інші ігри переміщено до компактного рядка іконок\n• Невеликі покращення стабільності\n",
    "full_description.txt":
        """💧 Water Sort Puzzle — Наливай, сортуй, видихни.

Сортуй кольорові рідини у пробірки та поверни порядок із хаосу. Глибоко заспокійлива головоломка, що винагороджує терпіння, стратегію та той ідеальний момент «ага!».

🌊 ЯК ГРАТИ
• Торкнись пробірки, щоб взяти верхній шар рідини
• Налий її на відповідний колір або в порожню пробірку
• Заповни кожну пробірку одним кольором, щоб пройти рівень
• Без обмежень часу — грай у своєму темпі

✨ ОСОБЛИВОСТІ
• 500 ручних рівнів — від м'яких головоломок для початківців до складних випробувань для експертів
• Плавні, шовковисті анімації наливання — спостерігай, як тече вода
• Щоденне Випробування — нова головоломка щодня з нагородами за серію
• Щоденні Місії — 3 свіжі цілі на день, заробляй бонусні монети
• Порівняння Ходів — побач свою кількість ходів проти пара та свій ранг (10% / 25% / 50%)
• Екран Статистики — стеж за пройденими рівнями, загальними наливаннями, щоденною серією та іншим
• Щоденна Серія Входів — отримуй більші нагороди, чим довше граєш поспіль
• Збереження Серії — занадто довго був відсутній? Витрать монети, щоб захистити свою серію
• Гарні звукові ефекти води та процедурна фонова музика
• Без таймера, без стресу — повністю розслаблюючий геймплей
• Заробляй монети та розблоковуй підсилення
• Система життів зі щедрою 30-хвилинною регенерацією
• Кнопки Підказки та Скасувати, коли застрягаєш
• Працює повністю офлайн
• Підтримує понад 20 мов

🏆 ПРОГРЕСІЯ РІВНІВ
Рівні поступово ускладнюються — без раптових стрибків:
• Туторіал (1–10):     3 кольори — вивчи основи
• Легкий (11–30):      4 кольори — здобувай впевненість
• Середній (31–130):   5 кольорів — справжній виклик починається
• Складний (131–300):  6–7 кольорів — справжня майстерність
• Експерт (301–500):   8 кольорів — остаточний виклик

📅 ЩОДЕННЕ ВИПРОБУВАННЯ
Свіжа головоломка щодня! Будуй свою серію для зростаючих бонусних монет. Пропустив день? Витрать монети, щоб врятувати серію та підтримати вогонь.

🎯 ЩОДЕННІ МІСІЇ
Три свіжі цілі щоопівночі:
• Пройди будь-який рівень · Налий 30 разів · Заверши 3 рівні
• Ідеальне рішення (без скасувань) · Заверши Щоденне Випробування
Заробляй до 75 бонусних монет на день просто граючи!

📊 СТАТИСТИКА ТА ПРОГРЕС
• Загалом пройдені рівні та ідеальні рішення
• Кумулятивні наливання — скільки води ти відсортував?
• Щоденна серія входів та особистий рекорд
• Поточний рівень і баланс монет

⚡ ПОРІВНЯННЯ ХОДІВ
Після кожного рівня побач, як ти стоїш:
• Твоя кількість ходів проти оптимального пара
• Рейтингова продуктивність: рівні 10% / 25% / 50%
Покращуй свій результат щоразу, коли граєш повторно!

🛒 МАГАЗИН
• Прибрати Рекламу — насолоджуйся безперервним досвідом назавжди
• Пакет Монет S — 50 монет для підказок та скасувань
• Пакет Монет L — 200 монет, найбільший набір
• Необмежені Скасування — більше ніколи не застрягай
• Додаткові Життя — миттєво відновлюй 5 життів
• Необмежені Життя (1 год) — грай вільно цілу годину
• Необмежені Життя (∞) — більше ніколи не втрачай життя
""",
}


def main():
    app_dir = REPO / APP / "metadata"
    en_dir = app_dir / "en-US"
    if not en_dir.is_dir():
        print(f"ERROR: source en-US not found at {en_dir}", file=sys.stderr)
        sys.exit(1)

    en_title = (en_dir / "title.txt").read_text()

    failures = []
    written = 0
    for locale, fields in T.items():
        short = LOCALES[locale]
        out = app_dir / locale
        out.mkdir(parents=True, exist_ok=True)
        # title.txt — copy English verbatim per TRANSLATIONS.md §3
        (out / "title.txt").write_text(en_title)
        written += 1

        for field, content in fields.items():
            text = content
            # ensure trailing newline (matches en-US convention)
            if not text.endswith("\n"):
                text = text + "\n"

            # validate length (strip trailing newline before measuring;
            # gen_translations.py validates the .strip() of LLM output)
            measured = text.strip()
            limit = LIMITS[field]
            if len(measured) > limit:
                failures.append(
                    f"{locale}/{field}: {len(measured)} > {limit}"
                )
                continue

            # banned-phrase check
            lower = measured.lower()
            for phrase in BANNED.get(short, []):
                if phrase.lower() in lower:
                    failures.append(
                        f"{locale}/{field}: banned phrase {phrase!r}"
                    )
                    break
            else:
                (out / field).write_text(text)
                written += 1

    print(f"Wrote {written} files across {len(T)} locales.")
    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
