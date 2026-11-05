# BudgetPlanner — store paste sheet

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
Budget Planner 2.0, rebuilt from scratch:
• Monthly envelopes with a running Left to assign figure
• Carry over or reset each envelope at month end
• Spending, overspend warnings and move-money between envelopes
• Bills with due-date reminders; mark paid to record the spending
• Savings goals with the monthly amount needed
• Month-over-month comparison
• Pro (one-time): unlimited envelopes and goals, full history, CSV export, accents, no ads
</en-US>

<ar>
Budget Planner 2.0، أُعيد بناؤه من الصفر:
• مظاريف شهرية مع رقم «المتبقي للتوزيع» المحدَّث دائمًا
• ترحيل أو تصفير كل مظروف في نهاية الشهر
• تسجيل المصروفات وتنبيهات التجاوز ونقل المال بين المظاريف
• فواتير بتذكير الاستحقاق؛ تحديدها كمدفوعة يسجّل المصروف
• أهداف ادخار مع المبلغ الشهري المطلوب
• مقارنة شهر بشهر
• Pro (دفعة واحدة): مظاريف وأهداف بلا حدود، سجل كامل، تصدير CSV، ألوان، بدون إعلانات
</ar>

<de-DE>
Budget Planner 2.0, komplett neu gebaut:
• Monatsumschläge mit laufendem Wert „Noch zu verteilen“
• Je Umschlag: übertragen oder am Monatsende zurücksetzen
• Ausgaben, Warnung bei Überziehung, Geld zwischen Umschlägen verschieben
• Rechnungen mit Fälligkeits-Erinnerung; „bezahlt“ bucht die Ausgabe
• Sparziele mit dem nötigen Monatsbetrag
• Vergleich von Monat zu Monat
• Pro (einmalig): unbegrenzt Umschläge und Ziele, ganzer Verlauf, CSV-Export, Akzente, keine Werbung
</de-DE>

<es-419>
Budget Planner 2.0, reconstruida desde cero:
• Sobres mensuales con la cifra Por asignar en tiempo real
• Arrastrar o reiniciar cada sobre a fin de mes
• Gastos, avisos de exceso y traspasos entre sobres
• Facturas con recordatorio de vencimiento; al marcarlas pagadas se registra el gasto
• Metas de ahorro con la cuota mensual necesaria
• Comparación mes a mes
• Pro (pago único): sobres y metas ilimitados, historial completo, exportación CSV, acentos, sin anuncios
</es-419>

<fr-FR>
Budget Planner 2.0, entièrement repensée :
• Enveloppes mensuelles avec un « reste à affecter » en continu
• Reporter ou remettre à zéro chaque enveloppe en fin de mois
• Dépenses, alertes de dépassement et transferts entre enveloppes
• Factures avec rappel d’échéance ; « payée » enregistre la dépense
• Objectifs d’épargne avec le montant mensuel nécessaire
• Comparaison d’un mois à l’autre
• Pro (achat unique) : enveloppes et objectifs illimités, historique, CSV, couleurs, sans pub
</fr-FR>

<hi-IN>
Budget Planner 2.0, नए सिरे से बनाया गया:
• “बाँटना बाकी” की लाइव रकम के साथ मासिक लिफ़ाफ़े
• हर लिफ़ाफ़ा महीने के अंत में आगे ले जाएँ या रीसेट करें
• खर्च, अधिक खर्च की चेतावनी और लिफ़ाफ़ों के बीच पैसे भेजना
• देय तिथि के रिमाइंडर वाले बिल; चुकाया चिह्नित करने पर खर्च दर्ज
• ज़रूरी मासिक रकम के साथ बचत लक्ष्य
• महीने-दर-महीने तुलना
• Pro (एक बार): असीमित लिफ़ाफ़े और लक्ष्य, पूरा इतिहास, CSV, रंग, कोई विज्ञापन नहीं
</hi-IN>

<id>
Budget Planner 2.0, dibangun ulang dari awal:
• Amplop bulanan dengan angka Belum dialokasikan yang selalu terbarui
• Bawa ke depan atau atur ulang tiap amplop di akhir bulan
• Pengeluaran, peringatan kelebihan, dan pindah uang antar amplop
• Tagihan dengan pengingat jatuh tempo; tandai lunas untuk mencatat pengeluaran
• Target tabungan dengan jumlah bulanan yang dibutuhkan
• Perbandingan bulan ke bulan
• Pro (sekali bayar): amplop dan target tanpa batas, riwayat penuh, CSV, aksen, tanpa iklan
</id>

<it-IT>
Budget Planner 2.0, rifatta da zero:
• Buste mensili con la cifra Da assegnare sempre aggiornata
• Riporta o azzera ogni busta a fine mese
• Spese, avvisi di sforamento e spostamenti tra buste
• Bollette con promemoria di scadenza; segnata come pagata registra la spesa
• Obiettivi di risparmio con la rata mensile necessaria
• Confronto mese su mese
• Pro (acquisto unico): buste e obiettivi illimitati, storico completo, esportazione CSV, colori, senza pubblicità
</it-IT>

<ja-JP>
Budget Planner 2.0、ゼロから作り直しました：
• 「未割り当て」をリアルタイム表示する月次の封筒
• 封筒ごとに月末の繰り越し／リセットを選択
• 支出の記録、使いすぎの警告、封筒間のお金の移動
• 期日の通知つき支払い。支払い済みにすると支出を記録
• 毎月必要な金額がわかる貯蓄目標
• 月ごとの比較
• Pro（買い切り）：封筒と目標が無制限、全履歴、CSV、アクセントカラー、広告なし
</ja-JP>

<pt-BR>
Budget Planner 2.0, refeito do zero:
• Envelopes mensais com o valor Falta distribuir sempre atualizado
• Acumular ou zerar cada envelope no fim do mês
• Gastos, avisos de estouro e transferência entre envelopes
• Contas com lembrete de vencimento; marcar como paga registra o gasto
• Metas de economia com o valor mensal necessário
• Comparação mês a mês
• Pro (compra única): envelopes e metas ilimitados, histórico completo, exportação CSV, cores, sem anúncios
</pt-BR>

