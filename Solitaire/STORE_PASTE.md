# Solitaire — store paste sheet

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
Solitaire 2.0 is a complete rebuild:
• 500 numbered draw-1 deals, each verified winnable by a solver
• Hint shows the next move of a winning line from where you are
• Tap a card to send it to its best spot, or drag to choose
• Free undo, auto-finish once every card is face-up
• A Daily Deal for everyone, easy early in the week, hard at the weekend
• Random deals in draw 1 or draw 3
• Seven table themes, left-handed layout and four-colour suits
</en-US>

<ar>
أُعيد بناء Solitaire 2.0 بالكامل:
• 500 توزيعة مرقّمة (سحب ورقة واحدة)، تحقّق محلّل من أن كل واحدة قابلة للفوز
• التلميح يُظهر النقلة التالية من خط فوز انطلاقًا من موضعك
• المس ورقة لتنتقل إلى أفضل مكان لها، أو اسحبها بنفسك
• تراجع مجاني وإنهاء تلقائي عندما تنكشف كل الأوراق
• توزيعة يومية للجميع: سهلة في بداية الأسبوع وصعبة في عطلته
• توزيعات عشوائية بسحب ورقة أو ثلاث
• سبعة أنماط للطاولة ووضع لليد اليسرى ورموز بأربعة ألوان
</ar>

<de-DE>
Solitaire 2.0 ist komplett neu gebaut:
• 500 nummerierte Partien (1 Karte ziehen), jede per Solver als lösbar geprüft
• Der Tipp zeigt den nächsten Zug eines Lösungswegs ab deiner Stellung
• Antippen schickt die Karte an den besten Platz, oder zieh sie selbst
• Gratis Rückgängig, Auto-Abschluss, wenn alle Karten offen liegen
• Ein Tagesspiel für alle: leicht zum Wochenstart, schwer am Wochenende
• Zufallspartien mit 1 oder 3 Karten
• Sieben Tischthemen, Linkshänder-Layout, Vierfarben-Symbole
</de-DE>

<es-419>
Solitaire 2.0 se rehízo por completo:
• 500 partidas numeradas (robar 1), todas verificadas como ganables
• La pista muestra el siguiente paso de una línea ganadora desde tu posición
• Toca una carta y va a su mejor lugar, o arrástrala
• Deshacer gratis y final automático con todas las cartas a la vista
• Partida diaria para todos: fácil a inicio de semana, difícil el finde
• Partidas al azar con robar 1 o robar 3
• Siete temas de mesa, modo zurdo y palos de cuatro colores
</es-419>

<fr-FR>
Solitaire 2.0 est entièrement reconstruit :
• 500 donnes numérotées (pioche 1), toutes vérifiées gagnables
• L'indice montre le coup suivant d'une ligne gagnante depuis votre position
• Touchez une carte pour l'envoyer au meilleur endroit, ou glissez-la
• Annulation gratuite, fin automatique quand tout est découvert
• Donne du jour pour tous : facile en début de semaine, dure le week-end
• Donnes aléatoires en pioche 1 ou pioche 3
• Sept thèmes de table, mode gaucher et couleurs à quatre teintes
</fr-FR>

<hi-IN>
Solitaire 2.0 पूरी तरह नए सिरे से बना है:
• 500 नंबर वाली डील (1 पत्ता खींचें), हर एक सॉल्वर से जीतने योग्य जाँची गई
• संकेत आपकी स्थिति से जीत की राह की अगली चाल दिखाता है
• पत्ते पर टैप करें, वह सबसे अच्छी जगह जाएगा; या खुद खींचें
• मुफ़्त पूर्ववत, सब पत्ते खुलते ही अपने आप पूरा
• सबके लिए एक डेली डील: हफ़्ते की शुरुआत में आसान, सप्ताहांत में कठिन
• 1 या 3 पत्ते खींचने वाली रैंडम डील
• सात टेबल थीम, बाएँ हाथ वाला लेआउट और चार रंगों के सूट
</hi-IN>

<id>
Solitaire 2.0 dibangun ulang sepenuhnya:
• 500 deal bernomor (ambil 1), masing-masing diverifikasi bisa dimenangkan oleh solver
• Petunjuk menunjukkan langkah berikutnya dari jalur menang dari posisimu
• Ketuk kartu agar pindah ke tempat terbaik, atau seret sendiri
• Urungkan gratis, selesai otomatis begitu semua kartu terbuka
• Deal Harian untuk semua: mudah di awal pekan, sulit di akhir pekan
• Deal acak dengan ambil 1 atau ambil 3
• Tujuh tema meja, tata letak kidal, dan simbol empat warna
</id>

<it-IT>
Solitaire 2.0 è stato ricostruito da zero:
• 500 smazzate numerate (pesca 1), tutte verificate vincibili
• L'aiuto mostra la mossa successiva di una linea vincente dalla tua posizione
• Tocca una carta e va al posto migliore, oppure trascinala
• Annulla gratis e chiusura automatica a carte tutte scoperte
• Smazzata del giorno per tutti: facile a inizio settimana, dura nel weekend
• Smazzate casuali con pesca 1 o pesca 3
• Sette temi del tavolo, modalità mancini e semi a quattro colori
</it-IT>

<ja-JP>
Solitaire 2.0 を全面的に作り直しました：
• 500の番号付きディール（1枚めくり）。すべてソルバーで勝てることを確認済み
• ヒントは今の局面から勝ち筋の次の一手を表示
• カードをタップで最適な場所へ、ドラッグで好きな場所へ
• 取り消しは無料、全カードが表になると自動で仕上げ
• 全員共通のデイリーディール：週の初めはやさしく、週末は手ごわく
• 1枚めくり・3枚めくりのランダムディール
• 7種類のテーブルテーマ、左利きレイアウト、4色スート
</ja-JP>

<pt-BR>
O Solitaire 2.0 foi refeito do zero:
• 500 partidas numeradas (comprar 1), todas verificadas como vencíveis
• A dica mostra o próximo lance de uma linha vencedora a partir da sua posição
• Toque numa carta e ela vai ao melhor lugar, ou arraste
• Desfazer grátis e final automático com todas as cartas viradas
• Partida diária para todos: fácil no começo da semana, difícil no fim
• Partidas aleatórias com comprar 1 ou comprar 3
• Sete temas de mesa, modo canhoto e naipes em quatro cores
</pt-BR>

<tr-TR>
Solitaire 2.0 baştan yeniden yapıldı:
• 500 numaralı el (1 kart çek), her biri bir çözücüyle kazanılabilir olarak doğrulandı
• İpucu, bulunduğun konumdan kazanan bir yolun sıradaki hamlesini gösterir
• Karta dokun, en iyi yerine gitsin; ya da sürükle
• Ücretsiz geri al, tüm kartlar açılınca otomatik bitiş
• Herkese aynı günlük el: hafta başı kolay, hafta sonu zor
• 1 veya 3 kart çekmeli rastgele eller
• Yedi masa teması, solak düzeni ve dört renkli takımlar
</tr-TR>

