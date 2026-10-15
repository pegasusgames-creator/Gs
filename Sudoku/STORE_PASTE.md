# Sudoku — store paste sheet

One file with every translated string for every locale, wrapped in
`<locale>…</locale>` blocks. Open in Play Console / App Store Connect,
find the right field, and paste the matching block for each language.

The 13 locales (Play Console tags): en-US, ar, de-DE, es-419, fr-FR, hi-IN, id, it-IT, ja-JP, pt-BR, tr-TR, uk, zh-CN

**Notes:**
- Indonesian uses tag `<id>` (not `id-ID`) — Play Console quirk.
- Ukrainian uses tag `<uk>` (not `uk-UA`) — Play Console quirk.
- Chinese uses `<zh-CN>` (Simplified). Arabic uses `<ar>` (RTL — Play
  Console renders right-to-left automatically when this locale is
  enabled).
- Title is intentionally English globally (per TRANSLATIONS.md §3) —
  not included here. Leave the title field blank for non-English
  locales; Play falls back to the default.

---


## RELEASE NOTES (≤500 chars per locale)

_Test and release → Production → release details_

<en-US>
Sudoku 3.0 is a complete rebuild:
• 500 new puzzles graded by solving technique, from singles to XY-Wing
• Hints fill a correct cell and name the technique
• Notes that clear themselves, conflict highlights, undo and erase
• Three-mistake limit with a second chance that keeps your board
• Daily puzzle with streaks, plus Endless mode at any difficulty
• Seven board themes and personal best times
</en-US>

<ar>
أُعيد بناء Sudoku 3.0 بالكامل:
• 500 لغز جديد مصنّف حسب تقنية الحل، من المفردات إلى XY-Wing
• التلميح يملأ خانة صحيحة ويذكر اسم التقنية
• ملاحظات تُنظّف نفسها، وإبراز التعارض، وتراجع ومسح
• ثلاثة أخطاء تُنهي اللغز، وفرصة ثانية تحفظ لوحتك
• لغز يومي مع سلاسل، ووضع لا نهائي بأي صعوبة
• سبعة أنماط للوحة وأفضل الأوقات
</ar>

<de-DE>
Sudoku 3.0 ist komplett neu gebaut:
• 500 neue Rätsel, nach Lösungstechnik eingestuft – von Singles bis XY-Wing
• Tipps füllen ein richtiges Feld und nennen die Technik
• Notizen, die sich selbst aufräumen, Konflikt-Markierung, Rückgängig und Löschen
• Drei Fehler beenden ein Rätsel – eine zweite Chance behält dein Brett
• Tagesrätsel mit Serien und ein Endlos-Modus in jeder Stufe
• Sieben Brett-Designs und persönliche Bestzeiten
</de-DE>

<es-419>
Sudoku 3.0 es una reconstrucción completa:
• 500 sudokus nuevos clasificados por técnica, de singles a XY-Wing
• Las pistas llenan una casilla correcta y nombran la técnica
• Notas que se limpian solas, conflictos resaltados, deshacer y borrar
• Tres errores terminan el sudoku; una segunda oportunidad conserva tu tablero
• Sudoku diario con rachas y modo Infinito en cualquier dificultad
• Siete temas de tablero y mejores tiempos
</es-419>

<fr-FR>
Sudoku 3.0 est entièrement reconstruit :
• 500 nouvelles grilles classées par technique, des singletons au XY-Wing
• Les indices remplissent une case juste et nomment la technique
• Notes qui se nettoient seules, conflits surlignés, annuler et effacer
• Trois erreurs terminent la grille ; une seconde chance garde votre plateau
• Grille du jour avec séries et mode Infini à toute difficulté
• Sept thèmes de grille et meilleurs temps
</fr-FR>

<hi-IN>
Sudoku 3.0 पूरी तरह नए सिरे से बना है:
• तकनीक के अनुसार श्रेणीबद्ध 500 नई पहेलियाँ, सिंगल से XY-Wing तक
• संकेत एक सही खाना भरता है और तकनीक का नाम बताता है
• खुद साफ़ होने वाले नोट्स, टकराव हाइलाइट, अनडू और मिटाएँ
• तीन गलतियों पर पहेली खत्म; दूसरा मौका आपका बोर्ड बचाता है
• स्ट्रीक वाली दैनिक पहेली और हर कठिनाई में एंडलेस मोड
• सात बोर्ड थीम और सबसे अच्छे समय
</hi-IN>

<id>
Sudoku 3.0 dibangun ulang sepenuhnya:
• 500 teka-teki baru yang dinilai menurut teknik, dari single sampai XY-Wing
• Petunjuk mengisi satu sel yang benar dan menyebut tekniknya
• Catatan yang bersih sendiri, sorotan bentrok, urungkan dan hapus
• Tiga kesalahan mengakhiri teka-teki; kesempatan kedua menyimpan papanmu
• Teka-teki harian dengan runtutan dan mode Tanpa Akhir di semua tingkat
• Tujuh tema papan dan waktu terbaik
</id>

<it-IT>
Sudoku 3.0 è stato ricostruito da zero:
• 500 nuovi sudoku classificati per tecnica, dai singoli all'XY-Wing
• I suggerimenti riempiono una casella corretta e nominano la tecnica
• Note che si puliscono da sole, conflitti evidenziati, annulla e cancella
• Tre errori chiudono il sudoku; una seconda possibilità salva la griglia
• Sudoku del giorno con serie e modalità Infinita a ogni difficoltà
• Sette temi della griglia e tempi migliori
</it-IT>

