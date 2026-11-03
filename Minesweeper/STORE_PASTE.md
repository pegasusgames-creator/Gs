# Minesweeper — store paste sheet

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
Minesweeper 2.0 is a complete rebuild:
• 500 no-guess fields, each checked by a logic solver from the first tap to the last mine
• Boards grow from 6×6 to 30×16, with pinch-zoom and pan
• Hints open a provably safe tile or flag a provable mine, and show the numbers behind it
• Long-press or Flag mode, plus chording on numbers
• Daily field with streaks, Endless mode, seven themes
• Hit a mine? Keep your field and carry on
</en-US>

<ar>
Minesweeper 2.0 إعادة بناء كاملة:
• 500 حقل بلا تخمين، فُحص كل منها بمحلل منطقي من النقرة الأولى حتى آخر لغم
• لوحات تكبر من 6×6 إلى 30×16، مع التكبير بإصبعين والتحريك
• التلميح يفتح مربعًا آمنًا مؤكدًا أو يضع علمًا على لغم مؤكد، ويُظهر الأرقام التي تثبت ذلك
• ضغطة مطوّلة أو وضع العلم، مع الفتح السريع من الأرقام
• حقل يومي مع سلسلة أيام، ووضع لا نهائي، وسبعة أنماط
• أصبت لغمًا؟ احتفظ بحقلك وتابع
</ar>

<de-DE>
Minesweeper 2.0 ist komplett neu gebaut:
• 500 Felder ohne Raten, jedes von einem Logik-Löser vom ersten Tipp bis zur letzten Mine geprüft
• Felder wachsen von 6×6 bis 30×16, mit Zoom und Verschieben
• Tipps öffnen ein beweisbar sicheres Feld oder markieren eine beweisbare Mine
• Langes Drücken oder Flaggenmodus, dazu Akkord auf Zahlen
• Tagesfeld mit Serie, Endlos-Modus, sieben Designs
• Mine getroffen? Behalte dein Feld und spiel weiter
</de-DE>

<es-419>
Minesweeper 2.0 es una reconstrucción completa:
• 500 campos sin adivinar, cada uno comprobado por un solucionador lógico del primer toque a la última mina
• Tableros de 6×6 a 30×16, con zoom y desplazamiento
• Las pistas abren una casilla segura demostrable o marcan una mina demostrable
• Mantén pulsado o usa el modo bandera, y acordes sobre los números
• Campo diario con racha, modo Infinito y siete temas
• ¿Pisaste una mina? Conserva tu campo y sigue
</es-419>

<fr-FR>
Minesweeper 2.0 est entièrement reconstruit :
• 500 champs sans hasard, chacun vérifié par un solveur logique du premier tap à la dernière mine
• Grilles de 6×6 à 30×16, avec zoom et déplacement
• Les indices ouvrent une case sûre prouvable ou marquent une mine prouvable
• Appui long ou mode drapeau, et accord sur les chiffres
• Champ du jour avec série, mode Infini et sept thèmes
• Une mine touchée ? Gardez votre champ et continuez
</fr-FR>

<hi-IN>
Minesweeper 2.0 पूरी तरह नए सिरे से बना है:
• 500 बिना-अंदाज़े वाले फ़ील्ड, हर एक को लॉजिक सॉल्वर ने पहले टैप से आख़िरी माइन तक जाँचा है
• बोर्ड 6×6 से 30×16 तक बढ़ते हैं, पिंच-ज़ूम और पैन के साथ
• हिंट एक साबित-सुरक्षित टाइल खोलता है या साबित माइन पर झंडा लगाता है, और उसके पीछे के नंबर दिखाता है
• लॉन्ग-प्रेस या फ़्लैग मोड, साथ में नंबरों पर कॉर्डिंग
• स्ट्रीक के साथ डेली फ़ील्ड, एंडलेस मोड, सात थीम
• माइन पर टैप हो गया? अपना फ़ील्ड बचाकर आगे खेलें
</hi-IN>

<id>
Minesweeper 2.0 dibangun ulang sepenuhnya:
• 500 ladang tanpa tebakan, masing-masing diperiksa pemecah logika dari ketukan pertama sampai ranjau terakhir
• Papan bertambah dari 6×6 sampai 30×16, dengan cubit untuk zoom dan geser
• Petunjuk membuka petak yang terbukti aman atau menandai ranjau pasti, dan menunjukkan angka buktinya
• Tekan lama atau Mode Bendera, plus chording pada angka
• Ladang harian dengan rentetan, mode Tanpa Akhir, tujuh tema
• Kena ranjau? Simpan ladangmu dan lanjutkan
</id>

<it-IT>
Minesweeper 2.0 è ricostruito da zero:
• 500 campi senza azzardo, ognuno verificato da un risolutore logico dal primo tocco all'ultima mina
• Griglie da 6×6 a 30×16, con zoom e spostamento
• I suggerimenti aprono una casella sicura dimostrabile o segnano una mina dimostrabile
• Pressione lunga o modalità bandierina, e accordo sui numeri
• Campo del giorno con serie, modalità Infinita e sette temi
• Hai colpito una mina? Tieni il campo e continua
</it-IT>

<ja-JP>
Minesweeper 2.0 を全面的に作り直しました:
• 運に頼らない500面。最初のタップから最後の地雷まで論理ソルバーで検証済み
• 盤面は6×6から30×16へ。ピンチで拡大、ドラッグで移動
• ヒントは確実に安全なマスを開けるか、確実な地雷に旗を立て、その根拠の数字を表示
• 長押しまたは旗モード、数字のまとめ開け(コード)にも対応
• 連続記録つきのデイリー盤面、エンドレスモード、7つのテーマ
• 地雷を踏んでも、盤面を残したまま続けられます
</ja-JP>

<pt-BR>
Minesweeper 2.0 foi totalmente refeito:
• 500 campos sem chute, cada um verificado por um solucionador lógico do primeiro toque à última mina
• Tabuleiros de 6×6 a 30×16, com zoom e arrastar
• Dicas abrem uma casa comprovadamente segura ou marcam uma mina comprovada
• Toque longo ou modo bandeira, e acorde nos números
• Campo diário com sequência, modo Infinito e sete temas
• Pisou numa mina? Mantenha seu campo e continue
</pt-BR>

