# BillSplit — store paste sheet

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
Bill Split 1.0, built from scratch:
• Itemised splits: add items and tap who shared each one
• Shared items split evenly or by custom shares
• Tax and tip as a percentage or an amount, in proportion or evenly
• Largest-remainder rounding, so shares add up to the bill exactly
• Share a plain-text summary
• Saved groups and bill history, currency picker
• Pro (one-time): unlimited groups and history, CSV export, accents, no ads
</en-US>

<ar>
Bill Split 1.0، مبني من الصفر:
• تقسيم حسب الأصناف: أضف الأصناف واضغط على من شاركها
• الأصناف المشتركة بالتساوي أو بحصص مخصّصة
• الضريبة والإكرامية كنسبة أو مبلغ، بالتناسب أو بالتساوي
• تقريب بطريقة أكبر باقٍ لتجمع الحصص الفاتورة بالضبط
• مشاركة ملخّص نصي
• مجموعات محفوظة وسجل واختيار العملة
• Pro (دفعة واحدة): مجموعات وسجل بلا حدود وتصدير CSV وألوان وبلا إعلانات
</ar>

<de-DE>
Bill Split 1.0, komplett neu gebaut:
• Rechnung nach Posten teilen: Posten hinzufügen, antippen, wer sie geteilt hat
• Geteilte Posten gleichmäßig oder mit eigenen Anteilen
• Steuer und Trinkgeld als Prozent oder Betrag, anteilig oder gleichmäßig
• Rundung nach dem größten Rest: Die Anteile ergeben die Rechnung exakt
• Zusammenfassung als Text teilen
• Gespeicherte Gruppen, Verlauf, Währungswahl
• Pro (einmalig): unbegrenzte Gruppen und Verlauf, CSV-Export, Akzentfarben, keine Werbung
</de-DE>

<es-419>
Bill Split 1.0, hecha desde cero:
• Cuenta por artículo: añade artículos y toca quién los compartió
• Artículos compartidos a partes iguales o personalizadas
• Impuesto y propina en porcentaje o importe, proporcional o igual
• Redondeo por mayor resto: las partes suman la cuenta exactamente
• Comparte un resumen en texto
• Grupos guardados, historial y selector de moneda
• Pro (pago único): grupos e historial ilimitados, CSV, acentos, sin anuncios
</es-419>

<fr-FR>
Bill Split 1.0, entièrement repensée :
• Partage par article : ajoutez les articles et touchez qui les a partagés
• Articles partagés à parts égales ou personnalisées
• Taxes et pourboire en pourcentage ou en montant, au prorata ou à parts égales
• Arrondi au plus fort reste : les parts font exactement l'addition
• Partage d'un récapitulatif en texte
• Groupes enregistrés, historique, choix de la devise
• Pro (achat unique) : groupes et historique illimités, export CSV, couleurs, sans pub
</fr-FR>

<hi-IN>
Bill Split 1.0, शुरू से नया:
• आइटम वार बँटवारा: आइटम जोड़ें और चुनें किसने बाँटा
• साझा आइटम बराबर या कस्टम हिस्सों में
• टैक्स और टिप प्रतिशत या राशि में, अनुपात से या बराबर
• सबसे बड़े शेष वाली राउंडिंग: हिस्से बिल के ठीक बराबर
• सारांश टेक्स्ट में शेयर करें
• सेव समूह, इतिहास और मुद्रा चयन
• Pro (एक बार): असीमित समूह और इतिहास, CSV, रंग, बिना विज्ञापन
</hi-IN>

<id>
Bill Split 1.0, dibuat dari nol:
• Bagi per item: tambahkan item dan ketuk siapa yang ikut
• Item bersama dibagi sama rata atau dengan bagian khusus
• Pajak dan tip berupa persen atau jumlah, proporsional atau sama rata
• Pembulatan sisa terbesar, jadi semua bagian pas sama dengan tagihan
• Bagikan ringkasan teks
• Grup tersimpan, riwayat, dan pilihan mata uang
• Pro (sekali bayar): grup dan riwayat tanpa batas, CSV, warna, tanpa iklan
</id>

<it-IT>
Bill Split 1.0, rifatta da zero:
• Conto per voce: aggiungi le voci e tocca chi le ha condivise
• Voci condivise in parti uguali o personalizzate
• Tasse e mancia in percentuale o importo, proporzionali o uguali
• Arrotondamento col resto più grande: le quote sommano esattamente il conto
• Condividi un riepilogo testuale
• Gruppi salvati, cronologia, scelta della valuta
• Pro (acquisto singolo): gruppi e cronologia illimitati, CSV, colori, senza pubblicità
</it-IT>

<ja-JP>
Bill Split 1.0(全面新作):
• 品目ごとの割り勘:品目を追加して分担者をタップ
• 共有品目は均等または比率指定で分割
• 税とチップは割合または金額、比例配分または均等
• 最大剰余法の端数処理で合計が請求額と一致
• テキストでまとめを共有
• グループ保存、履歴、通貨の選択
• Pro(買い切り):グループ・履歴無制限、CSV、アクセントカラー、広告なし
</ja-JP>

<pt-BR>
Bill Split 1.0, feito do zero:
• Conta por item: adicione itens e toque em quem dividiu
• Itens compartilhados em partes iguais ou personalizadas
• Imposto e gorjeta em porcentagem ou valor, proporcional ou igual
• Arredondamento pelo maior resto: as partes somam a conta exatamente
• Compartilhe um resumo em texto
• Grupos salvos, histórico e seletor de moeda
• Pro (compra única): grupos e histórico ilimitados, CSV, cores, sem anúncios
</pt-BR>