<ja-JP>
Sudoku 3.0 は全面的に作り直しました：
• 解法テクニックで難易度分けした新しい500問（シングルからXY-Wingまで）
• ヒントは正しいマスを1つ埋め、使った手筋の名前を表示
• 自動で整理されるメモ、矛盾のハイライト、元に戻す・消去
• ミス3回で終了、セカンドチャンスで盤面をそのまま続行
• 連続記録つきのデイリー問題と、好きな難易度のエンドレスモード
• 7種類の盤面テーマとベストタイム
</ja-JP>

<pt-BR>
O Sudoku 3.0 foi reconstruído do zero:
• 500 novos sudokus classificados por técnica, de singles a XY-Wing
• As dicas preenchem uma casa correta e dizem a técnica
• Notas que se limpam sozinhas, conflitos destacados, desfazer e apagar
• Três erros encerram o sudoku; uma segunda chance mantém seu tabuleiro
• Sudoku diário com sequências e modo Infinito em qualquer dificuldade
• Sete temas de tabuleiro e melhores tempos
</pt-BR>

<tr-TR>
Sudoku 3.0 baştan yeniden yapıldı:
• Tekniğe göre derecelenmiş 500 yeni bulmaca, tekillerden XY-Wing'e
• İpuçları doğru bir hücreyi doldurur ve tekniğin adını söyler
• Kendini temizleyen notlar, çakışma vurgusu, geri al ve sil
• Üç hata bulmacayı bitirir; ikinci şans tahtanı korur
• Serili günlük bulmaca ve her zorlukta Sonsuz mod
• Yedi tahta teması ve en iyi süreler
</tr-TR>

<uk>
Sudoku 3.0 повністю перебудовано:
• 500 нових головоломок за техніками розв'язання — від одиночок до XY-Wing
• Підказка заповнює правильну клітинку й називає техніку
• Нотатки, що прибираються самі, підсвічування конфліктів, скасування й стирання
• Три помилки завершують головоломку; другий шанс зберігає поле
• Щоденна головоломка із серіями та нескінченний режим будь-якої складності
• Сім тем поля й найкращий час
</uk>

<zh-CN>
Sudoku 3.0 全面重制：
• 500道按解题技巧分级的新谜题，从唯一数到XY-Wing
• 提示会填入一个正确格并说出所用技巧
• 自动整理的笔记、冲突高亮、撤销与擦除
• 错三次结束本局；第二次机会保留你的棋盘
• 带连胜记录的每日谜题，以及任意难度的无尽模式
• 七款棋盘主题与个人最佳时间
</zh-CN>

---

## SHORT DESCRIPTION (≤80 chars per locale)

_Grow → Store presence → Main store listing → Short description_

<en-US>
500 Sudoku puzzles graded by technique, a daily puzzle and hints that teach.
</en-US>

<ar>
500 لغز سودوكو مصنّفة حسب تقنية الحل، ولغز يومي، وتلميحات تعلّمك الخطوة.
</ar>

<de-DE>
500 Sudoku-Rätsel nach Lösungstechnik sortiert, Tagesrätsel, lehrreiche Tipps.
</de-DE>

<es-419>
500 sudokus clasificados por técnica, un reto diario y pistas que enseñan.
</es-419>

<fr-FR>
500 grilles de sudoku classées par technique, un défi quotidien et des indices.
</fr-FR>

<hi-IN>
तकनीक के अनुसार श्रेणीबद्ध 500 सुडोकू, रोज़ की पहेली और सिखाने वाले संकेत।
</hi-IN>

<id>
500 sudoku bertingkat menurut teknik, teka-teki harian, dan petunjuk mendidik.
</id>

<it-IT>
500 sudoku classificati per tecnica, una sfida quotidiana e suggerimenti utili.
</it-IT>

<ja-JP>
解法テクニックで難易度分けした数独500問、デイリー問題、学べるヒント。
</ja-JP>

<pt-BR>
500 sudokus classificados por técnica, um desafio diário e dicas que ensinam.
</pt-BR>

<tr-TR>
Tekniğe göre derecelenmiş 500 sudoku, günlük bulmaca ve öğreten ipuçları.
</tr-TR>

<uk>
500 судоку за техніками розв'язання, щоденна головоломка й навчальні підказки.
</uk>

<zh-CN>
500道按解题技巧分级的数独、每日挑战，以及会教你方法的提示。
</zh-CN>

---

## FULL DESCRIPTION (≤4000 chars per locale)

_Grow → Store presence → Main store listing → Full description_

<en-US>
Nine digits, eighty-one cells, one right answer — and a hint that tells you why.

Sudoku is the classic number puzzle, made for calm, focused play. Fill the grid so every row, column and 3×3 box holds the digits 1 to 9 exactly once. It works offline, so you can solve anywhere.

500 PUZZLES, GRADED BY TECHNIQUE
Difficulty comes from the logic a puzzle needs, not just from how many numbers are missing:
• Easy (1–125): singles only, with generous starting grids
• Medium (126–250): pointing pairs, box/line claims, naked and hidden pairs
• Hard (251–375): triples, quads and the X-Wing
• Expert (376–500): XY-Wing, XYZ-Wing and Swordfish
Every puzzle can be solved by logic alone.

HINTS THAT TEACH
Stuck? A hint fills one correct cell and names the technique that finds it — hidden single, pointing pair, X-Wing — so you learn the move, not just the answer.

TOOLS THAT FEEL RIGHT
• Notes mode for pencil marks; placing a digit clears it from nearby notes
• Highlights for the selected row, column and box, and every matching digit
• Clashing digits light up instantly
• Undo, erase, and a count of what's left on every number key
• Three mistakes end a puzzle; a second chance keeps your board
• A timer with personal best times for each difficulty
• Your board saves as you go, so Continue picks up exactly where you stopped

A NEW PUZZLE EVERY DAY
The Daily puzzle ramps from Easy on Monday to Expert on Sunday. Solve it to build a streak and earn bonus coins. Finished the campaign? Endless mode deals fresh boards at any difficulty.