<uk>
Solitaire 2.0 повністю перебудовано:
• 500 пронумерованих роздач (по 1 карті), кожну розв'язувач перевірив на виграшність
• Підказка показує наступний хід виграшної лінії з вашої позиції
• Торкніться карти, і вона полетить на найкраще місце, або перетягніть її
• Безкоштовне скасування й автозавершення, щойно всі карти відкриті
• Щоденна роздача для всіх: легка на початку тижня, складна у вихідні
• Випадкові роздачі по 1 або по 3 карти
• Сім тем столу, режим для лівші й чотириколірні масті
</uk>

<zh-CN>
Solitaire 2.0 全面重制：
• 500 局编号牌局（翻一张），每局都经求解器验证可以获胜
• 提示从你当前的局面给出制胜路线的下一步
• 点按纸牌即可送到最佳位置，也可以自己拖动
• 免费撤销，所有纸牌翻开后自动收尾
• 人人相同的每日牌局：周初简单，周末更难
• 翻一张或翻三张的随机牌局
• 七款牌桌主题、左手布局和四色花色
</zh-CN>

---

## SHORT DESCRIPTION (≤80 chars per locale)

_Grow → Store presence → Main store listing → Short description_

<en-US>
Classic Klondike: 500 deals, every one winnable, a Daily Deal and honest hints.
</en-US>

<ar>
كلوندايك الكلاسيكية: 500 توزيعة قابلة للفوز وتوزيعة يومية وتلميحات صادقة.
</ar>

<de-DE>
Klassisches Klondike: 500 lösbare Partien, ein Tagesspiel und ehrliche Tipps.
</de-DE>

<es-419>
Klondike clásico: 500 partidas ganables, una partida diaria y pistas reales.
</es-419>

<fr-FR>
Klondike classique : 500 donnes gagnables, donne du jour et indices fiables.
</fr-FR>

<hi-IN>
क्लासिक क्लोंडाइक: 500 डील, हर एक जीतने योग्य, डेली डील और सच्चे संकेत।
</hi-IN>

<id>
Klondike klasik: 500 deal, semuanya bisa dimenangkan, Deal Harian, dan petunjuk.
</id>

<it-IT>
Klondike classico: 500 smazzate vincibili, la smazzata del giorno e aiuti veri.
</it-IT>

<ja-JP>
定番のクロンダイク：500ディールすべて勝てる配り、毎日のデイリー、確かなヒント。
</ja-JP>

<pt-BR>
Klondike clássico: 500 partidas vencíveis, partida diária e dicas de verdade.
</pt-BR>

<tr-TR>
Klasik Klondike: 500 el, hepsi kazanılabilir, günlük el ve gerçek ipuçları.
</tr-TR>

<uk>
Класичний Klondike: 500 роздач, кожну можна виграти, щоденна роздача й підказки.
</uk>

<zh-CN>
经典克朗代克：500 局每局都能赢、每日一局，还有真正有用的提示。
</zh-CN>

---

## FULL DESCRIPTION (≤4000 chars per locale)

_Grow → Store presence → Main store listing → Full description_

<en-US>
Turn the last card, watch four Kings land, and see the whole deck cascade off the table.

Solitaire is classic Klondike, built for calm, unhurried play. Build the four foundations from Ace to King by suit, and stack the tableau down in alternating colours: red 6 on black 7. Only a King can fill an empty column. It works offline, so a quiet game is always in your pocket.

500 DEALS, EVERY ONE WINNABLE
Each numbered deal is dealt from a fixed seed and comes with a winning line found by a solver, and every one is re-checked by replaying that line to four complete foundations. Stuck? Undo a few moves and try another road: every numbered deal can be won from its first card. The deals run from quick openers to long, patient games.

HINTS FROM A WINNING LINE
Hint highlights the card to move and where it goes. It follows a winning line from your current position whenever the solver finds one, and says so plainly when it can't.

PLAYS THE WAY YOU EXPECT
• Tap a card and it jumps to its best spot, or drag it exactly where you want
• Move whole runs between columns
• Free undo and a one-tap restart
• Auto-finish sends every card home once the whole tableau is face-up
• Moves, classic score and a timer; three stars for winning at or under par
• Big, readable cards on phones and tablets
• Left-handed layout and four-colour suits in Settings

A DAILY DEAL FOR EVERYONE
One winnable deal a day, the same for every player: easier early in the week, harder at the weekend. Win it to build a streak and earn bonus coins.

RANDOM DEALS, DRAW 1 OR DRAW 3
Want a fresh shuffle? Random Deal shuffles a brand-new board in draw 1 or the harder draw 3. Not every random shuffle can be won, which is part of the fun. Random deals use a life; numbered deals and the Daily Deal are always free.

SEVEN TABLE THEMES
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite and Midnight each change the table and the card backs. Unlock them by winning deals, or Midnight with coins.

RELAXING AND SATISFYING
Soft card sounds, a gentle buzz when a card lands (switch it off in Settings) and a bouncing cascade every time you win. A good brain break for a coffee or a commute.

Free to play with optional ads and in-app purchases. The Season Pass removes ads, adds daily coins, unlocks every theme and gives unlimited hints.
</en-US>

<ar>
اقلب الورقة الأخيرة، وشاهد الملوك الأربعة تستقر، ثم الرزمة كلها تتقافز خارج الطاولة.

Solitaire هي لعبة كلوندايك الكلاسيكية، مصممة للعب الهادئ دون استعجال. ابنِ الأكوام الأساسية الأربعة من الآس إلى الملك حسب النوع، ورتّب الأعمدة تنازليًا بألوان متبادلة: 6 حمراء فوق 7 سوداء. لا يملأ العمود الفارغ إلا ملك. تعمل اللعبة بدون إنترنت، فتبقى معك جولة هادئة في كل مكان.

500 توزيعة، كلها قابلة للفوز
تُوزَّع كل توزيعة مرقّمة من بذرة ثابتة، ومعها خط فوز وجده محلّل. ويُعاد فحص كل واحدة بإعادة لعب ذلك الخط حتى تكتمل الأكوام الأساسية الأربعة. علقت؟ تراجع بضع نقلات وجرّب طريقًا آخر: كل توزيعة مرقّمة يمكن الفوز بها من أول ورقة. تتدرج التوزيعات من بدايات سريعة إلى جولات طويلة تحتاج الصبر.

تلميحات من خط فوز
يُبرز التلميح الورقة التي تُنقل ووجهتها. وهو يتبع خط فوز من موضعك الحالي كلما وجد المحلّل واحدًا، ويخبرك بوضوح عندما لا يجد.

تُلعب كما تتوقع
• المس ورقة فتقفز إلى أفضل مكان، أو اسحبها إلى حيث تريد بالضبط
• انقل سلاسل كاملة بين الأعمدة
• تراجع مجاني وإعادة بدء بلمسة واحدة
• إنهاء تلقائي: تعود كل الأوراق إلى أماكنها حين تنكشف الطاولة كلها
• عدد النقلات ونقاط كلاسيكية ومؤقت؛ ثلاث نجوم عند الفوز ضمن المعدل أو أقل
• أوراق كبيرة وواضحة على الهاتف والجهاز اللوحي
• وضع اليد اليسرى ورموز بأربعة ألوان في الإعدادات