<tr-TR>
Bill Split 1.0, sıfırdan yapıldı:
• Kalem kalem bölme: kalemleri ekleyin, paylaşanlara dokunun
• Ortak kalemler eşit ya da özel paylarla bölünür
• Vergi ve bahşiş yüzde veya tutar, orantılı ya da eşit
• En büyük kalan yöntemiyle yuvarlama: paylar hesabı tam tutar
• Özeti metin olarak paylaşın
• Kayıtlı gruplar, geçmiş ve para birimi seçimi
• Pro (tek seferlik): sınırsız grup ve geçmiş, CSV, renkler, reklamsız
</tr-TR>

<uk>
Bill Split 1.0, створено з нуля:
• Поділ по позиціях: додайте позиції й торкніться тих, хто ділив
• Спільні позиції порівну або власними частками
• Податок і чайові у відсотках чи сумою, пропорційно або порівну
• Округлення за найбільшим залишком: частки дають суму рахунку точно
• Підсумок можна надіслати текстом
• Збережені групи, історія, вибір валюти
• Pro (одноразово): необмежені групи й історія, CSV, кольори, без реклами
</uk>

<zh-CN>
Bill Split 1.0，全新打造:
• 按菜品分账:添加菜品，点选分摊的人
• 共享菜品可平均分，也可自定义份额
• 税费和小费可按百分比或金额，按比例或平均分摊
• 采用最大余数法取整，各人金额相加正好等于账单
• 以文本分享汇总
• 保存群组、历史账单、选择货币
• Pro(一次性购买):群组和历史无限、CSV 导出、主题色、无广告
</zh-CN>

---

## SHORT DESCRIPTION (≤80 chars per locale)

_Grow → Store presence → Main store listing → Short description_

<en-US>
Split a bill by item, with tax and tip. Shares add up to the cent. Offline.
</en-US>

<ar>
قسّم الفاتورة حسب الأصناف مع الضريبة والإكرامية. دقيقة حتى السنت. بلا إنترنت.
</ar>

<de-DE>
Rechnung nach Posten teilen, mit Steuer und Trinkgeld. Centgenau. Offline.
</de-DE>

<es-419>
Divide la cuenta por artículo, con impuesto y propina. Exacta al centavo.
</es-419>

<fr-FR>
Partagez l'addition par article, taxes et pourboire inclus. Au centime près.
</fr-FR>

<hi-IN>
आइटम के हिसाब से बिल बाँटें, टैक्स और टिप के साथ। पाई-पाई सही। ऑफ़लाइन।
</hi-IN>

<id>
Bagi tagihan per item, dengan pajak dan tip. Pas sampai sen. Tanpa internet.
</id>

<it-IT>
Dividi il conto voce per voce, con tasse e mancia. Esatto al centesimo. Offline.
</it-IT>

<ja-JP>
品目ごとの割り勘。税とチップ込みで、合計は1円(1セント)単位でぴったり。オフライン対応。
</ja-JP>

<pt-BR>
Divida a conta por item, com imposto e gorjeta. Exata ao centavo. Sem internet.
</pt-BR>

<tr-TR>
Hesabı kalem kalem böl, vergi ve bahşiş dahil. Kuruşu kuruşuna. Çevrimdışı.
</tr-TR>

<uk>
Діліть рахунок по позиціях, з податком і чайовими. Точно до копійки. Офлайн.
</uk>

<zh-CN>
按菜品分账，含税费和小费。精确到分，合计分毫不差。无需联网。
</zh-CN>

---

## FULL DESCRIPTION (≤4000 chars per locale)

_Grow → Store presence → Main store listing → Full description_

<en-US>
Four friends, one receipt, no arguments. Bill Split works out what each person owes, down to the cent: add the items, tap who shared each one, and let tax and tip fall where they belong.

ITEM BY ITEM
• Add each dish or drink with its price
• Tap the people who shared it: one person, a few, or everyone
• Shared items split evenly, or by custom shares (2 for a double portion, 1 for a normal one)
• Anything not yet assigned is flagged and left out of the total

TAX AND TIP
• Enter tax and tip as a percentage or a fixed amount
• Share them in proportion to what each person ordered, or evenly
• Calculate the tip on the items only, or on items plus tax

EXACT TO THE CENT
• Items, tax and tip are each rounded with the largest-remainder method: whole cents first, then the leftover cents go to the largest fractions
• The per-person totals always add up to the bill exactly, and the app shows you the check
• The method is explained on screen, so there are no mystery pennies

SHARE IT
• Send a plain-text summary with the total and what each person owes
• See every person's items, tax and tip in a breakdown

GROUPS AND HISTORY
• Save the people you split with often and load them into any bill
• Keep past bills and open them again later
• Pick your currency. This changes formatting only; the app never uses live exchange rates

PRIVATE AND OFFLINE
• No account, no sign-in. Everything stays on your phone and works without internet
• Back up to text you can copy or share, and restore it on any device
• Light and dark themes, accent colors, adjustable text size, 13 languages

BILL SPLIT PRO: one-time purchase, no subscription
• Unlimited saved groups (the free plan holds 3)
• Unlimited bill history (the free plan keeps 10)
• CSV export of your history
• Extra accent colors and no ads

Remove Ads is also available on its own as a one-time purchase.
</en-US>

<ar>
أربعة أصدقاء، فاتورة واحدة، بلا خلافات. يحسب Bill Split ما يدين به كل شخص حتى السنت: أضف الأصناف، واضغط على من شاركها، ودع الضريبة والإكرامية تذهب إلى مكانها الصحيح.

صنفًا صنفًا
• أضف كل طبق أو مشروب مع سعره
• اضغط على من شاركه: شخص واحد أو عدة أشخاص أو الجميع
• الأصناف المشتركة تُقسَّم بالتساوي أو بحصص مخصّصة (2 لحصة مضاعفة و1 لحصة عادية)
• ما لم يُسنَد بعد يظهر بتنبيه ويُستبعد من الإجمالي