<tr-TR>
Minesweeper 2.0 baştan yeniden yapıldı:
• Tahmin gerektirmeyen 500 alan, her biri ilk dokunuştan son mayına kadar bir mantık çözücüyle denetlendi
• Tahtalar 6×6'dan 30×16'ya büyür; iki parmakla yakınlaştırma ve kaydırma
• İpucu kanıtlanmış güvenli bir kareyi açar ya da kesin bir mayını işaretler ve bunu kanıtlayan sayıları gösterir
• Uzun basma veya Bayrak modu, sayılarda toplu açma
• Seri takipli günlük alan, Sonsuz mod, yedi tema
• Mayına mı bastın? Alanını koru ve devam et
</tr-TR>

<uk>
Minesweeper 2.0 повністю перебудовано:
• 500 полів без вгадування, кожне перевірене логічним розв'язувачем від першого дотику до останньої міни
• Поля зростають від 6×6 до 30×16, з масштабуванням щипком і прокручуванням
• Підказка відкриває доведено безпечну клітинку або позначає доведену міну й показує числа-доказ
• Довге натискання або режим прапорця, а також відкриття навколо чисел
• Щоденне поле із серією, нескінченний режим, сім тем
• Натрапили на міну? Збережіть поле й грайте далі
</uk>

<zh-CN>
Minesweeper 2.0 全面重制:
• 500 个无需猜测的雷区,每一个都经逻辑求解器从第一次点击验证到最后一颗雷
• 棋盘从 6×6 逐步扩大到 30×16,支持双指缩放和拖动
• 提示会打开一个可证明安全的格子,或标记一颗可证明的雷,并显示作为依据的数字
• 长按或插旗模式,数字上支持快速翻开
• 带连续记录的每日雷区、无尽模式、七种主题
• 踩到雷?保留棋盘继续玩
</zh-CN>

---

## SHORT DESCRIPTION (≤80 chars per locale)

_Grow → Store presence → Main store listing → Short description_

<en-US>
500 no-guess minefields, each solvable by logic. Daily field and smart hints.
</en-US>

<ar>
500 حقل ألغام بلا تخمين، كلها تُحل بالمنطق. حقل يومي وتلميحات ذكية.
</ar>

<de-DE>
500 Minenfelder ohne Raten, alle per Logik lösbar. Tagesfeld und kluge Tipps.
</de-DE>

<es-419>
500 campos minados sin adivinar, todos se resuelven con lógica. Reto diario.
</es-419>

<fr-FR>
500 champs de mines sans hasard, tous résolubles par la logique. Défi du jour.
</fr-FR>

<hi-IN>
500 बिना-अंदाज़े माइनफ़ील्ड, सब लॉजिक से हल। रोज़ का फ़ील्ड और स्मार्ट हिंट।
</hi-IN>

<id>
500 ladang ranjau tanpa menebak, semua bisa diselesaikan dengan logika.
</id>

<it-IT>
500 campi minati senza azzardo, risolvibili con la logica. Sfida del giorno.
</it-IT>

<ja-JP>
運に頼らない500面の地雷原。すべて論理だけで解ける。デイリー盤面と賢いヒント付き。
</ja-JP>

<pt-BR>
500 campos minados sem chute, todos resolvidos com lógica. Desafio diário.
</pt-BR>

<tr-TR>
Tahmin gerektirmeyen 500 mayın tarlası, hepsi mantıkla çözülür. Günlük alan.
</tr-TR>

<uk>
500 мінних полів без вгадування, усе розв'язує логіка. Щоденне поле й підказки.
</uk>

<zh-CN>
500 个无需猜测的雷区,全部可用逻辑解开。每日雷区与智能提示。
</zh-CN>

---

## FULL DESCRIPTION (≤4000 chars per locale)

_Grow → Store presence → Main store listing → Full description_

<en-US>
The first tap is always safe. The last one never needs luck.

Minesweeper is the classic mine-hunting logic puzzle, rebuilt so that every field can be cleared by reasoning alone. No coin-flip corners, no 50/50 endings: each of the 500 boards was checked by a logic solver from its starting tile to the final mine. Play offline, anywhere.

HOW IT WORKS
• Tap the marked ✕ to open your first area. It is always safe.
• Each number counts the mines touching that tile, diagonals included.
• Long-press, or switch on Flag mode, to mark a mine.
• Tap a number whose mines are all flagged to open the rest at once.
• Open every safe tile to clear the field.

500 FIELDS THAT GROW WITH YOU
Start on gentle 6×6 boards with five mines and work up through taller, denser fields to 30×16 expert boards with up to 104 mines. Early levels need only simple counting; later ones ask you to compare neighbouring numbers and watch the mine counter.

HINTS THAT NEVER GUESS
Stuck? A hint opens one tile that can be proven safe, or flags a mine that can be proven, and highlights the numbers that prove it with a one-line explanation. It also points out a misplaced flag.

MADE FOR A PHONE
• Tall, portrait-friendly boards
• Pinch to zoom and drag to pan on big fields, or fit the whole field on screen
• Crisp tiles and numbers at any zoom
• Satisfying cascade reveals, sound effects and optional vibration

STARS, DAILY FIELD AND ENDLESS
Earn up to three stars per field: one for clearing it, one for a clean sweep with no hints and no mines hit, and one for beating the par time. A new daily field arrives every day, small on Monday and expert on Sunday, and Endless mode keeps the boards coming after the campaign.

SEVEN THEMES
Survey, Canyon, Glacier, Orchid, Harvest, Ember and Midnight. Number colours are chosen to stay distinguishable for the common types of colour blindness.

Hit a mine? Keep your field with a rewarded video or a life and carry on.

Free to play with optional ads and in-app purchases.
</en-US>

<ar>
النقرة الأولى آمنة دائمًا، والأخيرة لا تحتاج أبدًا إلى الحظ.

Minesweeper هي لعبة الألغام المنطقية الكلاسيكية، أُعيد بناؤها بحيث يمكن تطهير كل حقل بالتفكير وحده. لا زوايا تعتمد على رمي العملة، ولا نهايات 50/50: كل لوحة من اللوحات الـ500 فحصها محلل منطقي من مربع البداية حتى آخر لغم. العب بدون إنترنت، في أي مكان.

طريقة اللعب
• انقر على المربع المميز بعلامة ✕ لفتح أول منطقة. إنه آمن دائمًا.
• كل رقم يعدّ الألغام الملامسة لذلك المربع، بما فيها القطرية.
• اضغط مطولًا، أو شغّل وضع العلم، لتضع علمًا على لغم.
• انقر على رقم وُضعت أعلام على كل ألغامه لتفتح بقية جيرانه دفعة واحدة.
• افتح كل المربعات الآمنة لتطهّر الحقل.