توزيعة يومية للجميع
توزيعة قابلة للفوز كل يوم، هي نفسها لكل اللاعبين: أسهل في بداية الأسبوع وأصعب في عطلته. فُز بها لتمدّ سلسلتك وتكسب عملات إضافية.

توزيعات عشوائية: سحب 1 أو 3
تريد خلطًا جديدًا؟ التوزيعة العشوائية تخلط طاولة جديدة تمامًا بسحب ورقة واحدة أو بسحب ثلاث الأصعب. ليست كل خلطة عشوائية قابلة للفوز، وهذا جزء من المتعة. التوزيعات العشوائية تستهلك حياة؛ أما المرقّمة واليومية فمجانية دائمًا.

سبعة أنماط للطاولة
Sea Glass وClubhouse Baize وHarbor وDesert Sand وVelvet وGraphite وMidnight تغيّر الطاولة وظهر الأوراق. افتحها بالفوز بالتوزيعات، وMidnight بالعملات.

مريحة وممتعة
أصوات أوراق ناعمة، واهتزاز خفيف عندما تستقر الورقة (يمكن إيقافه من الإعدادات)، وشلال أوراق متقافزة مع كل فوز. استراحة جميلة للعقل مع القهوة أو في الطريق.

مجانية مع إعلانات ومشتريات داخل التطبيق اختيارية. يزيل Season Pass الإعلانات، ويضيف عملات يومية، ويفتح كل الأنماط، ويمنح تلميحات غير محدودة.
</ar>

<de-DE>
Die letzte Karte umdrehen, vier Könige landen sehen – und dann tanzt das ganze Deck vom Tisch.

Solitaire ist klassisches Klondike für ruhiges, entspanntes Spielen. Baue die vier Ablagestapel nach Farbe vom Ass bis zum König auf und lege im Tableau absteigend mit wechselnden Farben an: rote 6 auf schwarze 7. Nur ein König darf eine leere Spalte füllen. Alles funktioniert offline, so hast du immer eine ruhige Partie dabei.

500 PARTIEN, JEDE LÖSBAR
Jede nummerierte Partie wird aus einem festen Startwert gemischt und hat einen von einem Solver gefundenen Lösungsweg. Jede wird erneut geprüft, indem dieser Weg bis zu vier vollständigen Ablagestapeln nachgespielt wird. Festgefahren? Nimm ein paar Züge zurück und versuch einen anderen Weg: Jede nummerierte Partie ist ab der ersten Karte gewinnbar. Es geht von schnellen Einsteigern bis zu langen, geduldigen Partien.

TIPPS AUS EINEM LÖSUNGSWEG
Der Tipp markiert die Karte und ihr Ziel. Er folgt einem Lösungsweg ab deiner aktuellen Stellung, wann immer der Solver einen findet, und sagt ehrlich, wenn nicht.

SPIELT SICH WIE ERWARTET
• Karte antippen und sie springt an den besten Platz, oder zieh sie genau dorthin, wo du willst
• Ganze Reihen zwischen Spalten verschieben
• Gratis Rückgängig und Neustart mit einem Tipp
• Auto-Abschluss bringt alle Karten heim, sobald das Tableau offen liegt
• Züge, klassische Punkte und ein Timer; drei Sterne für einen Sieg bis zum Par
• Große, gut lesbare Karten auf Handy und Tablet
• Linkshänder-Layout und Vierfarben-Symbole in den Einstellungen

EIN TAGESSPIEL FÜR ALLE
Jeden Tag eine lösbare Partie, für alle Spieler gleich: leichter zum Wochenstart, schwerer am Wochenende. Gewinne sie, um eine Serie aufzubauen und Bonusmünzen zu verdienen.

ZUFALLSPARTIEN, 1 ODER 3 KARTEN
Lust auf eine frische Mischung? Zufallspartie mischt ein ganz neues Spiel, mit 1 Karte oder dem schwereren Ziehen von 3 Karten. Nicht jede Zufallsmischung ist lösbar – das gehört dazu. Zufallspartien kosten ein Leben; nummerierte Partien und das Tagesspiel sind immer gratis.

SIEBEN TISCHTHEMEN
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite und Midnight ändern Tisch und Kartenrücken. Schalte sie durch gewonnene Partien frei, Midnight mit Münzen.

ENTSPANNEND UND BEFRIEDIGEND
Sanfte Kartengeräusche, ein leichtes Vibrieren beim Ablegen (abschaltbar in den Einstellungen) und nach jedem Sieg eine hüpfende Kartenkaskade. Eine gute Denkpause für Kaffee oder Pendelstrecke.

Kostenlos spielbar mit optionaler Werbung und In-App-Käufen. Der Season Pass entfernt Werbung, bringt tägliche Münzen, schaltet alle Themen frei und gibt unbegrenzte Tipps.
</de-DE>

<es-419>
Voltea la última carta, mira caer los cuatro Reyes y ve cómo todo el mazo sale rebotando de la mesa.

Solitaire es Klondike clásico, hecho para jugar con calma y sin prisa. Arma las cuatro bases del As al Rey por palo y baja en el tablero alternando colores: un 6 rojo sobre un 7 negro. Solo un Rey puede ocupar una columna vacía. Funciona sin conexión, así que siempre tienes una partida tranquila a mano.

500 PARTIDAS, TODAS GANABLES
Cada partida numerada se reparte desde una semilla fija y trae una línea ganadora encontrada por un solucionador. Todas se vuelven a comprobar repitiendo esa línea hasta completar las cuatro bases. ¿Te atascaste? Deshaz algunos movimientos y prueba otro camino: cada partida numerada se puede ganar desde la primera carta. Van desde aperturas rápidas hasta partidas largas y pacientes.

PISTAS DE UNA LÍNEA GANADORA
La pista resalta la carta que mover y su destino. Sigue una línea ganadora desde tu posición actual siempre que el solucionador encuentre una, y te lo dice con claridad cuando no.

SE JUEGA COMO ESPERAS
• Toca una carta y salta a su mejor lugar, o arrástrala justo adonde quieras
• Mueve escaleras completas entre columnas
• Deshacer gratis y reinicio con un toque
• Final automático: todas las cartas suben cuando el tablero queda boca arriba
• Movimientos, puntaje clásico y cronómetro; tres estrellas al ganar en el par o menos
• Cartas grandes y legibles en teléfonos y tabletas
• Modo zurdo y palos de cuatro colores en Ajustes

UNA PARTIDA DIARIA PARA TODOS
Una partida ganable cada día, la misma para todos: más fácil al inicio de la semana y más difícil el fin de semana. Gánala para sumar a tu racha y conseguir monedas extra.

