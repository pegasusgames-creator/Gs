#!/usr/bin/env python3
"""
add_translations.py
Injects a multi-language system (22 languages) into all 6 game.html files:
  - Language selector added to Settings screen
  - Login streak overlay fully translated
  - Key static UI strings translated (menu buttons, settings labels, overlays)
  - Language choice persisted in localStorage

Prioritised by puzzle-game revenue markets:
  EN, DE, FR, ES, PT, RU, JA, KO, ZH, AR, TR, IT, NL, PL, SV, NO, DA, FI, TH, VI, ID, HI
"""

import os
import re

BASE = "/home/pgs/Documents/Gs"
GAMES = ["BallSortPuzzle", "WaterSort", "Nonogram", "PipeConnect", "Puzzle2048", "UnblockPuzzle"]

# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATIONS  (key strings used across all games)
# ─────────────────────────────────────────────────────────────────────────────
TRANSLATIONS_JS = r"""
window.GAME_I18N = {
  en: {
    play:'Play', levels:'Levels', levelSelect:'Level Select', shop:'Shop',
    settings:'Settings', dailyChallenge:'Daily Challenge', back:'Back',
    sound:'Sound', music:'Music', resetProgress:'Reset Progress',
    removeAds:'Remove Ads', language:'Language',
    levelComplete:'Level Complete!', gameOver:'Game Over',
    hint:'Hint', undo:'Undo', skip:'Skip', quit:'Quit', menu:'Menu',
    noLives:'No Lives Left', watchAd:'Watch Ad for Life',
    lives:'Lives', coins:'Coins', buy:'Buy', owned:'Owned',
    next:'Next Level', retry:'Try Again',
    // Login streak
    ls_title:'Day %d Streak!',
    ls_sub:'Come back every day for bigger rewards',
    ls_bonus:'Today\'s Bonus',
    ls_claim:'Claim Reward!',
    ls_week:'One Week!',
    // Achievements
    ls_ach3:'🌟 3-Day Streak! +%d 🪙',
    ls_ach7:'🏆 One Full Week! +%d 🪙',
    ls_ach14:'💎 Two Weeks! +%d 🪙',
    ls_ach30:'👑 Legend! +%d 🪙',
  },
  de: {
    play:'Spielen', levels:'Level', levelSelect:'Level Auswahl', shop:'Shop',
    settings:'Einstellungen', dailyChallenge:'Tägliche Aufgabe', back:'Zurück',
    sound:'Ton', music:'Musik', resetProgress:'Fortschritt Zurücksetzen',
    removeAds:'Werbung Entfernen', language:'Sprache',
    levelComplete:'Level Geschafft!', gameOver:'Spiel Vorbei',
    hint:'Hinweis', undo:'Rückgängig', skip:'Überspringen', quit:'Beenden', menu:'Menü',
    noLives:'Keine Leben mehr', watchAd:'Werbung für ein Leben ansehen',
    lives:'Leben', coins:'Münzen', buy:'Kaufen', owned:'Besessen',
    next:'Nächstes Level', retry:'Nochmal versuchen',
    ls_title:'Tag %d Streak!',
    ls_sub:'Komm jeden Tag zurück für größere Belohnungen',
    ls_bonus:'Heutige Belohnung',
    ls_claim:'Belohnung Einfordern!',
    ls_ach3:'🌟 3-Tage Streak! +%d 🪙',
    ls_ach7:'🏆 Eine volle Woche! +%d 🪙',
    ls_ach14:'💎 Zwei Wochen! +%d 🪙',
    ls_ach30:'👑 Legende! +%d 🪙',
  },
  fr: {
    play:'Jouer', levels:'Niveaux', levelSelect:'Choisir un Niveau', shop:'Boutique',
    settings:'Paramètres', dailyChallenge:'Défi du Jour', back:'Retour',
    sound:'Son', music:'Musique', resetProgress:'Réinitialiser',
    removeAds:'Supprimer les Pubs', language:'Langue',
    levelComplete:'Niveau Terminé!', gameOver:'Partie Terminée',
    hint:'Indice', undo:'Annuler', skip:'Passer', quit:'Quitter', menu:'Menu',
    noLives:'Plus de Vies', watchAd:'Voir une Pub pour une Vie',
    lives:'Vies', coins:'Pièces', buy:'Acheter', owned:'Possédé',
    next:'Niveau Suivant', retry:'Réessayer',
    ls_title:'Jour %d Streak!',
    ls_sub:'Revenez chaque jour pour de meilleures récompenses',
    ls_bonus:'Bonus du Jour',
    ls_claim:'Récupérer!',
    ls_ach3:'🌟 3 Jours! +%d 🪙',
    ls_ach7:'🏆 Une Semaine Complète! +%d 🪙',
    ls_ach14:'💎 Deux Semaines! +%d 🪙',
    ls_ach30:'👑 Légende! +%d 🪙',
  },
  es: {
    play:'Jugar', levels:'Niveles', levelSelect:'Seleccionar Nivel', shop:'Tienda',
    settings:'Ajustes', dailyChallenge:'Reto Diario', back:'Volver',
    sound:'Sonido', music:'Música', resetProgress:'Reiniciar Progreso',
    removeAds:'Quitar Anuncios', language:'Idioma',
    levelComplete:'¡Nivel Completado!', gameOver:'Game Over',
    hint:'Pista', undo:'Deshacer', skip:'Saltar', quit:'Salir', menu:'Menú',
    noLives:'Sin Vidas', watchAd:'Ver Anuncio por una Vida',
    lives:'Vidas', coins:'Monedas', buy:'Comprar', owned:'Comprado',
    next:'Siguiente Nivel', retry:'Intentar de Nuevo',
    ls_title:'¡Día %d seguido!',
    ls_sub:'Vuelve cada día para mejores premios',
    ls_bonus:'Premio de Hoy',
    ls_claim:'¡Reclamar Premio!',
    ls_ach3:'🌟 ¡3 días! +%d 🪙',
    ls_ach7:'🏆 ¡Una semana completa! +%d 🪙',
    ls_ach14:'💎 ¡Dos semanas! +%d 🪙',
    ls_ach30:'👑 ¡Leyenda! +%d 🪙',
  },
  pt: {
    play:'Jogar', levels:'Níveis', levelSelect:'Selecionar Nível', shop:'Loja',
    settings:'Configurações', dailyChallenge:'Desafio Diário', back:'Voltar',
    sound:'Som', music:'Música', resetProgress:'Redefinir Progresso',
    removeAds:'Remover Anúncios', language:'Idioma',
    levelComplete:'Nível Completo!', gameOver:'Fim de Jogo',
    hint:'Dica', undo:'Desfazer', skip:'Pular', quit:'Sair', menu:'Menu',
    noLives:'Sem Vidas', watchAd:'Assistir Anúncio por uma Vida',
    lives:'Vidas', coins:'Moedas', buy:'Comprar', owned:'Adquirido',
    next:'Próximo Nível', retry:'Tentar Novamente',
    ls_title:'Dia %d seguido!',
    ls_sub:'Volte todo dia para prêmios maiores',
    ls_bonus:'Bônus de Hoje',
    ls_claim:'Resgatar Prêmio!',
    ls_ach3:'🌟 3 dias! +%d 🪙',
    ls_ach7:'🏆 Uma semana completa! +%d 🪙',
    ls_ach14:'💎 Duas semanas! +%d 🪙',
    ls_ach30:'👑 Lenda! +%d 🪙',
  },
  ru: {
    play:'Играть', levels:'Уровни', levelSelect:'Выбор Уровня', shop:'Магазин',
    settings:'Настройки', dailyChallenge:'Ежедневный Вызов', back:'Назад',
    sound:'Звук', music:'Музыка', resetProgress:'Сбросить Прогресс',
    removeAds:'Убрать Рекламу', language:'Язык',
    levelComplete:'Уровень Пройден!', gameOver:'Игра Окончена',
    hint:'Подсказка', undo:'Отмена', skip:'Пропустить', quit:'Выйти', menu:'Меню',
    noLives:'Нет жизней', watchAd:'Смотреть рекламу за жизнь',
    lives:'Жизни', coins:'Монеты', buy:'Купить', owned:'Куплено',
    next:'Следующий уровень', retry:'Попробовать снова',
    ls_title:'День %d подряд!',
    ls_sub:'Возвращайтесь каждый день за большими наградами',
    ls_bonus:'Бонус дня',
    ls_claim:'Забрать награду!',
    ls_ach3:'🌟 3 дня! +%d 🪙',
    ls_ach7:'🏆 Целая неделя! +%d 🪙',
    ls_ach14:'💎 Две недели! +%d 🪙',
    ls_ach30:'👑 Легенда! +%d 🪙',
  },
  ja: {
    play:'プレイ', levels:'レベル', levelSelect:'レベル選択', shop:'ショップ',
    settings:'設定', dailyChallenge:'デイリーチャレンジ', back:'戻る',
    sound:'サウンド', music:'音楽', resetProgress:'進行状況をリセット',
    removeAds:'広告を削除', language:'言語',
    levelComplete:'レベルクリア！', gameOver:'ゲームオーバー',
    hint:'ヒント', undo:'元に戻す', skip:'スキップ', quit:'終了', menu:'メニュー',
    noLives:'ライフがありません', watchAd:'広告を見てライフを獲得',
    lives:'ライフ', coins:'コイン', buy:'購入', owned:'購入済み',
    next:'次のレベル', retry:'もう一度',
    ls_title:'%d日連続ログイン！',
    ls_sub:'毎日ログインしてより大きな報酬をゲット',
    ls_bonus:'本日のボーナス',
    ls_claim:'報酬を受け取る！',
    ls_ach3:'🌟 3日連続！ +%d 🪙',
    ls_ach7:'🏆 1週間！ +%d 🪙',
    ls_ach14:'💎 2週間！ +%d 🪙',
    ls_ach30:'👑 レジェンド！ +%d 🪙',
  },
  ko: {
    play:'플레이', levels:'레벨', levelSelect:'레벨 선택', shop:'상점',
    settings:'설정', dailyChallenge:'일일 도전', back:'뒤로',
    sound:'사운드', music:'음악', resetProgress:'진행 초기화',
    removeAds:'광고 제거', language:'언어',
    levelComplete:'레벨 완료!', gameOver:'게임 오버',
    hint:'힌트', undo:'실행 취소', skip:'건너뛰기', quit:'종료', menu:'메뉴',
    noLives:'목숨 없음', watchAd:'광고 보고 목숨 얻기',
    lives:'목숨', coins:'코인', buy:'구매', owned:'구매됨',
    next:'다음 레벨', retry:'다시 시도',
    ls_title:'%d일 연속 접속!',
    ls_sub:'매일 돌아와서 더 큰 보상을 받으세요',
    ls_bonus:'오늘의 보너스',
    ls_claim:'보상 받기!',
    ls_ach3:'🌟 3일 연속! +%d 🪙',
    ls_ach7:'🏆 일주일 완료! +%d 🪙',
    ls_ach14:'💎 2주 완료! +%d 🪙',
    ls_ach30:'👑 레전드! +%d 🪙',
  },
  zh: {
    play:'开始游戏', levels:'关卡', levelSelect:'选择关卡', shop:'商店',
    settings:'设置', dailyChallenge:'每日挑战', back:'返回',
    sound:'音效', music:'音乐', resetProgress:'重置进度',
    removeAds:'去除广告', language:'语言',
    levelComplete:'关卡完成！', gameOver:'游戏结束',
    hint:'提示', undo:'撤销', skip:'跳过', quit:'退出', menu:'菜单',
    noLives:'没有生命了', watchAd:'看广告获得生命',
    lives:'生命', coins:'金币', buy:'购买', owned:'已购买',
    next:'下一关', retry:'再试一次',
    ls_title:'第%d天连续登录！',
    ls_sub:'每天回来获得更大的奖励',
    ls_bonus:'今日奖励',
    ls_claim:'领取奖励！',
    ls_ach3:'🌟 3天连续！ +%d 🪙',
    ls_ach7:'🏆 满一周！ +%d 🪙',
    ls_ach14:'💎 两周！ +%d 🪙',
    ls_ach30:'👑 传奇！ +%d 🪙',
  },
  ar: {
    play:'العب', levels:'المستويات', levelSelect:'اختر المستوى', shop:'المتجر',
    settings:'الإعدادات', dailyChallenge:'التحدي اليومي', back:'رجوع',
    sound:'الصوت', music:'الموسيقى', resetProgress:'إعادة التعيين',
    removeAds:'إزالة الإعلانات', language:'اللغة',
    levelComplete:'اكتمل المستوى!', gameOver:'انتهت اللعبة',
    hint:'تلميح', undo:'تراجع', skip:'تخطي', quit:'خروج', menu:'القائمة',
    noLives:'لا حياة متبقية', watchAd:'شاهد إعلاناً للحصول على حياة',
    lives:'حياة', coins:'عملات', buy:'اشتر', owned:'مُمتَلك',
    next:'المستوى التالي', retry:'حاول مجدداً',
    ls_title:'يوم %d متتالي!',
    ls_sub:'عد كل يوم للحصول على مكافآت أكبر',
    ls_bonus:'مكافأة اليوم',
    ls_claim:'احصل على المكافأة!',
    ls_ach3:'🌟 3 أيام! +%d 🪙',
    ls_ach7:'🏆 أسبوع كامل! +%d 🪙',
    ls_ach14:'💎 أسبوعان! +%d 🪙',
    ls_ach30:'👑 أسطورة! +%d 🪙',
  },
  tr: {
    play:'Oyna', levels:'Seviyeler', levelSelect:'Seviye Seç', shop:'Mağaza',
    settings:'Ayarlar', dailyChallenge:'Günlük Görev', back:'Geri',
    sound:'Ses', music:'Müzik', resetProgress:'İlerlemeyi Sıfırla',
    removeAds:'Reklamları Kaldır', language:'Dil',
    levelComplete:'Seviye Tamamlandı!', gameOver:'Oyun Bitti',
    hint:'İpucu', undo:'Geri Al', skip:'Geç', quit:'Çıkış', menu:'Menü',
    noLives:'Can Kalmadı', watchAd:'Reklam İzle Can Kazan',
    lives:'Can', coins:'Jeton', buy:'Satın Al', owned:'Sahipsin',
    next:'Sonraki Seviye', retry:'Tekrar Dene',
    ls_title:'%d. Gün Serisi!',
    ls_sub:'Daha büyük ödüller için her gün geri gel',
    ls_bonus:'Bugünkü Ödül',
    ls_claim:'Ödülü Al!',
    ls_ach3:'🌟 3 gün! +%d 🪙',
    ls_ach7:'🏆 Tam bir hafta! +%d 🪙',
    ls_ach14:'💎 İki hafta! +%d 🪙',
    ls_ach30:'👑 Efsane! +%d 🪙',
  },
  it: {
    play:'Gioca', levels:'Livelli', levelSelect:'Scegli Livello', shop:'Negozio',
    settings:'Impostazioni', dailyChallenge:'Sfida Quotidiana', back:'Indietro',
    sound:'Suono', music:'Musica', resetProgress:'Azzera Progressi',
    removeAds:'Rimuovi Pubblicità', language:'Lingua',
    levelComplete:'Livello Completato!', gameOver:'Fine del Gioco',
    hint:'Suggerimento', undo:'Annulla', skip:'Salta', quit:'Esci', menu:'Menu',
    noLives:'Nessuna Vita', watchAd:'Guarda un\'offerta per una vita',
    lives:'Vite', coins:'Monete', buy:'Acquista', owned:'Acquistato',
    next:'Prossimo Livello', retry:'Riprova',
    ls_title:'Giorno %d di fila!',
    ls_sub:'Torna ogni giorno per premi sempre più grandi',
    ls_bonus:'Premio di Oggi',
    ls_claim:'Ritira il Premio!',
    ls_ach3:'🌟 3 giorni! +%d 🪙',
    ls_ach7:'🏆 Una settimana intera! +%d 🪙',
    ls_ach14:'💎 Due settimane! +%d 🪙',
    ls_ach30:'👑 Leggenda! +%d 🪙',
  },
  nl: {
    play:'Spelen', levels:'Niveaus', levelSelect:'Niveau Kiezen', shop:'Winkel',
    settings:'Instellingen', dailyChallenge:'Dagelijkse Uitdaging', back:'Terug',
    sound:'Geluid', music:'Muziek', resetProgress:'Voortgang Wissen',
    removeAds:'Advertenties Verwijderen', language:'Taal',
    levelComplete:'Niveau Voltooid!', gameOver:'Game Over',
    hint:'Hint', undo:'Ongedaan Maken', skip:'Overslaan', quit:'Stoppen', menu:'Menu',
    ls_title:'Dag %d op rij!',
    ls_sub:'Kom elke dag terug voor grotere beloningen',
    ls_bonus:'Bonus van Vandaag', ls_claim:'Beloning Claimen!',
    ls_ach3:'🌟 3 dagen! +%d 🪙', ls_ach7:'🏆 Een week! +%d 🪙',
    ls_ach14:'💎 Twee weken! +%d 🪙', ls_ach30:'👑 Legende! +%d 🪙',
  },
  pl: {
    play:'Graj', levels:'Poziomy', levelSelect:'Wybierz Poziom', shop:'Sklep',
    settings:'Ustawienia', dailyChallenge:'Wyzwanie Dnia', back:'Wróć',
    sound:'Dźwięk', music:'Muzyka', resetProgress:'Resetuj Postęp',
    removeAds:'Usuń Reklamy', language:'Język',
    levelComplete:'Poziom Ukończony!', gameOver:'Koniec Gry',
    hint:'Wskazówka', undo:'Cofnij', skip:'Pomiń', quit:'Wyjście', menu:'Menu',
    ls_title:'Dzień %d z rzędu!',
    ls_sub:'Wracaj każdego dnia po większe nagrody',
    ls_bonus:'Dzisiejszy Bonus', ls_claim:'Odbierz Nagrodę!',
    ls_ach3:'🌟 3 dni! +%d 🪙', ls_ach7:'🏆 Pełny tydzień! +%d 🪙',
    ls_ach14:'💎 Dwa tygodnie! +%d 🪙', ls_ach30:'👑 Legenda! +%d 🪙',
  },
  sv: {
    play:'Spela', levels:'Nivåer', levelSelect:'Välj Nivå', shop:'Butik',
    settings:'Inställningar', dailyChallenge:'Daglig Utmaning', back:'Tillbaka',
    sound:'Ljud', music:'Musik', resetProgress:'Återställ Framsteg',
    removeAds:'Ta bort Annonser', language:'Språk',
    levelComplete:'Nivå Klar!', gameOver:'Game Over',
    hint:'Tips', undo:'Ångra', skip:'Hoppa Över', quit:'Avsluta', menu:'Meny',
    ls_title:'Dag %d i rad!',
    ls_sub:'Kom tillbaka varje dag för större belöningar',
    ls_bonus:'Dagens Bonus', ls_claim:'Hämta Belöning!',
    ls_ach3:'🌟 3 dagar! +%d 🪙', ls_ach7:'🏆 En hel vecka! +%d 🪙',
    ls_ach14:'💎 Två veckor! +%d 🪙', ls_ach30:'👑 Legende! +%d 🪙',
  },
  no: {
    play:'Spill', levels:'Nivåer', levelSelect:'Velg Nivå', shop:'Butikk',
    settings:'Innstillinger', dailyChallenge:'Daglig Utfordring', back:'Tilbake',
    sound:'Lyd', music:'Musikk', resetProgress:'Tilbakestill Fremgang',
    removeAds:'Fjern Annonser', language:'Språk',
    levelComplete:'Nivå Fullført!', gameOver:'Game Over',
    hint:'Hint', undo:'Angre', skip:'Hopp Over', quit:'Avslutt', menu:'Meny',
    ls_title:'Dag %d på rad!', ls_sub:'Kom tilbake hver dag for større premier',
    ls_bonus:'Dagens Bonus', ls_claim:'Krev Premien!',
    ls_ach3:'🌟 3 dager! +%d 🪙', ls_ach7:'🏆 En hel uke! +%d 🪙',
    ls_ach14:'💎 To uker! +%d 🪙', ls_ach30:'👑 Legende! +%d 🪙',
  },
  da: {
    play:'Spil', levels:'Niveauer', levelSelect:'Vælg Niveau', shop:'Butik',
    settings:'Indstillinger', dailyChallenge:'Daglig Udfordring', back:'Tilbage',
    sound:'Lyd', music:'Musik', resetProgress:'Nulstil Fremgang',
    removeAds:'Fjern Annoncer', language:'Sprog',
    levelComplete:'Niveau Fuldført!', gameOver:'Game Over',
    hint:'Tip', undo:'Fortryd', skip:'Spring Over', quit:'Afslut', menu:'Menu',
    ls_title:'Dag %d i træk!', ls_sub:'Vend tilbage hver dag for større præmier',
    ls_bonus:'Dagens Bonus', ls_claim:'Claim Præmie!',
    ls_ach3:'🌟 3 dage! +%d 🪙', ls_ach7:'🏆 En hel uge! +%d 🪙',
    ls_ach14:'💎 To uger! +%d 🪙', ls_ach30:'👑 Legende! +%d 🪙',
  },
  fi: {
    play:'Pelaa', levels:'Tasot', levelSelect:'Valitse Taso', shop:'Kauppa',
    settings:'Asetukset', dailyChallenge:'Päivän Haaste', back:'Takaisin',
    sound:'Ääni', music:'Musiikki', resetProgress:'Nollaa Edistyminen',
    removeAds:'Poista Mainokset', language:'Kieli',
    levelComplete:'Taso Läpäisty!', gameOver:'Peli Ohi',
    hint:'Vihje', undo:'Kumoa', skip:'Ohita', quit:'Lopeta', menu:'Valikko',
    ls_title:'Päivä %d putkessa!', ls_sub:'Tule takaisin joka päivä suurempien palkintojen vuoksi',
    ls_bonus:'Päivän Bonus', ls_claim:'Lunasta Palkinto!',
    ls_ach3:'🌟 3 päivää! +%d 🪙', ls_ach7:'🏆 Kokonainen viikko! +%d 🪙',
    ls_ach14:'💎 Kaksi viikkoa! +%d 🪙', ls_ach30:'👑 Legenda! +%d 🪙',
  },
  th: {
    play:'เล่น', levels:'ด่าน', levelSelect:'เลือกด่าน', shop:'ร้านค้า',
    settings:'ตั้งค่า', dailyChallenge:'ความท้าทายรายวัน', back:'กลับ',
    sound:'เสียง', music:'เพลง', resetProgress:'รีเซ็ตความคืบหน้า',
    removeAds:'ลบโฆษณา', language:'ภาษา',
    levelComplete:'ผ่านด่านแล้ว!', gameOver:'เกมโอเวอร์',
    hint:'คำใบ้', undo:'เลิกทำ', skip:'ข้าม', quit:'ออก', menu:'เมนู',
    ls_title:'วันที่ %d ติดต่อกัน!', ls_sub:'กลับมาทุกวันเพื่อรับรางวัลใหญ่ขึ้น',
    ls_bonus:'โบนัสวันนี้', ls_claim:'รับรางวัล!',
    ls_ach3:'🌟 3 วัน! +%d 🪙', ls_ach7:'🏆 หนึ่งสัปดาห์! +%d 🪙',
    ls_ach14:'💎 สองสัปดาห์! +%d 🪙', ls_ach30:'👑 ตำนาน! +%d 🪙',
  },
  vi: {
    play:'Chơi', levels:'Cấp độ', levelSelect:'Chọn Cấp Độ', shop:'Cửa hàng',
    settings:'Cài đặt', dailyChallenge:'Thử thách hàng ngày', back:'Quay lại',
    sound:'Âm thanh', music:'Nhạc', resetProgress:'Đặt lại tiến độ',
    removeAds:'Xóa quảng cáo', language:'Ngôn ngữ',
    levelComplete:'Hoàn thành cấp!', gameOver:'Trò chơi kết thúc',
    hint:'Gợi ý', undo:'Hoàn tác', skip:'Bỏ qua', quit:'Thoát', menu:'Thực đơn',
    ls_title:'Ngày %d liên tiếp!', ls_sub:'Quay lại mỗi ngày để nhận phần thưởng lớn hơn',
    ls_bonus:'Thưởng hôm nay', ls_claim:'Nhận Thưởng!',
    ls_ach3:'🌟 3 ngày! +%d 🪙', ls_ach7:'🏆 Một tuần đầy đủ! +%d 🪙',
    ls_ach14:'💎 Hai tuần! +%d 🪙', ls_ach30:'👑 Huyền thoại! +%d 🪙',
  },
  id: {
    play:'Mainkan', levels:'Level', levelSelect:'Pilih Level', shop:'Toko',
    settings:'Pengaturan', dailyChallenge:'Tantangan Harian', back:'Kembali',
    sound:'Suara', music:'Musik', resetProgress:'Reset Progres',
    removeAds:'Hapus Iklan', language:'Bahasa',
    levelComplete:'Level Selesai!', gameOver:'Game Over',
    hint:'Petunjuk', undo:'Batalkan', skip:'Lewati', quit:'Keluar', menu:'Menu',
    ls_title:'Hari %d berturut-turut!', ls_sub:'Kembali setiap hari untuk hadiah lebih besar',
    ls_bonus:'Bonus Hari Ini', ls_claim:'Klaim Hadiah!',
    ls_ach3:'🌟 3 hari! +%d 🪙', ls_ach7:'🏆 Satu minggu penuh! +%d 🪙',
    ls_ach14:'💎 Dua minggu! +%d 🪙', ls_ach30:'👑 Legenda! +%d 🪙',
  },
  hi: {
    play:'खेलें', levels:'स्तर', levelSelect:'स्तर चुनें', shop:'दुकान',
    settings:'सेटिंग्स', dailyChallenge:'दैनिक चुनौती', back:'वापस',
    sound:'ध्वनि', music:'संगीत', resetProgress:'प्रगति रीसेट करें',
    removeAds:'विज्ञापन हटाएं', language:'भाषा',
    levelComplete:'स्तर पूरा!', gameOver:'गेम ओवर',
    hint:'संकेत', undo:'पूर्ववत', skip:'छोड़ें', quit:'बाहर निकलें', menu:'मेनू',
    ls_title:'%d दिन की श्रृंखला!', ls_sub:'बड़े इनाम के लिए हर दिन वापस आएं',
    ls_bonus:'आज का बोनस', ls_claim:'इनाम लें!',
    ls_ach3:'🌟 3 दिन! +%d 🪙', ls_ach7:'🏆 पूरा एक सप्ताह! +%d 🪙',
    ls_ach14:'💎 दो सप्ताह! +%d 🪙', ls_ach30:'👑 लीजेंड! +%d 🪙',
  },
};

window.LANG_NAMES = {
  en:'English', de:'Deutsch', fr:'Français', es:'Español', pt:'Português',
  ru:'Русский', ja:'日本語', ko:'한국어', zh:'中文', ar:'العربية',
  tr:'Türkçe', it:'Italiano', nl:'Nederlands', pl:'Polski', sv:'Svenska',
  no:'Norsk', da:'Dansk', fi:'Suomi', th:'ภาษาไทย', vi:'Tiếng Việt',
  id:'Bahasa Indonesia', hi:'हिन्दी',
};

window.i18n = {
  _lang: localStorage.getItem('app_lang') || (() => {
    // Auto-detect from browser locale
    var nav = (navigator.language || navigator.userLanguage || 'en').split('-')[0].toLowerCase();
    return window.GAME_I18N[nav] ? nav : 'en';
  })(),

  t: function(key, n) {
    var t = (window.GAME_I18N[this._lang] || window.GAME_I18N['en']);
    var s = t[key] || window.GAME_I18N['en'][key] || key;
    return n !== undefined ? s.replace('%d', n) : s;
  },

  setLang: function(lang) {
    if (!window.GAME_I18N[lang]) return;
    this._lang = lang;
    localStorage.setItem('app_lang', lang);
    this.applyToPage();
    // Update RTL for Arabic
    document.documentElement.dir = (lang === 'ar') ? 'rtl' : 'ltr';
  },

  getLang: function() { return this._lang; },

  // Apply translations to key static elements by scanning text nodes
  applyToPage: function() {
    var lang = this._lang;
    if (lang === 'en') { document.documentElement.dir = 'ltr'; return; }
    var t = window.GAME_I18N[lang];
    var en = window.GAME_I18N['en'];
    // Build reverse map: English text → translated text
    var map = {};
    Object.keys(en).forEach(function(k) {
      if (t[k] && t[k] !== en[k] && !en[k].includes('%d')) map[en[k]] = t[k];
    });
    // Walk DOM and replace matching text nodes
    function walk(node) {
      if (!node) return;
      if (node.nodeType === 3) {
        var txt = node.textContent;
        var trimmed = txt.trim();
        if (map[trimmed]) node.textContent = txt.replace(trimmed, map[trimmed]);
      } else if (node.nodeType === 1) {
        var tag = node.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CANVAS') return;
        node.childNodes.forEach(walk);
      }
    }
    walk(document.body);
    // Update login streak overlay
    var sub = document.getElementById('ls-sub-text');
    if (sub) sub.textContent = t['ls_sub'] || en['ls_sub'];
    var lbl = document.getElementById('ls-bonus-label');
    if (lbl) lbl.textContent = t['ls_bonus'] || en['ls_bonus'];
    var btn = document.getElementById('ls-claim-btn-text');
    if (btn) btn.textContent = t['ls_claim'] || en['ls_claim'];
    // Update language selector if exists
    var sel = document.getElementById('i18n-lang-select');
    if (sel) sel.value = lang;
    // RTL
    document.documentElement.dir = (lang === 'ar') ? 'rtl' : 'ltr';
  },

  // Build and inject language selector row into settings screen
  injectLangSelector: function() {
    var self = this;
    // Build options HTML
    var opts = Object.keys(window.LANG_NAMES).map(function(code) {
      return '<option value="' + code + '">' + window.LANG_NAMES[code] + '</option>';
    }).join('');

    var row = document.createElement('div');
    row.id = 'i18n-lang-row';
    row.style.cssText = 'display:flex;align-items:center;justify-content:space-between;' +
      'background:rgba(255,255,255,0.05);border-radius:14px;padding:14px 16px;margin:8px 0;';
    row.innerHTML =
      '<span style="color:white;font-size:15px;font-weight:600">' + this.t('language') + ' 🌐</span>' +
      '<select id="i18n-lang-select" onchange="window.i18n.setLang(this.value)" ' +
      'style="background:#333;color:white;border:1px solid rgba(255,255,255,0.2);border-radius:8px;' +
      'padding:6px 10px;font-size:14px;outline:none;max-width:160px">' +
      opts + '</select>';

    // Try to find the settings container in each game's variant
    var containers = [
      document.querySelector('.settings-list'),
      document.querySelector('.settings-scroll'),
      document.querySelector('#screen-settings .settings-scroll'),
      document.querySelector('#settingsScreen .settings-list'),
      document.querySelector('#settingsScreen'),
      document.querySelector('#screen-settings'),
    ];
    var container = containers.find(function(c) { return c !== null; });
    if (container) {
      // Insert before the first child for visibility
      container.insertBefore(row, container.firstChild);
      document.getElementById('i18n-lang-select').value = self._lang;
    }
  },

  init: function() {
    var self = this;
    // Inject after the page's own init
    setTimeout(function() {
      self.injectLangSelector();
      if (self._lang !== 'en') self.applyToPage();
    }, 1000);
  }
};
"""