500 حقل تنمو معك
ابدأ بلوحات هادئة بحجم 6×6 فيها خمسة ألغام، ثم تقدّم عبر حقول أطول وأكثف حتى لوحات الخبراء 30×16 التي تضم حتى 104 ألغام. المستويات الأولى تحتاج إلى عدّ بسيط فقط، أما اللاحقة فتطلب منك مقارنة الأرقام المتجاورة ومراقبة عدّاد الألغام.

تلميحات لا تخمّن أبدًا
عالق؟ يفتح التلميح مربعًا يمكن إثبات أنه آمن، أو يضع علمًا على لغم يمكن إثباته، ويبرز الأرقام التي تثبت ذلك مع شرح من سطر واحد. كما ينبّهك إلى العلم الموضوع في غير مكانه.

مصممة للهاتف
• لوحات طولية تناسب الوضع العمودي
• قرّب بإصبعين واسحب للتحريك في الحقول الكبيرة، أو اعرض الحقل كله على الشاشة
• مربعات وأرقام واضحة بأي درجة تكبير
• فتح متتالٍ ممتع، ومؤثرات صوتية، واهتزاز اختياري

نجوم وحقل يومي ووضع لا نهائي
اربح حتى ثلاث نجوم في كل حقل: واحدة لتطهيره، وواحدة لإنهائه نظيفًا بلا تلميحات ودون إصابة أي لغم، وواحدة للتغلب على الوقت المستهدف. يصل حقل يومي جديد كل يوم، صغير يوم الاثنين وللخبراء يوم الأحد، ويواصل الوضع اللانهائي تقديم اللوحات بعد انتهاء الحملة.

سبعة أنماط
Survey وCanyon وGlacier وOrchid وHarvest وEmber وMidnight. ألوان الأرقام مختارة لتبقى مميزة مع أكثر أنواع عمى الألوان شيوعًا.

أصبت لغمًا؟ احتفظ بحقلك بمشاهدة فيديو مكافأة أو باستخدام حياة، وتابع اللعب.

مجانية اللعب مع إعلانات ومشتريات اختيارية داخل التطبيق.
</ar>

<de-DE>
Der erste Tipp ist immer sicher. Der letzte braucht nie Glück.

Minesweeper ist das klassische Logikrätsel um versteckte Minen, neu gebaut, damit sich jedes Feld allein durch Nachdenken räumen lässt. Keine Münzwurf-Ecken, kein 50/50 am Ende: Alle 500 Felder wurden von einem Logik-Löser vom Startfeld bis zur letzten Mine geprüft. Spielbar offline, überall.

SO FUNKTIONIERT ES
• Tippe auf das markierte ✕, um den ersten Bereich zu öffnen. Es ist immer sicher.
• Jede Zahl zählt die Minen, die dieses Feld berühren, diagonal eingeschlossen.
• Drücke lange oder schalte den Flaggenmodus ein, um eine Mine zu markieren.
• Tippe auf eine Zahl, deren Minen alle markiert sind, um den Rest auf einmal zu öffnen.
• Öffne jedes sichere Feld, um das Minenfeld zu räumen.

500 FELDER, DIE MIT DIR WACHSEN
Beginne mit sanften 6×6-Feldern mit fünf Minen und arbeite dich durch höhere, dichtere Felder bis zu 30×16-Expertenfeldern mit bis zu 104 Minen. Frühe Level brauchen nur einfaches Zählen, spätere verlangen, benachbarte Zahlen zu vergleichen und den Minenzähler im Blick zu behalten.

TIPPS, DIE NIE RATEN
Ein Tipp öffnet ein Feld, das beweisbar sicher ist, oder markiert eine beweisbare Mine und hebt die Zahlen hervor, die es beweisen, mit einer kurzen Erklärung. Er zeigt auch falsch gesetzte Flaggen.

FÜR DAS HANDY GEMACHT
• Hohe Felder im Hochformat
• Zoomen und Verschieben auf großen Feldern, oder das ganze Feld einpassen
• Scharfe Felder und Zahlen in jeder Zoomstufe
• Befriedigende Kaskaden, Soundeffekte und optionale Vibration

STERNE, TAGESFELD UND ENDLOS
Bis zu drei Sterne pro Feld: einer fürs Räumen, einer für einen sauberen Durchgang ohne Tipps und ohne Minentreffer, einer für die Zielzeit. Jeden Tag kommt ein neues Tagesfeld, montags klein und sonntags für Experten, und der Endlos-Modus liefert nach der Kampagne weitere Felder.

SIEBEN DESIGNS
Survey, Canyon, Glacier, Orchid, Harvest, Ember und Midnight. Die Zahlenfarben bleiben auch bei den häufigsten Formen der Farbenblindheit unterscheidbar.

Mine getroffen? Behalte dein Feld mit einem Belohnungsvideo oder einem Leben und spiel weiter.

Kostenlos spielbar, mit optionaler Werbung und In-App-Käufen.
</de-DE>

<es-419>
El primer toque siempre es seguro. El último nunca necesita suerte.

Minesweeper es el clásico rompecabezas lógico de minas ocultas, reconstruido para que cada campo se pueda despejar solo razonando. Sin esquinas a cara o cruz ni finales al 50/50: los 500 tableros fueron comprobados por un solucionador lógico desde la casilla inicial hasta la última mina. Juega sin conexión, donde quieras.

CÓMO SE JUEGA
• Toca la ✕ marcada para abrir tu primera zona. Siempre es segura.
• Cada número cuenta las minas que tocan esa casilla, incluidas las diagonales.
• Mantén pulsado, o activa el modo bandera, para marcar una mina.
• Toca un número con todas sus minas marcadas para abrir el resto de una vez.
• Abre todas las casillas seguras para despejar el campo.

500 CAMPOS QUE CRECEN CONTIGO
Empieza con tableros suaves de 6×6 y cinco minas, y avanza por campos más altos y densos hasta tableros expertos de 30×16 con hasta 104 minas. Los primeros niveles solo piden contar; los siguientes te hacen comparar números vecinos y vigilar el contador de minas.

PISTAS QUE NUNCA ADIVINAN
Una pista abre una casilla que se puede demostrar segura, o marca una mina demostrable, y resalta los números que lo prueban con una breve explicación. También señala una bandera mal puesta.