<tr-TR>
Budget Planner 2.0, baştan yazıldı:
• Dağıtılacak tutarı anlık gösteren aylık zarflar
• Her zarfı ay sonunda devret ya da sıfırla
• Harcama, aşım uyarıları ve zarflar arası para aktarımı
• Son ödeme hatırlatmalı faturalar; ödendi işaretlemek harcamayı kaydeder
• Gereken aylık tutarı gösteren birikim hedefleri
• Aydan aya karşılaştırma
• Pro (tek seferlik): sınırsız zarf ve hedef, tüm geçmiş, CSV dışa aktarma, vurgu renkleri, reklamsız
</tr-TR>

<uk>
Budget Planner 2.0, створено заново:
• Місячні конверти з актуальною сумою «Залишилось розподілити»
• Переносити чи скидати кожен конверт наприкінці місяця
• Витрати, попередження про перевитрату, перенесення між конвертами
• Рахунки з нагадуванням; «сплачено» записує витрату
• Цілі накопичення з потрібною місячною сумою
• Порівняння місяць до місяця
• Pro (разова покупка): безліч конвертів і цілей, уся історія, CSV, кольори, без реклами
</uk>

<zh-CN>
Budget Planner 2.0，全新重构：
• 月度信封，实时显示“待分配”金额
• 每个信封月底可选择结转或清零
• 记录支出、超支提醒、在信封之间转移资金
• 账单到期提醒；标记已付即记录支出
• 储蓄目标，并给出每月所需金额
• 月与月对比
• Pro（一次性购买）：信封和目标不限量、完整历史、CSV 导出、主题色、无广告
</zh-CN>

---

## SHORT DESCRIPTION (≤80 chars per locale)

_Grow → Store presence → Main store listing → Short description_

<en-US>
Plan monthly envelopes, track bills and savings goals, see what is left.
</en-US>

<ar>
خطّط لمظاريف الشهر وتابع الفواتير وأهداف الادخار. يعمل بدون إنترنت.
</ar>

<de-DE>
Plane Monatsumschläge, behalte Rechnungen und Sparziele im Blick. Auch offline.
</de-DE>

<es-419>
Planea sobres mensuales, controla facturas y metas de ahorro. Sin conexión.
</es-419>

<fr-FR>
Planifiez vos enveloppes, suivez factures et objectifs d’épargne. Hors ligne.
</fr-FR>

<hi-IN>
मासिक लिफ़ाफ़े बनाएँ, बिल और बचत लक्ष्य ट्रैक करें। ऑफ़लाइन चलता है।
</hi-IN>

<id>
Rencanakan amplop bulanan, pantau tagihan dan target tabungan. Tanpa internet.
</id>

<it-IT>
Pianifica le buste del mese, tieni d’occhio bollette e obiettivi. Offline.
</it-IT>

<ja-JP>
月ごとの封筒で予算を立て、支払いと貯蓄目標を管理。オフラインで使えます。
</ja-JP>

<pt-BR>
Planeje envelopes mensais, acompanhe contas e metas de economia. Offline.
</pt-BR>

<tr-TR>
Aylık zarfları planla, faturaları ve birikim hedeflerini takip et. Çevrimdışı.
</tr-TR>

<uk>
Плануйте місячні конверти, стежте за рахунками й цілями. Працює офлайн.
</uk>

<zh-CN>
按月规划信封预算，管理账单和储蓄目标，随时看到还剩多少。可离线使用。
</zh-CN>

---

## FULL DESCRIPTION (≤4000 chars per locale)

_Grow → Store presence → Main store listing → Full description_

<en-US>
Decide what your money will do before the month starts. Budget Planner splits your monthly income into envelopes, keeps a running "left to assign" figure, and shows what is still free in each envelope as you spend. It plans the month ahead; it is not a quick expense logger.

PLAN THE MONTH
• Add your income, then assign it to envelopes until Left to assign reaches zero
• Start a new month from last month's plan in one tap, or spread what is left across your envelopes
• Over-assigned? The figure turns red and tells you by how much

SPEND FROM ENVELOPES
• Record spending against an envelope, with a note and a date
• Warnings when an envelope is almost used up or overspent
• Move money between envelopes to cover a shortfall; your total never changes

A ROLLOVER RULE FOR EACH ENVELOPE
• Choose carry over or reset at the end of the month, per envelope
• Carried money (or an overspend) stays in the envelope; reset money goes back to Left to assign

BILLS AND SAVINGS GOALS
• Bills with a due day and a reminder on the day, 1 day or 3 days before
• Mark a bill paid and the amount is recorded as spending in its envelope
• Savings goals with a target date and the amount to set aside each month

COMPARE MONTHS
• This month beside last month: income, assigned and spent
• See which envelopes changed the most

EXACT TO THE CENT
• Every amount is kept in whole cents and every split is rounded so that no cent goes missing: assigned plus left always equals income, and moving money never changes your total
• Pick your currency. This changes formatting only; the app never uses live exchange rates

PRIVATE AND OFFLINE
• No account, no sign-in. Everything stays on your phone and works without internet
• Back up to text you can copy or share, and restore it on any device
• Light and dark themes, accent colors, adjustable text size, 13 languages

BUDGET PLANNER PRO: one-time purchase, no subscription
• Unlimited envelopes (the free plan has 8) and savings goals (free: 3)
• Month history beyond the last 3 months
• CSV export of your budget
• Extra accent colors and no ads

Remove Ads is also available on its own as a one-time purchase.
</en-US>

<ar>
قرّر ماذا سيفعل مالك قبل أن يبدأ الشهر. يقسّم Budget Planner دخلك الشهري على مظاريف، ويُبقي رقم «المتبقي للتوزيع» محدّثًا، ويُظهر ما بقي حرًّا في كل مظروف أثناء الإنفاق. التطبيق يخطّط للشهر مسبقًا؛ وليس مجرد سجلّ سريع للمصروفات.

خطّط للشهر
• أضف دخلك ووزّعه على المظاريف حتى يصل «المتبقي للتوزيع» إلى الصفر
• ابدأ شهرًا جديدًا من خطة الشهر الماضي بلمسة واحدة، أو وزّع المتبقي على مظاريفك
• وزّعت أكثر من اللازم؟ يتحول الرقم إلى الأحمر ويُخبرك بالفرق

أنفق من المظاريف
• سجّل المصروفات على مظروف مع ملاحظة وتاريخ
• تنبيهات عندما يوشك المظروف على النفاد أو يتجاوز حدّه
• انقل المال بين المظاريف لتغطية العجز؛ إجماليك لا يتغير أبدًا