PARTIDAS AL AZAR, ROBAR 1 O 3
¿Quieres una mezcla nueva? La partida al azar baraja un tablero nuevo con robar 1 o con el más difícil robar 3. No todas las mezclas al azar se pueden ganar, y eso también es parte de la gracia. Las partidas al azar usan una vida; las numeradas y la diaria son siempre gratis.

SIETE TEMAS DE MESA
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite y Midnight cambian la mesa y el reverso de las cartas. Desbloquéalos ganando partidas, o Midnight con monedas.

RELAJANTE Y SATISFACTORIO
Sonidos suaves de cartas, una vibración ligera al colocar una carta (se apaga en Ajustes) y una cascada de cartas que rebotan cada vez que ganas. Un buen descanso para el cerebro con un café o en el camino.

Gratis con anuncios y compras dentro de la app opcionales. El Season Pass quita los anuncios, suma monedas cada día, desbloquea todos los temas y da pistas ilimitadas.
</es-419>

<fr-FR>
Retournez la dernière carte, regardez les quatre Rois se poser, puis tout le paquet cascader hors de la table.

Solitaire, c'est le Klondike classique, pensé pour jouer au calme, sans se presser. Montez les quatre fondations de l'As au Roi par couleur, et descendez le tableau en alternant rouge et noir : un 6 rouge sur un 7 noir. Seul un Roi peut occuper une colonne vide. Tout fonctionne hors ligne : une partie tranquille vous attend partout.

500 DONNES, TOUTES GAGNABLES
Chaque donne numérotée est distribuée à partir d'une graine fixe et accompagnée d'une ligne gagnante trouvée par un solveur. Chacune est revérifiée en rejouant cette ligne jusqu'à quatre fondations complètes. Bloqué ? Annulez quelques coups et tentez un autre chemin : chaque donne numérotée peut être gagnée dès la première carte. Elles vont des ouvertures rapides aux longues parties patientes.

DES INDICES TIRÉS D'UNE LIGNE GAGNANTE
L'indice met en évidence la carte à jouer et sa destination. Il suit une ligne gagnante depuis votre position dès que le solveur en trouve une, et vous le dit franchement quand ce n'est pas le cas.

UN JEU QUI RÉPOND COMME PRÉVU
• Touchez une carte et elle file à sa meilleure place, ou glissez-la exactement où vous voulez
• Déplacez des séquences entières entre colonnes
• Annulation gratuite et redémarrage en un geste
• Fin automatique : toutes les cartes rentrent dès que le tableau est entièrement visible
• Coups, score classique et chronomètre ; trois étoiles en gagnant au par ou mieux
• De grandes cartes lisibles sur téléphone et tablette
• Mode gaucher et couleurs à quatre teintes dans les Réglages

UNE DONNE DU JOUR POUR TOUS
Une donne gagnable par jour, la même pour tous les joueurs : plus facile en début de semaine, plus dure le week-end. Gagnez-la pour prolonger votre série et gagner des pièces bonus.

DONNES ALÉATOIRES, PIOCHE 1 OU 3
Envie d'un nouveau mélange ? La donne aléatoire mélange un jeu tout neuf en pioche 1 ou en pioche 3, plus difficile. Tous les mélanges aléatoires ne sont pas gagnables, et c'est aussi ce qui fait le sel du jeu. Les donnes aléatoires utilisent une vie ; les donnes numérotées et la donne du jour sont toujours gratuites.

SEPT THÈMES DE TABLE
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite et Midnight changent la table et le dos des cartes. Débloquez-les en gagnant des donnes, ou Midnight avec des pièces.

RELAXANT ET SATISFAISANT
Des bruits de cartes doux, une légère vibration quand une carte se pose (désactivable dans les Réglages) et une cascade de cartes rebondissantes à chaque victoire. Une bonne pause pour le cerveau, le temps d'un café ou d'un trajet.

Gratuit avec publicités et achats intégrés facultatifs. Le Season Pass supprime les publicités, ajoute des pièces chaque jour, débloque tous les thèmes et offre des indices illimités.
</fr-FR>

<hi-IN>
आख़िरी पत्ता पलटिए, चारों बादशाहों को अपनी जगह बैठते देखिए, और फिर पूरी गड्डी को टेबल से उछलते हुए बहते देखिए।

Solitaire क्लासिक क्लोंडाइक है, आराम से, बिना जल्दबाज़ी के खेलने के लिए। चारों फ़ाउंडेशन को सूट के हिसाब से इक्के से बादशाह तक बनाइए, और टेबल पर रंग बदलते हुए घटते क्रम में पत्ते रखिए: काले 7 पर लाल 6। ख़ाली कॉलम में सिर्फ़ बादशाह रखा जा सकता है। यह ऑफ़लाइन चलता है, इसलिए एक शांत बाज़ी हमेशा आपकी जेब में रहती है।

500 डील, हर एक जीतने योग्य
हर नंबर वाली डील एक तय सीड से बाँटी जाती है और उसके साथ सॉल्वर की खोजी हुई जीत की राह होती है। हर डील को उस राह को चारों फ़ाउंडेशन पूरे होने तक दोबारा खेलकर फिर से जाँचा गया है। अटक गए? कुछ चालें पूर्ववत करें और दूसरा रास्ता आज़माएँ: हर नंबर वाली डील पहले पत्ते से जीती जा सकती है। डील छोटी, तेज़ शुरुआत से लेकर लंबी, धैर्य वाली बाज़ियों तक जाती हैं।

जीत की राह से संकेत
संकेत चलने वाले पत्ते और उसकी मंज़िल को चमकाता है। जब भी सॉल्वर आपकी मौजूदा स्थिति से जीत की राह ढूँढ़ लेता है, संकेत उसी पर चलता है, और न मिलने पर साफ़ बता देता है।

जैसा आप चाहें, वैसा खेल
• पत्ते पर टैप करें और वह सबसे अच्छी जगह कूद जाएगा, या उसे ठीक वहाँ खींचें जहाँ चाहें
• पूरी कतारें एक कॉलम से दूसरे में ले जाएँ
• मुफ़्त पूर्ववत और एक टैप में फिर से शुरू
• अपने आप पूरा: टेबल के सारे पत्ते खुलते ही बाक़ी पत्ते ख़ुद घर पहुँचते हैं
• चालें, क्लासिक स्कोर और टाइमर; पार के भीतर जीतने पर तीन सितारे
• फ़ोन और टैबलेट पर बड़े, साफ़ पढ़ने लायक पत्ते
• सेटिंग्स में बाएँ हाथ वाला लेआउट और चार रंगों के सूट

सबके लिए एक डेली डील
हर दिन एक जीतने योग्य डील, सभी खिलाड़ियों के लिए एक जैसी: हफ़्ते की शुरुआत में आसान, सप्ताहांत में कठिन। जीतकर अपनी स्ट्रीक बढ़ाइए और बोनस सिक्के पाइए।