HECHO PARA EL TELÉFONO
• Tableros altos, cómodos en vertical
• Pellizca para hacer zoom y arrastra para moverte, o ajusta el campo completo a la pantalla
• Casillas y números nítidos en cualquier zoom
• Cascadas satisfactorias, efectos de sonido y vibración opcional

ESTRELLAS, CAMPO DIARIO E INFINITO
Hasta tres estrellas por campo: una por despejarlo, otra por una limpieza sin pistas ni minas pisadas y otra por superar el tiempo objetivo. Cada día llega un campo nuevo, pequeño el lunes y experto el domingo, y el modo Infinito sigue cuando terminas la campaña.

SIETE TEMAS
Survey, Canyon, Glacier, Orchid, Harvest, Ember y Midnight. Los colores de los números se distinguen también con los tipos más comunes de daltonismo.

¿Pisaste una mina? Conserva tu campo con un video con recompensa o una vida y sigue jugando.

Gratis, con anuncios opcionales y compras dentro de la app.
</es-419>

<fr-FR>
Le premier tap est toujours sûr. Le dernier n'a jamais besoin de chance.

Minesweeper est le grand classique de la logique et des mines cachées, reconstruit pour que chaque champ puisse être déblayé par le seul raisonnement. Pas de coin à pile ou face, pas de fin à 50/50 : les 500 grilles ont été vérifiées par un solveur logique de la case de départ jusqu'à la dernière mine. Jouez hors ligne, partout.

COMMENT JOUER
• Touchez le ✕ marqué pour ouvrir votre première zone. Il est toujours sûr.
• Chaque chiffre compte les mines qui touchent cette case, diagonales comprises.
• Appuyez longuement, ou activez le mode drapeau, pour marquer une mine.
• Touchez un chiffre dont toutes les mines sont marquées pour ouvrir le reste d'un coup.
• Ouvrez toutes les cases sûres pour déblayer le champ.

500 CHAMPS QUI GRANDISSENT AVEC VOUS
Commencez par de douces grilles 6×6 à cinq mines, puis montez vers des champs plus hauts et plus denses jusqu'aux grilles expertes 30×16 avec jusqu'à 104 mines. Les premiers niveaux demandent de simplement compter ; les suivants de comparer des chiffres voisins et de surveiller le compteur de mines.

DES INDICES QUI NE DEVINENT JAMAIS
Un indice ouvre une case dont la sûreté se prouve, ou marque une mine prouvable, et met en évidence les chiffres qui le prouvent avec une courte explication. Il signale aussi un drapeau mal placé.

PENSÉ POUR LE TÉLÉPHONE
• Grilles hautes, confortables en portrait
• Pincez pour zoomer et glissez pour vous déplacer, ou affichez tout le champ
• Cases et chiffres nets à tous les niveaux de zoom
• Cascades satisfaisantes, effets sonores et vibration en option

ÉTOILES, CHAMP DU JOUR ET INFINI
Jusqu'à trois étoiles par champ : une pour le déblayer, une pour un sans-faute sans indice ni mine touchée, une pour battre le temps cible. Un nouveau champ arrive chaque jour, petit le lundi et expert le dimanche, et le mode Infini prend le relais après la campagne.

SEPT THÈMES
Survey, Canyon, Glacier, Orchid, Harvest, Ember et Midnight. Les couleurs des chiffres restent distinguables pour les formes les plus courantes de daltonisme.

Une mine touchée ? Gardez votre champ grâce à une vidéo récompensée ou une vie, et continuez.

Gratuit, avec publicités facultatives et achats intégrés.
</fr-FR>

<hi-IN>
पहला टैप हमेशा सुरक्षित है। आख़िरी टैप को कभी किस्मत की ज़रूरत नहीं पड़ती।

Minesweeper छिपी माइनों वाली क्लासिक लॉजिक पहेली है, जिसे इस तरह नए सिरे से बनाया गया है कि हर फ़ील्ड सिर्फ़ सोच-समझकर साफ़ हो सके। सिक्का उछालने वाले कोने नहीं, 50/50 वाला अंत नहीं: सभी 500 बोर्ड एक लॉजिक सॉल्वर ने शुरुआती टाइल से आख़िरी माइन तक जाँचे हैं। ऑफ़लाइन खेलें, कहीं भी।

कैसे खेलें
• पहला हिस्सा खोलने के लिए ✕ वाली टाइल पर टैप करें। यह हमेशा सुरक्षित है।
• हर नंबर बताता है कि उस टाइल को छूने वाली कितनी माइन हैं, तिरछी भी शामिल।
• माइन पर झंडा लगाने के लिए लॉन्ग-प्रेस करें या फ़्लैग मोड चालू करें।
• जिस नंबर की सारी माइनों पर झंडे लगे हों, उस पर टैप करके बाकी टाइलें एक साथ खोलें।
• फ़ील्ड साफ़ करने के लिए हर सुरक्षित टाइल खोलें।

500 फ़ील्ड जो आपके साथ बढ़ते हैं
पाँच माइन वाले आसान 6×6 बोर्ड से शुरुआत करें और लंबे, घने फ़ील्ड से होते हुए 104 माइन तक वाले 30×16 एक्सपर्ट बोर्ड तक पहुँचें। शुरुआती लेवल में बस सीधी गिनती चाहिए; बाद के लेवल में पास-पास के नंबरों की तुलना करनी होती है और माइन काउंटर पर नज़र रखनी होती है।

हिंट जो कभी अंदाज़ा नहीं लगाते
अटक गए? हिंट ऐसी टाइल खोलता है जिसका सुरक्षित होना साबित किया जा सके, या ऐसी माइन पर झंडा लगाता है जो साबित हो सके, और एक लाइन की व्याख्या के साथ वे नंबर हाइलाइट करता है जो इसे साबित करते हैं। यह ग़लत जगह लगा झंडा भी बता देता है।

फ़ोन के लिए बनाया गया
• लंबे, पोर्ट्रेट के अनुकूल बोर्ड
• बड़े फ़ील्ड पर पिंच करके ज़ूम करें और खींचकर पैन करें, या पूरा फ़ील्ड स्क्रीन पर फ़िट करें
• किसी भी ज़ूम पर साफ़ टाइलें और नंबर
• मज़ेदार कैस्केड रिवील, साउंड इफ़ेक्ट और वैकल्पिक वाइब्रेशन