قاعدة ترحيل لكل مظروف
• اختر الترحيل أو التصفير في نهاية الشهر لكل مظروف على حدة
• المال المرحَّل (أو التجاوز) يبقى في المظروف؛ والمال المصفَّر يعود إلى «المتبقي للتوزيع»

الفواتير وأهداف الادخار
• فواتير بيوم استحقاق وتذكير في اليوم نفسه أو قبله بيوم أو 3 أيام
• عند تحديد الفاتورة كمدفوعة يُسجَّل المبلغ كمصروف في مظروفها
• أهداف ادخار بتاريخ مستهدف والمبلغ الذي تدّخره كل شهر

قارن الأشهر
• هذا الشهر بجانب الشهر الماضي: الدخل والموزَّع والمصروف
• اعرف أي المظاريف تغيّرت أكثر

دقة حتى آخر وحدة
• تُحفظ كل المبالغ بأصغر وحدة صحيحة ويُقرَّب كل تقسيم بحيث لا تضيع أي وحدة: الموزَّع مع المتبقي يساوي الدخل دائمًا، ونقل المال لا يغيّر الإجمالي
• اختر عملتك. هذا يغيّر التنسيق فقط؛ فالتطبيق لا يستخدم أسعار صرف مباشرة

خاص وبدون إنترنت
• بلا حساب وبلا تسجيل دخول. كل شيء يبقى على هاتفك ويعمل بدون إنترنت
• نسخ احتياطي كنص يمكن نسخه أو مشاركته واستعادته على أي جهاز
• مظهران فاتح وداكن، ألوان تمييز، حجم نص قابل للضبط، 13 لغة

BUDGET PLANNER PRO: شراء لمرة واحدة بدون اشتراك
• مظاريف غير محدودة (النسخة المجانية: 8) وأهداف ادخار (المجانية: 3)
• سجل أقدم من آخر 3 أشهر
• تصدير ميزانيتك بصيغة CSV
• ألوان تمييز إضافية وبدون إعلانات

«إزالة الإعلانات» متاحة أيضًا منفردة كشراء لمرة واحدة.
</ar>

<de-DE>
Entscheide, was dein Geld tun soll, bevor der Monat beginnt. Budget Planner teilt dein Monatseinkommen auf Umschläge auf, zeigt laufend, was noch zu verteilen ist, und wie viel in jedem Umschlag noch frei ist, während du ausgibst. Die App plant den Monat im Voraus – sie ist kein schneller Ausgabenlogger.

DEN MONAT PLANEN
• Einkommen eintragen und auf Umschläge verteilen, bis „Noch zu verteilen“ null ist
• Neuen Monat mit einem Tipp aus dem Plan des Vormonats starten oder den Rest auf Umschläge verteilen
• Zu viel verteilt? Der Wert wird rot und zeigt den Betrag

AUS UMSCHLÄGEN AUSGEBEN
• Ausgaben mit Notiz und Datum einem Umschlag zuordnen
• Warnungen, wenn ein Umschlag fast leer oder überzogen ist
• Geld zwischen Umschlägen verschieben, um Lücken zu schließen; die Gesamtsumme bleibt gleich

EINE ÜBERTRAGSREGEL PRO UMSCHLAG
• Am Monatsende übertragen oder zurücksetzen – für jeden Umschlag einzeln
• Übertragenes Geld (oder eine Überziehung) bleibt im Umschlag; zurückgesetztes Geld geht zurück zu „Noch zu verteilen“

RECHNUNGEN UND SPARZIELE
• Rechnungen mit Fälligkeitstag und Erinnerung am Tag selbst, 1 oder 3 Tage vorher
• „Bezahlt“ markieren bucht den Betrag als Ausgabe im zugehörigen Umschlag
• Sparziele mit Zieldatum und dem Betrag, den du jeden Monat zurücklegst

MONATE VERGLEICHEN
• Dieser Monat neben dem letzten: Einkommen, verteilt, ausgegeben
• Sieh, welche Umschläge sich am stärksten verändert haben

CENT-GENAU
• Alle Beträge werden in ganzen Cent geführt und jede Aufteilung so gerundet, dass kein Cent verloren geht: verteilt plus übrig ergibt immer das Einkommen, und Verschieben ändert nie die Summe
• Wähle deine Währung. Das ändert nur die Darstellung; die App nutzt nie Live-Wechselkurse

PRIVAT UND OFFLINE
• Kein Konto, keine Anmeldung. Alles bleibt auf deinem Handy und funktioniert ohne Internet
• Sicherung als Text zum Kopieren oder Teilen, Wiederherstellung auf jedem Gerät
• Helles und dunkles Design, Akzentfarben, einstellbare Textgröße, 13 Sprachen

BUDGET PLANNER PRO: einmaliger Kauf, kein Abo
• Unbegrenzt Umschläge (kostenlos: 8) und Sparziele (kostenlos: 3)
• Monatsverlauf über die letzten 3 Monate hinaus
• CSV-Export deines Budgets
• Zusätzliche Akzentfarben und keine Werbung

„Werbung entfernen“ gibt es auch einzeln als einmaligen Kauf.
</de-DE>

<es-419>
Decide qué hará tu dinero antes de que empiece el mes. Budget Planner reparte tu ingreso mensual en sobres, mantiene una cifra "por asignar" en tiempo real y muestra lo que aún queda libre en cada sobre mientras gastas. Planifica el mes por adelantado; no es un registro rápido de gastos.

PLANIFICA EL MES
• Añade tus ingresos y asígnalos a sobres hasta que Por asignar llegue a cero
• Empieza un mes nuevo con el plan del anterior en un toque, o reparte lo que sobra entre tus sobres
• ¿Asignaste de más? La cifra se pone roja y te dice cuánto

GASTA DESDE LOS SOBRES
• Registra gastos en un sobre, con nota y fecha
• Avisos cuando un sobre está casi agotado o excedido
• Mueve dinero entre sobres para cubrir un faltante; tu total nunca cambia

UNA REGLA DE ARRASTRE PARA CADA SOBRE
• Elige arrastrar o reiniciar a fin de mes, sobre por sobre
• El dinero arrastrado (o un exceso) se queda en el sobre; el reiniciado vuelve a Por asignar