الضريبة والإكرامية
• أدخل الضريبة والإكرامية كنسبة مئوية أو مبلغ ثابت
• وزّعهما بالتناسب مع ما طلبه كل شخص، أو بالتساوي
• احسب الإكرامية على الأصناف فقط أو على الأصناف مع الضريبة

بدقة السنت
• تُقرَّب الأصناف والضريبة والإكرامية كلٌّ على حدة بطريقة أكبر باقٍ: السنتات الكاملة أولًا، ثم تذهب السنتات المتبقية إلى أكبر الكسور
• مجموع حصص الأشخاص يساوي الفاتورة بالضبط دائمًا، ويعرض التطبيق لك التحقق
• تُشرح الطريقة على الشاشة، فلا سنتات غامضة

شارك الملخّص
• أرسل ملخّصًا نصيًا بالإجمالي وما يدين به كل شخص
• شاهد أصناف كل شخص وضريبته وإكراميته في تفصيل واضح

المجموعات والسجل
• احفظ الأشخاص الذين تقسّم معهم كثيرًا وحمّلهم في أي فاتورة
• احتفظ بالفواتير السابقة وافتحها لاحقًا
• اختر عملتك. هذا يغيّر التنسيق فقط؛ لا يستخدم التطبيق أسعار صرف مباشرة

خاص وبلا إنترنت
• بلا حساب وبلا تسجيل دخول. كل شيء يبقى على هاتفك ويعمل بلا إنترنت
• انسخ احتياطيًا كنص يمكنك نسخه أو مشاركته واستعده على أي جهاز
• سمات فاتحة وداكنة وألوان تمييز وحجم نص قابل للضبط و13 لغة

BILL SPLIT PRO: شراء لمرة واحدة بلا اشتراك
• مجموعات محفوظة بلا حدود (الخطة المجانية تتسع لـ 3)
• سجل فواتير بلا حدود (الخطة المجانية تحتفظ بـ 10)
• تصدير السجل بصيغة CSV
• ألوان تمييز إضافية وبلا إعلانات

وتتوفر «إزالة الإعلانات» أيضًا وحدها كشراء لمرة واحدة.
</ar>

<de-DE>
Vier Freunde, eine Rechnung, kein Streit. Bill Split rechnet centgenau aus, was jede Person zahlt: Posten eintragen, antippen, wer sie geteilt hat, und Steuer und Trinkgeld landen dort, wo sie hingehören.

POSTEN FÜR POSTEN
• Jedes Gericht und Getränk mit Preis erfassen
• Antippen, wer geteilt hat: eine Person, ein paar oder alle
• Geteilte Posten gleichmäßig oder mit eigenen Anteilen (2 für eine doppelte Portion, 1 für eine normale)
• Noch nicht zugeordnete Posten werden markiert und nicht mitgerechnet

STEUER UND TRINKGELD
• Steuer und Trinkgeld als Prozentwert oder fester Betrag
• Anteilig nach Bestellung oder gleichmäßig auf alle verteilen
• Trinkgeld nur auf die Posten oder auf Posten plus Steuer berechnen

CENTGENAU
• Posten, Steuer und Trinkgeld werden jeweils nach dem Verfahren des größten Rests gerundet: erst die ganzen Cent, dann gehen die übrigen Cent an die größten Nachkommaanteile
• Die Summe der Einzelbeträge ergibt immer genau die Rechnung, und die App zeigt die Kontrolle
• Das Verfahren wird in der App erklärt, ohne geheimnisvolle Cent

TEILEN
• Zusammenfassung als Text mit Gesamtbetrag und Anteil jeder Person senden
• Posten, Steuer und Trinkgeld jeder Person in der Aufschlüsselung sehen

GRUPPEN UND VERLAUF
• Leute, mit denen du oft teilst, speichern und in jede Rechnung laden
• Frühere Rechnungen aufbewahren und später wieder öffnen
• Währung wählen: Das betrifft nur die Darstellung, die App nutzt nie aktuelle Wechselkurse

PRIVAT UND OFFLINE
• Kein Konto, keine Anmeldung. Alles bleibt auf deinem Handy und funktioniert ohne Internet
• Als Text sichern, kopieren oder teilen und auf jedem Gerät wiederherstellen
• Helles und dunkles Design, Akzentfarben, einstellbare Textgröße, 13 Sprachen

BILL SPLIT PRO: Einmalkauf, kein Abo
• Unbegrenzt gespeicherte Gruppen (kostenlos: 3)
• Unbegrenzter Rechnungsverlauf (kostenlos: 10)
• CSV-Export des Verlaufs
• Zusätzliche Akzentfarben und keine Werbung

„Werbung entfernen“ gibt es auch einzeln als Einmalkauf.
</de-DE>

<es-419>
Cuatro amigos, una cuenta, ninguna discusión. Bill Split calcula lo que debe cada persona, hasta el centavo: añade los artículos, toca quién compartió cada uno y deja que el impuesto y la propina vayan donde corresponde.

ARTÍCULO POR ARTÍCULO
• Añade cada plato o bebida con su precio
• Toca a quienes lo compartieron: una persona, varias o todas
• Los artículos compartidos se dividen a partes iguales o con partes personalizadas (2 para una porción doble, 1 para una normal)
• Lo que aún no está asignado se marca y se deja fuera del total

IMPUESTO Y PROPINA
• Escribe el impuesto y la propina como porcentaje o importe fijo
• Repártelos en proporción a lo que pidió cada persona, o a partes iguales
• Calcula la propina solo sobre los artículos o sobre artículos más impuesto