स्टार, डेली फ़ील्ड और एंडलेस
हर फ़ील्ड पर तीन तक स्टार कमाएँ: एक उसे साफ़ करने का, एक बिना हिंट और बिना माइन छुए साफ़ स्वीप का, और एक तय समय से पहले पूरा करने का। हर दिन एक नया डेली फ़ील्ड आता है, सोमवार को छोटा और रविवार को एक्सपर्ट, और कैंपेन के बाद एंडलेस मोड बोर्ड देता रहता है।

सात थीम
Survey, Canyon, Glacier, Orchid, Harvest, Ember और Midnight। नंबरों के रंग इस तरह चुने गए हैं कि रंग-अंधता के आम प्रकारों में भी वे अलग-अलग पहचाने जा सकें।

माइन पर टैप हो गया? रिवॉर्डेड वीडियो या एक लाइफ़ से अपना फ़ील्ड बचाएँ और खेलते रहें।

खेलने के लिए मुफ़्त, वैकल्पिक विज्ञापनों और इन-ऐप ख़रीदारी के साथ।
</hi-IN>

<id>
Ketukan pertama selalu aman. Ketukan terakhir tak pernah butuh keberuntungan.

Minesweeper adalah teka-teki logika klasik berburu ranjau, dibangun ulang agar setiap ladang bisa dibersihkan hanya dengan bernalar. Tidak ada sudut untung-untungan, tidak ada akhir 50/50: setiap dari 500 papan sudah diperiksa pemecah logika dari petak awal sampai ranjau terakhir. Main offline, di mana saja.

CARA BERMAIN
• Ketuk petak bertanda ✕ untuk membuka area pertama. Petak itu selalu aman.
• Setiap angka menghitung ranjau yang menyentuh petak itu, termasuk diagonal.
• Tekan lama, atau nyalakan Mode Bendera, untuk menandai ranjau.
• Ketuk angka yang semua ranjaunya sudah ditandai untuk membuka sisanya sekaligus.
• Buka semua petak aman untuk membersihkan ladang.

500 LADANG YANG TUMBUH BERSAMAMU
Mulai dari papan 6×6 yang ringan dengan lima ranjau, lalu naik melewati ladang yang lebih tinggi dan padat hingga papan ahli 30×16 dengan hingga 104 ranjau. Level awal cukup dengan hitungan sederhana; level berikutnya memintamu membandingkan angka yang bertetangga dan memperhatikan penghitung ranjau.

PETUNJUK YANG TIDAK PERNAH MENEBAK
Buntu? Petunjuk membuka satu petak yang bisa dibuktikan aman, atau menandai ranjau yang bisa dibuktikan, dan menyorot angka-angka yang membuktikannya dengan penjelasan satu baris. Petunjuk juga memberi tahu bendera yang salah tempat.

DIBUAT UNTUK PONSEL
• Papan tinggi yang nyaman dalam mode potret
• Cubit untuk zoom dan seret untuk menggeser di ladang besar, atau tampilkan seluruh ladang di layar
• Petak dan angka tetap tajam di zoom berapa pun
• Pembukaan beruntun yang memuaskan, efek suara, dan getaran opsional

BINTANG, LADANG HARIAN, DAN TANPA AKHIR
Raih hingga tiga bintang per ladang: satu karena menyelesaikannya, satu untuk sapuan bersih tanpa petunjuk dan tanpa kena ranjau, dan satu karena mengalahkan waktu target. Ladang harian baru datang setiap hari, kecil di hari Senin dan tingkat ahli di hari Minggu, dan mode Tanpa Akhir terus menyediakan papan setelah kampanye.

TUJUH TEMA
Survey, Canyon, Glacier, Orchid, Harvest, Ember, dan Midnight. Warna angka dipilih agar tetap bisa dibedakan untuk jenis buta warna yang umum.

Kena ranjau? Simpan ladangmu dengan video berhadiah atau satu nyawa, lalu lanjutkan.

Gratis dimainkan, dengan iklan dan pembelian dalam aplikasi yang opsional.
</id>

<it-IT>
Il primo tocco è sempre sicuro. L'ultimo non ha mai bisogno di fortuna.

Minesweeper è il classico rompicapo logico delle mine nascoste, ricostruito perché ogni campo si possa sgombrare solo ragionando. Niente angoli a testa o croce, niente finali al 50/50: tutte le 500 griglie sono state verificate da un risolutore logico dalla casella di partenza all'ultima mina. Gioca offline, ovunque.

COME SI GIOCA
• Tocca la ✕ segnata per aprire la prima zona. È sempre sicura.
• Ogni numero conta le mine che toccano quella casella, diagonali comprese.
• Tieni premuto, o attiva la modalità bandierina, per segnare una mina.
• Tocca un numero con tutte le mine segnate per aprire il resto in un colpo.
• Apri tutte le caselle sicure per sgombrare il campo.

500 CAMPI CHE CRESCONO CON TE
Parti da tranquille griglie 6×6 con cinque mine e sali attraverso campi più alti e fitti fino alle griglie esperte 30×16 con fino a 104 mine. I primi livelli chiedono solo di contare; i successivi di confrontare numeri vicini e tenere d'occhio il contatore delle mine.

SUGGERIMENTI CHE NON TIRANO A INDOVINARE
Un suggerimento apre una casella dimostrabilmente sicura, o segna una mina dimostrabile, ed evidenzia i numeri che lo provano con una breve spiegazione. Segnala anche una bandierina sbagliata.

PENSATO PER IL TELEFONO
• Griglie alte, comode in verticale
• Pizzica per lo zoom e trascina per spostarti, o adatta tutto il campo allo schermo
• Caselle e numeri nitidi a ogni zoom
• Cascate appaganti, effetti sonori e vibrazione facoltativa

STELLE, CAMPO DEL GIORNO E INFINITO
Fino a tre stelle per campo: una per sgombrarlo, una per un percorso pulito senza suggerimenti né mine colpite, una per battere il tempo obiettivo. Ogni giorno arriva un nuovo campo, piccolo il lunedì ed esperto la domenica, e la modalità Infinita continua dopo la campagna.

SETTE TEMI
Survey, Canyon, Glacier, Orchid, Harvest, Ember e Midnight. I colori dei numeri restano distinguibili per le forme più comuni di daltonismo.

Hai colpito una mina? Tieni il campo con un video premio o una vita e continua.

Gratis, con pubblicità facoltativa e acquisti in-app.
</it-IT>