SEVEN BOARD THEMES
Ink, Pencil, Matcha, Coral, Ocean, Espresso and Midnight each recolour the whole grid. Unlock them by solving puzzles, or Midnight with coins.

RELAXING AND SATISFYING
Soft sounds, gentle vibration (switch it off in Settings) and a small celebration whenever a row, column or box falls into place.

Free to play with optional ads and in-app purchases. The Season Pass removes ads, adds daily coins, unlocks every theme and gives unlimited hints.
</en-US>

<ar>
تسعة أرقام، إحدى وثمانون خانة، إجابة صحيحة واحدة — وتلميح يشرح لك السبب.

سودوكو هو لغز الأرقام الكلاسيكي للعب الهادئ والمركّز. املأ الشبكة بحيث يحتوي كل صف وعمود ومربع 3×3 على الأرقام من 1 إلى 9 مرة واحدة فقط. تعمل اللعبة دون اتصال.

500 لغز مصنّفة حسب التقنية
تأتي الصعوبة من المنطق الذي يتطلبه كل لغز:
• سهل (1–125): مفردات فقط مع أرقام بداية كثيرة
• متوسط (126–250): أزواج مُشيرة، وتقليص المربع/الخط، وأزواج مكشوفة ومخفية
• صعب (251–375): ثلاثيات ورباعيات وX-Wing
• خبير (376–500): XY-Wing وXYZ-Wing وSwordfish
كل لغز يُحل بالمنطق وحده.

تلميحات تعلّمك
يملأ التلميح خانة صحيحة ويذكر التقنية التي تكشفها، فتتعلم الخطوة لا الإجابة فقط.

أدوات مريحة
• وضع الملاحظات؛ عند وضع رقم يُحذف من الملاحظات المجاورة
• إبراز الصف والعمود والمربع والأرقام المتطابقة
• الأرقام المتعارضة تُضاء فورًا
• تراجع ومسح وعدّاد للأرقام المتبقية على كل زر
• ثلاثة أخطاء تُنهي اللغز، وفرصة ثانية تحفظ لوحتك
• مؤقت مع أفضل وقت لكل مستوى
• حفظ تلقائي: زر المتابعة يعيدك إلى حيث توقفت تمامًا

لغز جديد كل يوم
يبدأ اللغز اليومي سهلًا يوم الاثنين ويصل إلى مستوى الخبير يوم الأحد. حلّه لتطيل سلسلتك وتكسب عملات إضافية. أنهيت الحملة؟ الوضع اللانهائي يقدّم لوحات جديدة بأي صعوبة.

سبعة أنماط للوحة
Ink وPencil وMatcha وCoral وOcean وEspresso وMidnight تغيّر ألوان الشبكة كلها.

مريحة وممتعة
أصوات ناعمة واهتزاز خفيف (يمكن إيقافه من الإعدادات) واحتفال صغير عند اكتمال صف أو عمود أو مربع.

مجانية مع إعلانات اختيارية ومشتريات داخل التطبيق.
</ar>

<de-DE>
Neun Ziffern, einundachtzig Felder, eine richtige Antwort – und ein Tipp, der dir sagt, warum.

Sudoku ist das klassische Zahlenrätsel für ruhiges, konzentriertes Spielen. Fülle das Gitter so, dass jede Zeile, jede Spalte und jeder 3×3-Block die Ziffern 1 bis 9 genau einmal enthält. Alles funktioniert offline.

500 RÄTSEL, NACH TECHNIK EINGESTUFT
Die Schwierigkeit ergibt sich aus der Logik, die ein Rätsel verlangt:
• Leicht (1–125): nur Singles, großzügige Startgitter
• Mittel (126–250): Pointing Pairs, Block/Linie-Reduktion, nackte und versteckte Paare
• Schwer (251–375): Tripel, Quadrupel und X-Wing
• Experte (376–500): XY-Wing, XYZ-Wing und Swordfish
Jedes Rätsel lässt sich allein mit Logik lösen.

TIPPS, DIE ETWAS BEIBRINGEN
Ein Tipp füllt ein richtiges Feld und nennt die Technik, die es findet. So lernst du den Zug, nicht nur die Lösung.

WERKZEUGE, DIE SICH RICHTIG ANFÜHLEN
• Notizmodus für Kandidaten; eine gesetzte Ziffer verschwindet aus den Notizen ringsum
• Markierung von Zeile, Spalte, Block und allen gleichen Ziffern
• Widersprüche leuchten sofort auf
• Rückgängig, Löschen und eine Restanzeige auf jeder Zifferntaste
• Drei Fehler beenden ein Rätsel; eine zweite Chance behält dein Brett
• Timer mit Bestzeiten für jede Stufe
• Dein Brett wird laufend gespeichert – Weiter macht genau dort weiter

JEDEN TAG EIN NEUES RÄTSEL
Das Tagesrätsel steigert sich von Leicht am Montag bis Experte am Sonntag. Baue eine Serie auf und verdiene Bonusmünzen. Kampagne geschafft? Der Endlos-Modus liefert neue Bretter in jeder Stufe.

SIEBEN BRETT-DESIGNS
Ink, Pencil, Matcha, Coral, Ocean, Espresso und Midnight färben das ganze Gitter neu.

ENTSPANNEND UND BEFRIEDIGEND
Sanfte Klänge, dezente Vibration (in den Einstellungen abschaltbar) und eine kleine Feier, wenn eine Zeile, Spalte oder ein Block fertig ist.

Kostenlos spielbar mit optionaler Werbung und In-App-Käufen.
</de-DE>

<es-419>
Nueve dígitos, ochenta y una casillas, una sola respuesta correcta… y una pista que te explica por qué.