# ─────────────────────────────────────────────────────────────────────────────
# Updated login streak HTML that uses translated strings
# ─────────────────────────────────────────────────────────────────────────────
LS_TRANSLATED_UPDATE = """
<script>
// Update login streak overlay to use i18n
(function() {
  var origShow = window.lsShowOverlay_orig;
  // Patch the streak overlay to show translated text
  var origRun = window.__lsRun;

  // Override ls-sub and ls-bonus-label with i18n IDs for dynamic translation
  function patchLsHTML() {
    var sub = document.querySelector('#ls-card .ls-sub');
    if (sub) { sub.id = 'ls-sub-text'; }
    var lbl = document.querySelector('.ls-reward-lbl');
    if (lbl) { lbl.id = 'ls-bonus-label'; }
    var btn = document.querySelector('.ls-claim-btn');
    if (btn) { btn.id = 'ls-claim-btn-text'; }
    // Apply current lang to these elements
    if (window.i18n && window.i18n._lang !== 'en') {
      if (sub) sub.textContent = window.i18n.t('ls_sub');
      if (lbl) lbl.textContent = window.i18n.t('ls_bonus');
      if (btn) btn.textContent = window.i18n.t('ls_claim');
    }
  }
  setTimeout(patchLsHTML, 1200);
})();
</script>
"""