FACTURAS Y METAS DE AHORRO
• Facturas con día de vencimiento y recordatorio el mismo día, 1 o 3 días antes
• Al marcar una factura como pagada, el importe se registra como gasto en su sobre
• Metas de ahorro con fecha objetivo y la cuota mensual que debes apartar

COMPARA MESES
• Este mes junto al anterior: ingresos, asignado y gastado
• Mira qué sobres cambiaron más

AL CENTAVO
• Todos los importes se guardan en centavos enteros y cada reparto se redondea para que no se pierda ninguno: asignado más lo que queda siempre suma el ingreso, y mover dinero nunca cambia el total
• Elige tu moneda. Solo cambia el formato; la app nunca usa tipos de cambio en vivo

PRIVADA Y SIN CONEXIÓN
• Sin cuenta ni inicio de sesión. Todo se queda en tu teléfono y funciona sin internet
• Copia de seguridad como texto que puedes copiar o compartir y restaurar en cualquier dispositivo
• Temas claro y oscuro, colores de acento, tamaño de texto ajustable, 13 idiomas

BUDGET PLANNER PRO: compra única, sin suscripción
• Sobres ilimitados (el plan gratis tiene 8) y metas de ahorro (gratis: 3)
• Historial de más de 3 meses
• Exportación CSV de tu presupuesto
• Colores de acento extra y sin anuncios

Quitar anuncios también está disponible por separado como compra única.
</es-419>

<fr-FR>
Décidez de ce que fera votre argent avant le début du mois. Budget Planner répartit votre revenu mensuel en enveloppes, tient à jour un « reste à affecter » et montre ce qui reste libre dans chaque enveloppe à mesure que vous dépensez. Il planifie le mois à l’avance ; ce n’est pas un simple carnet de dépenses.

PLANIFIER LE MOIS
• Ajoutez vos revenus et affectez-les aux enveloppes jusqu’à ce que le reste à affecter atteigne zéro
• Démarrez un nouveau mois depuis le plan du précédent en un geste, ou répartissez le reste entre vos enveloppes
• Trop affecté ? Le montant passe au rouge et indique l’écart

DÉPENSER DEPUIS LES ENVELOPPES
• Enregistrez les dépenses dans une enveloppe, avec note et date
• Alertes quand une enveloppe est presque épuisée ou dépassée
• Déplacez de l’argent entre enveloppes pour combler un manque ; votre total ne change jamais

UNE RÈGLE DE REPORT PAR ENVELOPPE
• Choisissez report ou remise à zéro en fin de mois, enveloppe par enveloppe
• L’argent reporté (ou un dépassement) reste dans l’enveloppe ; l’argent remis à zéro retourne au reste à affecter

FACTURES ET OBJECTIFS D’ÉPARGNE
• Factures avec jour d’échéance et rappel le jour même, 1 ou 3 jours avant
• Marquer une facture comme payée enregistre la dépense dans son enveloppe
• Objectifs d’épargne avec date cible et montant à mettre de côté chaque mois

COMPARER LES MOIS
• Ce mois à côté du précédent : revenus, affecté et dépensé
• Repérez les enveloppes qui ont le plus varié

AU CENTIME PRÈS
• Tous les montants sont gérés en centimes entiers et chaque répartition est arrondie pour qu’aucun centime ne disparaisse : affecté plus reste égale toujours le revenu, et déplacer de l’argent ne change jamais le total
• Choisissez votre devise. Cela ne change que l’affichage ; l’appli n’utilise jamais de taux de change en direct

PRIVÉ ET HORS LIGNE
• Pas de compte, pas de connexion. Tout reste sur votre téléphone et fonctionne sans internet
• Sauvegarde sous forme de texte à copier ou partager, restauration sur n’importe quel appareil
• Thèmes clair et sombre, couleurs d’accent, taille du texte réglable, 13 langues

BUDGET PLANNER PRO : achat unique, sans abonnement
• Enveloppes illimitées (version gratuite : 8) et objectifs d’épargne (gratuit : 3)
• Historique au-delà des 3 derniers mois
• Export CSV de votre budget
• Couleurs d’accent en plus et aucune publicité

« Supprimer les pubs » est aussi proposé seul, en achat unique.
</fr-FR>

<hi-IN>
महीना शुरू होने से पहले तय करें कि आपका पैसा क्या करेगा। Budget Planner आपकी मासिक आय को लिफ़ाफ़ों में बाँटता है, “बाँटना बाकी” की रकम लगातार दिखाता है और खर्च करते समय हर लिफ़ाफ़े में बचा पैसा बताता है। यह महीने की पहले से योजना बनाता है; यह खर्च दर्ज करने का सिर्फ़ तेज़ रजिस्टर नहीं है।

महीने की योजना बनाएँ
• आय जोड़ें और उसे लिफ़ाफ़ों में तब तक बाँटें जब तक “बाँटना बाकी” शून्य न हो जाए
• एक टैप में पिछले महीने की योजना से नया महीना शुरू करें, या बचा हुआ पैसा लिफ़ाफ़ों में बाँट दें
• ज़्यादा बाँट दिया? रकम लाल हो जाती है और अंतर बताती है

लिफ़ाफ़ों से खर्च करें
• नोट और तारीख के साथ किसी लिफ़ाफ़े में खर्च दर्ज करें
• लिफ़ाफ़ा लगभग खत्म हो या सीमा पार हो तो चेतावनी
• कमी पूरी करने के लिए लिफ़ाफ़ों के बीच पैसे भेजें; आपका कुल कभी नहीं बदलता

हर लिफ़ाफ़े के लिए आगे ले जाने का नियम
• महीने के अंत में आगे ले जाएँ या रीसेट करें, हर लिफ़ाफ़े के लिए अलग
• आगे ले जाया गया पैसा (या अधिक खर्च) लिफ़ाफ़े में रहता है; रीसेट वाला पैसा “बाँटना बाकी” में लौट जाता है

बिल और बचत लक्ष्य
• देय दिन वाले बिल और उसी दिन, 1 या 3 दिन पहले रिमाइंडर
• बिल को चुकाया चिह्नित करने पर रकम उसके लिफ़ाफ़े में खर्च के रूप में दर्ज हो जाती है
• लक्ष्य तिथि वाले बचत लक्ष्य और हर महीने अलग रखने की रकम

महीनों की तुलना करें
• इस महीने को पिछले के साथ देखें: आय, बाँटा गया और खर्च
• देखें कि किन लिफ़ाफ़ों में सबसे ज़्यादा बदलाव हुआ