रैंडम डील: 1 या 3 पत्ते
नया फेंटा हुआ खेल चाहिए? रैंडम डील एक बिल्कुल नई टेबल फेंटती है, 1 पत्ता खींचकर या ज़्यादा कठिन 3 पत्ते खींचकर। हर रैंडम फेंट जीती नहीं जा सकती, और यही इसका मज़ा है। रैंडम डील में एक जान लगती है; नंबर वाली डील और डेली डील हमेशा मुफ़्त हैं।

सात टेबल थीम
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite और Midnight टेबल और पत्तों की पीठ बदल देते हैं। डील जीतकर इन्हें खोलें, या Midnight सिक्कों से।

आरामदायक और संतोषजनक
पत्तों की नरम आवाज़ें, पत्ता बैठने पर हल्का कंपन (सेटिंग्स में बंद करें) और हर जीत पर उछलते पत्तों का झरना। चाय-कॉफ़ी या सफ़र के बीच दिमाग़ के लिए अच्छा ब्रेक।

मुफ़्त में खेलें, वैकल्पिक विज्ञापन और इन-ऐप ख़रीदारी के साथ। Season Pass विज्ञापन हटाता है, रोज़ सिक्के देता है, सभी थीम खोलता है और असीमित संकेत देता है।
</hi-IN>

<id>
Balik kartu terakhir, lihat empat King mendarat, lalu saksikan seluruh dek memantul turun dari meja.

Solitaire adalah Klondike klasik untuk bermain dengan tenang dan santai. Susun empat fondasi dari As sampai King menurut jenisnya, dan turunkan kartu di meja dengan warna berselang: 6 merah di atas 7 hitam. Hanya King yang boleh mengisi kolom kosong. Bisa dimainkan offline, jadi permainan santai selalu ada di saku.

500 DEAL, SEMUANYA BISA DIMENANGKAN
Setiap deal bernomor dikocok dari seed tetap dan dilengkapi jalur menang yang ditemukan oleh solver. Semuanya dicek ulang dengan memainkan jalur itu sampai keempat fondasi penuh. Buntu? Urungkan beberapa langkah dan coba jalan lain: setiap deal bernomor bisa dimenangkan sejak kartu pertama. Mulai dari pembuka cepat sampai permainan panjang yang butuh kesabaran.

PETUNJUK DARI JALUR MENANG
Petunjuk menyorot kartu yang perlu dipindah dan tujuannya. Petunjuk mengikuti jalur menang dari posisimu saat ini setiap kali solver menemukannya, dan memberi tahu dengan jujur jika tidak.

DIMAINKAN SESUAI HARAPAN
• Ketuk kartu dan ia melompat ke tempat terbaik, atau seret tepat ke tempat yang kamu mau
• Pindahkan deretan kartu utuh antarkolom
• Urungkan gratis dan mulai ulang dengan satu ketukan
• Selesai otomatis: semua kartu pulang begitu meja terbuka seluruhnya
• Jumlah langkah, skor klasik, dan pengatur waktu; tiga bintang jika menang di par atau kurang
• Kartu besar dan mudah dibaca di ponsel dan tablet
• Tata letak kidal dan simbol empat warna di Pengaturan

DEAL HARIAN UNTUK SEMUA
Satu deal yang bisa dimenangkan setiap hari, sama untuk semua pemain: lebih mudah di awal pekan, lebih sulit di akhir pekan. Menangkan untuk menjaga rentetan dan mendapat koin bonus.

DEAL ACAK, AMBIL 1 ATAU 3
Ingin kocokan baru? Deal acak mengocok meja yang benar-benar baru dengan ambil 1 atau ambil 3 yang lebih sulit. Tidak semua kocokan acak bisa dimenangkan, dan itu bagian dari serunya. Deal acak memakai satu nyawa; deal bernomor dan Deal Harian selalu gratis.

TUJUH TEMA MEJA
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite, dan Midnight mengubah meja dan punggung kartu. Buka dengan memenangkan deal, atau Midnight dengan koin.

SANTAI DAN MEMUASKAN
Suara kartu yang lembut, getaran halus saat kartu mendarat (bisa dimatikan di Pengaturan), dan air terjun kartu yang memantul setiap kali kamu menang. Jeda yang pas untuk otak sambil ngopi atau di perjalanan.

Gratis dimainkan dengan iklan dan pembelian dalam aplikasi opsional. Season Pass menghapus iklan, menambah koin harian, membuka semua tema, dan memberi petunjuk tanpa batas.
</id>

<it-IT>
Gira l'ultima carta, guarda i quattro Re posarsi e poi l'intero mazzo rimbalzare giù dal tavolo.

Solitaire è il Klondike classico, pensato per giocare con calma e senza fretta. Costruisci le quattro fondazioni dall'Asso al Re per seme e scendi nel tableau alternando i colori: un 6 rosso su un 7 nero. Solo un Re può occupare una colonna vuota. Funziona offline, così una partita tranquilla è sempre in tasca.

500 SMAZZATE, TUTTE VINCIBILI
Ogni smazzata numerata viene distribuita da un seme fisso e ha una linea vincente trovata da un risolutore. Ognuna viene ricontrollata rigiocando quella linea fino a quattro fondazioni complete. Bloccato? Annulla qualche mossa e prova un'altra strada: ogni smazzata numerata si può vincere dalla prima carta. Si va da aperture veloci a partite lunghe e pazienti.

AIUTI DA UNA LINEA VINCENTE
L'aiuto evidenzia la carta da muovere e la sua destinazione. Segue una linea vincente dalla tua posizione attuale ogni volta che il risolutore ne trova una, e te lo dice chiaramente quando non succede.

SI GIOCA COME TI ASPETTI
• Tocca una carta e salta al posto migliore, oppure trascinala esattamente dove vuoi
• Sposta intere sequenze tra le colonne
• Annulla gratis e ricomincia con un tocco
• Chiusura automatica: tutte le carte salgono appena il tableau è scoperto
• Mosse, punteggio classico e cronometro; tre stelle vincendo entro il par
• Carte grandi e leggibili su telefono e tablet
• Modalità mancini e semi a quattro colori nelle Impostazioni

UNA SMAZZATA DEL GIORNO PER TUTTI
Una smazzata vincibile al giorno, uguale per tutti i giocatori: più facile a inizio settimana, più dura nel weekend. Vincila per allungare la serie e guadagnare monete bonus.

SMAZZATE CASUALI, PESCA 1 O 3
Vuoi un mescolamento nuovo? La smazzata casuale mescola un tavolo nuovo con pesca 1 o con il più difficile pesca 3. Non tutte le smazzate casuali sono vincibili, ed è parte del divertimento. Le smazzate casuali usano una vita; quelle numerate e quella del giorno sono sempre gratis.

SETTE TEMI DEL TAVOLO
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite e Midnight cambiano il tavolo e il dorso delle carte. Sbloccali vincendo smazzate, oppure Midnight con le monete.

RILASSANTE E APPAGANTE
Suoni morbidi delle carte, una leggera vibrazione quando una carta si posa (disattivabile nelle Impostazioni) e una cascata di carte che rimbalzano a ogni vittoria. Una bella pausa per la mente, con un caffè o in viaggio.