EXACTO AL CENTAVO
• Artículos, impuesto y propina se redondean cada uno con el método del mayor resto: primero los centavos enteros y los sobrantes van a las fracciones más grandes
• Los totales por persona siempre suman la cuenta exactamente, y la app te muestra la comprobación
• El método se explica en pantalla, sin centavos misteriosos

COMPÁRTELO
• Envía un resumen en texto con el total y lo que debe cada persona
• Mira los artículos, el impuesto y la propina de cada persona en un desglose

GRUPOS E HISTORIAL
• Guarda a las personas con las que sueles dividir y cárgalas en cualquier cuenta
• Conserva cuentas anteriores y ábrelas después
• Elige tu moneda. Solo cambia el formato; la app nunca usa tipos de cambio en vivo

PRIVADO Y SIN INTERNET
• Sin cuenta ni inicio de sesión. Todo se queda en tu teléfono y funciona sin conexión
• Respalda en texto que puedes copiar o compartir y restáuralo en cualquier dispositivo
• Temas claro y oscuro, colores de acento, tamaño de texto ajustable, 13 idiomas

BILL SPLIT PRO: pago único, sin suscripción
• Grupos guardados ilimitados (el plan gratuito permite 3)
• Historial de cuentas ilimitado (el plan gratuito guarda 10)
• Exportación CSV del historial
• Colores de acento extra y sin anuncios

También puedes comprar solo Quitar anuncios con un pago único.
</es-419>

<fr-FR>
Quatre amis, une addition, aucune dispute. Bill Split calcule ce que chacun doit, au centime près : ajoutez les articles, touchez qui les a partagés et laissez les taxes et le pourboire se répartir comme il se doit.

ARTICLE PAR ARTICLE
• Ajoutez chaque plat ou boisson avec son prix
• Touchez ceux qui l'ont partagé : une personne, quelques-unes ou tout le monde
• Les articles partagés se divisent à parts égales ou en parts personnalisées (2 pour une double portion, 1 pour une normale)
• Ce qui n'est pas encore attribué est signalé et laissé de côté dans le total

TAXES ET POURBOIRE
• Saisissez taxes et pourboire en pourcentage ou en montant fixe
• Répartissez-les au prorata de la commande de chacun, ou à parts égales
• Calculez le pourboire sur les articles seuls ou sur articles plus taxes

AU CENTIME PRÈS
• Articles, taxes et pourboire sont arrondis chacun selon la méthode du plus fort reste : d'abord les centimes entiers, puis les centimes restants vont aux plus grandes fractions
• Les totaux par personne font toujours exactement l'addition, et l'appli affiche la vérification
• La méthode est expliquée à l'écran, sans centimes mystérieux

PARTAGEZ
• Envoyez un récapitulatif en texte avec le total et la part de chacun
• Consultez les articles, taxes et pourboire de chaque personne dans un détail

GROUPES ET HISTORIQUE
• Enregistrez les personnes avec qui vous partagez souvent et chargez-les dans n'importe quelle addition
• Gardez les additions passées et rouvrez-les plus tard
• Choisissez votre devise. Cela ne change que l'affichage ; l'appli n'utilise jamais de taux de change en direct

PRIVÉ ET HORS LIGNE
• Pas de compte, pas de connexion. Tout reste sur votre téléphone et fonctionne sans internet
• Sauvegardez sous forme de texte à copier ou partager et restaurez sur n'importe quel appareil
• Thèmes clair et sombre, couleurs d'accent, taille de texte réglable, 13 langues

BILL SPLIT PRO : achat unique, sans abonnement
• Groupes enregistrés illimités (la version gratuite en garde 3)
• Historique des additions illimité (la version gratuite en garde 10)
• Export CSV de l'historique
• Couleurs d'accent en plus et aucune publicité

« Supprimer les pubs » existe aussi seul, en achat unique.
</fr-FR>

<hi-IN>
चार दोस्त, एक बिल, कोई बहस नहीं। Bill Split पाई-पाई तक बताता है कि हर व्यक्ति को कितना देना है: आइटम जोड़ें, चुनें कि हर एक किसने बाँटा, और टैक्स व टिप को सही जगह बँटने दें।

आइटम दर आइटम
• हर डिश या ड्रिंक को उसकी कीमत के साथ जोड़ें
• चुनें किसने बाँटा: एक व्यक्ति, कुछ लोग या सब
• साझा आइटम बराबर या कस्टम हिस्सों में बँटते हैं (2 यानी दोगुना हिस्सा, 1 यानी सामान्य)
• जो अभी किसी को असाइन नहीं हुआ, उस पर निशान लगता है और वह कुल में नहीं गिना जाता

टैक्स और टिप
• टैक्स और टिप प्रतिशत या तय राशि में डालें
• हर किसी के ऑर्डर के अनुपात में बाँटें, या बराबर
• टिप सिर्फ़ आइटम पर या आइटम + टैक्स पर निकालें

पाई-पाई सटीक
• आइटम, टैक्स और टिप हर एक को 'सबसे बड़ा शेष' तरीके से राउंड किया जाता है: पहले पूरे पैसे, फिर बचे पैसे सबसे बड़े अंशों को
• हर व्यक्ति के कुल का जोड़ हमेशा बिल के ठीक बराबर रहता है, और ऐप जाँच दिखाता है
• तरीका स्क्रीन पर समझाया गया है, कोई रहस्यमय पैसा नहीं

शेयर करें
• कुल और हर व्यक्ति की देनदारी का सादा टेक्स्ट सारांश भेजें
• हर व्यक्ति के आइटम, टैक्स और टिप का ब्योरा देखें

समूह और इतिहास
• जिनके साथ अक्सर बिल बाँटते हैं उन्हें सेव करें और किसी भी बिल में लोड करें
• पुराने बिल रखें और बाद में दोबारा खोलें
• अपनी मुद्रा चुनें। इससे सिर्फ़ फ़ॉर्मैट बदलता है; ऐप लाइव विनिमय दर कभी इस्तेमाल नहीं करता