पाई-पाई सटीक
• सभी रकमें पूरी पाई/सेंट इकाइयों में रखी जाती हैं और हर बँटवारा इस तरह राउंड होता है कि कोई इकाई गायब न हो: बाँटा हुआ और बाकी हमेशा आय के बराबर होता है, और पैसे भेजने से कुल कभी नहीं बदलता
• अपनी मुद्रा चुनें। इससे केवल प्रारूप बदलता है; ऐप कभी लाइव विनिमय दर नहीं लेता

निजी और ऑफ़लाइन
• कोई खाता या साइन-इन नहीं। सब कुछ आपके फ़ोन में रहता है और बिना इंटरनेट चलता है
• कॉपी या शेयर किए जा सकने वाले टेक्स्ट के रूप में बैकअप लें और किसी भी डिवाइस पर रीस्टोर करें
• लाइट और डार्क थीम, अतिरिक्त रंग, बदलने योग्य टेक्स्ट आकार, 13 भाषाएँ

BUDGET PLANNER PRO: एक बार की खरीद, कोई सब्सक्रिप्शन नहीं
• असीमित लिफ़ाफ़े (मुफ़्त प्लान: 8) और बचत लक्ष्य (मुफ़्त: 3)
• पिछले 3 महीनों से पुराना इतिहास
• आपके बजट का CSV एक्सपोर्ट
• अतिरिक्त रंग और कोई विज्ञापन नहीं

“विज्ञापन हटाएँ” अलग से भी एक बार की खरीद के रूप में उपलब्ध है।
</hi-IN>

<id>
Tentukan tugas uangmu sebelum bulan dimulai. Budget Planner membagi penghasilan bulananmu ke dalam amplop, menjaga angka "belum dialokasikan" tetap terbarui, dan menunjukkan sisa tiap amplop saat kamu membelanjakan. Aplikasi ini merencanakan bulan ke depan; bukan pencatat pengeluaran cepat.

RENCANAKAN BULANMU
• Tambahkan penghasilan lalu alokasikan ke amplop sampai Belum dialokasikan menjadi nol
• Mulai bulan baru dari rencana bulan lalu dengan satu ketukan, atau bagi sisanya ke amplop-amplopmu
• Kelebihan alokasi? Angkanya berubah merah dan menunjukkan selisihnya

BELANJA DARI AMPLOP
• Catat pengeluaran pada sebuah amplop, lengkap dengan catatan dan tanggal
• Peringatan saat amplop hampir habis atau kelebihan
• Pindahkan uang antar amplop untuk menutup kekurangan; totalmu tidak pernah berubah

ATURAN SISA UNTUK SETIAP AMPLOP
• Pilih bawa ke depan atau atur ulang di akhir bulan, per amplop
• Uang yang dibawa (atau kelebihan belanja) tetap di amplop; uang yang diatur ulang kembali ke Belum dialokasikan

TAGIHAN DAN TARGET TABUNGAN
• Tagihan dengan tanggal jatuh tempo dan pengingat pada hari itu, 1 atau 3 hari sebelumnya
• Tandai tagihan lunas dan jumlahnya tercatat sebagai pengeluaran di amplopnya
• Target tabungan dengan tanggal target dan jumlah yang perlu disisihkan tiap bulan

BANDINGKAN BULAN
• Bulan ini di samping bulan lalu: penghasilan, dialokasikan, dan terpakai
• Lihat amplop mana yang paling berubah

TEPAT HINGGA SEN
• Semua jumlah disimpan dalam satuan sen utuh dan setiap pembagian dibulatkan agar tidak ada yang hilang: dialokasikan ditambah sisa selalu sama dengan penghasilan, dan memindahkan uang tidak pernah mengubah total
• Pilih mata uangmu. Ini hanya mengubah format; aplikasi tidak pernah memakai kurs langsung

PRIVAT DAN TANPA INTERNET
• Tanpa akun, tanpa masuk. Semua tetap di ponselmu dan berfungsi tanpa internet
• Cadangkan sebagai teks yang bisa disalin atau dibagikan, lalu pulihkan di perangkat mana pun
• Tema terang dan gelap, warna aksen, ukuran teks yang bisa diatur, 13 bahasa

BUDGET PLANNER PRO: sekali bayar, tanpa langganan
• Amplop tanpa batas (paket gratis: 8) dan target tabungan (gratis: 3)
• Riwayat lebih dari 3 bulan terakhir
• Ekspor CSV anggaranmu
• Warna aksen tambahan dan tanpa iklan

Hapus Iklan juga tersedia terpisah sebagai pembelian sekali bayar.
</id>

<it-IT>
Decidi cosa farà il tuo denaro prima che il mese cominci. Budget Planner divide il reddito mensile in buste, mantiene una cifra "da assegnare" aggiornata e mostra quanto resta libero in ogni busta mentre spendi. Pianifica il mese in anticipo; non è un semplice registro delle spese.

PIANIFICA IL MESE
• Aggiungi le entrate e assegnale alle buste finché Da assegnare arriva a zero
• Inizia un nuovo mese dal piano del precedente con un tocco, o distribuisci il resto tra le buste
• Assegnato troppo? La cifra diventa rossa e indica di quanto

SPENDI DALLE BUSTE
• Registra le spese su una busta, con nota e data
• Avvisi quando una busta è quasi esaurita o sforata
• Sposta denaro tra le buste per coprire un ammanco; il totale non cambia mai

UNA REGOLA DI RIPORTO PER OGNI BUSTA
• Scegli riporta o azzera a fine mese, busta per busta
• Il denaro riportato (o uno sforamento) resta nella busta; quello azzerato torna in Da assegnare

BOLLETTE E OBIETTIVI DI RISPARMIO
• Bollette con giorno di scadenza e promemoria il giorno stesso, 1 o 3 giorni prima
• Segnare una bolletta come pagata registra la spesa nella sua busta
• Obiettivi di risparmio con data e la rata mensile da mettere da parte

CONFRONTA I MESI
• Questo mese accanto al precedente: entrate, assegnato e speso
• Scopri quali buste sono cambiate di più

AL CENTESIMO
• Tutti gli importi sono tenuti in centesimi interi e ogni ripartizione è arrotondata perché nessun centesimo vada perso: assegnato più residuo fa sempre il reddito, e spostare denaro non cambia mai il totale
• Scegli la valuta. Cambia solo la formattazione; l’app non usa mai tassi di cambio in tempo reale