Sudoku es el clásico rompecabezas numérico, pensado para jugar con calma y concentración. Completa la cuadrícula para que cada fila, columna y caja de 3×3 tenga los dígitos del 1 al 9 una sola vez. Funciona sin conexión.

500 SUDOKUS CLASIFICADOS POR TÉCNICA
La dificultad depende de la lógica que pide cada sudoku:
• Fácil (1–125): solo singles, con muchos números iniciales
• Medio (126–250): pares señaladores, reducción caja/línea, pares desnudos y ocultos
• Difícil (251–375): tríos, cuartetos y X-Wing
• Experto (376–500): XY-Wing, XYZ-Wing y Swordfish
Todos se resuelven solo con lógica.

PISTAS QUE ENSEÑAN
Una pista llena una casilla correcta y nombra la técnica que la encuentra, para que aprendas la jugada y no solo la respuesta.

HERRAMIENTAS CÓMODAS
• Modo notas; al colocar un dígito se borra de las notas cercanas
• Resaltado de fila, columna, caja y dígitos iguales
• Los dígitos en conflicto se marcan al instante
• Deshacer, borrar y un contador de lo que falta en cada tecla
• Tres errores terminan el sudoku; una segunda oportunidad conserva tu tablero
• Cronómetro con tu mejor tiempo en cada dificultad
• Tu tablero se guarda solo: Continuar retoma exactamente donde lo dejaste

UN SUDOKU NUEVO CADA DÍA
El sudoku diario sube de Fácil el lunes a Experto el domingo. Resuélvelo para mantener tu racha y ganar monedas extra. ¿Terminaste la campaña? El modo Infinito reparte tableros nuevos en cualquier dificultad.

SIETE TEMAS DE TABLERO
Ink, Pencil, Matcha, Coral, Ocean, Espresso y Midnight cambian el color de toda la cuadrícula.

RELAJANTE Y SATISFACTORIO
Sonidos suaves, vibración ligera (se apaga en Ajustes) y una pequeña celebración cuando completas una fila, columna o caja.

Gratis, con anuncios opcionales y compras dentro de la app.
</es-419>

<fr-FR>
Neuf chiffres, quatre-vingt-une cases, une seule bonne réponse — et un indice qui vous explique pourquoi.

Sudoku est le casse-tête chiffré classique, fait pour jouer au calme. Remplissez la grille pour que chaque ligne, colonne et bloc 3×3 contienne les chiffres de 1 à 9 une seule fois. Tout fonctionne hors ligne.

500 GRILLES CLASSÉES PAR TECHNIQUE
La difficulté vient de la logique exigée par chaque grille :
• Facile (1–125) : singletons uniquement, grilles bien remplies
• Moyen (126–250) : paires pointantes, réduction bloc/ligne, paires nues et cachées
• Difficile (251–375) : triplets, quadruplets et X-Wing
• Expert (376–500) : XY-Wing, XYZ-Wing et Swordfish
Chaque grille se résout par la seule logique.

DES INDICES QUI ENSEIGNENT
Un indice remplit une case juste et nomme la technique qui la trouve : vous apprenez le coup, pas seulement la réponse.

DES OUTILS AGRÉABLES
• Mode notes ; poser un chiffre l'efface des notes voisines
• Surlignage de la ligne, de la colonne, du bloc et des chiffres identiques
• Les chiffres en conflit s'allument aussitôt
• Annuler, effacer et un compteur de chiffres restants sur chaque touche
• Trois erreurs terminent la grille ; une seconde chance garde votre plateau
• Chronomètre et meilleurs temps pour chaque niveau
• Sauvegarde automatique : Continuer reprend exactement là où vous étiez

UNE NOUVELLE GRILLE CHAQUE JOUR
La grille du jour va de Facile le lundi à Expert le dimanche. Résolvez-la pour prolonger votre série et gagner des pièces bonus. Campagne terminée ? Le mode Infini propose de nouvelles grilles à toute difficulté.

SEPT THÈMES DE GRILLE
Ink, Pencil, Matcha, Coral, Ocean, Espresso et Midnight recolorent toute la grille.

RELAXANT ET SATISFAISANT
Sons doux, vibration légère (désactivable dans les Réglages) et une petite fête quand une ligne, une colonne ou un bloc est complet.

Gratuit, avec publicités facultatives et achats intégrés.
</fr-FR>

<hi-IN>
नौ अंक, इक्यासी खाने, एक ही सही जवाब — और एक संकेत जो बताता है क्यों।

सुडोकू शांत और एकाग्र खेल के लिए क्लासिक संख्या पहेली है। ग्रिड ऐसे भरें कि हर पंक्ति, हर स्तंभ और हर 3×3 बॉक्स में 1 से 9 तक के अंक एक-एक बार आएँ। यह ऑफ़लाइन चलता है।

तकनीक के अनुसार 500 पहेलियाँ
कठिनाई इस बात से तय होती है कि पहेली किस तर्क की माँग करती है:
• आसान (1–125): सिर्फ़ सिंगल, ज़्यादा शुरुआती अंक
• मध्यम (126–250): पॉइंटिंग पेयर, बॉक्स/लाइन रिडक्शन, नेकेड और हिडन पेयर
• कठिन (251–375): ट्रिपल, क्वाड और X-Wing
• विशेषज्ञ (376–500): XY-Wing, XYZ-Wing और Swordfish
हर पहेली सिर्फ़ तर्क से हल होती है।

सिखाने वाले संकेत
संकेत एक सही खाना भरता है और वह तकनीक बताता है जिससे वह मिला, ताकि आप सिर्फ़ जवाब नहीं, चाल भी सीखें।