निजी और ऑफ़लाइन
• कोई अकाउंट या साइन-इन नहीं। सब कुछ आपके फ़ोन पर रहता है और बिना इंटरनेट चलता है
• कॉपी या शेयर करने लायक टेक्स्ट में बैकअप लें और किसी भी डिवाइस पर रीस्टोर करें
• लाइट और डार्क थीम, एक्सेंट रंग, बदलने योग्य टेक्स्ट साइज़, 13 भाषाएँ

BILL SPLIT PRO: एक बार की खरीद, कोई सब्सक्रिप्शन नहीं
• असीमित सेव किए समूह (मुफ़्त प्लान में 3)
• असीमित बिल इतिहास (मुफ़्त प्लान में 10)
• इतिहास का CSV एक्सपोर्ट
• अतिरिक्त एक्सेंट रंग और विज्ञापन-मुक्त

'विज्ञापन हटाएँ' अलग से भी एक बार की खरीद के रूप में उपलब्ध है।
</hi-IN>

<id>
Empat teman, satu tagihan, tanpa debat. Bill Split menghitung berapa yang harus dibayar tiap orang sampai ke sen: tambahkan item, ketuk siapa yang ikut tiap item, dan biarkan pajak serta tip jatuh ke tempat yang semestinya.

ITEM DEMI ITEM
• Tambahkan setiap makanan atau minuman beserta harganya
• Ketuk orang yang ikut: satu orang, beberapa, atau semuanya
• Item bersama dibagi sama rata, atau dengan bagian khusus (2 untuk porsi ganda, 1 untuk porsi biasa)
• Yang belum ditetapkan diberi tanda dan tidak dihitung dalam total

PAJAK DAN TIP
• Masukkan pajak dan tip sebagai persen atau jumlah tetap
• Bagi sesuai pesanan masing-masing, atau sama rata
• Hitung tip hanya dari item, atau dari item ditambah pajak

PAS SAMPAI SEN
• Item, pajak, dan tip masing-masing dibulatkan dengan metode sisa terbesar: sen utuh dulu, lalu sisa sen diberikan ke pecahan terbesar
• Total per orang selalu persis sama dengan tagihan, dan aplikasi menunjukkan pemeriksaannya
• Metodenya dijelaskan di layar, jadi tidak ada sen misterius

BAGIKAN
• Kirim ringkasan teks berisi total dan bagian tiap orang
• Lihat rincian item, pajak, dan tip setiap orang

GRUP DAN RIWAYAT
• Simpan orang-orang yang sering patungan dan muat ke tagihan mana pun
• Simpan tagihan lama dan buka lagi nanti
• Pilih mata uang Anda. Ini hanya mengubah format; aplikasi tidak pernah memakai kurs langsung

PRIVAT DAN OFFLINE
• Tanpa akun, tanpa login. Semua tetap di ponsel Anda dan berjalan tanpa internet
• Cadangkan sebagai teks yang bisa disalin atau dibagikan, lalu pulihkan di perangkat mana pun
• Tema terang dan gelap, warna aksen, ukuran teks yang bisa diatur, 13 bahasa

BILL SPLIT PRO: sekali bayar, tanpa langganan
• Grup tersimpan tanpa batas (paket gratis menampung 3)
• Riwayat tagihan tanpa batas (paket gratis menyimpan 10)
• Ekspor CSV riwayat
• Warna aksen tambahan dan tanpa iklan

Hapus Iklan juga tersedia terpisah sebagai pembelian sekali bayar.
</id>

<it-IT>
Quattro amici, un solo conto, nessuna discussione. Bill Split calcola quanto deve ciascuno, fino al centesimo: aggiungi le voci, tocca chi le ha condivise e lascia che tasse e mancia vadano dove devono.

VOCE PER VOCE
• Aggiungi ogni piatto o bevanda con il suo prezzo
• Tocca chi l'ha condivisa: una persona, alcune o tutti
• Le voci condivise si dividono in parti uguali o con quote personalizzate (2 per una porzione doppia, 1 per una normale)
• Ciò che non è ancora assegnato viene segnalato ed escluso dal totale

TASSE E MANCIA
• Inserisci tasse e mancia come percentuale o importo fisso
• Ripartiscile in proporzione a ciò che ha ordinato ciascuno, oppure in parti uguali
• Calcola la mancia solo sulle voci o su voci più tasse

ESATTO AL CENTESIMO
• Voci, tasse e mancia sono arrotondate ciascuna con il metodo del resto più grande: prima i centesimi interi, poi quelli avanzati alle frazioni maggiori
• I totali per persona sommano sempre esattamente il conto e l'app mostra la verifica
• Il metodo è spiegato sullo schermo, senza centesimi misteriosi

CONDIVIDI
• Invia un riepilogo testuale con il totale e quanto deve ciascuno
• Vedi voci, tasse e mancia di ogni persona in un dettaglio

GRUPPI E CRONOLOGIA
• Salva le persone con cui dividi spesso e caricale in qualsiasi conto
• Conserva i conti passati e riaprili più tardi
• Scegli la valuta. Cambia solo la formattazione; l'app non usa mai tassi di cambio in tempo reale

PRIVATA E OFFLINE
• Nessun account, nessun accesso. Tutto resta sul telefono e funziona senza internet
• Esegui il backup come testo da copiare o condividere e ripristinalo su qualsiasi dispositivo
• Temi chiaro e scuro, colori d'accento, dimensione del testo regolabile, 13 lingue

BILL SPLIT PRO: acquisto singolo, nessun abbonamento
• Gruppi salvati illimitati (il piano gratuito ne tiene 3)
• Cronologia dei conti illimitata (il piano gratuito ne tiene 10)
• Esportazione CSV della cronologia
• Colori d'accento extra e nessuna pubblicità