<ja-JP>
最初のタップは必ず安全。最後のタップに運はいらない。

Minesweeper は地雷探しの定番論理パズルを、どの盤面も推理だけでクリアできるように作り直したゲームです。運任せの角も、最後の二択もありません。500面すべてを、論理ソルバーがスタートのマスから最後の地雷まで検証しています。オフラインでどこでも遊べます。

遊び方
• ✕ の付いたマスをタップして最初のエリアを開けます。このマスは必ず安全です。
• 数字は、そのマスに接している地雷の数です(斜めも含みます)。
• 長押し、または旗モードをオンにして、地雷に旗を立てます。
• 地雷にすべて旗が立った数字をタップすると、残りのマスをまとめて開けられます。
• 安全なマスをすべて開ければクリアです。

あなたと一緒に育つ500の盤面
地雷5個のやさしい6×6から始まり、縦に長く密度の高い盤面を経て、地雷が最大104個ある30×16のエキスパート盤面へ。序盤は単純な数え方だけで解けますが、後半は隣り合う数字を見比べ、残り地雷数にも目を配る必要があります。

決して当てずっぽうにしないヒント
行き詰まったら?ヒントは安全だと証明できるマスを1つ開けるか、証明できる地雷に旗を立て、その根拠となる数字を一行の説明つきでハイライトします。間違った場所の旗も教えてくれます。

スマホのために設計
• 縦画面に合う縦長の盤面
• 大きな盤面はピンチで拡大、ドラッグで移動。盤面全体を画面に収めることも
• どの倍率でもくっきりしたマスと数字
• 気持ちのいい連鎖オープン、効果音、オンオフできる振動

星、デイリー盤面、エンドレス
1つの盤面で最大3つの星:クリアで1つ、ヒントなし・地雷なしのクリーンクリアで1つ、目標タイム以内で1つ。毎日新しいデイリー盤面が届き、月曜は小さく、日曜はエキスパート。キャンペーンの後もエンドレスモードで盤面が続きます。

7つのテーマ
Survey、Canyon、Glacier、Orchid、Harvest、Ember、Midnight。数字の色は、よくあるタイプの色覚特性でも見分けやすいように選んでいます。

地雷を踏んだ?リワード動画かライフ1つで盤面を残したまま続けられます。

基本プレイ無料。広告とアプリ内課金はオプションです。
</ja-JP>

<pt-BR>
O primeiro toque é sempre seguro. O último nunca depende de sorte.

Minesweeper é o clássico quebra-cabeça lógico de minas escondidas, refeito para que todo campo possa ser limpo só com raciocínio. Nada de cantos no cara ou coroa nem finais no 50/50: os 500 tabuleiros foram verificados por um solucionador lógico da casa inicial até a última mina. Jogue offline, em qualquer lugar.

COMO JOGAR
• Toque no ✕ marcado para abrir a primeira área. Ele é sempre seguro.
• Cada número conta as minas que tocam aquela casa, incluindo as diagonais.
• Toque e segure, ou ative o modo bandeira, para marcar uma mina.
• Toque num número com todas as minas marcadas para abrir o resto de uma vez.
• Abra todas as casas seguras para limpar o campo.

500 CAMPOS QUE CRESCEM COM VOCÊ
Comece em tabuleiros tranquilos de 6×6 com cinco minas e avance por campos mais altos e densos até tabuleiros de especialista de 30×16 com até 104 minas. Os primeiros níveis pedem só contagem; os seguintes pedem comparar números vizinhos e ficar de olho no contador de minas.

DICAS QUE NUNCA CHUTAM
Uma dica abre uma casa que pode ser provada segura, ou marca uma mina que pode ser provada, e destaca os números que provam isso com uma explicação curta. Ela também aponta uma bandeira errada.

FEITO PARA O CELULAR
• Tabuleiros altos, confortáveis na vertical
• Pinça para dar zoom e arraste para mover, ou encaixe o campo inteiro na tela
• Casas e números nítidos em qualquer zoom
• Cascatas satisfatórias, efeitos sonoros e vibração opcional

ESTRELAS, CAMPO DIÁRIO E INFINITO
Até três estrelas por campo: uma por limpar, uma por uma partida limpa sem dicas e sem pisar em minas, e uma por bater o tempo-alvo. Um campo novo chega todo dia, pequeno na segunda e de especialista no domingo, e o modo Infinito continua depois da campanha.

SETE TEMAS
Survey, Canyon, Glacier, Orchid, Harvest, Ember e Midnight. As cores dos números continuam distinguíveis nos tipos mais comuns de daltonismo.

Pisou numa mina? Mantenha seu campo com um vídeo premiado ou uma vida e continue.

Grátis, com anúncios opcionais e compras no app.
</pt-BR>

<tr-TR>
İlk dokunuş her zaman güvenli. Sonuncusu asla şansa ihtiyaç duymaz.

Minesweeper, klasik mayın avı mantık bulmacasının her alanın yalnızca akıl yürüterek temizlenebileceği şekilde yeniden yapılmış hâli. Yazı-tura köşeleri yok, 50/50 bitişler yok: 500 tahtanın her biri bir mantık çözücüyle başlangıç karesinden son mayına kadar denetlendi. Çevrimdışı, her yerde oyna.

NASIL OYNANIR
• İlk bölgeyi açmak için ✕ işaretli kareye dokun. Her zaman güvenlidir.
• Her sayı, o kareye değen mayınları sayar; çaprazlar da dahil.
• Mayını işaretlemek için uzun bas ya da Bayrak modunu aç.
• Tüm mayınları işaretlenmiş bir sayıya dokunarak kalan kareleri tek seferde aç.
• Alanı temizlemek için tüm güvenli kareleri aç.

SENİNLE BÜYÜYEN 500 ALAN
Beş mayınlı sakin 6×6 tahtalarla başla; daha uzun ve daha yoğun alanlardan geçerek 104 mayına kadar içeren 30×16 uzman tahtalarına ulaş. İlk bölümler yalnızca basit sayma ister; sonrakiler komşu sayıları karşılaştırmanı ve mayın sayacını izlemeni gerektirir.

ASLA TAHMİN ETMEYEN İPUÇLARI
Takıldın mı? İpucu, güvenli olduğu kanıtlanabilen bir kareyi açar ya da kanıtlanabilen bir mayını işaretler; bunu kanıtlayan sayıları tek satırlık bir açıklamayla vurgular. Yanlış yere konmuş bir bayrağı da gösterir.