Gratis con pubblicità e acquisti in-app facoltativi. Il Season Pass rimuove la pubblicità, aggiunge monete ogni giorno, sblocca tutti i temi e dà aiuti illimitati.
</it-IT>

<ja-JP>
最後の一枚をめくり、4枚のキングが組札に収まると、デッキ全体が弾みながらテーブルから流れ落ちます。

Solitaire は、のんびり落ち着いて遊べる定番のクロンダイクです。4つの組札をスートごとにエースからキングまで積み上げ、場札は色を交互に一つずつ下げて重ねます（黒の7に赤の6）。空いた列に置けるのはキングだけ。オフラインで遊べるので、いつでもどこでも静かな一局を。

500ディール、すべて勝てる
番号付きディールはそれぞれ固定のシードから配られ、ソルバーが見つけた勝ち筋付き。その手順を4つの組札が完成するまで再生して、一つ残らず再確認しています。行き詰まったら？ 何手か戻して別の道を試しましょう。番号付きディールは最初の一枚から必ず勝てます。すぐ終わる序盤から、じっくり粘る長い一局まで揃っています。

勝ち筋から出すヒント
ヒントは動かすカードと行き先を光らせます。ソルバーが今の局面から勝ち筋を見つけられればそれに沿い、見つからないときは正直にそう伝えます。

思いどおりに遊べる
• カードをタップすると最適な場所へ。ドラッグすれば好きな場所へ
• 列のまとまりをそのまま別の列へ移動
• 取り消しは無料、リスタートもワンタップ
• 自動仕上げ：場札がすべて表になれば、残りのカードは自動で組札へ
• 手数、クラシックスコア、タイマー。パー以内で勝てば星3つ
• スマホでもタブレットでも大きく読みやすいカード
• 設定で左利きレイアウトと4色スートを選べます

みんなのデイリーディール
毎日ひとつ、全プレイヤー共通の勝てるディール。週の初めはやさしく、週末は手ごわく。勝って連続記録を伸ばし、ボーナスコインを手に入れましょう。

ランダムディール：1枚めくり・3枚めくり
新しいシャッフルで遊びたいときは、ランダムディールでまったく新しい盤面を。1枚めくりか、より難しい3枚めくりを選べます。ランダムな配りは必ず勝てるとは限りません。それもまた楽しみのひとつ。ランダムディールはライフを1つ使います。番号付きディールとデイリーディールはいつでも無料です。

7種類のテーブルテーマ
Sea Glass、Clubhouse Baize、Harbor、Desert Sand、Velvet、Graphite、Midnight がテーブルとカードの裏面を変えます。ディールに勝って解放、Midnight はコインで。

癒やされて、気持ちいい
やわらかなカードの音、カードが収まるときの軽い振動（設定でオフにできます）、そして勝つたびに弾むカードの滝。コーヒーのお供や通勤中の、ちょうどいい脳の休憩に。

基本プレイ無料。任意の広告とアプリ内課金があります。Season Pass で広告なし、毎日コイン、全テーマ解放、ヒント無制限に。
</ja-JP>

<pt-BR>
Vire a última carta, veja os quatro Reis pousarem e o baralho inteiro sair quicando da mesa.

Solitaire é o Klondike clássico, feito para jogar com calma, sem pressa. Monte as quatro fundações do Ás ao Rei por naipe e desça no tableau alternando as cores: um 6 vermelho sobre um 7 preto. Só um Rei pode ocupar uma coluna vazia. Funciona offline, então uma partida tranquila está sempre no seu bolso.

500 PARTIDAS, TODAS VENCÍVEIS
Cada partida numerada é distribuída a partir de uma semente fixa e vem com uma linha vencedora encontrada por um solucionador. Todas são conferidas de novo, repetindo essa linha até completar as quatro fundações. Travou? Desfaça alguns lances e tente outro caminho: toda partida numerada pode ser vencida desde a primeira carta. Vão de aberturas rápidas a partidas longas e pacientes.

DICAS DE UMA LINHA VENCEDORA
A dica destaca a carta a mover e o destino. Ela segue uma linha vencedora a partir da sua posição atual sempre que o solucionador encontra uma, e avisa com clareza quando não encontra.

JOGA DO JEITO QUE VOCÊ ESPERA
• Toque numa carta e ela vai para o melhor lugar, ou arraste para onde quiser
• Mova sequências inteiras entre colunas
• Desfazer grátis e reinício com um toque
• Final automático: todas as cartas sobem quando o tableau fica todo virado
• Lances, pontuação clássica e cronômetro; três estrelas ao vencer no par ou menos
• Cartas grandes e legíveis no celular e no tablet
• Modo canhoto e naipes em quatro cores nas Configurações

UMA PARTIDA DIÁRIA PARA TODOS
Uma partida vencível por dia, a mesma para todos: mais fácil no começo da semana, mais difícil no fim de semana. Vença para aumentar sua sequência e ganhar moedas bônus.

PARTIDAS ALEATÓRIAS, COMPRAR 1 OU 3
Quer um embaralhamento novo? A partida aleatória embaralha uma mesa nova com comprar 1 ou com o mais difícil comprar 3. Nem toda mistura aleatória pode ser vencida, e isso faz parte da graça. Partidas aleatórias usam uma vida; as numeradas e a diária são sempre grátis.

SETE TEMAS DE MESA
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite e Midnight mudam a mesa e o verso das cartas. Desbloqueie vencendo partidas, ou o Midnight com moedas.

RELAXANTE E SATISFATÓRIO
Sons suaves de cartas, uma vibração leve quando a carta encaixa (desligue nas Configurações) e uma cascata de cartas quicando a cada vitória. Uma boa pausa para a mente no café ou no caminho.

Grátis, com anúncios e compras no app opcionais. O Season Pass remove os anúncios, dá moedas todo dia, desbloqueia todos os temas e libera dicas ilimitadas.
</pt-BR>

<tr-TR>
Son kartı çevir, dört Papazın yerine oturuşunu izle ve bütün destenin masadan sekerek akışını seyret.

Solitaire, sakin ve acelesiz oynamak için yapılmış klasik Klondike. Dört temel desteyi takıma göre Astan Papaza kur, masadaki sütunlarda renkleri değiştirerek aşağı doğru diz: siyah 7'nin üstüne kırmızı 6. Boş bir sütuna yalnızca Papaz konabilir. Çevrimdışı çalışır, böylece sakin bir oyun hep cebinde.

500 EL, HEPSİ KAZANILABİLİR
Her numaralı el sabit bir tohumdan dağıtılır ve bir çözücünün bulduğu kazanan bir yolla gelir. Hepsi, bu yol dört temel deste tamamlanana kadar yeniden oynatılarak tekrar kontrol edilir. Takıldın mı? Birkaç hamle geri al ve başka bir yol dene: her numaralı el ilk karttan itibaren kazanılabilir. Eller hızlı açılışlardan uzun, sabır isteyen oyunlara uzanır.