Rimuovi pubblicità è disponibile anche da solo come acquisto singolo.
</it-IT>

<ja-JP>
4人で1枚のレシート、もめごとなし。Bill Splitは、各自の支払額を端数まで正確に計算します。品目を追加して、誰がシェアしたかをタップするだけ。税とチップも、あるべき場所に配分されます。

品目ごとに
• 料理や飲み物を価格つきで追加
• シェアした人をタップ:1人、数人、全員
• 共有品目は均等割り、または比率指定(2は2倍の量、1は通常の量)
• まだ割り当てていない品目は警告が出て、合計には含まれません

税とチップ
• 税とチップを割合または固定金額で入力
• 各自の注文額に比例して、または均等に配分
• チップは品目のみ、または品目+税を基準に計算

端数まで正確
• 品目・税・チップはそれぞれ最大剰余法で丸めます。まず整数分を配り、余りは小数部分の大きい人から順に配分
• 各自の合計は常に請求額とぴったり一致し、アプリが確認を表示します
• 方法は画面上で説明するので、不明な端数は出ません

共有
• 合計と各自の支払額をテキストでまとめて送れます
• 各自の品目・税・チップの内訳を確認できます

グループと履歴
• よく割り勘するメンバーを保存して、どの会計にも読み込めます
• 過去の会計を保存して、あとから開き直せます
• 通貨を選択できます。変わるのは表示形式のみで、為替レートは使いません

プライベートでオフライン
• アカウントもログインも不要。データは端末内に残り、ネットなしで動きます
• コピー・共有できるテキストでバックアップし、別の端末で復元できます
• ライト/ダークテーマ、アクセントカラー、文字サイズ調整、13言語

BILL SPLIT PRO:買い切り、サブスクなし
• 保存グループが無制限(無料版は3つ)
• 会計履歴が無制限(無料版は10件)
• 履歴のCSV書き出し
• アクセントカラー追加・広告なし

「広告を削除」は単体でも買い切りで購入できます。
</ja-JP>

<pt-BR>
Quatro amigos, uma conta, nenhuma discussão. O Bill Split calcula quanto cada pessoa deve, até o centavo: adicione os itens, toque em quem dividiu cada um e deixe o imposto e a gorjeta caírem onde devem.

ITEM POR ITEM
• Adicione cada prato ou bebida com o preço
• Toque em quem dividiu: uma pessoa, algumas ou todas
• Itens compartilhados são divididos em partes iguais ou personalizadas (2 para uma porção dupla, 1 para uma normal)
• O que ainda não foi atribuído é sinalizado e fica fora do total

IMPOSTO E GORJETA
• Digite imposto e gorjeta como porcentagem ou valor fixo
• Divida em proporção ao que cada um pediu, ou igualmente
• Calcule a gorjeta só sobre os itens ou sobre itens mais imposto

EXATO AO CENTAVO
• Itens, imposto e gorjeta são arredondados cada um pelo método do maior resto: primeiro os centavos inteiros, depois os que sobram vão para as maiores frações
• Os totais por pessoa sempre somam a conta exatamente, e o app mostra a conferência
• O método é explicado na tela, sem centavos misteriosos

COMPARTILHE
• Envie um resumo em texto com o total e quanto cada pessoa deve
• Veja os itens, o imposto e a gorjeta de cada pessoa em um detalhamento

GRUPOS E HISTÓRICO
• Salve as pessoas com quem você costuma dividir e carregue em qualquer conta
• Guarde contas passadas e abra de novo depois
• Escolha sua moeda. Muda só a formatação; o app nunca usa câmbio ao vivo

PRIVADO E SEM INTERNET
• Sem conta, sem login. Tudo fica no seu celular e funciona sem conexão
• Faça backup em texto para copiar ou compartilhar e restaure em qualquer aparelho
• Temas claro e escuro, cores de destaque, tamanho de texto ajustável, 13 idiomas

BILL SPLIT PRO: compra única, sem assinatura
• Grupos salvos ilimitados (o plano grátis guarda 3)
• Histórico de contas ilimitado (o plano grátis guarda 10)
• Exportação CSV do histórico
• Cores de destaque extras e sem anúncios

Remover anúncios também está disponível sozinho, como compra única.
</pt-BR>

<tr-TR>
Dört arkadaş, tek hesap, sıfır tartışma. Bill Split herkesin ne ödeyeceğini kuruşuna kadar hesaplar: kalemleri ekleyin, her birini kimin paylaştığına dokunun, vergi ve bahşiş de olması gereken yere dağılsın.

KALEM KALEM
• Her yemeği veya içeceği fiyatıyla ekleyin
• Paylaşanlara dokunun: bir kişi, birkaç kişi ya da herkes
• Ortak kalemler eşit ya da özel paylarla bölünür (çift porsiyon için 2, normal için 1)
• Henüz kimseye atanmamış kalemler işaretlenir ve toplamın dışında bırakılır

VERGİ VE BAHŞİŞ
• Vergi ve bahşişi yüzde ya da sabit tutar olarak girin
• Herkesin siparişine orantılı ya da eşit dağıtın
• Bahşişi yalnızca kalemler üzerinden ya da kalemler artı vergi üzerinden hesaplayın

KURUŞU KURUŞUNA
• Kalemler, vergi ve bahşiş ayrı ayrı en büyük kalan yöntemiyle yuvarlanır: önce tam kuruşlar, artanlar en büyük kesirlere gider
• Kişi başı toplamlar her zaman hesabı tam olarak tutar ve uygulama kontrolü gösterir
• Yöntem ekranda açıklanır, gizemli kuruş olmaz