TELEFON İÇİN TASARLANDI
• Dikey ekrana uygun uzun tahtalar
• Büyük alanlarda iki parmakla yakınlaştır ve sürükleyerek kaydır ya da tüm alanı ekrana sığdır
• Her yakınlaştırmada keskin kareler ve sayılar
• Tatmin edici zincirleme açılışlar, ses efektleri ve isteğe bağlı titreşim

YILDIZLAR, GÜNLÜK ALAN VE SONSUZ MOD
Her alanda üç yıldıza kadar kazan: biri temizlediğin için, biri ipucu kullanmadan ve mayına basmadan yaptığın temiz tarama için, biri de hedef süreyi geçtiğin için. Her gün yeni bir günlük alan gelir; pazartesi küçük, pazar uzman seviyesinde. Sonsuz mod ise kampanyadan sonra da tahta getirmeye devam eder.

YEDİ TEMA
Survey, Canyon, Glacier, Orchid, Harvest, Ember ve Midnight. Sayı renkleri, renk körlüğünün yaygın türlerinde de ayırt edilebilecek şekilde seçildi.

Mayına mı bastın? Ödüllü bir video ya da bir canla alanını koru ve devam et.

Ücretsiz oynanır; isteğe bağlı reklamlar ve uygulama içi satın almalar içerir.
</tr-TR>

<uk>
Перший дотик завжди безпечний. Останньому ніколи не потрібна удача.

Minesweeper — класична логічна головоломка про пошук мін, перебудована так, щоб кожне поле можна було розчистити самими лише міркуваннями. Жодних кутів навмання, жодних фіналів 50/50: кожне з 500 полів перевірив логічний розв'язувач від стартової клітинки до останньої міни. Грайте офлайн, будь-де.

ЯК ГРАТИ
• Торкніться клітинки з позначкою ✕, щоб відкрити першу ділянку. Вона завжди безпечна.
• Кожне число показує, скільки мін торкається цієї клітинки, включно з діагоналями.
• Натисніть і утримуйте або ввімкніть режим прапорця, щоб позначити міну.
• Торкніться числа, усі міни якого позначено, щоб відкрити решту сусідів одразу.
• Відкрийте всі безпечні клітинки, щоб розчистити поле.

500 ПОЛІВ, ЩО РОСТУТЬ РАЗОМ ІЗ ВАМИ
Почніть із легких полів 6×6 з п'ятьма мінами й пройдіть крізь вищі та щільніші поля до експертних 30×16, де до 104 мін. Ранні рівні потребують лише простого підрахунку; пізніші вимагають порівнювати сусідні числа й стежити за лічильником мін.

ПІДКАЗКИ, ЯКІ НІКОЛИ НЕ ВГАДУЮТЬ
Застрягли? Підказка відкриває клітинку, безпечність якої можна довести, або позначає міну, яку можна довести, і підсвічує числа, що це доводять, з поясненням в один рядок. Вона також вказує на хибно поставлений прапорець.

СТВОРЕНО ДЛЯ ТЕЛЕФОНА
• Високі поля, зручні у вертикальній орієнтації
• Масштабуйте щипком і перетягуйте великі поля або вмістіть усе поле на екрані
• Чіткі клітинки й числа за будь-якого масштабу
• Приємні каскадні відкриття, звукові ефекти та вібрація за бажанням

ЗІРКИ, ЩОДЕННЕ ПОЛЕ Й НЕСКІНЧЕННИЙ РЕЖИМ
Отримуйте до трьох зірок за поле: одну за розчищення, одну за чисте проходження без підказок і без влучань у міни, і одну за перевершений цільовий час. Щодня з'являється нове щоденне поле — маленьке в понеділок і експертне в неділю, а нескінченний режим постачає поля й після кампанії.

СІМ ТЕМ
Survey, Canyon, Glacier, Orchid, Harvest, Ember і Midnight. Кольори чисел підібрано так, щоб їх можна було розрізнити за найпоширеніших типів дальтонізму.

Натрапили на міну? Збережіть поле завдяки відео з винагородою або життю й грайте далі.

Безкоштовна гра з необов'язковою рекламою та покупками в застосунку.
</uk>

<zh-CN>
第一次点击永远安全,最后一步也从不靠运气。

Minesweeper 是经典的找雷逻辑游戏,经过重新打造,让每一个雷区都能只凭推理清除。没有靠抛硬币的角落,没有五五开的结局:全部 500 个棋盘都由逻辑求解器从起始格一路验证到最后一颗雷。可离线游玩,随时随地。

玩法
• 点击标有 ✕ 的格子,打开第一片区域。它永远是安全的。
• 每个数字表示与该格相邻的雷的数量,包括斜向。
• 长按,或开启插旗模式,为地雷插旗。
• 点击周围地雷已全部插旗的数字,一次翻开其余的格子。
• 翻开所有安全格,即可清除雷区。

与你一同成长的 500 个雷区
从只有五颗雷的轻松 6×6 棋盘开始,经过更高、更密的雷区,一路挑战最多 104 颗雷的 30×16 专家棋盘。前期关卡只需要简单计数;后期则需要比较相邻的数字,并留意剩余雷数。

从不瞎猜的提示
卡住了?提示会打开一个可以证明安全的格子,或为一颗可以证明的雷插旗,并高亮作为依据的数字,附上一行说明。它还会指出插错位置的旗子。

为手机打造
• 适合竖屏的纵向棋盘
• 大雷区可双指缩放、拖动浏览,也可让整个雷区铺满屏幕
• 任何缩放下格子和数字都清晰锐利
• 畅快的连锁翻开、音效以及可选的振动

星级、每日雷区与无尽模式
每个雷区最多可得三颗星:清除得一颗,不用提示且未踩雷的完美清扫得一颗,在目标时间内完成再得一颗。每天都有新的每日雷区,周一较小,周日为专家级;完成战役后,无尽模式还会源源不断地提供新棋盘。

七种主题
Survey、Canyon、Glacier、Orchid、Harvest、Ember 和 Midnight。数字配色经过挑选,在常见类型的色觉障碍下也能区分。

踩到雷?观看奖励视频或使用一条命,即可保留棋盘继续游戏。

免费游玩,含可选广告和应用内购买。
</zh-CN>

---

## SUBTITLE (≤30 chars per locale)

_Apple App Store Connect → App Information → Subtitle_