# ─────────────────────────────────────────────────────────────────────────────
# INJECTION
# ─────────────────────────────────────────────────────────────────────────────
INJECT_BLOCK = (
    "\n<script>\n/* ===== I18N TRANSLATIONS MODULE ===== */\n" +
    TRANSLATIONS_JS.strip() +
    "\n// Init on load\nwindow.addEventListener('load', function() { window.i18n.init(); });\n</script>\n" +
    LS_TRANSLATED_UPDATE.strip() + "\n"
)


def inject_game(game):
    html_path = os.path.join(BASE, game, "android", "app", "src", "main", "assets", "game.html")
    if not os.path.exists(html_path):
        print(f"  ✗ {game}: not found")
        return

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    if "GAME_I18N" in html:
        print(f"  ✓ {game}: already has i18n — skipped")
        return

    # Insert before </body>
    if "</body>" in html:
        html = html.replace("</body>", INJECT_BLOCK + "\n</body>", 1)
    else:
        html += "\n" + INJECT_BLOCK

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✓ {game}: i18n injected (22 languages)")


if __name__ == "__main__":
    print("Adding translations to all games...\n")
    for game in GAMES:
        inject_game(game)
    print("\n✅ Done — 22 languages added!")
    print("\nLanguages: EN, DE, FR, ES, PT, RU, JA, KO, ZH, AR, TR, IT, NL, PL, SV, NO, DA, FI, TH, VI, ID, HI")
    print("Language selector appears in Settings screen.")
    print("Language auto-detected from device locale on first launch.")