KAZANAN BİR YOLDAN İPUÇLARI
İpucu oynanacak kartı ve gideceği yeri işaretler. Çözücü bir yol bulduğunda mevcut konumundan kazanan bir yolu izler; bulamazsa bunu açıkça söyler.

BEKLEDİĞİN GİBİ OYNANIR
• Karta dokun, en iyi yerine zıplasın; ya da tam istediğin yere sürükle
• Sütunlar arasında bütün dizileri taşı
• Ücretsiz geri al ve tek dokunuşla yeniden başlat
• Otomatik bitiş: masadaki tüm kartlar açılınca hepsi yerine gider
• Hamle sayısı, klasik puan ve süre; par veya altında kazanınca üç yıldız
• Telefon ve tablette büyük, okunaklı kartlar
• Ayarlarda solak düzeni ve dört renkli takımlar

HERKESE GÜNLÜK EL
Her gün kazanılabilir bir el, tüm oyuncular için aynı: hafta başı daha kolay, hafta sonu daha zor. Kazanarak serini büyüt ve bonus jeton topla.

RASTGELE ELLER, 1 VEYA 3 KART
Taze bir karışım mı istiyorsun? Rastgele el, 1 kart çekmeli ya da daha zor 3 kart çekmeli yepyeni bir masa karıştırır. Her rastgele karışım kazanılamaz, bu da işin tadı. Rastgele eller bir can kullanır; numaralı eller ve günlük el her zaman ücretsizdir.

YEDİ MASA TEMASI
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite ve Midnight masayı ve kart arkalarını değiştirir. El kazanarak aç, Midnight'ı jetonla al.

RAHATLATICI VE TATMİN EDİCİ
Yumuşak kart sesleri, bir kart yerine oturunca hafif bir titreşim (Ayarlardan kapatılabilir) ve her zaferde sekerek akan bir kart şelalesi. Bir kahve ya da yolculuk için iyi bir zihin molası.

Ücretsiz; isteğe bağlı reklamlar ve uygulama içi satın almalar içerir. Season Pass reklamları kaldırır, her gün jeton ekler, tüm temaları açar ve sınırsız ipucu verir.
</tr-TR>

<uk>
Переверніть останню карту, подивіться, як лягають чотири королі, — і вся колода каскадом зістрибує зі столу.

Solitaire — це класичний пасьянс Klondike (Косинка) для спокійної, неквапливої гри. Збирайте чотири бази від туза до короля за мастями, а на столі викладайте спадні ряди з чергуванням кольорів: червона 6 на чорну 7. Порожній стовпчик може зайняти лише король. Гра працює офлайн, тож спокійна партія завжди під рукою.

500 РОЗДАЧ, КОЖНУ МОЖНА ВИГРАТИ
Кожна пронумерована роздача тасується з фіксованого зерна й має виграшну лінію, знайдену розв'язувачем. Кожну перевіряють заново, програючи цю лінію до чотирьох повних баз. Застрягли? Скасуйте кілька ходів і спробуйте інший шлях: кожну пронумеровану роздачу можна виграти з першої карти. Роздачі йдуть від швидких розминок до довгих, терплячих партій.

ПІДКАЗКИ З ВИГРАШНОЇ ЛІНІЇ
Підказка підсвічує карту, яку варто походити, і куди. Вона йде виграшною лінією з вашої поточної позиції щоразу, коли розв'язувач її знаходить, і чесно каже, коли ні.

ГРАЄТЬСЯ ТАК, ЯК ВИ ОЧІКУЄТЕ
• Торкніться карти, і вона стрибне на найкраще місце, або перетягніть її куди завгодно
• Переносьте цілі ряди між стовпчиками
• Безкоштовне скасування й перезапуск одним дотиком
• Автозавершення: щойно весь стіл відкритий, карти самі йдуть на бази
• Ходи, класичний рахунок і таймер; три зірки за перемогу в межах пару
• Великі, чіткі карти на телефоні й планшеті
• Режим для лівші й чотириколірні масті в Налаштуваннях

ЩОДЕННА РОЗДАЧА ДЛЯ ВСІХ
Одна виграшна роздача на день, однакова для всіх гравців: легша на початку тижня, складніша у вихідні. Вигравайте, щоб тримати серію й отримувати бонусні монети.

ВИПАДКОВІ РОЗДАЧІ: ПО 1 АБО ПО 3
Хочете свіжу колоду? Випадкова роздача тасує зовсім новий стіл по 1 карті або складніший варіант по 3. Не кожну випадкову роздачу можна виграти — у цьому й цікавість. Випадкові роздачі витрачають життя; пронумеровані й щоденна завжди безкоштовні.

СІМ ТЕМ СТОЛУ
Sea Glass, Clubhouse Baize, Harbor, Desert Sand, Velvet, Graphite і Midnight змінюють стіл і сорочки карт. Відкривайте їх перемогами, а Midnight — за монети.

СПОКІЙНО Й ПРИЄМНО
М'які звуки карт, легка вібрація, коли карта лягає (вимикається в Налаштуваннях), і каскад карт, що підстрибують, після кожної перемоги. Гарна перерва для мозку за кавою чи в дорозі.

Безкоштовна гра з необов'язковою рекламою та покупками в застосунку. Season Pass прибирає рекламу, щодня додає монети, відкриває всі теми й дає необмежені підказки.
</uk>

<zh-CN>
翻开最后一张牌，看四张 K 依次归位，整副牌随即在牌桌上弹跳着倾泻而下。

Solitaire 是经典的克朗代克纸牌，专为不慌不忙的轻松对局打造。按花色把四个收牌堆从 A 叠到 K，在牌桌上按红黑交替、点数递减排列：红 6 放在黑 7 上。只有 K 能放进空列。支持离线游玩，随时随地来一局安静的纸牌。

500 局，每局都能赢
每一局编号牌局都由固定种子发牌，并附有一条由求解器找到的制胜路线。每一局都会按这条路线重新走一遍，直到四个收牌堆全部完成，逐一复核。卡住了？撤销几步换条路试试：每一局编号牌局从第一张牌起都能赢。从轻快的开局到需要耐心的长局，一应俱全。

来自制胜路线的提示
提示会高亮要移动的牌和它的去处。只要求解器能从你当前的局面找到制胜路线，提示就会沿着它走；找不到时也会如实告诉你。

手感如你所料
• 点按纸牌，它会跳到最佳位置；也可以拖到你想放的任何地方
• 在列之间整组移动纸牌
• 免费撤销，一键重开
• 自动收尾：牌桌上的牌全部翻开后，剩下的牌自动归位
• 步数、经典计分和计时；在标准步数内获胜得三颗星
• 手机和平板上都有大而清晰的纸牌
• 设置中可选左手布局和四色花色

人人都有的每日牌局
每天一局可以获胜的牌局，所有玩家都一样：周初更简单，周末更难。赢下它来延续连胜，赚取额外金币。

随机牌局：翻一张或翻三张
想来一副新洗的牌？随机牌局会洗出全新的牌桌，可选翻一张或更难的翻三张。并非每一副随机洗出的牌都能赢，这也是乐趣所在。随机牌局会消耗一条生命；编号牌局和每日牌局永远免费。