आरामदायक टूल
• नोट्स मोड; अंक रखते ही आसपास के नोट्स से हट जाता है
• चुनी हुई पंक्ति, स्तंभ, बॉक्स और एक जैसे अंक हाइलाइट
• टकराने वाले अंक तुरंत चमकते हैं
• अनडू, मिटाएँ और हर बटन पर बचे अंकों की गिनती
• तीन गलतियों पर पहेली खत्म; दूसरा मौका आपका बोर्ड बचाता है
• हर कठिनाई के लिए सबसे अच्छा समय दिखाने वाला टाइमर
• बोर्ड अपने-आप सेव होता है: Continue ठीक वहीं से शुरू करता है

हर दिन नई पहेली
दैनिक पहेली सोमवार को आसान से रविवार को विशेषज्ञ तक जाती है। स्ट्रीक बढ़ाने और बोनस सिक्के पाने के लिए हल करें। अभियान पूरा? एंडलेस मोड हर कठिनाई में नए बोर्ड देता है।

सात बोर्ड थीम
Ink, Pencil, Matcha, Coral, Ocean, Espresso और Midnight पूरे ग्रिड का रंग बदल देते हैं।

सुकूनभरा और संतोषजनक
मुलायम आवाज़ें, हल्का वाइब्रेशन (सेटिंग्स में बंद करें) और पंक्ति, स्तंभ या बॉक्स पूरा होने पर छोटा जश्न।

मुफ़्त, वैकल्पिक विज्ञापनों और इन-ऐप खरीदारी के साथ।
</hi-IN>

<id>
Sembilan angka, delapan puluh satu sel, satu jawaban benar — dan petunjuk yang menjelaskan alasannya.

Sudoku adalah teka-teki angka klasik untuk bermain dengan tenang dan fokus. Isi kisi agar setiap baris, kolom, dan kotak 3×3 berisi angka 1 sampai 9 tepat satu kali. Bisa dimainkan offline.

500 TEKA-TEKI MENURUT TEKNIK
Kesulitan ditentukan oleh logika yang dibutuhkan:
• Mudah (1–125): hanya single, banyak angka awal
• Sedang (126–250): pointing pair, reduksi kotak/garis, pasangan terbuka dan tersembunyi
• Sulit (251–375): triple, quad, dan X-Wing
• Ahli (376–500): XY-Wing, XYZ-Wing, dan Swordfish
Setiap teka-teki bisa diselesaikan hanya dengan logika.

PETUNJUK YANG MENGAJAR
Petunjuk mengisi satu sel yang benar dan menyebut teknik yang menemukannya, jadi kamu belajar langkahnya, bukan sekadar jawabannya.

ALAT YANG NYAMAN
• Mode catatan; angka yang ditempatkan otomatis hilang dari catatan sekitar
• Sorotan baris, kolom, kotak, dan angka yang sama
• Angka yang bentrok langsung menyala
• Urungkan, hapus, dan hitungan sisa di setiap tombol angka
• Tiga kesalahan mengakhiri teka-teki; kesempatan kedua menyimpan papanmu
• Pengatur waktu dengan waktu terbaik tiap tingkat
• Papan tersimpan otomatis: Lanjutkan tepat dari tempat kamu berhenti

TEKA-TEKI BARU SETIAP HARI
Teka-teki harian naik dari Mudah di hari Senin sampai Ahli di hari Minggu. Selesaikan untuk menjaga runtutan dan dapatkan koin bonus. Kampanye selesai? Mode Tanpa Akhir menyajikan papan baru di semua tingkat.

TUJUH TEMA PAPAN
Ink, Pencil, Matcha, Coral, Ocean, Espresso, dan Midnight mengubah warna seluruh kisi.

SANTAI DAN MEMUASKAN
Suara lembut, getaran halus (bisa dimatikan di Setelan), dan perayaan kecil setiap kali baris, kolom, atau kotak lengkap.

Gratis dengan iklan opsional dan pembelian dalam aplikasi.
</id>

<it-IT>
Nove cifre, ottantuno caselle, una sola risposta giusta — e un suggerimento che ti spiega perché.

Sudoku è il classico rompicapo numerico, pensato per giocare con calma e concentrazione. Completa la griglia in modo che ogni riga, colonna e riquadro 3×3 contenga le cifre da 1 a 9 una sola volta. Funziona offline.

500 SUDOKU CLASSIFICATI PER TECNICA
La difficoltà dipende dalla logica che ogni sudoku richiede:
• Facile (1–125): solo singoli, con molti numeri iniziali
• Medio (126–250): coppie puntanti, riduzione riquadro/linea, coppie nude e nascoste
• Difficile (251–375): triple, quaterne e X-Wing
• Esperto (376–500): XY-Wing, XYZ-Wing e Swordfish
Ogni sudoku si risolve con la sola logica.

SUGGERIMENTI CHE INSEGNANO
Un suggerimento riempie una casella corretta e nomina la tecnica che la trova: impari la mossa, non solo la risposta.

STRUMENTI COMODI
• Modalità note; inserire una cifra la toglie dalle note vicine
• Evidenziazione di riga, colonna, riquadro e cifre uguali
• Le cifre in conflitto si accendono subito
• Annulla, cancella e un contatore delle cifre mancanti su ogni tasto
• Tre errori chiudono il sudoku; una seconda possibilità salva la griglia
• Cronometro con il tuo tempo migliore per ogni livello
• Salvataggio automatico: Continua riprende esattamente da dove eri

UN NUOVO SUDOKU OGNI GIORNO
Il sudoku del giorno sale da Facile il lunedì a Esperto la domenica. Risolvilo per allungare la serie e guadagnare monete bonus. Campagna finita? La modalità Infinita offre nuove griglie a ogni difficoltà.