PRIVATO E OFFLINE
• Nessun account, nessun accesso. Tutto resta sul telefono e funziona senza internet
• Backup come testo da copiare o condividere, ripristinabile su qualsiasi dispositivo
• Temi chiaro e scuro, colori di accento, dimensione del testo regolabile, 13 lingue

BUDGET PLANNER PRO: acquisto unico, nessun abbonamento
• Buste illimitate (piano gratuito: 8) e obiettivi di risparmio (gratuito: 3)
• Storico oltre gli ultimi 3 mesi
• Esportazione CSV del budget
• Colori di accento extra e nessuna pubblicità

Anche Rimuovi pubblicità è disponibile da solo come acquisto unico.
</it-IT>

<ja-JP>
月が始まる前に、お金の使い道を決めましょう。Budget Planner は月の収入を封筒に分け、「未割り当て」の金額を常に表示し、使うたびに各封筒の残りを示します。月を先に計画するアプリで、手早い支出記録アプリではありません。

月を計画する
• 収入を追加し、「未割り当て」がゼロになるまで封筒に割り当てます
• ワンタップで先月の計画から新しい月を始めたり、残りを封筒に配分したりできます
• 割り当てすぎると金額が赤くなり、超過額を表示します

封筒から使う
• メモと日付つきで封筒に支出を記録
• 封筒がほぼ空、または超過すると警告
• 不足分は封筒間でお金を移して補えます。合計は変わりません

封筒ごとの繰り越しルール
• 月末に「繰り越す」か「リセット」かを封筒ごとに選べます
• 繰り越したお金（または超過分）は封筒に残り、リセットしたお金は「未割り当て」に戻ります

支払いと貯蓄目標
• 期日を決めて、当日・1日前・3日前に通知する支払い
• 支払い済みにすると、その封筒の支出として金額が記録されます
• 目標日つきの貯蓄目標と、毎月取り分ける金額

月を比べる
• 今月と先月を並べて表示：収入、割り当て、支出
• 変化の大きかった封筒がわかります

1円（1セント）まで正確
• 金額は最小単位の整数で保持し、どの分割も端数が消えないように丸めます。割り当て済みと残りの合計は常に収入と一致し、お金を移しても合計は変わりません
• 通貨を選べます。変わるのは表示形式のみで、リアルタイムの為替レートは使いません

プライベートでオフライン
• アカウントもログインも不要。データは端末内にとどまり、インターネットなしで動作します
• コピーや共有ができるテキストでバックアップし、どの端末でも復元できます
• ライト／ダークテーマ、アクセントカラー、文字サイズ調整、13言語に対応

BUDGET PLANNER PRO：買い切り、サブスクなし
• 封筒（無料版は8個）と貯蓄目標（無料版は3件）が無制限
• 直近3か月より前の履歴
• 予算のCSVエクスポート
• 追加のアクセントカラーと広告なし

「広告を削除」だけを単体の買い切りとして購入することもできます。
</ja-JP>

<pt-BR>
Decida o que o seu dinheiro vai fazer antes de o mês começar. O Budget Planner divide a renda mensal em envelopes, mantém um valor "falta distribuir" atualizado e mostra o que ainda está livre em cada envelope conforme você gasta. Ele planeja o mês com antecedência; não é um simples registro de gastos.

PLANEJE O MÊS
• Adicione sua renda e distribua nos envelopes até o Falta distribuir chegar a zero
• Comece um mês novo com o plano do anterior em um toque, ou divida o que sobrou entre os envelopes
• Distribuiu demais? O valor fica vermelho e mostra a diferença

GASTE A PARTIR DOS ENVELOPES
• Registre gastos em um envelope, com nota e data
• Avisos quando um envelope está quase esgotado ou estourado
• Mova dinheiro entre envelopes para cobrir uma falta; seu total nunca muda

UMA REGRA DE ACÚMULO PARA CADA ENVELOPE
• Escolha acumular ou zerar no fim do mês, envelope por envelope
• O dinheiro acumulado (ou um estouro) fica no envelope; o zerado volta para Falta distribuir

CONTAS E METAS DE ECONOMIA
• Contas com dia de vencimento e lembrete no próprio dia, 1 ou 3 dias antes
• Marcar uma conta como paga registra o valor como gasto no envelope dela
• Metas de economia com data e o valor a separar a cada mês

COMPARE OS MESES
• Este mês ao lado do anterior: renda, distribuído e gasto
• Veja quais envelopes mais mudaram

CENTAVO POR CENTAVO
• Todos os valores são guardados em centavos inteiros e cada divisão é arredondada para que nenhum centavo se perca: distribuído mais o que falta sempre dá a renda, e mover dinheiro nunca muda o total
• Escolha sua moeda. Isso muda só a formatação; o app nunca usa câmbio em tempo real

PRIVADO E OFFLINE
• Sem conta e sem login. Tudo fica no seu telefone e funciona sem internet
• Backup em texto para copiar ou compartilhar e restaurar em qualquer aparelho
• Temas claro e escuro, cores de destaque, tamanho de texto ajustável, 13 idiomas

BUDGET PLANNER PRO: compra única, sem assinatura
• Envelopes ilimitados (plano grátis: 8) e metas de economia (grátis: 3)
• Histórico além dos últimos 3 meses
• Exportação CSV do orçamento
• Cores de destaque extras e sem anúncios

Remover anúncios também está disponível separadamente como compra única.
</pt-BR>

<tr-TR>
Ay başlamadan paranın ne yapacağına karar ver. Budget Planner aylık gelirini zarflara böler, "dağıtılacak" tutarı canlı tutar ve harcadıkça her zarfta ne kadar yer kaldığını gösterir. Ayı önceden planlar; hızlı bir harcama defteri değildir.

AYI PLANLA
• Gelirini ekle, Dağıtılacak tutar sıfıra inene kadar zarflara ayır
• Yeni ayı tek dokunuşla geçen ayın planından başlat ya da kalanı zarflara dağıt
• Fazla mı dağıttın? Tutar kırmızı olur ve farkı söyler

ZARFLARDAN HARCA
• Harcamayı bir zarfa not ve tarihle kaydet
• Zarf neredeyse bittiğinde ya da aşıldığında uyarı
• Açığı kapatmak için zarflar arasında para aktar; toplamın hiç değişmez