PAYLAŞIN
• Toplamı ve herkesin ödeyeceği tutarı içeren düz metin özet gönderin
• Herkesin kalem, vergi ve bahşiş dökümünü görün

GRUPLAR VE GEÇMİŞ
• Sık hesap böldüğünüz kişileri kaydedin ve istediğiniz hesaba yükleyin
• Geçmiş hesapları saklayın, sonra yeniden açın
• Para biriminizi seçin. Yalnızca biçimi değiştirir; uygulama canlı döviz kuru kullanmaz

GİZLİ VE ÇEVRİMDIŞI
• Hesap yok, giriş yok. Her şey telefonunuzda kalır ve internetsiz çalışır
• Kopyalayıp paylaşabileceğiniz metin olarak yedekleyin, istediğiniz cihazda geri yükleyin
• Açık ve koyu tema, vurgu renkleri, ayarlanabilir yazı boyutu, 13 dil

BILL SPLIT PRO: tek seferlik satın alma, abonelik yok
• Sınırsız kayıtlı grup (ücretsiz sürümde 3)
• Sınırsız hesap geçmişi (ücretsiz sürümde 10)
• Geçmişi CSV olarak dışa aktarma
• Ek vurgu renkleri ve reklamsız kullanım

Reklamları Kaldır tek seferlik satın alma olarak ayrıca da sunulur.
</tr-TR>

<uk>
Четверо друзів, один рахунок, жодних суперечок. Bill Split до копійки рахує, скільки винен кожен: додайте позиції, торкніться тих, хто ділив кожну, а податок і чайові розподіляться, як слід.

ПОЗИЦІЯ ЗА ПОЗИЦІЄЮ
• Додавайте кожну страву чи напій із ціною
• Торкайтеся тих, хто ділив: одна людина, кілька або всі
• Спільні позиції діляться порівну або власними частками (2 для подвійної порції, 1 для звичайної)
• Позиції, яких ще нікому не призначено, позначаються й не входять до суми

ПОДАТОК І ЧАЙОВІ
• Вводьте податок і чайові у відсотках або фіксованою сумою
• Розподіляйте пропорційно замовленому або порівну
• Рахуйте чайові лише від позицій або від позицій разом із податком

ТОЧНО ДО КОПІЙКИ
• Позиції, податок і чайові округлюються окремо методом найбільшого залишку: спершу цілі копійки, а решта — найбільшим дробам
• Суми по людях завжди точно дають рахунок, а застосунок показує перевірку
• Метод пояснено на екрані, тож жодних загадкових копійок

ПОДІЛІТЬСЯ
• Надішліть підсумок текстом із загальною сумою та часткою кожного
• Дивіться позиції, податок і чайові кожної людини в розбивці

ГРУПИ ТА ІСТОРІЯ
• Зберігайте людей, з якими часто ділите рахунок, і завантажуйте їх у будь-який рахунок
• Зберігайте минулі рахунки й відкривайте їх згодом
• Оберіть валюту. Змінюється лише формат; застосунок ніколи не використовує живі курси

ПРИВАТНО Й ОФЛАЙН
• Без облікового запису й входу. Усе лишається на телефоні й працює без інтернету
• Резервна копія текстом, який можна скопіювати чи надіслати, відновлюється на будь-якому пристрої
• Світла й темна теми, акцентні кольори, регульований розмір тексту, 13 мов

BILL SPLIT PRO: одноразова покупка, без підписки
• Необмежена кількість збережених груп (безкоштовно — 3)
• Необмежена історія рахунків (безкоштовно — 10)
• Експорт історії в CSV
• Додаткові акцентні кольори й без реклами

«Вимкнути рекламу» також доступно окремо як одноразова покупка.
</uk>

<zh-CN>
四个朋友，一张账单，不再争吵。Bill Split 帮你把每个人该付的钱算到分:添加菜品，点选谁一起分摊，税费和小费也会落到该去的地方。

逐项分账
• 添加每道菜或每杯饮品及其价格
• 点选分摊的人:一个人、几个人或所有人
• 共享菜品可平均分，也可自定义份额(2 表示两倍的量，1 表示正常的量)
• 尚未分配的菜品会被标出，且不计入合计

税费和小费
• 税费和小费可按百分比或固定金额输入
• 按每个人点单的比例分摊，或平均分摊
• 小费可只按菜品计算，也可按菜品加税费计算

精确到分
• 菜品、税费和小费各自采用最大余数法取整:先分配整数分，剩余的分按小数部分从大到小分配
• 每个人的合计相加永远正好等于账单，应用还会显示核对结果
• 方法会在屏幕上说明，不会出现莫名其妙的零头

分享
• 以纯文本发送汇总，含总额和每个人应付的金额
• 查看每个人的菜品、税费和小费明细

群组和历史
• 保存经常一起分账的人，随时载入任何账单
• 保留过往账单，之后随时再打开
• 选择货币。仅改变显示格式，应用从不使用实时汇率

私密且离线
• 无需账号和登录。所有数据都留在手机上，无需联网即可使用
• 以可复制或分享的文本备份，并在任何设备上恢复
• 浅色和深色主题、主题色、可调文字大小、13 种语言

BILL SPLIT PRO:一次性购买，无订阅
• 无限保存群组(免费版 3 个)
• 无限历史账单(免费版 10 条)
• 导出历史记录为 CSV
• 更多主题色，无广告

“去除广告”也可单独一次性购买。
</zh-CN>

---

## SUBTITLE (≤30 chars per locale)

_Apple App Store Connect → App Information → Subtitle_

<en-US>
Itemised splits, exact cents
</en-US>

<ar>
تقسيم بالأصناف وبدقة السنت
</ar>

<de-DE>
Posten teilen, centgenau
</de-DE>

<es-419>
Cuentas por artículo, exactas
</es-419>