SETTE TEMI DELLA GRIGLIA
Ink, Pencil, Matcha, Coral, Ocean, Espresso e Midnight ricolorano tutta la griglia.

RILASSANTE E APPAGANTE
Suoni morbidi, vibrazione leggera (si disattiva nelle Impostazioni) e una piccola festa quando completi una riga, una colonna o un riquadro.

Gratis, con pubblicità facoltativa e acquisti in-app.
</it-IT>

<ja-JP>
9つの数字、81のマス、正解はひとつ。そして「なぜそうなるか」を教えてくれるヒント。

数独は、落ち着いて集中できる定番の数字パズルです。すべての行・列・3×3のブロックに1〜9の数字が1回ずつ入るように盤面を埋めましょう。オフラインで遊べます。

解法テクニックで分けた500問
難易度は、問題が必要とする論理で決まります。
• やさしい（1〜125）：シングルのみ、ヒント数字が多め
• ふつう（126〜250）：ポインティングペア、ボックス/ライン、ネイキッド/ヒドゥンペア
• むずかしい（251〜375）：トリプル、クアッド、X-Wing
• エキスパート（376〜500）：XY-Wing、XYZ-Wing、Swordfish
どの問題も論理だけで解けます。

学べるヒント
ヒントは正しいマスを1つ埋め、それを見つける手筋の名前を表示します。答えだけでなく、解き方が身につきます。

使いやすい機能
• メモモード：数字を置くと周りのメモから自動で消去
• 選んだ行・列・ブロックと同じ数字をハイライト
• 矛盾する数字はすぐに表示
• 元に戻す、消去、各キーに残り個数を表示
• ミス3回で終了、セカンドチャンスで盤面を保持
• 難易度ごとのベストタイムを記録するタイマー
• 盤面は自動保存。「続ける」で中断したところから再開

毎日の新しい一題
デイリー問題は月曜の「やさしい」から日曜の「エキスパート」まで難しくなります。解いて連続記録を伸ばし、ボーナスコインを獲得しましょう。キャンペーンを終えたら、エンドレスモードで好きな難易度の新しい盤面に挑戦できます。

7種類の盤面テーマ
Ink、Pencil、Matcha、Coral、Ocean、Espresso、Midnight が盤面全体の色を変えます。

癒やされる手ごたえ
やさしい効果音、控えめなバイブ（設定でオフ可能）、行・列・ブロックがそろうたびの小さなお祝い。

基本プレイ無料。任意の広告とアプリ内購入があります。
</ja-JP>

<pt-BR>
Nove dígitos, oitenta e uma casas, uma única resposta certa — e uma dica que explica o porquê.

Sudoku é o clássico quebra-cabeça numérico, feito para jogar com calma e foco. Preencha a grade para que cada linha, coluna e caixa 3×3 tenha os dígitos de 1 a 9 uma única vez. Funciona offline.

500 SUDOKUS CLASSIFICADOS POR TÉCNICA
A dificuldade vem da lógica que cada sudoku exige:
• Fácil (1–125): só singles, com muitos números iniciais
• Médio (126–250): pares apontadores, redução caixa/linha, pares nus e ocultos
• Difícil (251–375): trios, quartetos e X-Wing
• Especialista (376–500): XY-Wing, XYZ-Wing e Swordfish
Todos podem ser resolvidos só com lógica.

DICAS QUE ENSINAM
Uma dica preenche uma casa correta e diz qual técnica a encontra, para você aprender a jogada e não só a resposta.

FERRAMENTAS CONFORTÁVEIS
• Modo notas; ao colocar um dígito ele some das notas vizinhas
• Destaque da linha, coluna, caixa e dos dígitos iguais
• Dígitos em conflito acendem na hora
• Desfazer, apagar e um contador do que falta em cada tecla
• Três erros encerram o sudoku; uma segunda chance mantém seu tabuleiro
• Cronômetro com seu melhor tempo em cada dificuldade
• Seu tabuleiro é salvo sozinho: Continuar volta exatamente de onde parou

UM SUDOKU NOVO TODO DIA
O sudoku diário vai de Fácil na segunda a Especialista no domingo. Resolva para manter sua sequência e ganhar moedas bônus. Terminou a campanha? O modo Infinito traz tabuleiros novos em qualquer dificuldade.

SETE TEMAS DE TABULEIRO
Ink, Pencil, Matcha, Coral, Ocean, Espresso e Midnight mudam a cor de toda a grade.

RELAXANTE E SATISFATÓRIO
Sons suaves, vibração leve (desliga em Configurações) e uma pequena comemoração quando você completa uma linha, coluna ou caixa.

Grátis, com anúncios opcionais e compras no app.
</pt-BR>

<tr-TR>
Dokuz rakam, seksen bir hücre, tek bir doğru cevap — ve nedenini anlatan bir ipucu.

Sudoku, sakin ve odaklı oynamak için klasik sayı bulmacasıdır. Her satır, sütun ve 3×3 kutuda 1'den 9'a kadar rakamlar birer kez olacak şekilde ızgarayı doldur. İnternetsiz çalışır.

TEKNİĞE GÖRE DERECELENMİŞ 500 BULMACA
Zorluk, bulmacanın istediği mantıktan gelir:
• Kolay (1–125): sadece tekiller, bol başlangıç rakamı
• Orta (126–250): işaret eden çiftler, kutu/çizgi eleme, açık ve gizli çiftler
• Zor (251–375): üçlüler, dörtlüler ve X-Wing
• Uzman (376–500): XY-Wing, XYZ-Wing ve Swordfish
Her bulmaca yalnızca mantıkla çözülebilir.

ÖĞRETEN İPUÇLARI
Bir ipucu doğru bir hücreyi doldurur ve onu bulan tekniğin adını söyler; sadece cevabı değil, hamleyi de öğrenirsin.