<en-US>
No-guess logic, 500 fields
</en-US>

<ar>
منطق بلا تخمين، 500 حقل
</ar>

<de-DE>
Logik ohne Raten, 500 Felder
</de-DE>

<es-419>
Lógica sin adivinar, 500
</es-419>

<fr-FR>
Logique sans hasard, 500
</fr-FR>

<hi-IN>
बिना अंदाज़े, 500 लॉजिक फ़ील्ड
</hi-IN>

<id>
Logika tanpa tebak, 500 ladang
</id>

<it-IT>
Logica senza azzardo, 500
</it-IT>

<ja-JP>
運ゼロの論理パズル、500面
</ja-JP>

<pt-BR>
Lógica sem chute, 500 campos
</pt-BR>

<tr-TR>
Tahminsiz mantık, 500 alan
</tr-TR>

<uk>
Без вгадування, 500 полів
</uk>

<zh-CN>
无需猜测的逻辑扫雷,500关
</zh-CN>

---

## KEYWORDS (≤100 chars per locale)

_Apple App Store Connect → Version → Keywords_

<en-US>
minesweeper,mines,no guess,logic puzzle,flags,offline,classic,brain game,daily puzzle,relaxing
</en-US>

<ar>
كاسحة الألغام,ألغام,بلا تخمين,لغز منطقي,أعلام,بدون إنترنت,كلاسيكي,ألعاب ذكاء,لغز يومي,مريح
</ar>

<de-DE>
minesweeper,minen,ohne raten,logikrätsel,flaggen,offline,klassiker,denkspiel,täglich,entspannend
</de-DE>

<es-419>
buscaminas,minesweeper,minas,sin adivinar,lógica,banderas,sin conexión,clásico,diario,relajante
</es-419>

<fr-FR>
démineur,minesweeper,mines,sans hasard,logique,drapeaux,hors ligne,classique,défi du jour,zen
</fr-FR>

<hi-IN>
माइनस्वीपर,minesweeper,माइन,बिना अंदाज़े,लॉजिक पज़ल,झंडा,ऑफ़लाइन,क्लासिक,दिमागी खेल,डेली पज़ल
</hi-IN>

<id>
minesweeper,ranjau,tanpa tebak,teka-teki logika,bendera,offline,klasik,asah otak,harian,santai
</id>

<it-IT>
campo minato,minesweeper,mine,senza azzardo,logica,bandierine,offline,classico,giornaliero,relax
</it-IT>

<ja-JP>
マインスイーパー,マインスイーパ,地雷,運ゼロ,論理パズル,旗,オフライン,定番,脳トレ,デイリー
</ja-JP>

<pt-BR>
campo minado,minesweeper,minas,sem chute,lógica,bandeiras,offline,clássico,desafio diário,relaxar
</pt-BR>

<tr-TR>
mayın tarlası,minesweeper,mayın,tahminsiz,mantık bulmacası,bayrak,çevrimdışı,klasik,zeka,günlük
</tr-TR>

<uk>
сапер,minesweeper,міни,без вгадування,логічна головоломка,прапорці,офлайн,класика,щоденна
</uk>

<zh-CN>
扫雷,minesweeper,地雷,无猜测,逻辑解谜,插旗,离线,经典,益智,每日挑战
</zh-CN>

---

## PROMOTIONAL TEXT (≤170 chars per locale)

_Apple App Store Connect → Version → Promotional Text_

<en-US>
Every field can be cleared by logic alone, no 50/50 guesses. 500 boards from 6×6 to 30×16, a daily field and hints that show why a tile is safe.
</en-US>

<ar>
كل حقل يمكن تطهيره بالمنطق وحده، بلا تخمين 50/50. ‏500 لوحة من 6×6 إلى 30×16، وحقل يومي، وتلميحات تشرح لماذا المربع آمن.
</ar>

<de-DE>
Jedes Feld lässt sich allein mit Logik räumen, ohne 50/50-Raten. 500 Felder von 6×6 bis 30×16, ein Tagesfeld und Tipps, die zeigen, warum ein Feld sicher ist.
</de-DE>

<es-419>
Cada campo se despeja solo con lógica, sin adivinar al 50/50. 500 tableros de 6×6 a 30×16, un campo diario y pistas que muestran por qué una casilla es segura.
</es-419>

<fr-FR>
Chaque champ se déblaie par la seule logique, sans pari à 50/50. 500 grilles de 6×6 à 30×16, un champ du jour et des indices qui montrent pourquoi une case est sûre.
</fr-FR>

<hi-IN>
हर फ़ील्ड सिर्फ़ लॉजिक से साफ़ हो सकता है, कोई 50/50 अंदाज़ा नहीं। 6×6 से 30×16 तक 500 बोर्ड, रोज़ का फ़ील्ड और हिंट जो बताते हैं कि कोई टाइल सुरक्षित क्यों है।
</hi-IN>

<id>
Setiap ladang bisa dibersihkan hanya dengan logika, tanpa tebakan 50/50. 500 papan dari 6×6 sampai 30×16, ladang harian, dan petunjuk yang menjelaskan kenapa petak aman.
</id>

<it-IT>
Ogni campo si sgombra solo con la logica, senza azzardi al 50/50. 500 griglie da 6×6 a 30×16, un campo del giorno e suggerimenti che spiegano perché una casella è sicura.
</it-IT>

<ja-JP>
どの盤面も論理だけで解ける、二択の運任せなし。6×6から30×16までの500面、毎日のデイリー盤面、マスが安全な理由を示すヒント。
</ja-JP>

<pt-BR>
Todo campo pode ser limpo só com lógica, sem chutar no 50/50. 500 tabuleiros de 6×6 a 30×16, um campo diário e dicas que mostram por que uma casa é segura.
</pt-BR>

<tr-TR>
Her alan yalnızca mantıkla temizlenebilir, 50/50 tahmin yok. 6×6'dan 30×16'ya 500 tahta, günlük alan ve bir karenin neden güvenli olduğunu gösteren ipuçları.
</tr-TR>

<uk>
Кожне поле можна розчистити лише логікою, без вгадування 50/50. 500 полів від 6×6 до 30×16, щоденне поле й підказки, що пояснюють, чому клітинка безпечна.
</uk>

<zh-CN>
每个雷区都能只靠逻辑清除,没有五五开的运气局。从 6×6 到 30×16 共 500 个棋盘,每日雷区,以及告诉你格子为何安全的提示。
</zh-CN>

---