HER ZARF İÇİN BİR DEVİR KURALI
• Ay sonunda devret ya da sıfırla, zarf zarf seç
• Devreden para (veya aşım) zarfta kalır; sıfırlanan para Dağıtılacak tutara döner

FATURALAR VE BİRİKİM HEDEFLERİ
• Son ödeme günü olan faturalar; aynı gün, 1 gün veya 3 gün önce hatırlatma
• Faturayı ödendi işaretlemek tutarı kendi zarfında harcama olarak kaydeder
• Hedef tarihli birikim hedefleri ve her ay ayırman gereken tutar

AYLARI KARŞILAŞTIR
• Bu ay geçen ayın yanında: gelir, dağıtılan ve harcanan
• En çok değişen zarfları gör

KURUŞUNA KADAR
• Tüm tutarlar tam kuruş olarak tutulur ve her bölüşüm hiçbir kuruş kaybolmayacak şekilde yuvarlanır: dağıtılan artı kalan her zaman geliri verir, para aktarmak toplamı asla değiştirmez
• Para birimini seç. Bu yalnızca biçimi değiştirir; uygulama canlı döviz kuru kullanmaz

ÖZEL VE İNTERNETSİZ
• Hesap yok, oturum açma yok. Her şey telefonunda kalır ve internetsiz çalışır
• Kopyalayıp paylaşabileceğin metin olarak yedekle, her cihazda geri yükle
• Açık ve koyu tema, vurgu renkleri, ayarlanabilir yazı boyutu, 13 dil

BUDGET PLANNER PRO: tek seferlik satın alma, abonelik yok
• Sınırsız zarf (ücretsiz plan: 8) ve birikim hedefi (ücretsiz: 3)
• Son 3 aydan öncesine ait geçmiş
• Bütçeni CSV olarak dışa aktarma
• Ek vurgu renkleri ve reklamsız kullanım

Reklamları Kaldır da tek başına, tek seferlik satın alma olarak mevcuttur.
</tr-TR>

<uk>
Вирішіть, що робитимуть ваші гроші, ще до початку місяця. Budget Planner розподіляє місячний дохід по конвертах, постійно показує суму «залишилось розподілити» і те, скільки ще вільно в кожному конверті, коли ви витрачаєте. Він планує місяць наперед і не є швидким журналом витрат.

ПЛАНУЙТЕ МІСЯЦЬ
• Додайте дохід і розподіліть його по конвертах, доки «Залишилось розподілити» не стане нулем
• Почніть новий місяць із плану минулого одним дотиком або розподіліть залишок по конвертах
• Розподілили забагато? Сума стає червоною й показує на скільки

ВИТРАЧАЙТЕ З КОНВЕРТІВ
• Записуйте витрати на конверт із нотаткою та датою
• Попередження, коли конверт майже порожній або перевищений
• Переносьте гроші між конвертами, щоб покрити нестачу; загальна сума не змінюється

ПРАВИЛО ПЕРЕНЕСЕННЯ ДЛЯ КОЖНОГО КОНВЕРТА
• Наприкінці місяця — переносити чи скидати, для кожного конверта окремо
• Перенесені гроші (або перевитрата) лишаються в конверті; скинуті повертаються до «Залишилось розподілити»

РАХУНКИ ТА ЦІЛІ НАКОПИЧЕННЯ
• Рахунки з днем оплати та нагадуванням у цей день, за 1 або 3 дні
• Позначте рахунок сплаченим — суму буде записано як витрату в його конверті
• Цілі накопичення з цільовою датою та сумою, яку треба відкладати щомісяця

ПОРІВНЮЙТЕ МІСЯЦІ
• Цей місяць поруч із минулим: дохід, розподілено, витрачено
• Дивіться, які конверти змінилися найбільше

З ТОЧНІСТЮ ДО КОПІЙКИ
• Усі суми зберігаються в цілих копійках, а кожен розподіл округлюється так, щоб жодна копійка не зникла: розподілене плюс залишок завжди дорівнює доходу, а перенесення грошей ніколи не змінює загальну суму
• Оберіть валюту. Це змінює лише формат; застосунок ніколи не використовує поточні курси

ПРИВАТНО Й ОФЛАЙН
• Без облікового запису та входу. Усе лишається на телефоні й працює без інтернету
• Резервна копія як текст, яким можна поділитися, і відновлення на будь-якому пристрої
• Світла й темна теми, акцентні кольори, регульований розмір тексту, 13 мов

BUDGET PLANNER PRO: разова покупка, без підписки
• Необмежена кількість конвертів (безкоштовно: 8) і цілей (безкоштовно: 3)
• Історія понад останні 3 місяці
• Експорт бюджету в CSV
• Додаткові акцентні кольори й без реклами

«Вимкнути рекламу» також доступно окремо як разова покупка.
</uk>

<zh-CN>
在月初之前，先决定钱要做什么。Budget Planner 把月收入分进信封，实时显示“待分配”金额，并在你花钱时告诉你每个信封还剩多少。它用来提前规划整个月，不是一个快速记账本。

规划这个月
• 添加收入，把它分配到各个信封，直到“待分配”为零
• 一键用上个月的计划开始新月份，或把剩余的钱分给各个信封
• 分配多了？金额会变红，并告诉你多了多少

从信封里花钱
• 把支出记到某个信封，可附备注和日期
• 信封快用完或超支时会提醒
• 在信封之间转移资金来补缺口，总额始终不变

每个信封一条结转规则
• 月底选择结转还是清零，每个信封各自设定
• 结转的钱（或超支）留在信封里；清零的钱回到“待分配”

账单与储蓄目标
• 账单可设到期日，并在当天、提前 1 天或 3 天提醒
• 把账单标为已付，金额会记为对应信封的支出
• 储蓄目标含目标日期，以及每月需要存下的金额

对比月份
• 把本月与上月并排查看：收入、已分配、已花
• 看出哪些信封变化最大

精确到分
• 所有金额都以整数“分”保存，每次拆分都经过取整处理，不会丢失一分钱：已分配加剩余始终等于收入，转移资金也不会改变总额
• 可选择货币。这只影响显示格式；应用从不使用实时汇率

隐私且离线
• 无需账号，无需登录。所有数据都留在手机上，没有网络也能用
• 以可复制或分享的文本备份，并可在任何设备上恢复
• 浅色和深色主题、主题色、可调文字大小、13 种语言