七款牌桌主题
Sea Glass、Clubhouse Baize、Harbor、Desert Sand、Velvet、Graphite 和 Midnight 会改变牌桌和牌背。赢下牌局即可解锁，Midnight 可用金币购买。

轻松又解压
柔和的翻牌声，纸牌落定时轻轻一震（可在设置中关闭），每次获胜还有弹跳的纸牌瀑布。喝咖啡或通勤路上的绝佳大脑小憩。

免费游玩，含可选广告和应用内购买。Season Pass 可去除广告、每日赠送金币、解锁全部主题并提供无限提示。
</zh-CN>

---

## SUBTITLE (≤30 chars per locale)

_Apple App Store Connect → App Information → Subtitle_

<en-US>
500 winnable Klondike deals
</en-US>

<ar>
500 توزيعة كلوندايك رابحة
</ar>

<de-DE>
500 lösbare Klondike-Partien
</de-DE>

<es-419>
500 partidas Klondike ganables
</es-419>

<fr-FR>
500 donnes Klondike gagnables
</fr-FR>

<hi-IN>
500 जीतने योग्य क्लोंडाइक डील
</hi-IN>

<id>
500 deal Klondike, bisa menang
</id>

<it-IT>
500 smazzate Klondike vincenti
</it-IT>

<ja-JP>
必ず勝てるクロンダイク500ディール
</ja-JP>

<pt-BR>
500 partidas de Klondike
</pt-BR>

<tr-TR>
500 kazanılabilir Klondike eli
</tr-TR>

<uk>
500 виграшних роздач Klondike
</uk>

<zh-CN>
500 局必胜克朗代克纸牌
</zh-CN>

---

## KEYWORDS (≤100 chars per locale)

_Apple App Store Connect → Version → Keywords_

<en-US>
solitaire,klondike,card game,patience,classic cards,daily deal,draw 3,offline,relaxing,brain game
</en-US>

<ar>
سوليتير,كلوندايك,ورق اللعب,لعبة ورق,صبر,توزيعة يومية,سحب 3,بدون إنترنت,مريحة,solitaire
</ar>

<de-DE>
solitaire,klondike,patience,kartenspiel,solitär,tagesspiel,draw 3,offline,entspannend,karten
</de-DE>

<es-419>
solitario,klondike,solitaire,cartas,juego de cartas,partida diaria,robar 3,sin conexión,relajante
</es-419>

<fr-FR>
solitaire,klondike,patience,jeu de cartes,réussite,donne du jour,pioche 3,hors ligne,relaxant
</fr-FR>

<hi-IN>
सॉलिटेयर,क्लोंडाइक,ताश,कार्ड गेम,पेशेंस,डेली डील,ऑफ़लाइन,आरामदायक,solitaire,klondike
</hi-IN>

<id>
solitaire,klondike,kartu,permainan kartu,patience,deal harian,ambil 3,offline,santai,otak
</id>

<it-IT>
solitario,klondike,solitaire,carte,gioco di carte,partita del giorno,pesca 3,offline,rilassante
</it-IT>

<ja-JP>
ソリティア,クロンダイク,トランプ,カードゲーム,一人遊び,デイリー,3枚めくり,オフライン,癒し,脳トレ
</ja-JP>

<pt-BR>
paciência,solitaire,klondike,cartas,jogo de cartas,partida diária,comprar 3,offline,relaxante
</pt-BR>

<tr-TR>
solitaire,klondike,iskambil,kart oyunu,sabır oyunu,günlük el,3 kart çek,çevrimdışı,rahatlatıcı
</tr-TR>

<uk>
пасьянс,косинка,klondike,solitaire,карти,карткова гра,щоденна роздача,офлайн,розслаблення
</uk>

<zh-CN>
纸牌,接龙,克朗代克,solitaire,扑克,单人纸牌,每日挑战,翻三张,离线,休闲,益智
</zh-CN>

---

## PROMOTIONAL TEXT (≤170 chars per locale)

_Apple App Store Connect → Version → Promotional Text_

<en-US>
Every numbered deal is verified winnable, and Hint shows the next move of a winning line. Tap to move, drag to choose, free undo. Relaxing and offline.
</en-US>

<ar>
كل توزيعة مرقّمة مُتحقَّق من أنها قابلة للفوز، والتلميح يُظهر النقلة التالية من خط فوز. المس، اسحب، وتراجع مجانًا. مريحة وتعمل بدون إنترنت.
</ar>

<de-DE>
Jede nummerierte Partie ist garantiert lösbar, und der Tipp zeigt den nächsten Zug eines Lösungswegs. Tippen, ziehen, gratis rückgängig. Entspannt und offline.
</de-DE>

<es-419>
Cada partida numerada está verificada como ganable y la pista muestra el siguiente paso de una línea ganadora. Toca, arrastra, deshaz gratis. Sin conexión.
</es-419>

<fr-FR>
Chaque donne numérotée est vérifiée gagnable, et l'indice montre le coup suivant d'une ligne gagnante. Touchez, glissez, annulez gratuitement. Relaxant, hors ligne.
</fr-FR>

<hi-IN>
हर नंबर वाली डील जीतने योग्य होने के लिए जाँची गई है, और संकेत जीत की राह की अगली चाल दिखाता है। टैप करें, खींचें, मुफ़्त में पूर्ववत करें। आरामदायक और ऑफ़लाइन।
</hi-IN>

<id>
Setiap deal bernomor sudah diverifikasi bisa dimenangkan, dan Petunjuk menunjukkan langkah berikutnya dari jalur menang. Ketuk, seret, urungkan gratis. Offline.
</id>

<it-IT>
Ogni smazzata numerata è verificata vincibile e l'aiuto mostra la mossa successiva di una linea vincente. Tocca, trascina, annulla gratis. Rilassante e offline.
</it-IT>

<ja-JP>
番号付きディールはすべて勝てることを検証済み。ヒントは勝ち筋の次の一手を示します。タップで移動、ドラッグで自由に、取り消しは無料。オフラインでゆったり。
</ja-JP>

<pt-BR>
Cada partida numerada é verificada como vencível, e a dica mostra o próximo lance de uma linha vencedora. Toque, arraste, desfaça grátis. Relaxante e offline.
</pt-BR>

<tr-TR>
Her numaralı elin kazanılabilir olduğu doğrulandı; ipucu, kazanan bir yolun sıradaki hamlesini gösterir. Dokun, sürükle, ücretsiz geri al. Rahatlatıcı ve çevrimdışı.
</tr-TR>

<uk>
Кожну пронумеровану роздачу перевірено на виграшність, а підказка показує наступний хід виграшної лінії. Торкайтеся, перетягуйте, скасовуйте безкоштовно. Офлайн.
</uk>

<zh-CN>
每一局编号牌局都经过验证可以获胜，提示会给出制胜路线的下一步。点按移动、拖动自选、免费撤销。轻松休闲，离线可玩。
</zh-CN>

---