<fr-FR>
Additions détaillées, exactes
</fr-FR>

<hi-IN>
आइटम वार बँटवारा, सटीक
</hi-IN>

<id>
Bagi per item, pas sampai sen
</id>

<it-IT>
Conti per voce, al centesimo
</it-IT>

<ja-JP>
品目別の割り勘、端数まで正確
</ja-JP>

<pt-BR>
Contas por item, exatas
</pt-BR>

<tr-TR>
Kalem kalem, kuruşu kuruşuna
</tr-TR>

<uk>
Рахунок по позиціях, точно
</uk>

<zh-CN>
按菜品分账，精确到分
</zh-CN>

---

## KEYWORDS (≤100 chars per locale)

_Apple App Store Connect → Version → Keywords_

<en-US>
split bill,bill splitter,split check,restaurant bill,share expenses,tax and tip,group payment
</en-US>

<ar>
تقسيم الفاتورة,حساب المطعم,الإكرامية,تقاسم المصاريف,حساب جماعي,من يدفع كم,الضريبة
</ar>

<de-DE>
Rechnung teilen,Restaurantrechnung,Trinkgeld,Kosten teilen,Gruppenrechnung,Wer zahlt was,Steuer
</de-DE>

<es-419>
dividir cuenta,dividir gastos,propina,cuenta restaurante,cuentas en grupo,quién paga qué,impuesto
</es-419>

<fr-FR>
partager addition,diviser la note,pourboire,note de restaurant,frais en groupe,qui doit quoi,taxes
</fr-FR>

<hi-IN>
बिल बाँटना,रेस्टोरेंट बिल,टिप,खर्च बाँटना,ग्रुप बिल,कौन कितना देगा,टैक्स
</hi-IN>

<id>
bagi tagihan,patungan,tagihan restoran,tip,bagi biaya,siapa bayar berapa,pajak,split bill
</id>

<it-IT>
dividere il conto,spese di gruppo,mancia,conto ristorante,chi paga cosa,tasse,dividere spese
</it-IT>

<ja-JP>
割り勘,会計,飲み会,チップ,立替,精算,税,グループ会計
</ja-JP>

<pt-BR>
dividir conta,rachar conta,gorjeta,conta de restaurante,despesas em grupo,quem paga o quê,imposto
</pt-BR>

<tr-TR>
hesap bölme,hesabı bölüşme,restoran hesabı,bahşiş,masraf paylaşımı,kim ne ödedi,vergi
</tr-TR>

<uk>
поділ рахунку,розділити рахунок,чайові,рахунок у ресторані,спільні витрати,хто скільки винен,податок
</uk>

<zh-CN>
分账,AA制,聚餐,餐厅账单,小费,拼单,算账,谁付多少,税费
</zh-CN>

---

## PROMOTIONAL TEXT (≤170 chars per locale)

_Apple App Store Connect → Version → Promotional Text_

<en-US>
Add the items, tap who shared each one, and see what every person owes. Tax and tip included, and the shares add up to the bill to the cent. Works offline.
</en-US>

<ar>
أضف الأصناف، واضغط على من شاركها، وشاهد ما يدين به كل شخص. مع الضريبة والإكرامية، والحصص تجمع الفاتورة بالضبط حتى السنت. يعمل بلا إنترنت.
</ar>

<de-DE>
Posten eintragen, antippen, wer sie geteilt hat, und sehen, was jede Person zahlt. Mit Steuer und Trinkgeld, die Anteile ergeben die Rechnung auf den Cent. Auch offline.
</de-DE>

<es-419>
Añade los artículos, toca quién compartió cada uno y mira cuánto debe cada persona. Con impuesto y propina; las partes suman la cuenta al centavo. Sin internet.
</es-419>

<fr-FR>
Ajoutez les articles, touchez qui les a partagés et voyez ce que chacun doit. Taxes et pourboire inclus, parts exactes au centime près. Hors ligne.
</fr-FR>

<hi-IN>
आइटम जोड़ें, चुनें कि हर एक किसने बाँटा, और देखें हर व्यक्ति को कितना देना है। टैक्स और टिप शामिल, और हिस्से बिल के ठीक बराबर बनते हैं। ऑफ़लाइन चलता है।
</hi-IN>

<id>
Tambahkan item, ketuk siapa yang ikut tiap item, dan lihat berapa yang harus dibayar masing-masing. Pajak dan tip termasuk, hasilnya pas dengan tagihan. Bisa offline.
</id>

<it-IT>
Aggiungi le voci, tocca chi le ha condivise e vedi quanto deve ciascuno. Tasse e mancia incluse, e le quote sommano il conto al centesimo. Funziona offline.
</it-IT>

<ja-JP>
品目を追加して、誰がシェアしたかをタップするだけ。税・チップ込みの各自の支払額が、請求額とぴったり合う形で分かります。オフラインでも使えます。
</ja-JP>

<pt-BR>
Adicione os itens, toque em quem dividiu cada um e veja quanto cada pessoa deve. Com imposto e gorjeta, e as partes somam a conta ao centavo. Funciona sem internet.
</pt-BR>

<tr-TR>
Kalemleri ekleyin, her birini kimin paylaştığına dokunun ve herkesin ne ödeyeceğini görün. Vergi ve bahşiş dahil, paylar hesabı kuruşu kuruşuna tutar. Çevrimdışı.
</tr-TR>

<uk>
Додайте позиції, торкніться тих, хто ділив кожну, і побачте, скільки винен кожен. Податок і чайові враховано, частки дають суму рахунку до копійки. Працює офлайн.
</uk>

<zh-CN>
添加菜品，点选谁一起分摊，立刻看到每个人该付多少。税费和小费已含，各人金额相加正好等于账单，精确到分。离线可用。
</zh-CN>

---