RAHAT ARAÇLAR
• Not modu; bir rakam yerleşince çevredeki notlardan silinir
• Seçili satır, sütun, kutu ve aynı rakamlar vurgulanır
• Çakışan rakamlar anında yanar
• Geri al, sil ve her tuşta kalan rakam sayısı
• Üç hata bulmacayı bitirir; ikinci şans tahtanı korur
• Her zorluk için en iyi süre tutan zamanlayıcı
• Tahtan otomatik kaydedilir: Devam tam kaldığın yerden sürer

HER GÜN YENİ BİR BULMACA
Günlük bulmaca pazartesi Kolay'dan pazar Uzman'a yükselir. Serini büyütmek ve bonus jeton kazanmak için çöz. Kampanyayı bitirdin mi? Sonsuz mod her zorlukta yeni tahtalar getirir.

YEDİ TAHTA TEMASI
Ink, Pencil, Matcha, Coral, Ocean, Espresso ve Midnight tüm ızgaranın rengini değiştirir.

RAHATLATICI VE TATMİN EDİCİ
Yumuşak sesler, hafif titreşim (Ayarlar'dan kapatılabilir) ve bir satır, sütun ya da kutu tamamlandığında küçük bir kutlama.

Ücretsiz; isteğe bağlı reklamlar ve uygulama içi satın alımlar içerir.
</tr-TR>

<uk>
Дев'ять цифр, вісімдесят одна клітинка, одна правильна відповідь — і підказка, яка пояснює чому.

Судоку — класична числова головоломка для спокійної, зосередженої гри. Заповніть сітку так, щоб у кожному рядку, стовпці та квадраті 3×3 цифри від 1 до 9 трапилися рівно один раз. Гра працює офлайн.

500 ГОЛОВОЛОМОК ЗА ТЕХНІКАМИ
Складність визначає логіка, якої потребує головоломка:
• Легко (1–125): лише одиночки, багато початкових цифр
• Середньо (126–250): вказівні пари, квадрат/лінія, відкриті й приховані пари
• Складно (251–375): трійки, четвірки та X-Wing
• Експерт (376–500): XY-Wing, XYZ-Wing і Swordfish
Кожну головоломку можна розв'язати лише логікою.

ПІДКАЗКИ, ЩО НАВЧАЮТЬ
Підказка заповнює правильну клітинку й називає техніку, яка її знаходить, — ви вивчаєте хід, а не лише відповідь.

ЗРУЧНІ ІНСТРУМЕНТИ
• Режим нотаток; поставлена цифра зникає з нотаток поруч
• Підсвічування рядка, стовпця, квадрата й однакових цифр
• Конфліктні цифри підсвічуються одразу
• Скасування, стирання й лічильник залишку на кожній клавіші
• Три помилки завершують головоломку; другий шанс зберігає поле
• Таймер із найкращим часом для кожного рівня
• Поле зберігається автоматично: «Продовжити» повертає туди, де ви зупинилися

НОВА ГОЛОВОЛОМКА ЩОДНЯ
Щоденна головоломка ускладнюється від «Легко» в понеділок до «Експерт» у неділю. Розв'язуйте, щоб продовжувати серію й отримувати бонусні монети. Пройшли кампанію? Нескінченний режим дає нові поля будь-якої складності.

СІМ ТЕМ ПОЛЯ
Ink, Pencil, Matcha, Coral, Ocean, Espresso і Midnight перефарбовують усю сітку.

СПОКІЙНО Й ПРИЄМНО
М'які звуки, легка вібрація (вимикається в налаштуваннях) і маленьке свято, коли заповнено рядок, стовпець чи квадрат.

Безкоштовно, з необов'язковою рекламою та покупками в застосунку.
</uk>

<zh-CN>
九个数字，八十一个格子，只有一个正确答案——还有告诉你原因的提示。

数独是经典的数字谜题，适合安静专注地游玩。填满棋盘，让每一行、每一列和每个3×3宫都恰好包含1到9各一次。支持离线游玩。

按技巧分级的500道谜题
难度取决于谜题需要的逻辑：
• 简单（1–125）：只需唯一数，初始数字较多
• 中等（126–250）：区块摒除、行列摒除、显性与隐性数对
• 困难（251–375）：三数组、四数组与X-Wing
• 专家（376–500）：XY-Wing、XYZ-Wing与Swordfish
每道题都能只靠逻辑解开。

会教人的提示
提示会填入一个正确格，并说出找到它的技巧，让你学会方法，而不只是答案。

顺手的工具
• 笔记模式；填入数字后会自动从周围笔记中删除
• 高亮所选行、列、宫以及相同数字
• 冲突数字即时标出
• 撤销、擦除，每个数字键显示剩余数量
• 错三次结束本局；第二次机会保留你的棋盘
• 计时器记录每个难度的最佳时间
• 棋盘自动保存，“继续”准确回到你离开的地方

每天一道新谜题
每日谜题从周一的简单逐步升到周日的专家。完成即可延续连胜并获得额外金币。通关战役后，无尽模式可在任意难度带来新棋盘。

七款棋盘主题
Ink、Pencil、Matcha、Coral、Ocean、Espresso与Midnight会改变整个棋盘的配色。

轻松又满足
柔和音效、轻微振动（可在设置中关闭），每完成一行、一列或一宫都有小小的庆祝。

免费游玩，含可选广告与应用内购买。
</zh-CN>

---

## SUBTITLE (≤30 chars per locale)

_Apple App Store Connect → App Information → Subtitle_

<en-US>
Graded logic, daily puzzles
</en-US>

<ar>
منطق متدرّج وألغاز يومية
</ar>

<de-DE>
Logik nach Technik, täglich
</de-DE>

<es-419>
Lógica por técnica, cada día
</es-419>

<fr-FR>
Logique graduée, défi du jour
</fr-FR>

<hi-IN>
तकनीक से कठिनाई, रोज़ पहेली
</hi-IN>

<id>
Logika bertingkat, tiap hari
</id>

<it-IT>
Logica a tecniche, ogni giorno
</it-IT>

<ja-JP>
解法で難易度分け・毎日の一題
</ja-JP>

<pt-BR>
Lógica por técnica, todo dia
</pt-BR>

<tr-TR>
Tekniğe göre zorluk, her gün
</tr-TR>

<uk>
Логіка за техніками, щодня
</uk>

<zh-CN>
按解题技巧分级 · 每日一题
</zh-CN>

---

## KEYWORDS (≤100 chars per locale)

_Apple App Store Connect → Version → Keywords_

<en-US>
sudoku,number puzzle,logic puzzle,brain game,daily sudoku,offline,classic,relaxing,9x9,notes
</en-US>

<ar>
سودوكو,لغز أرقام,ألغاز منطق,ألعاب ذكاء,سودوكو يومي,بدون إنترنت,كلاسيكي,مريح
</ar>

<de-DE>
sudoku,zahlenrätsel,logikrätsel,denkspiel,gehirnjogging,offline,klassisch,entspannend,täglich
</de-DE>

<es-419>
sudoku,rompecabezas numérico,lógica,juego mental,sudoku diario,sin conexión,clásico,relajante
</es-419>

<fr-FR>
sudoku,casse-tête,logique,jeu de chiffres,sudoku du jour,hors ligne,classique,relaxant,grille
</fr-FR>

<hi-IN>
सुडोकू,sudoku,संख्या पहेली,तर्क पहेली,दिमागी खेल,दैनिक सुडोकू,ऑफ़लाइन,क्लासिक
</hi-IN>

<id>
sudoku,teka-teki angka,logika,asah otak,sudoku harian,offline,klasik,santai,9x9
</id>

<it-IT>
sudoku,rompicapo numerico,logica,giochi mentali,sudoku del giorno,offline,classico,rilassante
</it-IT>

<ja-JP>
数独,ナンプレ,sudoku,パズル,脳トレ,ロジック,オフライン,毎日,クラシック
</ja-JP>

<pt-BR>
sudoku,quebra-cabeça numérico,lógica,jogo de raciocínio,sudoku diário,offline,clássico,relaxante
</pt-BR>

<tr-TR>
sudoku,sayı bulmacası,mantık,zeka oyunu,günlük sudoku,çevrimdışı,klasik,rahatlatıcı,9x9
</tr-TR>

<uk>
судоку,sudoku,числова головоломка,логіка,тренування мозку,щоденне судоку,офлайн,класика
</uk>

<zh-CN>
数独,sudoku,数字谜题,逻辑,益智,脑力训练,每日数独,离线,经典
</zh-CN>

---

## PROMOTIONAL TEXT (≤170 chars per locale)

_Apple App Store Connect → Version → Promotional Text_

<en-US>
Four difficulty bands graded by solving technique, a new Daily puzzle every day and hints that name the move. Relaxing, offline, 500 puzzles.
</en-US>

<ar>
أربعة مستويات مصنّفة حسب تقنية الحل، ولغز يومي جديد كل يوم، وتلميحات تذكر اسم الخطوة. مريحة وتعمل دون اتصال، 500 لغز.
</ar>

<de-DE>
Vier Schwierigkeitsstufen nach Lösungstechnik, jeden Tag ein neues Tagesrätsel und Tipps, die den Zug benennen. Entspannend, offline, 500 Rätsel.
</de-DE>

<es-419>
Cuatro niveles clasificados por técnica de resolución, un sudoku diario nuevo y pistas que nombran la jugada. Relajante, sin conexión, 500 sudokus.
</es-419>

<fr-FR>
Quatre niveaux classés par technique de résolution, une nouvelle grille du jour chaque jour et des indices qui nomment le coup. Relaxant, hors ligne.
</fr-FR>

<hi-IN>
हल करने की तकनीक के अनुसार चार स्तर, हर दिन नई दैनिक पहेली और चाल का नाम बताने वाले संकेत। सुकूनभरा, ऑफ़लाइन, 500 पहेलियाँ।
</hi-IN>

<id>
Empat tingkat kesulitan menurut teknik penyelesaian, teka-teki harian baru setiap hari, dan petunjuk yang menyebut nama langkahnya. Santai, offline.
</id>

<it-IT>
Quattro livelli classificati per tecnica risolutiva, un nuovo sudoku del giorno ogni giorno e suggerimenti che nominano la mossa. Rilassante, offline.
</it-IT>

<ja-JP>
解法テクニックで分けた4段階の難易度、毎日新しいデイリー問題、手筋の名前を教えるヒント。オフラインでじっくり楽しめる500問。
</ja-JP>

<pt-BR>
Quatro níveis classificados por técnica de resolução, um novo sudoku diário todo dia e dicas que dizem o nome da jogada. Relaxante, offline, 500 sudokus.
</pt-BR>

<tr-TR>
Çözüm tekniğine göre dört zorluk seviyesi, her gün yeni bir günlük bulmaca ve hamlenin adını söyleyen ipuçları. Rahatlatıcı, çevrimdışı, 500 bulmaca.
</tr-TR>

<uk>
Чотири рівні складності за техніками розв'язання, нова щоденна головоломка щодня й підказки, що називають хід. Спокійно, офлайн, 500 головоломок.
</uk>

<zh-CN>
按解题技巧划分的四个难度、每天一道新的每日谜题，以及说出技巧名称的提示。轻松解压，支持离线，共500题。
</zh-CN>

---