BUDGET PLANNER PRO：一次性购买，无订阅
• 不限数量的信封（免费版 8 个）和储蓄目标（免费版 3 个）
• 超过最近 3 个月的历史记录
• 导出预算 CSV
• 更多主题色且无广告

“去除广告”也可单独一次性购买。
</zh-CN>

---

## SUBTITLE (≤30 chars per locale)

_Apple App Store Connect → App Information → Subtitle_

<en-US>
Monthly envelope budgeting
</en-US>

<ar>
ميزانية شهرية بالمظاريف
</ar>

<de-DE>
Monatsbudget mit Umschlägen
</de-DE>

<es-419>
Presupuesto mensual en sobres
</es-419>

<fr-FR>
Budget mensuel par enveloppes
</fr-FR>

<hi-IN>
लिफ़ाफ़ों से मासिक बजट
</hi-IN>

<id>
Anggaran bulanan dengan amplop
</id>

<it-IT>
Budget mensile a buste
</it-IT>

<ja-JP>
封筒で管理する月次予算
</ja-JP>

<pt-BR>
Orçamento mensal em envelopes
</pt-BR>

<tr-TR>
Zarflarla aylık bütçe
</tr-TR>

<uk>
Місячний бюджет у конвертах
</uk>

<zh-CN>
信封法月度预算
</zh-CN>

---

## KEYWORDS (≤100 chars per locale)

_Apple App Store Connect → Version → Keywords_

<en-US>
budget planner,envelope budget,monthly budget,zero based budget,savings goals,bill reminders
</en-US>

<ar>
مخطط ميزانية,ميزانية شهرية,طريقة المظاريف,أهداف الادخار,تذكير الفواتير,توفير
</ar>

<de-DE>
Budgetplaner,Umschlagmethode,Monatsbudget,Haushaltsbuch,Sparziele,Rechnungen Erinnerung
</de-DE>

<es-419>
presupuesto mensual,método de sobres,planificador,metas de ahorro,recordatorio de facturas,ahorro
</es-419>

<fr-FR>
budget mensuel,méthode des enveloppes,planificateur,objectifs d’épargne,rappel factures,épargne
</fr-FR>

<hi-IN>
बजट प्लानर,मासिक बजट,लिफ़ाफ़ा विधि,बचत लक्ष्य,बिल रिमाइंडर,बचत
</hi-IN>

<id>
perencana anggaran,anggaran bulanan,metode amplop,target tabungan,pengingat tagihan,menabung
</id>

<it-IT>
budget mensile,metodo delle buste,pianificatore,obiettivi di risparmio,promemoria bollette,risparmio
</it-IT>

<ja-JP>
予算管理,家計簿,封筒式,貯蓄目標,支払い通知,月次予算
</ja-JP>

<pt-BR>
orçamento mensal,método dos envelopes,planejador,metas de economia,lembrete de contas,poupança
</pt-BR>

<tr-TR>
bütçe planlayıcı,aylık bütçe,zarf yöntemi,birikim hedefi,fatura hatırlatıcı,tasarruf
</tr-TR>

<uk>
планувальник бюджету,місячний бюджет,метод конвертів,цілі накопичення,нагадування про рахунки
</uk>

<zh-CN>
预算规划,月度预算,信封预算,储蓄目标,账单提醒,理财
</zh-CN>

---

## PROMOTIONAL TEXT (≤170 chars per locale)

_Apple App Store Connect → Version → Promotional Text_

<en-US>
Give every bit of income a job. Split your month into envelopes, watch Left to assign reach zero, and compare months. Bills, goals and reminders included. Works offline.
</en-US>

<ar>
امنح كل جزء من دخلك مهمة. وزّع الشهر على مظاريف، وأنزل المتبقي للتوزيع إلى الصفر، وقارن الأشهر. فواتير وأهداف. يعمل بدون إنترنت.
</ar>

<de-DE>
Gib jedem Teil deines Einkommens eine Aufgabe. Teile den Monat auf Umschläge auf, bring „Noch zu verteilen“ auf null, vergleiche Monate. Rechnungen und Ziele. Offline.
</de-DE>

<es-419>
Dale un destino a cada parte de tu ingreso. Reparte el mes en sobres, lleva Por asignar a cero y compara meses. Incluye facturas y metas. Funciona sin conexión.
</es-419>

<fr-FR>
Donnez une mission à chaque centime de revenu. Répartissez le mois en enveloppes, ramenez le reste à affecter à zéro, comparez les mois. Factures, objectifs. Hors ligne.
</fr-FR>

<hi-IN>
आय के हर हिस्से को काम दें। महीने को लिफ़ाफ़ों में बाँटें, “बाँटना बाकी” को शून्य तक लाएँ और महीनों की तुलना करें। बिल और लक्ष्य शामिल। ऑफ़लाइन।
</hi-IN>

<id>
Beri tugas pada setiap bagian penghasilan. Bagi bulan ke dalam amplop, bawa Belum dialokasikan ke nol, dan bandingkan bulan. Tagihan dan target ada. Tanpa internet.
</id>

<it-IT>
Dai un compito a ogni parte del reddito. Dividi il mese in buste, porta Da assegnare a zero e confronta i mesi. Bollette e obiettivi inclusi. Funziona offline.
</it-IT>

<ja-JP>
収入のすべてに役割を。月を封筒に分けて「未割り当て」をゼロにし、月どうしを比べましょう。支払いと目標も管理。オフラインで使えます。
</ja-JP>

<pt-BR>
Dê uma função a cada parte da renda. Divida o mês em envelopes, leve o Falta distribuir a zero e compare os meses. Contas e metas incluídas. Funciona offline.
</pt-BR>

<tr-TR>
Gelirinin her parçasına bir görev ver. Ayı zarflara böl, Dağıtılacak tutarı sıfıra indir ve ayları karşılaştır. Fatura ve hedefler dahil. İnternetsiz çalışır.
</tr-TR>

<uk>
Дайте призначення кожній частині доходу. Розподіліть місяць по конвертах, доведіть «Залишилось розподілити» до нуля й порівнюйте місяці. Рахунки та цілі. Офлайн.
</uk>

<zh-CN>
让每一笔收入都有用途。把一个月分进信封，把“待分配”降到零，再对比各月。含账单与目标，可离线使用。
</zh-CN>

---
