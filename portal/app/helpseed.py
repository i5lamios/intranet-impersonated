"""Starter articles for the IT Help Center (edited afterwards in the intranet by AD group Intranet-IT-Editors)."""

ARTICLES = [
    {"slug": "mobile-mail", "category": "mail", "sort": 10,
     "title": {"en": "Set up work e-mail on your phone",
               "ru": "Настройка рабочей почты на телефоне",
               "az": "İş poçtunu telefonda quraşdırmaq"},
     "body": {
         "en": """<h3>Recommended: Microsoft Outlook app</h3><ol>
<li>Install <b>Microsoft Outlook</b> from the App Store or Google Play.</li>
<li>Open it, tap <b>Add account</b> and enter your work e-mail address (name.surname@example.com).</li>
<li>Enter your Windows (computer) password. The server is found automatically.</li>
<li>If the app asks for details: server <b>mail.example.com</b>, domain <b>COMPANY</b>, user name = your Windows login.</li></ol>
<h3>iPhone Mail / Android e-mail apps</h3><p>Add an <b>Exchange</b> account with the same details: e-mail, password,
server <b>mail.example.com</b>, domain <b>COMPANY</b>.</p>
<h3>After you change your password</h3><p>Update it on the phone straight away (Outlook asks for it). A phone that keeps
trying the old password can lock your account.</p>""",
         "ru": """<h3>Рекомендуем: приложение Microsoft Outlook</h3><ol>
<li>Установите <b>Microsoft Outlook</b> из App Store или Google Play.</li>
<li>Откройте его, нажмите <b>Добавить учётную запись</b> и введите рабочий адрес (имя.фамилия@example.com).</li>
<li>Введите пароль от Windows (компьютера). Сервер определится автоматически.</li>
<li>Если приложение спросит параметры: сервер <b>mail.example.com</b>, домен <b>COMPANY</b>, имя пользователя — ваш логин Windows.</li></ol>
<h3>Почта iPhone / почтовые приложения Android</h3><p>Добавьте учётную запись <b>Exchange</b> с теми же данными:
адрес, пароль, сервер <b>mail.example.com</b>, домен <b>COMPANY</b>.</p>
<h3>После смены пароля</h3><p>Сразу обновите пароль на телефоне (Outlook сам попросит). Телефон, который продолжает
вводить старый пароль, может заблокировать учётную запись.</p>""",
         "az": """<h3>Tövsiyə: Microsoft Outlook tətbiqi</h3><ol>
<li>App Store və ya Google Play-dən <b>Microsoft Outlook</b> tətbiqini quraşdırın.</li>
<li>Tətbiqi açın, <b>Hesab əlavə et</b> düyməsini basın və iş poçtunuzu yazın (ad.soyad@example.com).</li>
<li>Windows (kompüter) şifrənizi daxil edin. Server avtomatik tapılır.</li>
<li>Tətbiq məlumat istəsə: server <b>mail.example.com</b>, domen <b>COMPANY</b>, istifadəçi adı — Windows loginiz.</li></ol>
<h3>iPhone Mail / Android poçt tətbiqləri</h3><p>Eyni məlumatlarla <b>Exchange</b> hesabı əlavə edin: poçt ünvanı, şifrə,
server <b>mail.example.com</b>, domen <b>COMPANY</b>.</p>
<h3>Şifrəni dəyişdikdən sonra</h3><p>Telefonda da dərhal yeniləyin (Outlook özü soruşacaq). Köhnə şifrəni yoxlamağa
davam edən telefon hesabınızı bloklaya bilər.</p>"""}},
    {"slug": "change-password", "category": "accounts", "sort": 20,
     "title": {"en": "How to change your password", "ru": "Как сменить пароль", "az": "Şifrəni necə dəyişmək olar"},
     "body": {
         "en": """<h3>On an office computer</h3><p>Press <b>Ctrl + Alt + Del</b> → <b>Change a password</b>. Enter the old password
once and the new one twice.</p>
<h3>In Outlook on the web</h3><p>Open <a href="https://mail.example.com/owa">mail.example.com/owa</a> → Settings ⚙ →
Options → General → My account → <b>Change your password</b>.</p>
<h3>Away from the office, password expired</h3><p>A secure self-service page for changing an expired password from the
internet is being prepared. Until then, contact IT (see “How to get IT help”).</p>
<h3>Then</h3><p>Update the password on your phone (mail) and in the VPN client. Windows warns you a few days before
the password expires — change it in the office before it runs out.</p>""",
         "ru": """<h3>На рабочем компьютере</h3><p>Нажмите <b>Ctrl + Alt + Del</b> → <b>Изменить пароль</b>. Введите старый пароль
один раз и новый — дважды.</p>
<h3>В Outlook в браузере</h3><p>Откройте <a href="https://mail.example.com/owa">mail.example.com/owa</a> → Настройки ⚙ →
Параметры → Общие → Моя учётная запись → <b>Изменить пароль</b>.</p>
<h3>Вне офиса, пароль истёк</h3><p>Готовится защищённая страница самообслуживания для смены истёкшего пароля через
интернет. До её запуска обратитесь в ИТ (см. «Как получить помощь ИТ»).</p>
<h3>После смены</h3><p>Обновите пароль на телефоне (почта) и в VPN-клиенте. Windows предупреждает за несколько дней до
окончания срока — меняйте пароль в офисе заранее.</p>""",
         "az": """<h3>Ofis kompüterində</h3><p><b>Ctrl + Alt + Del</b> → <b>Şifrəni dəyiş</b>. Köhnə şifrəni bir dəfə, yenisini iki
dəfə daxil edin.</p>
<h3>Outlook veb versiyasında</h3><p><a href="https://mail.example.com/owa">mail.example.com/owa</a> → Parametrlər ⚙ →
Seçimlər → Ümumi → Hesabım → <b>Şifrəni dəyiş</b>.</p>
<h3>Ofisdən kənardasınız və şifrənin müddəti bitib</h3><p>Müddəti bitmiş şifrəni internetdən dəyişmək üçün təhlükəsiz
özünəxidmət səhifəsi hazırlanır. O vaxta qədər İT ilə əlaqə saxlayın (“İT-dən necə kömək almaq olar”).</p>
<h3>Sonra</h3><p>Şifrəni telefonda (poçt) və VPN proqramında yeniləyin. Windows şifrənin müddəti bitməzdən bir neçə gün
əvvəl xəbərdarlıq edir — ofisdə vaxtında dəyişin.</p>"""}},
    {"slug": "sign-in-passkey", "category": "accounts", "sort": 25,
     "title": {"en": "Sign in with a passkey (Face ID, fingerprint)", "ru": "Вход с passkey (Face ID, отпечаток)", "az": "Passkey ilə giriş (Face ID, barmaq izi)"},
     "body": {
         "en": """<p>A passkey lets you sign in with <b>Face ID, your fingerprint or the phone PIN</b> instead of typing a password. It is safer than a password: it only works on the real Company sign-in page and cannot be stolen by a fake site. Your face or fingerprint never leaves the phone.</p>
<h3>Set it up</h3><ol>
<li>Sign in to the intranet on your phone (office Wi-Fi or VPN). If the phone has no passkey yet, you see <b>Sign in with Face ID or fingerprint</b>.</li>
<li>Press <b>Set up passkey</b>, confirm with Face ID, fingerprint or PIN, and give it a name (for example "My iPhone").</li>
<li>You come back to the intranet. You also get an e-mail "New passkey added": if you did not add it, contact IT at once.</li></ol>
<p><b>Not now</b> hides the question for 3 days. You can add one any time in <b>My profile → Passkeys → Add a passkey</b>.</p>
<h3>Sign in</h3><p>On the sign-in page press <b>Sign in with Passkey</b> and confirm with Face ID, fingerprint or PIN.</p>
<ul><li><b>Office Wi-Fi and VPN:</b> the passkey replaces your password.</li>
<li><b>Outside the office</b> (Cloud): the passkey replaces both the password and the one-time code. Without a passkey you still enter password + code.</li>
<li><b>Office PCs</b> (and company laptops on VPN) sign you in automatically, nothing to type.</li></ul>
<h3>Change or delete</h3><p><b>My profile → Passkeys</b>: <b>Rename</b> or <b>Delete</b>. Lost your phone? Delete its passkey (or ask IT) — your password keeps working. A new phone: add a new passkey; passkeys saved in iCloud Keychain or Google Password Manager move to a new phone by themselves.</p>""",
         "ru": """<p>Passkey (ключ доступа) позволяет входить по <b>Face ID, отпечатку пальца или PIN-коду телефона</b> вместо пароля. Это надёжнее пароля: ключ работает только на настоящей странице входа Company, и поддельный сайт не может его украсть. Лицо и отпечаток не покидают телефон.</p>
<h3>Как настроить</h3><ol>
<li>Войдите в интранет с телефона (офисный Wi-Fi или VPN). Если на телефоне ещё нет passkey, появится окно <b>Вход по Face ID или отпечатку пальца</b>.</li>
<li>Нажмите <b>Настроить passkey</b>, подтвердите Face ID, отпечатком или PIN и дайте название (например, «Мой iPhone»).</li>
<li>Вы вернётесь в интранет. Также придёт письмо «New passkey added»: если это были не вы, сразу обратитесь в ИТ.</li></ol>
<p><b>Не сейчас</b> скрывает вопрос на 3 дня. Добавить ключ можно в любое время: <b>Мой профиль → Ключи доступа → Добавить passkey</b>.</p>
<h3>Вход</h3><p>На странице входа нажмите <b>Sign in with Passkey</b> и подтвердите Face ID, отпечатком или PIN.</p>
<ul><li><b>Офисный Wi-Fi и VPN:</b> passkey заменяет пароль.</li>
<li><b>Вне офиса</b> (Cloud): passkey заменяет и пароль, и одноразовый код. Без passkey по-прежнему пароль + код.</li>
<li><b>Офисные ПК</b> (и рабочие ноутбуки через VPN) входят автоматически.</li></ul>
<h3>Изменить или удалить</h3><p><b>Мой профиль → Ключи доступа</b>: <b>Переименовать</b> или <b>Удалить</b>. Потеряли телефон — удалите его ключ (или обратитесь в ИТ), пароль продолжит работать. Новый телефон — добавьте новый ключ; ключи в iCloud Keychain или Google Password Manager переходят на новый телефон сами.</p>""",
         "az": """<p>Passkey parol yazmaq əvəzinə <b>Face ID, barmaq izi və ya telefonun PIN kodu</b> ilə daxil olmağa imkan verir. Paroldan təhlükəsizdir: yalnız əsl Company giriş səhifəsində işləyir, saxta sayt onu oğurlaya bilməz. Üzünüz və barmaq iziniz telefondan çıxmır.</p>
<h3>Quraşdırmaq</h3><ol>
<li>Telefonda intranetə daxil olun (ofis Wi-Fi və ya VPN). Telefonda hələ passkey yoxdursa, <b>Face ID və ya barmaq izi ilə giriş</b> pəncərəsi görünəcək.</li>
<li><b>Passkey quraşdır</b> basın, Face ID, barmaq izi və ya PIN ilə təsdiqləyin və ad verin (məsələn, «Mənim iPhone»).</li>
<li>İntranetə qayıdacaqsınız. «New passkey added» məktubu da gələcək: bunu siz etməmisinizsə, dərhal İT-yə müraciət edin.</li></ol>
<p><b>İndi yox</b> sualı 3 günlük gizlədir. İstənilən vaxt əlavə edə bilərsiniz: <b>Profilim → Passkey-lər → Passkey əlavə et</b>.</p>
<h3>Giriş</h3><p>Giriş səhifəsində <b>Sign in with Passkey</b> basın və Face ID, barmaq izi və ya PIN ilə təsdiqləyin.</p>
<ul><li><b>Ofis Wi-Fi və VPN:</b> passkey parolu əvəz edir.</li>
<li><b>Ofisdən kənarda</b> (Cloud): passkey həm parolu, həm də birdəfəlik kodu əvəz edir. Passkey olmadan yenə parol + kod.</li>
<li><b>Ofis kompüterləri</b> (və VPN ilə şirkət noutbukları) avtomatik daxil olur.</li></ul>
<h3>Dəyişmək və ya silmək</h3><p><b>Profilim → Passkey-lər</b>: <b>Adını dəyiş</b> və ya <b>Sil</b>. Telefonu itirmisiniz — onun passkey-ni silin (və ya İT-yə müraciət edin), parolunuz işləməyə davam edir. Yeni telefon — yeni passkey əlavə edin; iCloud Keychain və ya Google Password Manager-dəki passkey-lər yeni telefona özü keçir.</p>"""}},
    {"slug": "password-policy", "category": "accounts", "sort": 30,
     "title": {"en": "Password rules and good practice", "ru": "Правила и советы по паролям",
               "az": "Şifrə qaydaları və tövsiyələr"},
     "body": {
         "en": """<h3>Rules</h3><ul><li>The password expires every <b>42 days</b>.</li>
<li>It must contain characters from at least three groups: capital letters, small letters, digits, symbols.</li>
<li>It must not contain your user name or parts of your full name.</li></ul>
<h3>Good practice</h3><ul><li>Use a <b>passphrase</b> of 12 or more characters, e.g. three unrelated words with a number:
<i>Lamp-Harbour-Pepper-27</i>.</li><li>Do not reuse your work password anywhere else.</li>
<li>Never tell your password to anyone — <b>IT will never ask for it</b>, by phone or e-mail.</li>
<li>Do not write it on paper near your computer.</li></ul>""",
         "ru": """<h3>Правила</h3><ul><li>Срок действия пароля — <b>42 дня</b>.</li>
<li>Пароль должен содержать символы минимум трёх групп: заглавные буквы, строчные буквы, цифры, знаки.</li>
<li>Пароль не должен содержать имя пользователя или части ФИО.</li></ul>
<h3>Советы</h3><ul><li>Используйте <b>парольную фразу</b> от 12 символов, например три несвязанных слова и число:
<i>Lamp-Harbour-Pepper-27</i>.</li><li>Не используйте рабочий пароль на других сайтах.</li>
<li>Никому не сообщайте пароль — <b>ИТ никогда его не спрашивает</b>, ни по телефону, ни по почте.</li>
<li>Не записывайте пароль на бумаге рядом с компьютером.</li></ul>""",
         "az": """<h3>Qaydalar</h3><ul><li>Şifrənin müddəti <b>42 gündür</b>.</li>
<li>Şifrədə ən azı üç qrupdan simvol olmalıdır: böyük hərflər, kiçik hərflər, rəqəmlər, işarələr.</li>
<li>Şifrədə istifadəçi adınız və ya ad-soyadınızın hissələri olmamalıdır.</li></ul>
<h3>Tövsiyələr</h3><ul><li>12 və daha çox simvoldan ibarət <b>şifrə ifadəsi</b> istifadə edin, məsələn, bir-biri ilə əlaqəsiz
üç söz və rəqəm: <i>Lamp-Harbour-Pepper-27</i>.</li><li>İş şifrənizi başqa saytlarda istifadə etməyin.</li>
<li>Şifrəni heç kimə deməyin — <b>İT onu heç vaxt soruşmur</b>, nə telefonla, nə poçtla.</li>
<li>Şifrəni kompüterin yanında kağıza yazmayın.</li></ul>"""}},
    {"slug": "phishing", "category": "security", "sort": 40,
     "title": {"en": "Suspicious e-mail? Report it", "ru": "Подозрительное письмо? Сообщите",
               "az": "Şübhəli məktub? Xəbər verin"},
     "body": {
         "en": """<p>Signs of phishing: urgency (“your mailbox will be closed”), a request for your password or a payment, a sender
address that does not match the name, links that point to a strange site, unexpected attachments.</p>
<h3>What to do</h3><ol><li>Do not click links or open attachments.</li><li>Forward the message to IT as an attachment, or
tell IT in Chat.</li><li>If you already entered your password — change it at once and tell IT.</li></ol>""",
         "ru": """<p>Признаки фишинга: срочность («ваш ящик будет закрыт»), просьба ввести пароль или оплатить, адрес отправителя
не совпадает с именем, ссылки на странные сайты, неожиданные вложения.</p>
<h3>Что делать</h3><ol><li>Не переходите по ссылкам и не открывайте вложения.</li><li>Перешлите письмо в ИТ вложением
или напишите ИТ в Chat.</li><li>Если вы уже ввели пароль — сразу смените его и сообщите ИТ.</li></ol>""",
         "az": """<p>Fişinq əlamətləri: təcililik (“poçt qutunuz bağlanacaq”), şifrə və ya ödəniş tələbi, ada uyğun gəlməyən
göndərən ünvanı, qəribə sayta aparan keçidlər, gözlənilməz qoşmalar.</p>
<h3>Nə etməli</h3><ol><li>Keçidlərə klikləməyin, qoşmaları açmayın.</li><li>Məktubu İT-yə qoşma kimi göndərin və ya Chat-da
İT-yə yazın.</li><li>Şifrəni artıq daxil etmisinizsə — dərhal dəyişin və İT-yə xəbər verin.</li></ol>"""}},
    {"slug": "it-help", "category": "support", "sort": 50,
     "title": {"en": "How to get IT help", "ru": "Как получить помощь ИТ", "az": "İT-dən necə kömək almaq olar"},
     "body": {
         "en": """<ul><li><b>IT Helpdesk</b>: <a href="https://helpdesk.example.com">helpdesk.example.com</a> — create a request,
follow its status.</li><li><b>Company Chat</b>: write to the IT team for quick questions.</li>
<li>Urgent (no e-mail, cannot log in): call IT — numbers in the <a href="/directory?q=IT">directory</a>.</li></ul>
<p>Please include: what you tried to do, the exact error message (a screenshot helps), your computer name.</p>""",
         "ru": """<ul><li><b>ИТ Helpdesk</b>: <a href="https://helpdesk.example.com">helpdesk.example.com</a> — создайте заявку и
следите за её статусом.</li><li><b>Company Chat</b>: напишите команде ИТ по быстрым вопросам.</li>
<li>Срочно (нет почты, не входит в систему): позвоните в ИТ — номера в <a href="/directory?q=IT">справочнике</a>.</li></ul>
<p>Укажите: что вы пытались сделать, точный текст ошибки (поможет скриншот), имя компьютера.</p>""",
         "az": """<ul><li><b>İT Helpdesk</b>: <a href="https://helpdesk.example.com">helpdesk.example.com</a> — müraciət yaradın,
statusunu izləyin.</li><li><b>Company Chat</b>: qısa suallar üçün İT komandasına yazın.</li>
<li>Təcili (poçt yoxdur, sistemə daxil ola bilmirsiniz): İT-yə zəng edin — nömrələr <a href="/directory?q=IT">ünvan
kitabında</a>.</li></ul><p>Zəhmət olmasa yazın: nə etmək istəyirdiniz, xətanın dəqiq mətni (ekran şəkli kömək edir),
kompüterin adı.</p>"""}},

    # ---- Intranet & apps (category "apps") ----
    {"slug": "report-problem", "category": "support", "sort": 45,
     "title": {"en": "Report a problem to IT", "ru": "Сообщить о проблеме в ИТ", "az": "Problemi İT-yə bildirmək"},
     "body": {
         "en": """<p>Something does not work — printer, Outlook, Wi-Fi, a program? Tell IT from the intranet in a minute.</p><ol>
<li>Open <b>Report a problem</b> (Home, or the Help Center).</li>
<li>Choose what it is about, write it in a few words and what happens. Say how urgent it is and where you are.</li>
<li>Add a screenshot if you can (on a PC: <b>Win + Shift + S</b>, then paste into Paint and save; on a phone: a photo of the screen).</li>
<li>Press <b>Send to IT</b>. Your name, phone, office and browser are added for you.</li></ol>
<p>The request goes to the IT Helpdesk; under <b>My requests</b> you see its number and status.
<b>You cannot work at all?</b> Send the form and also call IT.</p>""",
         "ru": """<p>Что-то не работает — принтер, Outlook, Wi-Fi, программа? Сообщите в ИТ из интранета за минуту.</p><ol>
<li>Откройте <b>Сообщить о проблеме</b> (на главной или в Справочном центре).</li>
<li>Выберите тему, коротко опишите, что происходит. Укажите срочность и где вы находитесь.</li>
<li>Добавьте снимок экрана, если можете (на ПК: <b>Win + Shift + S</b>, вставьте в Paint и сохраните; на телефоне — фото экрана).</li>
<li>Нажмите <b>Отправить в ИТ</b>. Ваше имя, телефон, офис и браузер добавятся сами.</li></ol>
<p>Заявка попадает в ИТ Helpdesk; в разделе <b>Мои заявки</b> видны её номер и статус.
<b>Совсем не можете работать?</b> Отправьте форму и позвоните в ИТ.</p>""",
         "az": """<p>Nəsə işləmir — printer, Outlook, Wi-Fi, proqram? İntranetdən bir dəqiqəyə İT-yə bildirin.</p><ol>
<li><b>Problem barədə bildir</b> açın (ana səhifədə və ya Yardım mərkəzində).</li>
<li>Mövzunu seçin, nə baş verdiyini qısaca yazın. Təcililiyi və harada olduğunuzu qeyd edin.</li>
<li>Mümkünsə ekran şəkli əlavə edin (kompüterdə: <b>Win + Shift + S</b>, Paint-ə yapışdırıb saxlayın; telefonda — ekranın şəkli).</li>
<li><b>İT-yə göndər</b> basın. Adınız, telefonunuz, ofisiniz və brauzeriniz avtomatik əlavə olunur.</li></ol>
<p>Sorğu İT Helpdesk-ə düşür; <b>Mənim sorğularım</b> bölməsində nömrəsi və statusu görünür.
<b>Heç işləyə bilmirsiniz?</b> Formanı göndərin və İT-yə zəng də edin.</p>"""}},

    {"slug": "intranet-start", "category": "apps", "sort": 5,
     "title": {"en": "Getting started with the intranet", "ru": "Как пользоваться интранетом", "az": "İntranetdən necə istifadə etmək"},
     "body": {
         "en": """<p>The intranet <b>intranet.example.com</b> works in the office and over VPN. You are signed in automatically
with your Windows account — no extra password.</p>
<h3>What is where</h3><ul>
<li><b>Home</b> — applications, news, birthdays, weather, HSE status.</li>
<li><b>Directory</b> — find colleagues, call, write, chat; each person's page shows their department colleagues.</li>
<li><b>Rooms</b> — book Meeting Room 4 and 5.</li>
<li><b>HSE</b> — report a hazard, see the HSE board. <b>Training</b> — your certificates.</li>
<li><b>Documents</b> — HR policies and forms. <b>Help</b> — these instructions.</li></ul>
<h3>Language</h3><p>Choose <b>EN / RU / AZ</b> at the top right. The intranet remembers your choice.</p>
<h3>Look for the <span class="hq">?</span></h3><p>The round <b>?</b> next to a page title opens the instruction for that page.</p>
<h3>Something looks old or broken?</h3><p>Press <b>Ctrl + F5</b> to reload the page. Still wrong — tell the IT Helpdesk.</p>""",
         "ru": """<p>Интранет <b>intranet.example.com</b> работает в офисе и через VPN. Вход выполняется автоматически под вашей
учётной записью Windows — отдельный пароль не нужен.</p>
<h3>Что где находится</h3><ul>
<li><b>Главная</b> — приложения, новости, дни рождения, погода, состояние HSE.</li>
<li><b>Справочник</b> — найти коллегу, позвонить, написать, открыть чат; на странице сотрудника — коллеги его отдела.</li>
<li><b>Переговорные</b> — бронирование Meeting Room 4 и 5.</li>
<li><b>HSE</b> — сообщить об опасности, доска HSE. <b>Обучение</b> — ваши сертификаты.</li>
<li><b>Документы</b> — политики и бланки HR. <b>Помощь</b> — эти инструкции.</li></ul>
<h3>Язык</h3><p>Выберите <b>EN / RU / AZ</b> справа вверху. Интранет запомнит выбор.</p>
<h3>Ищите значок <span class="hq">?</span></h3><p>Круглый <b>?</b> рядом с заголовком страницы открывает инструкцию к ней.</p>
<h3>Страница выглядит устаревшей или не работает?</h3><p>Нажмите <b>Ctrl + F5</b>. Не помогло — обратитесь в ИТ Helpdesk.</p>""",
         "az": """<p>İntranet <b>intranet.example.com</b> ofisdə və VPN vasitəsilə işləyir. Windows hesabınızla avtomatik daxil
olursunuz — ayrıca şifrə lazım deyil.</p>
<h3>Nə haradadır</h3><ul>
<li><b>Ana səhifə</b> — tətbiqlər, xəbərlər, ad günləri, hava, HSE vəziyyəti.</li>
<li><b>Kataloq</b> — həmkarı tapın, zəng edin, yazın, çata keçin; əməkdaşın səhifəsində şöbə həmkarları görünür.</li>
<li><b>Otaqlar</b> — Meeting Room 4 və 5 rezervasiyası.</li>
<li><b>HSE</b> — təhlükə barədə bildiriş, HSE lövhəsi. <b>Təlim</b> — sertifikatlarınız.</li>
<li><b>Sənədlər</b> — HR qaydaları və formaları. <b>Kömək</b> — bu təlimatlar.</li></ul>
<h3>Dil</h3><p>Yuxarı sağda <b>EN / RU / AZ</b> seçin. İntranet seçiminizi yadda saxlayır.</p>
<h3><span class="hq">?</span> işarəsinə baxın</h3><p>Səhifə başlığının yanındakı dairəvi <b>?</b> həmin səhifənin təlimatını açır.</p>
<h3>Səhifə köhnə görünür və ya işləmir?</h3><p><b>Ctrl + F5</b> basın. Kömək etməsə — İT Helpdesk-ə yazın.</p>"""}},

    {"slug": "book-meeting-room", "category": "apps", "sort": 10,
     "title": {"en": "Book a meeting room", "ru": "Как забронировать переговорную", "az": "İclas otağını necə sifariş etmək"},
     "body": {
         "en": """<h3>In the intranet</h3><ol>
<li>Open <b>Rooms</b>. You see Meeting Room 4 and Meeting Room 5 for the chosen day; grey blocks are taken. <b>Week</b> shows the whole week.</li>
<li>Click a free slot and pick a length, drag across the time you need, or press <b>+ Book a room</b>. Check the room, date and time, and write a subject.</li>
<li>Under <b>Invite colleagues</b> type a name and pick people from the list. Each person shows as Free, Tentative, Busy or Out of office for that time.</li>
<li>Press <b>Book</b>. You are the organizer: the meeting is in your Outlook calendar, invitations go out from you and the room confirms it.</li></ol>
<h3>Confirm the meeting with the QR code</h3><p>Each room has a QR code on the door. Scan it and press <b>Check in</b>, <b>from 10 minutes before the start until 10 minutes after it</b>.
If nobody confirms, the room can be released for others. You can also press <b>Check in</b> on the booking under <b>My bookings</b>. Meetings booked from Outlook are not released.</p>
<p>The QR page opens on office Wi-Fi or VPN, not on mobile data. It also shows whether the room is free, and you can book it on the spot.</p>
<h3>Repeating meetings</h3><p>When booking, choose <b>Repeat</b> (every week, every 2 weeks or every month) and how many times, up to 12. Dates when the room is busy are skipped, and you see which ones.
Each date is a separate meeting with its own invitation, so you can change one date without touching the others. To cancel, choose <b>Only this date</b> or <b>This and later dates</b>.</p>
<h3>Rules</h3><ul><li>07:00–21:00, up to <b>4 hours</b> per booking.</li><li>Up to <b>60 days</b> ahead, at most <b>10</b> upcoming bookings per person, or <b>30</b> with repeating meetings.</li>
<li>A room that is already taken cannot be booked twice.</li></ul>
<h3>Change or cancel</h3><p>Under <b>My bookings</b> press <b>Edit</b> (time, room, subject, people — everyone gets the update) or
<b>Cancel</b> (everyone gets the cancellation). You can also change the meeting in Outlook like any of your meetings.</p>
<h3>From Outlook</h3><p>New meeting → <b>Rooms</b> / <b>Scheduling Assistant</b> → add <b>Meeting Room 4</b> or <b>Meeting Room 5</b>
(meetingroom4@ / meetingroom5@example.com). Outlook bookings show in the intranet too.</p>""",
         "ru": """<h3>В интранете</h3><ol>
<li>Откройте <b>Переговорные</b>. На выбранный день видны Meeting Room 4 и Meeting Room 5; серые блоки — занято. <b>Неделя</b> показывает всю неделю.</li>
<li>Нажмите на свободное время и выберите длительность, протяните мышью по нужному времени или нажмите <b>+ Забронировать переговорную</b>. Проверьте комнату, дату и время, напишите тему.</li>
<li>В поле <b>Пригласить коллег</b> введите имя и выберите людей из списка. У каждого видно, свободен ли он в это время: свободен, под вопросом, занят или нет на месте.</li>
<li>Нажмите <b>Забронировать</b>. Вы — организатор: встреча в вашем календаре Outlook, приглашения уходят от вас, комната подтверждает бронь.</li></ol>
<h3>Подтвердите встречу по QR-коду</h3><p>На двери каждой комнаты есть QR-код. Отсканируйте его и нажмите <b>Отметиться</b> — <b>в промежутке от 10 минут до начала до 10 минут после него</b>.
Если никто не подтвердит, комнату могут освободить для других. Можно также нажать <b>Отметиться</b> у брони в разделе <b>Мои брони</b>. Встречи, забронированные из Outlook, не освобождаются.</p>
<p>Страница QR-кода открывается через офисный Wi-Fi или VPN, но не через мобильный интернет. На ней также видно, свободна ли комната, и можно сразу её забронировать.</p>
<h3>Повторяющиеся встречи</h3><p>При бронировании выберите <b>Повтор</b> (каждую неделю, каждые 2 недели или каждый месяц) и количество раз, до 12. Даты, когда комната занята, пропускаются, и вы увидите какие.
Каждая дата — отдельная встреча со своим приглашением, поэтому одну дату можно изменить, не трогая остальные. При отмене выберите <b>Только эту дату</b> или <b>Эту и следующие даты</b>.</p>
<h3>Правила</h3><ul><li>С 07:00 до 21:00, не более <b>4 часов</b> за раз.</li><li>Не более чем на <b>60 дней</b> вперёд, до <b>10</b> будущих броней на человека, с повторяющимися встречами — до <b>30</b>.</li>
<li>Занятую комнату забронировать нельзя.</li></ul>
<h3>Изменить или отменить</h3><p>В разделе <b>Мои брони</b> нажмите <b>Изменить</b> (время, комната, тема, участники — все получат
обновление) или <b>Отменить</b> (все получат отмену). Встречу можно менять и в Outlook, как любую свою встречу.</p>
<h3>Из Outlook</h3><p>Новая встреча → <b>Комнаты</b> / <b>Помощник по планированию</b> → добавьте <b>Meeting Room 4</b> или
<b>Meeting Room 5</b> (meetingroom4@ / meetingroom5@example.com). Брони из Outlook тоже видны в интранете.</p>""",
         "az": """<h3>İntranetdə</h3><ol>
<li><b>Otaqlar</b> bölməsini açın. Seçilmiş gün üçün Meeting Room 4 və Meeting Room 5 görünür; boz bloklar — məşğuldur. <b>Həftə</b> bütün həftəni göstərir.</li>
<li>Boş vaxta klikləyib müddəti seçin, lazım olan vaxtın üzərində siçanı sürüşdürün və ya <b>+ Otaq sifariş et</b> basın. Otağı, tarixi və vaxtı yoxlayın, mövzunu yazın.</li>
<li><b>Həmkarları dəvət et</b> sahəsində ad yazın və siyahıdan seçin. Hər kəsin həmin vaxt üçün vəziyyəti görünür: boşdur, dəqiq deyil, məşğuldur və ya ofisdə yoxdur.</li>
<li><b>Sifariş et</b> basın. Təşkilatçı sizsiniz: görüş Outlook təqviminizdədir, dəvətlər sizdən gedir, otaq təsdiqləyir.</li></ol>
<h3>Görüşü QR kodla təsdiqləyin</h3><p>Hər otağın qapısında QR kod var. Onu skan edib <b>Qeydiyyat</b> basın — <b>başlamağa 10 dəqiqə qalmışdan başlayandan 10 dəqiqə sonraya qədər</b>.
Heç kim təsdiqləməsə, otaq başqaları üçün azad edilə bilər. <b>Sifarişlərim</b> bölməsində sifarişin yanındakı <b>Qeydiyyat</b> düyməsini də basa bilərsiniz. Outlook-dan sifariş edilən görüşlər azad edilmir.</p>
<p>QR səhifəsi ofis Wi-Fi və ya VPN ilə açılır, mobil internetlə açılmır. Orada otağın boş olub-olmadığı da görünür və onu yerindəcə sifariş edə bilərsiniz.</p>
<h3>Təkrarlanan görüşlər</h3><p>Sifariş edəndə <b>Təkrar</b> (hər həftə, hər 2 həftədən bir və ya hər ay) və neçə dəfə olduğunu seçin, ən çox 12. Otağın məşğul olduğu tarixlər buraxılır və hansılar olduğunu görürsünüz.
Hər tarix öz dəvəti olan ayrıca görüşdür, ona görə bir tarixi digərlərinə toxunmadan dəyişə bilərsiniz. Ləğv edəndə <b>Yalnız bu tarix</b> və ya <b>Bu və sonrakı tarixlər</b> seçin.</p>
<h3>Qaydalar</h3><ul><li>07:00–21:00, bir sifariş ən çox <b>4 saat</b>.</li><li>Ən çox <b>60 gün</b> qabaqcadan, bir nəfərə ən çox <b>10</b> gələcək sifariş, təkrarlanan görüşlərlə birlikdə <b>30</b>.</li>
<li>Məşğul otağı ikinci dəfə sifariş etmək olmur.</li></ul>
<h3>Dəyişmək və ya ləğv etmək</h3><p><b>Sifarişlərim</b> bölməsində <b>Redaktə et</b> (vaxt, otaq, mövzu, iştirakçılar — hamı yeniləmə
alır) və ya <b>Ləğv et</b> (hamı ləğv barədə məlumat alır). Görüşü Outlook-da da öz görüşünüz kimi dəyişə bilərsiniz.</p>
<h3>Outlook-dan</h3><p>Yeni görüş → <b>Otaqlar</b> / <b>Planlaşdırma köməkçisi</b> → <b>Meeting Room 4</b> və ya <b>Meeting Room 5</b> əlavə edin
(meetingroom4@ / meetingroom5@example.com). Outlook sifarişləri intranetdə də görünür.</p>"""}},

    {"slug": "directory-calls", "category": "apps", "sort": 20,
     "title": {"en": "Find a colleague and call", "ru": "Найти коллегу и позвонить", "az": "Həmkarı tapmaq və zəng etmək"},
     "body": {
         "en": """<ol><li>Open <b>Directory</b> and type a name, job title, department, extension or phone number.</li>
<li>Filter by department or office; switch between <b>Cards</b> and <b>List</b> (the intranet remembers your choice).</li>
<li>Click a person for the full card: extension, mobile, e-mail, office and colleagues in the same department.</li></ol>
<h3>Buttons</h3><ul><li><b>Green phone</b> — call the extension. <b>Phone</b> icon — call the mobile.</li>
<li><b>Envelope</b> — new e-mail. <b>Speech bubble</b> — open a chat in Company Chat.</li></ul>
<h3>How the call is made</h3><ul><li><b>On a computer</b> every call opens the <b>3CX web client</b> (one tab, signed in with your 3CX
account) with the number already typed — press the green <b>call</b> button.</li><li><b>On a phone</b> extensions go to 3CX; mobile and outside numbers use the normal phone dialer.</li></ul>
<h3>Your own details are wrong?</h3><p>Fix your mobile, office and photo in <b>My profile</b>. Name, title, department, office
phone and extension are kept by HR and IT.</p>""",
         "ru": """<ol><li>Откройте <b>Справочник</b> и введите имя, должность, отдел, внутренний или телефонный номер.</li>
<li>Фильтруйте по отделу или офису; переключайте вид <b>Карточки</b> / <b>Список</b> (выбор запоминается).</li>
<li>Нажмите на сотрудника — откроется карточка: внутренний, мобильный, e-mail, офис и коллеги того же отдела.</li></ol>
<h3>Кнопки</h3><ul><li><b>Зелёная трубка</b> — звонок на внутренний. Значок <b>телефона</b> — звонок на мобильный.</li>
<li><b>Конверт</b> — новое письмо. <b>Облачко</b> — чат в Company Chat.</li></ul>
<h3>Как выполняется звонок</h3><ul><li><b>На компьютере</b> любой звонок открывает <b>веб-клиент 3CX</b> (одна вкладка, вход под
вашей учётной записью 3CX) с уже набранным номером — нажмите зелёную кнопку <b>вызова</b>.</li><li><b>На телефоне</b> внутренние номера идут через 3CX, мобильные и
внешние — через обычную звонилку.</li></ul>
<h3>Ваши данные неверны?</h3><p>Мобильный, офис и фото исправьте в <b>Моём профиле</b>. Имя, должность, отдел, рабочий
телефон и внутренний номер ведут HR и IT.</p>""",
         "az": """<ol><li><b>Kataloq</b> bölməsini açın və ad, vəzifə, şöbə, daxili və ya telefon nömrəsini yazın.</li>
<li>Şöbəyə və ya ofisə görə süzün; <b>Kartlar</b> / <b>Siyahı</b> görünüşünü seçin (seçim yadda qalır).</li>
<li>Əməkdaşa klikləyin — tam kart açılır: daxili nömrə, mobil, e-poçt, ofis və eyni şöbədən həmkarlar.</li></ol>
<h3>Düymələr</h3><ul><li><b>Yaşıl dəstək</b> — daxili nömrəyə zəng. <b>Telefon</b> işarəsi — mobilə zəng.</li>
<li><b>Zərf</b> — yeni məktub. <b>Bulud</b> — Company Chat-da yazışma.</li></ul>
<h3>Zəng necə edilir</h3><ul><li><b>Kompüterdə</b> hər zəng <b>3CX veb-klientini</b> nömrə artıq yığılmış halda açır (bir tab, 3CX
hesabınızla) — yaşıl <b>zəng</b> düyməsini basın.</li><li><b>Telefonda</b> daxili nömrələr 3CX ilə, mobil və xarici nömrələr adi zəng proqramı ilə yığılır.</li></ul>
<h3>Məlumatlarınız səhvdir?</h3><p>Mobil nömrəni, ofisi və şəkli <b>Profilim</b> bölməsində düzəldin. Ad, vəzifə, şöbə, iş telefonu və
daxili nömrəni HR və İT aparır.</p>"""}},

    {"slug": "my-profile", "category": "apps", "sort": 30,
     "title": {"en": "Update your mobile, office and photo", "ru": "Обновить мобильный, офис и фото", "az": "Mobil nömrəni, ofisi və şəkli yeniləmək"},
     "body": {
         "en": """<ol><li>Open <b>My profile</b> (your name at the top right, or the tile on Home).</li>
<li>Change your <b>Mobile</b> or <b>Office</b> and press <b>Save</b>.</li>
<li>For the photo press <b>Change photo</b> and choose a clear, recent face photo.</li></ol>
<p>Changes are saved to Active Directory: the directory, Outlook address book and phones update within minutes.</p>
<p><b>Name, title, department, office phone and extension</b> are kept by HR and IT — ask them to change these.</p>""",
         "ru": """<ol><li>Откройте <b>Мой профиль</b> (ваше имя справа вверху или плитка на главной).</li>
<li>Измените <b>Мобильный</b> или <b>Офис</b> и нажмите <b>Сохранить</b>.</li>
<li>Для фото нажмите <b>Сменить фото</b> и выберите чёткое свежее фото лица.</li></ol>
<p>Изменения сохраняются в Active Directory: справочник, адресная книга Outlook и телефоны обновятся за несколько минут.</p>
<p><b>Имя, должность, отдел, рабочий телефон и внутренний номер</b> ведут HR и IT — обратитесь к ним.</p>""",
         "az": """<ol><li><b>Profilim</b> bölməsini açın (yuxarı sağda adınız və ya ana səhifədəki kart).</li>
<li><b>Mobil</b> nömrənizi və ya <b>Ofis</b>i dəyişib <b>Yadda saxla</b> basın.</li>
<li>Şəkil üçün <b>Şəkli dəyiş</b> basın və aydın, təzə üz şəkli seçin.</li></ol>
<p>Dəyişikliklər Active Directory-də saxlanılır: kataloq, Outlook ünvan kitabçası və telefonlar bir neçə dəqiqəyə yenilənir.</p>
<p><b>Ad, vəzifə, şöbə, iş telefonu və daxili nömrəni</b> HR və İT aparır — dəyişmək üçün onlara müraciət edin.</p>"""}},

    {"slug": "notifications", "category": "apps", "sort": 40,
     "title": {"en": "Turn on intranet notifications", "ru": "Включить уведомления интранета", "az": "İntranet bildirişlərini açmaq"},
     "body": {
         "en": """<p>Notifications tell you about new news and emergency messages even when the intranet is closed.</p><ol>
<li>Press the <b>bell</b> at the top right (or <b>Notifications</b> in My profile).</li>
<li>Allow notifications when the browser asks.</li></ol>
<p><b>iPhone:</b> first open the intranet in Safari, tap <b>Share → Add to Home Screen</b>, open it from the home screen and
then press the bell.</p><p><b>Blocked?</b> Allow notifications for intranet.example.com in the browser settings (lock icon
left of the address).</p>""",
         "ru": """<p>Уведомления сообщают о новых новостях и экстренных сообщениях, даже когда интранет закрыт.</p><ol>
<li>Нажмите <b>колокольчик</b> справа вверху (или <b>Уведомления</b> в Моём профиле).</li>
<li>Разрешите уведомления, когда браузер спросит.</li></ol>
<p><b>iPhone:</b> сначала откройте интранет в Safari, нажмите <b>Поделиться → На экран «Домой»</b>, откройте его с экрана
«Домой» и затем нажмите колокольчик.</p><p><b>Заблокировано?</b> Разрешите уведомления для intranet.example.com в
настройках браузера (замок слева от адреса).</p>""",
         "az": """<p>Bildirişlər intranet bağlı olanda da yeni xəbərlər və təcili mesajlar barədə xəbər verir.</p><ol>
<li>Yuxarı sağda <b>zəng</b> işarəsini basın (və ya Profilimdə <b>Bildirişlər</b>).</li>
<li>Brauzer soruşanda bildirişlərə icazə verin.</li></ol>
<p><b>iPhone:</b> əvvəlcə intraneti Safari-də açın, <b>Paylaş → Əsas ekrana əlavə et</b> seçin, əsas ekrandan açın və sonra
zəng işarəsini basın.</p><p><b>Bloklanıb?</b> Brauzer ayarlarında intranet.example.com üçün bildirişlərə icazə verin
(ünvanın solundakı kilid).</p>"""}},

    {"slug": "cloud", "category": "apps", "sort": 50,
     "title": {"en": "Company Cloud: store and share files", "ru": "Company Cloud: хранение и обмен файлами", "az": "Company Cloud: faylları saxlamaq və paylaşmaq"},
     "body": {
         "en": """<p><b>cloud.example.com</b> is the company file storage (office and VPN). Sign in with your Windows account.</p>
<h3>In the browser</h3><ul><li><b>+ New</b> → upload files or create a folder / document. Drag and drop works too.</li>
<li>Files open in the browser; earlier versions are kept (… → <b>Versions</b>).</li>
<li>Deleted by mistake? <b>Deleted files</b> at the bottom left.</li></ul>
<h3>Share</h3><ol><li>Press the <b>share</b> icon next to a file or folder.</li>
<li>Type a colleague's name or a team group and choose <b>Can view</b> or <b>Can edit</b>.</li>
<li>A <b>share link</b> needs a password — send the password separately.</li></ol>
<h3>HR documents</h3><p>The shared folder <b>HR Sənədləri</b> holds HR forms and policies (edited by HR).</p>
<h3>On your computer and phone</h3><ul><li>Computer: install the <b>Nextcloud Desktop</b> app (ask IT), server
<b>https://cloud.example.com</b>, sign in in the browser window. Your files then appear as a folder.</li>
<li>Phone: <b>Nextcloud</b> app from the App Store / Google Play, same server address (works on VPN).</li></ul>
<p>Personal space: 5 GB. Do not store passwords or personal data of others in shared folders.</p>""",
         "ru": """<p><b>cloud.example.com</b> — файловое хранилище компании (офис и VPN). Вход под учётной записью Windows.</p>
<h3>В браузере</h3><ul><li><b>+ Новый</b> → загрузить файлы или создать папку / документ. Можно перетащить мышью.</li>
<li>Файлы открываются в браузере; старые версии сохраняются (… → <b>Версии</b>).</li>
<li>Удалили по ошибке? <b>Удалённые файлы</b> слева внизу.</li></ul>
<h3>Поделиться</h3><ol><li>Нажмите значок <b>общего доступа</b> рядом с файлом или папкой.</li>
<li>Введите имя коллеги или группу команды и выберите <b>Просмотр</b> или <b>Редактирование</b>.</li>
<li>Для <b>публичной ссылки</b> нужен пароль — отправьте пароль отдельно.</li></ol>
<h3>Документы HR</h3><p>Общая папка <b>HR Sənədləri</b> — бланки и политики HR (редактирует HR).</p>
<h3>На компьютере и телефоне</h3><ul><li>Компьютер: приложение <b>Nextcloud Desktop</b> (попросите ИТ), сервер
<b>https://cloud.example.com</b>, вход в окне браузера. Файлы появятся как обычная папка.</li>
<li>Телефон: приложение <b>Nextcloud</b> из App Store / Google Play, тот же адрес сервера (работает через VPN).</li></ul>
<p>Личное место: 5 ГБ. Не храните пароли и персональные данные других людей в общих папках.</p>""",
         "az": """<p><b>cloud.example.com</b> — şirkətin fayl anbarıdır (ofis və VPN). Windows hesabınızla daxil olun.</p>
<h3>Brauzerdə</h3><ul><li><b>+ Yeni</b> → fayl yükləyin və ya qovluq / sənəd yaradın. Siçanla sürükləmək də olar.</li>
<li>Fayllar brauzerdə açılır; köhnə versiyalar saxlanılır (… → <b>Versiyalar</b>).</li>
<li>Səhvən sildiniz? Aşağı solda <b>Silinmiş fayllar</b>.</li></ul>
<h3>Paylaşmaq</h3><ol><li>Fayl və ya qovluğun yanındakı <b>paylaş</b> işarəsini basın.</li>
<li>Həmkarın adını və ya komanda qrupunu yazın, <b>Baxış</b> və ya <b>Redaktə</b> seçin.</li>
<li><b>Paylaşım linki</b> üçün şifrə lazımdır — şifrəni ayrıca göndərin.</li></ol>
<h3>HR sənədləri</h3><p><b>HR Sənədləri</b> ümumi qovluğunda HR formaları və qaydaları var (HR redaktə edir).</p>
<h3>Kompüterdə və telefonda</h3><ul><li>Kompüter: <b>Nextcloud Desktop</b> proqramı (İT-dən istəyin), server
<b>https://cloud.example.com</b>, brauzer pəncərəsində daxil olun. Fayllar adi qovluq kimi görünəcək.</li>
<li>Telefon: App Store / Google Play-dən <b>Nextcloud</b> tətbiqi, eyni server ünvanı (VPN ilə işləyir).</li></ul>
<p>Şəxsi yer: 5 GB. Ümumi qovluqlarda şifrələr və başqalarının şəxsi məlumatlarını saxlamayın.</p>"""}},

    {"slug": "chat", "category": "apps", "sort": 60,
     "title": {"en": "Company Chat: messages and channels", "ru": "Company Chat: сообщения и каналы", "az": "Company Chat: mesajlar və kanallar"},
     "body": {
         "en": """<p><b>chat.example.com</b> is the company messenger (office and VPN). Every employee already has an account.</p>
<h3>Sign in</h3><p>Press <b>Company SSO</b> — you are signed in with your Windows account.</p>
<h3>Use</h3><ul><li><b>Direct message</b>: <b>+</b> next to Direct messages → choose a colleague. From the intranet
directory the <b>speech bubble</b> opens a chat directly.</li>
<li><b>Channels</b>: <b>+</b> → Browse channels to join a team channel, or create one for your project.</li>
<li>Write <b>@name</b> to notify a person, <b>@channel</b> only when everyone must read it.</li>
<li>Drag files into the message box to send them. Reply in a <b>thread</b> to keep conversations tidy.</li></ul>
<h3>On your phone</h3><p>Install <b>Mattermost</b> from the App Store / Google Play, server <b>https://chat.example.com</b>,
then <b>Company SSO</b> (works on VPN).</p>
<p>Chat is for work: do not send passwords — use the IT vault or tell them in person.</p>""",
         "ru": """<p><b>chat.example.com</b> — корпоративный мессенджер (офис и VPN). У каждого сотрудника уже есть учётная запись.</p>
<h3>Вход</h3><p>Нажмите <b>Company SSO</b> — вход выполнится под учётной записью Windows.</p>
<h3>Работа</h3><ul><li><b>Личное сообщение</b>: <b>+</b> рядом с «Личные сообщения» → выберите коллегу. В справочнике
интранета <b>облачко</b> сразу открывает чат.</li>
<li><b>Каналы</b>: <b>+</b> → Обзор каналов, чтобы вступить в канал команды, или создайте канал для проекта.</li>
<li>Пишите <b>@имя</b>, чтобы уведомить человека; <b>@channel</b> — только когда прочитать должны все.</li>
<li>Перетащите файл в поле сообщения, чтобы отправить. Отвечайте в <b>ветке</b>, чтобы не смешивать темы.</li></ul>
<h3>На телефоне</h3><p>Установите <b>Mattermost</b> из App Store / Google Play, сервер <b>https://chat.example.com</b>, затем
<b>Company SSO</b> (работает через VPN).</p>
<p>Чат — для работы: не пересылайте пароли.</p>""",
         "az": """<p><b>chat.example.com</b> — şirkətin messencеridir (ofis və VPN). Hər əməkdaşın artıq hesabı var.</p>
<h3>Giriş</h3><p><b>Company SSO</b> düyməsini basın — Windows hesabınızla daxil olursunuz.</p>
<h3>İstifadə</h3><ul><li><b>Şəxsi mesaj</b>: «Direct messages» yanında <b>+</b> → həmkarı seçin. İntranet kataloqunda
<b>bulud</b> işarəsi çatı birbaşa açır.</li>
<li><b>Kanallar</b>: <b>+</b> → Browse channels ilə komanda kanalına qoşulun və ya layihə üçün kanal yaradın.</li>
<li>Bir nəfərə xəbər vermək üçün <b>@ad</b> yazın; <b>@channel</b> — yalnız hamı oxumalı olanda.</li>
<li>Faylı göndərmək üçün mesaj sahəsinə sürükləyin. Mövzular qarışmasın deyə <b>thread</b>-də cavab verin.</li></ul>
<h3>Telefonda</h3><p>App Store / Google Play-dən <b>Mattermost</b> quraşdırın, server <b>https://chat.example.com</b>, sonra
<b>Company SSO</b> (VPN ilə işləyir).</p>
<p>Çat iş üçündür: şifrələri göndərməyin.</p>"""}},

    {"slug": "report-hazard", "category": "apps", "sort": 70,
     "title": {"en": "Report a hazard or near miss", "ru": "Сообщить об опасности или почти-происшествии", "az": "Təhlükə və ya az qala hadisə barədə bildirmək"},
     "body": {
         "en": """<p>Saw something unsafe, a near miss, or good practice? Tell HSE — it takes a minute.</p><ol>
<li>Open <b>HSE</b> → <b>Report a hazard</b> (also on Home).</li>
<li>Choose the type: <b>Near miss</b>, <b>Unsafe act</b>, <b>Unsafe condition</b> or <b>Good practice</b>.</li>
<li>Write when and where it happened, what you saw and any action already taken. Add a photo if you can.</li>
<li>Tick <b>Report anonymously</b> if you prefer — your name is then not stored.</li>
<li>Press <b>Send to HSE</b>. Under <b>My reports</b> on the HSE page you see the status, HSE's answer and how many
follow-up actions are done. You also get an e-mail when HSE changes the status.</li></ol>
<h3>An HSE action was given to you</h3><p>When HSE asks you to fix something, you get an e-mail and a notification, and the
action is shown on the Home page and under <b>My HSE actions</b> on the HSE page. When it is done, press <b>Mark done</b> and
write in a line what was done — HSE is told at once. Past the due date, a reminder comes once a week.</p>
<p><b>Emergency? Do not use the form</b> — stop the work and call your supervisor / emergency number first.</p>""",
         "ru": """<p>Заметили опасность, почти-происшествие или хорошую практику? Сообщите в HSE — это минута.</p><ol>
<li>Откройте <b>HSE</b> → <b>Сообщить об опасности</b> (есть и на главной).</li>
<li>Выберите тип: <b>Почти-происшествие</b>, <b>Опасное действие</b>, <b>Опасное условие</b> или <b>Хорошая практика</b>.</li>
<li>Укажите, когда и где, что вы увидели и какие меры уже приняты. Добавьте фото, если можете.</li>
<li>Отметьте <b>Анонимно</b>, если хотите — тогда ваше имя не сохраняется.</li>
<li>Нажмите <b>Отправить в HSE</b>. В разделе <b>Мои сообщения</b> на странице HSE видны статус, ответ HSE и сколько
корректирующих задач выполнено. Когда HSE меняет статус, вам приходит письмо.</li></ol>
<h3>Вам назначена задача HSE</h3><p>Когда HSE поручает вам что-то исправить, приходит письмо и уведомление, а задача видна на
главной и в разделе <b>Мои задачи HSE</b> на странице HSE. Когда сделаете — нажмите <b>Отметить выполненным</b> и коротко
напишите, что сделано: HSE узнает сразу. После срока напоминание приходит раз в неделю.</p>
<p><b>Экстренная ситуация? Не используйте форму</b> — остановите работу и сначала звоните руководителю / по номеру экстренной службы.</p>""",
         "az": """<p>Təhlükəli bir şey, az qala hadisə və ya yaxşı təcrübə gördünüz? HSE-yə bildirin — bir dəqiqə çəkir.</p><ol>
<li><b>HSE</b> → <b>Təhlükə barədə bildir</b> açın (ana səhifədə də var).</li>
<li>Növü seçin: <b>Az qala hadisə</b>, <b>Təhlükəli hərəkət</b>, <b>Təhlükəli şərait</b> və ya <b>Yaxşı təcrübə</b>.</li>
<li>Nə vaxt və harada olduğunu, nə gördüyünüzü və görülmüş tədbiri yazın. Mümkünsə şəkil əlavə edin.</li>
<li>İstəsəniz <b>Anonim bildir</b> seçin — onda adınız saxlanılmır.</li>
<li><b>HSE-yə göndər</b> basın. HSE səhifəsində <b>Bildirişlərim</b> bölməsində status, HSE-nin cavabı və neçə düzəldici
tapşırığın icra olunduğu görünür. HSE statusu dəyişəndə sizə məktub gəlir.</li></ol>
<h3>Sizə HSE tapşırığı verilib</h3><p>HSE sizdən nəyisə düzəltməyi xahiş edəndə məktub və bildiriş gəlir, tapşırıq ana səhifədə və
HSE səhifəsində <b>Mənim HSE tapşırıqlarım</b> bölməsində görünür. Edəndən sonra <b>İcra olundu kimi qeyd et</b> basın və nə
edildiyini bir cümlə ilə yazın — HSE dərhal xəbər tutur. Son tarix keçəndə həftədə bir xatırlatma gəlir.</p>
<p><b>Təcili hal? Formadan istifadə etməyin</b> — işi dayandırın və əvvəlcə rəhbərinizə / təcili xidmətə zəng edin.</p>"""}},

    {"slug": "my-certificates", "category": "apps", "sort": 80,
     "title": {"en": "Check your certificates and training", "ru": "Ваши сертификаты и обучение", "az": "Sertifikatlarınız və təlimlər"},
     "body": {
         "en": """<p><b>Training</b> shows the certificates HSE recorded for you, with expiry dates and status
(<b>Valid</b>, <b>Due ≤ 30 / 60 days</b>, <b>Expired</b>). You get reminders 60, 30 and 7 days before a certificate expires (e-mail, a phone / browser notification and a note on
the Home page); from 30 days your manager gets a copy.</p>
<p>Something missing or wrong? Send the certificate (scan or photo) to HSE — they update it.</p>""",
         "ru": """<p>В разделе <b>Обучение</b> — сертификаты, которые HSE внёс для вас, со сроками и статусом
(<b>Действует</b>, <b>Истекает ≤ 30 / 60 дней</b>, <b>Истёк</b>). Напоминания приходят за 60, 30 и 7 дней до окончания (письмо, уведомление на телефон / в браузер и отметка на главной);
с 30 дней копия идёт вашему руководителю.</p>
<p>Чего-то нет или ошибка? Отправьте сертификат (скан или фото) в HSE — они исправят.</p>""",
         "az": """<p><b>Təlim</b> bölməsində HSE-nin sizin üçün qeyd etdiyi sertifikatlar, bitmə tarixi və statusu ilə görünür
(<b>Etibarlı</b>, <b>≤ 30 / 60 gün qalıb</b>, <b>Müddəti bitib</b>). Müddət bitməzdən 60, 30 və 7 gün əvvəl xatırlatma gəlir (məktub, telefona / brauzerə bildiriş və ana səhifədə qeyd);
30 gündən rəhbərinizə də surət gedir.</p>
<p>Nəsə yoxdur və ya səhvdir? Sertifikatı (skan və ya şəkil) HSE-yə göndərin — onlar düzəldəcək.</p>"""}},
    # ---- IT how-tos (added 2026-11-01) ----
    {'slug': 'vpn', 'category': 'remote', 'sort': 10, 'title': {'en': 'Work from home or a site: VPN', 'ru': 'Работа из дома или с объекта: VPN', 'az': 'Evdən və ya obyektdən iş: VPN'}, 'body': {'en': '<p>The VPN connects your laptop to the office network, so the intranet, Cloud, Chat and network folders work outside the office.</p>\n<h3>Installation</h3><p>FortiClient VPN is installed and set up by IT — <a href="https://helpdesk.example.com">create a Helpdesk request</a>. Do not download it yourself.</p>\n<h3>Connect</h3><ol><li>Open <b>FortiClient</b> and choose the Company connection.</li>\n<li>Enter your Windows user name and password.</li><li>Enter the <b>6-digit code</b> from your authenticator app when asked.</li>\n<li>Wait for <b>Connected</b>. Disconnect when you finish.</li></ol>\n<h3>It does not connect</h3><ul><li>Check the internet works (open any website).</li><li>Code rejected: wait for a new code and type it quickly; check the phone clock is automatic.</li>\n<li>Password expired: see <a href="/help/password-outside">change an expired password outside the office</a> or call IT.</li>\n<li>Still not working: <a href="https://helpdesk.example.com">Helpdesk</a> — write the error message or attach a screenshot.</li></ul>', 'ru': '<p>VPN подключает ноутбук к офисной сети: интранет, Cloud, Chat и сетевые папки работают вне офиса.</p>\n<h3>Установка</h3><p>FortiClient VPN устанавливает и настраивает ИТ — <a href="https://helpdesk.example.com">создайте заявку в Helpdesk</a>. Не скачивайте его сами.</p>\n<h3>Подключение</h3><ol><li>Откройте <b>FortiClient</b> и выберите подключение Company.</li>\n<li>Введите логин и пароль Windows.</li><li>Когда спросит, введите <b>6-значный код</b> из приложения-аутентификатора.</li>\n<li>Дождитесь <b>Connected</b>. По окончании работы отключитесь.</li></ol>\n<h3>Не подключается</h3><ul><li>Проверьте, работает ли интернет (откройте любой сайт).</li><li>Код не принят: дождитесь нового кода и введите его сразу; время на телефоне должно быть автоматическим.</li>\n<li>Пароль истёк: см. <a href="/help/password-outside">смена истёкшего пароля вне офиса</a> или позвоните в ИТ.</li>\n<li>Не помогло: <a href="https://helpdesk.example.com">Helpdesk</a> — укажите текст ошибки или приложите снимок экрана.</li></ul>', 'az': '<p>VPN noutbuku ofis şəbəkəsinə qoşur: intranet, Cloud, Chat və şəbəkə qovluqları ofisdən kənarda işləyir.</p>\n<h3>Quraşdırma</h3><p>FortiClient VPN-i İT quraşdırır və tənzimləyir — <a href="https://helpdesk.example.com">Helpdesk-də sorğu yaradın</a>. Özünüz yükləməyin.</p>\n<h3>Qoşulma</h3><ol><li><b>FortiClient</b>-i açın və Company bağlantısını seçin.</li>\n<li>Windows istifadəçi adınızı və şifrənizi daxil edin.</li><li>Soruşanda autentifikator tətbiqindən <b>6 rəqəmli kodu</b> yazın.</li>\n<li><b>Connected</b> yazısını gözləyin. İşi bitirəndə ayrılın.</li></ol>\n<h3>Qoşulmur</h3><ul><li>İnternetin işlədiyini yoxlayın (istənilən saytı açın).</li><li>Kod qəbul olunmur: yeni kodu gözləyin və dərhal yazın; telefonda saat avtomatik olmalıdır.</li>\n<li>Şifrənin müddəti bitib: <a href="/help/password-outside">ofisdən kənarda şifrəni dəyişmək</a> və ya İT-yə zəng edin.</li>\n<li>Kömək etmədi: <a href="https://helpdesk.example.com">Helpdesk</a> — xəta mətnini yazın və ya ekran şəklini əlavə edin.</li></ul>'}},
    {'slug': 'new-phone-token', 'category': 'remote', 'sort': 20, 'title': {'en': 'New phone or lost authenticator app', 'ru': 'Новый телефон или потерян аутентификатор', 'az': 'Yeni telefon və ya autentifikator itib'}, 'body': {'en': '<p>The 6-digit VPN code comes from the authenticator app IT set up on your phone. The code is tied to that phone.</p>\n<h3>Before you change phones</h3><p><a href="https://helpdesk.example.com">Create a Helpdesk request</a> a few days ahead — IT moves the code to the new phone. Do not delete the app from the old phone until it works on the new one.</p>\n<h3>Phone lost, stolen or reset</h3><ol><li>Tell IT at once (Helpdesk or phone) — IT blocks the old code so nobody else can use it.</li>\n<li>IT gives you a new code (scan a QR code in the app).</li></ol>\n<p>Until then the VPN does not work for you. In the office you can keep working as usual.</p>', 'ru': '<p>6-значный код VPN приходит из приложения-аутентификатора, которое ИТ настроил на вашем телефоне. Код привязан к этому телефону.</p>\n<h3>Перед сменой телефона</h3><p><a href="https://helpdesk.example.com">Создайте заявку в Helpdesk</a> за несколько дней — ИТ перенесёт код на новый телефон. Не удаляйте приложение со старого телефона, пока всё не заработает на новом.</p>\n<h3>Телефон утерян, украден или сброшен</h3><ol><li>Сразу сообщите в ИТ (Helpdesk или по телефону) — ИТ заблокирует старый код.</li>\n<li>ИТ выдаст новый код (отсканируйте QR-код в приложении).</li></ol>\n<p>До этого VPN у вас работать не будет. В офисе можно работать как обычно.</p>', 'az': '<p>6 rəqəmli VPN kodu İT-nin telefonunuzda quraşdırdığı autentifikator tətbiqindən gəlir. Kod həmin telefona bağlıdır.</p>\n<h3>Telefonu dəyişməzdən əvvəl</h3><p>Bir neçə gün qabaq <a href="https://helpdesk.example.com">Helpdesk-də sorğu yaradın</a> — İT kodu yeni telefona köçürür. Yeni telefonda işləməyənə qədər köhnə telefondan tətbiqi silməyin.</p>\n<h3>Telefon itib, oğurlanıb və ya sıfırlanıb</h3><ol><li>Dərhal İT-yə xəbər verin (Helpdesk və ya telefon) — İT köhnə kodu bloklayır.</li>\n<li>İT yeni kod verir (tətbiqdə QR kodu skan edin).</li></ol>\n<p>O vaxta qədər VPN sizin üçün işləməyəcək. Ofisdə adi qaydada işləyə bilərsiniz.</p>'}},
    {'slug': 'password-outside', 'category': 'remote', 'sort': 30, 'title': {'en': 'Change an expired password outside the office', 'ru': 'Смена истёкшего пароля вне офиса', 'az': 'Ofisdən kənarda müddəti bitmiş şifrəni dəyişmək'}, 'body': {'en': '<p>If your Windows password has expired and you are outside the office (no VPN), use <b>password.example.com</b>.</p><ol>\n<li>Open <b>https://password.example.com</b> on your phone or computer.</li><li>Enter your user name and the <b>6-digit code</b> from your authenticator app (the VPN code).</li>\n<li>Enter your current (expired) password and a new one — at least 12 characters, three of: small letters, capitals, digits, symbols.</li>\n<li>Press <b>Change password</b>. You get a confirmation e-mail.</li></ol>\n<p>Then update the password on your phone (mail app) and in FortiClient. Works only from Azerbaijan and Georgia. If you did not change your password yourself, call IT immediately.</p>', 'ru': '<p>Если пароль Windows истёк, а вы вне офиса (без VPN), используйте <b>password.example.com</b>.</p><ol>\n<li>Откройте <b>https://password.example.com</b> на телефоне или компьютере.</li><li>Введите логин и <b>6-значный код</b> из приложения-аутентификатора (код VPN).</li>\n<li>Введите текущий (истёкший) пароль и новый — не менее 12 символов, три из: строчные, заглавные, цифры, знаки.</li>\n<li>Нажмите <b>Сменить пароль</b>. Придёт письмо-подтверждение.</li></ol>\n<p>Затем обновите пароль на телефоне (почта) и в FortiClient. Работает только из Азербайджана и Грузии. Если пароль меняли не вы — срочно звоните в ИТ.</p>', 'az': '<p>Windows şifrənizin müddəti bitibsə və ofisdən kənardasınızsa (VPN olmadan), <b>password.example.com</b> istifadə edin.</p><ol>\n<li>Telefonda və ya kompüterdə <b>https://password.example.com</b> açın.</li><li>İstifadəçi adınızı və autentifikator tətbiqindən <b>6 rəqəmli kodu</b> (VPN kodu) yazın.</li>\n<li>Cari (müddəti bitmiş) şifrəni və yenisini yazın — ən azı 12 simvol, üçü: kiçik, böyük hərflər, rəqəmlər, işarələr.</li>\n<li><b>Şifrəni dəyiş</b> basın. Təsdiq məktubu gələcək.</li></ol>\n<p>Sonra şifrəni telefonda (poçt) və FortiClient-də yeniləyin. Yalnız Azərbaycan və Gürcüstandan işləyir. Şifrəni siz dəyişməmisinizsə — dərhal İT-yə zəng edin.</p>'}, 'published': False},
    {'slug': '3cx-phone', 'category': 'mail', 'sort': 20, 'title': {'en': '3CX phone: apps, voicemail, transfer, forwarding', 'ru': 'Телефон 3CX: приложения, голосовая почта, перевод, переадресация', 'az': '3CX telefonu: tətbiqlər, səsli poçt, köçürmə, yönləndirmə'}, 'body': {'en': '<h3>Your 3CX account</h3><p>Accounts and extension numbers are given by IT — <a href="https://helpdesk.example.com">Helpdesk request</a>. You receive a welcome e-mail with the login.</p>\n<h3>Where to use it</h3><ul><li><b>Browser</b>: company.3cx.example:5001 (sign in with your extension and password).</li>\n<li><b>Phone</b>: <b>3CX</b> app from the App Store / Google Play — scan the QR code from the welcome e-mail.</li>\n<li><b>Computer</b>: the 3CX app for Windows, or the browser. Calls from the intranet directory open the 3CX dialer with the number — press the green button.</li></ul>\n<h3>Voicemail</h3><p>Dial <b>999</b> to listen to messages and record your greeting. New voicemails also arrive by e-mail.</p>\n<h3>Transfer a call</h3><p>During the call press <b>Transfer</b>, type the extension and confirm. <b>Attended</b> transfer lets you speak to the colleague first.</p>\n<h3>Away, offshore or on leave</h3><p>Change your <b>status</b> (Away / Out of office) in the app; calls then follow the forwarding set for that status (e.g. to your mobile or voicemail) — set it under Settings → Status.</p>', 'ru': '<h3>Учётная запись 3CX</h3><p>Учётные записи и внутренние номера выдаёт ИТ — <a href="https://helpdesk.example.com">заявка в Helpdesk</a>. Вы получите приветственное письмо с данными для входа.</p>\n<h3>Где пользоваться</h3><ul><li><b>Браузер</b>: company.3cx.example:5001 (вход по внутреннему номеру и паролю).</li>\n<li><b>Телефон</b>: приложение <b>3CX</b> из App Store / Google Play — отсканируйте QR-код из приветственного письма.</li>\n<li><b>Компьютер</b>: приложение 3CX для Windows или браузер. Звонок из справочника интранета открывает набор номера в 3CX — нажмите зелёную кнопку.</li></ul>\n<h3>Голосовая почта</h3><p>Наберите <b>999</b>, чтобы прослушать сообщения и записать приветствие. Новые сообщения приходят и на почту.</p>\n<h3>Перевод звонка</h3><p>Во время звонка нажмите <b>Transfer</b>, введите внутренний номер и подтвердите. <b>Attended</b> — сначала поговорить с коллегой.</p>\n<h3>Нет на месте, на объекте, в отпуске</h3><p>Смените <b>статус</b> (Away / Out of office) в приложении; звонки пойдут по переадресации этого статуса (например, на мобильный или в голосовую почту) — настройка в Settings → Status.</p>', 'az': '<h3>3CX hesabınız</h3><p>Hesabları və daxili nömrələri İT verir — <a href="https://helpdesk.example.com">Helpdesk sorğusu</a>. Giriş məlumatları ilə xoş gəldin məktubu alacaqsınız.</p>\n<h3>Harada istifadə etmək</h3><ul><li><b>Brauzer</b>: company.3cx.example:5001 (daxili nömrə və şifrə ilə giriş).</li>\n<li><b>Telefon</b>: App Store / Google Play-dən <b>3CX</b> tətbiqi — xoş gəldin məktubundakı QR kodu skan edin.</li>\n<li><b>Kompüter</b>: Windows üçün 3CX tətbiqi və ya brauzer. İntranet kataloqundan zəng 3CX-də nömrəni yığılmış açır — yaşıl düyməni basın.</li></ul>\n<h3>Səsli poçt</h3><p>Mesajları dinləmək və salamlamanı yazmaq üçün <b>999</b> yığın. Yeni mesajlar e-poçta da gəlir.</p>\n<h3>Zəngi köçürmək</h3><p>Zəng zamanı <b>Transfer</b> basın, daxili nömrəni yazın və təsdiqləyin. <b>Attended</b> — əvvəlcə həmkarla danışmaq.</p>\n<h3>Yerində deyil, obyektdə, məzuniyyətdə</h3><p>Tətbiqdə <b>statusu</b> dəyişin (Away / Out of office); zənglər həmin statusun yönləndirməsi ilə gedəcək (məs. mobilə və ya səsli poçta) — Settings → Status bölməsində.</p>'}},
    {'slug': 'outlook-basics', 'category': 'mail', 'sort': 30, 'title': {'en': 'Outlook basics: signature, out of office, shared mailbox, calendar', 'ru': 'Outlook: подпись, автоответ, общий ящик, календарь', 'az': 'Outlook: imza, avtomatik cavab, ümumi qutu, təqvim'}, 'body': {'en': '<h3>Signature</h3><p>Outlook: <b>File → Options → Mail → Signatures</b>. Web (mail.example.com): <b>Settings → Mail → Compose and reply</b>. Use the company template from HR.</p>\n<h3>Out of office</h3><p>Outlook: <b>File → Automatic Replies</b>. Web: <b>Settings → Mail → Automatic replies</b>. Set start and end dates and say who to contact.</p>\n<h3>Shared mailbox</h3><p>Access is given by IT (<a href="https://helpdesk.example.com">Helpdesk</a>, approved by the mailbox owner). It appears in Outlook by itself after a restart. To send from it, choose it in the <b>From</b> field.</p>\n<h3>Share your calendar</h3><p>Calendar → right-click your calendar → <b>Sharing permissions</b> → add a colleague → choose what they see.</p>\n<h3>Book a room</h3><p>See <a href="/help/book-meeting-room">Book a meeting room</a>.</p>\n<h3>"Mailbox almost full"</h3><p>Empty <b>Deleted Items</b>, delete big old attachments (sort by size), and save files to Cloud instead of e-mail. Still full — Helpdesk.</p>', 'ru': '<h3>Подпись</h3><p>Outlook: <b>Файл → Параметры → Почта → Подписи</b>. Веб (mail.example.com): <b>Параметры → Почта → Создание и ответ</b>. Используйте шаблон компании от HR.</p>\n<h3>Автоответ (нет на месте)</h3><p>Outlook: <b>Файл → Автоматические ответы</b>. Веб: <b>Параметры → Почта → Автоматические ответы</b>. Укажите даты и к кому обращаться.</p>\n<h3>Общий почтовый ящик</h3><p>Доступ выдаёт ИТ (<a href="https://helpdesk.example.com">Helpdesk</a>, с согласия владельца ящика). После перезапуска он появится в Outlook сам. Чтобы отправить от его имени, выберите его в поле <b>От</b>.</p>\n<h3>Общий доступ к календарю</h3><p>Календарь → правый клик по своему календарю → <b>Разрешения на общий доступ</b> → добавьте коллегу → выберите, что он видит.</p>\n<h3>Бронирование переговорной</h3><p>См. <a href="/help/book-meeting-room">Как забронировать переговорную</a>.</p>\n<h3>«Почтовый ящик почти заполнен»</h3><p>Очистите <b>Удалённые</b>, удалите старые большие вложения (сортировка по размеру), храните файлы в Cloud, а не в почте. Не помогло — Helpdesk.</p>', 'az': '<h3>İmza</h3><p>Outlook: <b>File → Options → Mail → Signatures</b>. Veb (mail.example.com): <b>Settings → Mail → Compose and reply</b>. HR-dan şirkət şablonundan istifadə edin.</p>\n<h3>Avtomatik cavab (yerində deyiləm)</h3><p>Outlook: <b>File → Automatic Replies</b>. Veb: <b>Settings → Mail → Automatic replies</b>. Tarixləri və kimə müraciət etməyi yazın.</p>\n<h3>Ümumi poçt qutusu</h3><p>Girişi İT verir (<a href="https://helpdesk.example.com">Helpdesk</a>, qutunun sahibinin razılığı ilə). Yenidən başladandan sonra Outlook-da özü görünəcək. Ondan göndərmək üçün <b>From</b> sahəsində seçin.</p>\n<h3>Təqvimi paylaşmaq</h3><p>Calendar → öz təqviminizə sağ klik → <b>Sharing permissions</b> → həmkarı əlavə edin → nə görəcəyini seçin.</p>\n<h3>Otaq rezervasiyası</h3><p>Bax: <a href="/help/book-meeting-room">İclas otağını necə rezerv etmək</a>.</p>\n<h3>«Poçt qutusu dolmaq üzrədir»</h3><p><b>Deleted Items</b>-i təmizləyin, böyük köhnə qoşmaları silin (ölçüyə görə sıralayın), faylları poçtda deyil, Cloud-da saxlayın. Kömək etmədi — Helpdesk.</p>'}},
    {'slug': 'printers', 'category': 'devices', 'sort': 10, 'title': {'en': 'Printers and scanning', 'ru': 'Принтеры и сканирование', 'az': 'Printerlər və skan'}, 'body': {'en': '<h3>Add a printer</h3><ol><li>Windows: <b>Settings → Bluetooth &amp; devices → Printers &amp; scanners → Add device</b>.</li>\n<li>Choose the printer of your floor / room (the name is on the label on the printer).</li><li>Not in the list? <a href="https://helpdesk.example.com">Helpdesk</a> — tell the printer name and your room.</li></ol>\n<h3>Scan</h3><p>On the printer choose <b>Scan → E-mail</b> (or Scan to folder, if set up for your department) and pick your address. Scans of documents with personal data: send them only to yourself and delete them from the printer list.</p>\n<h3>Problems</h3><p>Paper jam or toner — follow the printer screen; otherwise Helpdesk with the printer name and the error shown.</p>', 'ru': '<h3>Добавить принтер</h3><ol><li>Windows: <b>Параметры → Bluetooth и устройства → Принтеры и сканеры → Добавить устройство</b>.</li>\n<li>Выберите принтер своего этажа / кабинета (имя на наклейке на принтере).</li><li>Нет в списке? <a href="https://helpdesk.example.com">Helpdesk</a> — укажите имя принтера и кабинет.</li></ol>\n<h3>Сканирование</h3><p>На принтере выберите <b>Scan → E-mail</b> (или в папку, если это настроено для отдела) и свой адрес. Сканы с персональными данными отправляйте только себе.</p>\n<h3>Проблемы</h3><p>Замятие бумаги или тонер — следуйте подсказкам на экране принтера; иначе Helpdesk с именем принтера и текстом ошибки.</p>', 'az': '<h3>Printer əlavə etmək</h3><ol><li>Windows: <b>Settings → Bluetooth &amp; devices → Printers &amp; scanners → Add device</b>.</li>\n<li>Mərtəbənizin / otağınızın printerini seçin (adı printerin üzərindəki etiketdədir).</li><li>Siyahıda yoxdur? <a href="https://helpdesk.example.com">Helpdesk</a> — printerin adını və otağınızı yazın.</li></ol>\n<h3>Skan</h3><p>Printerdə <b>Scan → E-mail</b> (və ya şöbəniz üçün qurulubsa qovluğa) seçin və ünvanınızı seçin. Şəxsi məlumatlı sənədlərin skanını yalnız özünüzə göndərin.</p>\n<h3>Problemlər</h3><p>Kağız ilişib və ya toner — printer ekranındakı göstərişlərə əməl edin; əks halda printerin adı və xəta ilə Helpdesk.</p>'}},
    {'slug': 'where-to-save', 'category': 'devices', 'sort': 20, 'title': {'en': 'Where to save your files', 'ru': 'Где хранить файлы', 'az': 'Faylları harada saxlamaq'}, 'body': {'en': '<ul><li><b>Company Cloud</b> — your work files and team folders. Reachable from every device, versions kept, deleted files can be restored. <a href="/help/cloud">How to use Cloud</a>.</li>\n<li><b>Your PC (Desktop, Documents, Downloads)</b> — only for temporary files. If the laptop breaks or is lost, these files are gone.</li>\n<li><b>E-mail</b> — not a file store: send a Cloud share link instead of big attachments.</li>\n<li><b>USB sticks and private cloud services</b> (personal Google Drive, WhatsApp, etc.) — not for company documents.</li></ul>\n<p>Leaving the company or changing laptop? Move your files to Cloud first — IT can help (<a href="https://helpdesk.example.com">Helpdesk</a>).</p>', 'ru': '<ul><li><b>Company Cloud</b> — рабочие файлы и папки команд. Доступ с любого устройства, версии сохраняются, удалённое можно восстановить. <a href="/help/cloud">Как пользоваться Cloud</a>.</li>\n<li><b>Ваш компьютер (Рабочий стол, Документы, Загрузки)</b> — только для временных файлов. Если ноутбук сломается или потеряется, эти файлы пропадут.</li>\n<li><b>Почта</b> — не хранилище: вместо больших вложений отправьте ссылку из Cloud.</li>\n<li><b>Флешки и личные облака</b> (личный Google Drive, WhatsApp и т. п.) — не для документов компании.</li></ul>\n<p>Увольнение или замена ноутбука? Сначала перенесите файлы в Cloud — ИТ поможет (<a href="https://helpdesk.example.com">Helpdesk</a>).</p>', 'az': '<ul><li><b>Company Cloud</b> — iş faylları və komanda qovluqları. İstənilən cihazdan giriş, versiyalar saxlanılır, silinənləri bərpa etmək olar. <a href="/help/cloud">Cloud-dan necə istifadə etmək</a>.</li>\n<li><b>Kompüteriniz (Desktop, Documents, Downloads)</b> — yalnız müvəqqəti fayllar üçün. Noutbuk xarab olsa və ya itsə, bu fayllar itir.</li>\n<li><b>E-poçt</b> — fayl anbarı deyil: böyük qoşmalar əvəzinə Cloud linki göndərin.</li>\n<li><b>Fleşkalar və şəxsi bulud xidmətləri</b> (şəxsi Google Drive, WhatsApp və s.) — şirkət sənədləri üçün deyil.</li></ul>\n<p>İşdən çıxırsınız və ya noutbuku dəyişirsiniz? Əvvəlcə faylları Cloud-a köçürün — İT kömək edər (<a href="https://helpdesk.example.com">Helpdesk</a>).</p>'}},
    {'slug': 'requests', 'category': 'support', 'sort': 20, 'title': {'en': 'Request software, access, a new starter or a leaver', 'ru': 'Заявки: программы, доступы, новый сотрудник, увольнение', 'az': 'Sorğular: proqram, giriş, yeni işçi, işdən çıxma'}, 'body': {'en': '<p>All requests go to the <a href="https://helpdesk.example.com">IT Helpdesk</a> — that way nothing is forgotten and you see the status.</p><ul>\n<li><b>Software</b>: name and why you need it. Paid software needs your manager\'s approval.</li>\n<li><b>Access</b> to a shared folder, mailbox, group or system: what exactly, read or change, approved by the owner / your manager.</li>\n<li><b>New starter</b> (manager or HR): name, position, department, start date, equipment, phone, who they replace — <b>at least 3 working days</b> before the first day.</li>\n<li><b>Leaver</b> (manager or HR): last working day, who takes over mail and files. Accounts are closed on the last day.</li>\n<li><b>Equipment</b>: laptop, monitor, headset, phone — with your manager\'s approval.</li></ul>\n<p>Urgent problem that stops your work? Call IT as well.</p>', 'ru': '<p>Все заявки — в <a href="https://helpdesk.example.com">ИТ Helpdesk</a>: так ничего не теряется и виден статус.</p><ul>\n<li><b>Программы</b>: название и для чего. Платные — с согласия руководителя.</li>\n<li><b>Доступ</b> к общей папке, ящику, группе или системе: что именно, чтение или изменение, согласие владельца / руководителя.</li>\n<li><b>Новый сотрудник</b> (руководитель или HR): ФИО, должность, отдел, дата выхода, техника, телефон, кого заменяет — <b>минимум за 3 рабочих дня</b> до первого дня.</li>\n<li><b>Увольнение</b> (руководитель или HR): последний день, кому передать почту и файлы. Учётные записи закрываются в последний день.</li>\n<li><b>Техника</b>: ноутбук, монитор, гарнитура, телефон — с согласия руководителя.</li></ul>\n<p>Срочная проблема, работа стоит? Позвоните в ИТ тоже.</p>', 'az': '<p>Bütün sorğular <a href="https://helpdesk.example.com">İT Helpdesk</a>-ə — belə heç nə unudulmur və status görünür.</p><ul>\n<li><b>Proqram</b>: adı və nə üçün lazımdır. Ödənişli proqramlar rəhbərin razılığı ilə.</li>\n<li>Ümumi qovluğa, poçt qutusuna, qrupa və ya sistemə <b>giriş</b>: dəqiq nə, oxumaq və ya dəyişmək, sahibin / rəhbərin razılığı.</li>\n<li><b>Yeni işçi</b> (rəhbər və ya HR): ad, vəzifə, şöbə, başlama tarixi, avadanlıq, telefon, kimi əvəz edir — ilk gündən <b>ən azı 3 iş günü</b> əvvəl.</li>\n<li><b>İşdən çıxma</b> (rəhbər və ya HR): son iş günü, poçt və fayllar kimə verilir. Hesablar son gün bağlanır.</li>\n<li><b>Avadanlıq</b>: noutbuk, monitor, qulaqlıq, telefon — rəhbərin razılığı ilə.</li></ul>\n<p>İşinizi dayandıran təcili problem? İT-yə zəng də edin.</p>'}},
    {'slug': 'security-habits', 'category': 'security', 'sort': 20, 'title': {'en': 'Everyday security habits', 'ru': 'Безопасность каждый день', 'az': 'Gündəlik təhlükəsizlik vərdişləri'}, 'body': {'en': '<ul><li><b>Lock your screen</b> when you leave the desk: <b>Windows + L</b>.</li>\n<li><b>Never share your password</b> — not with colleagues, not with IT. IT will never ask for it.</li>\n<li><b>Do not send passwords</b> by e-mail, Chat or WhatsApp. Need to give someone access? <a href="https://helpdesk.example.com">Helpdesk</a>.</li>\n<li><b>Unknown USB sticks</b>: do not plug them in. Use Cloud to move files.</li>\n<li><b>Travel and offshore</b>: keep the laptop with you, use VPN on hotel / public Wi-Fi, do not leave it in the car.</li>\n<li><b>Lost laptop or phone</b>: tell IT the same day.</li>\n<li><b>Suspicious e-mail</b>: see <a href="/help/phishing">Suspicious e-mail? Report it</a>.</li>\n<li><b>Updates</b>: when Windows asks to restart for updates, do it the same day.</li></ul>', 'ru': '<ul><li><b>Блокируйте экран</b>, отходя от стола: <b>Windows + L</b>.</li>\n<li><b>Никому не говорите пароль</b> — ни коллегам, ни ИТ. ИТ никогда его не спрашивает.</li>\n<li><b>Не пересылайте пароли</b> почтой, в Chat или WhatsApp. Нужно дать доступ? <a href="https://helpdesk.example.com">Helpdesk</a>.</li>\n<li><b>Чужие флешки</b> не вставляйте. Для передачи файлов — Cloud.</li>\n<li><b>Командировки и объекты</b>: ноутбук держите при себе, в отеле / публичном Wi-Fi работайте через VPN, не оставляйте его в машине.</li>\n<li><b>Потеряли ноутбук или телефон</b>: сообщите в ИТ в тот же день.</li>\n<li><b>Подозрительное письмо</b>: см. <a href="/help/phishing">Подозрительное письмо? Сообщите</a>.</li>\n<li><b>Обновления</b>: если Windows просит перезагрузку, сделайте её в тот же день.</li></ul>', 'az': '<ul><li>Masadan uzaqlaşanda <b>ekranı kilidləyin</b>: <b>Windows + L</b>.</li>\n<li><b>Şifrənizi heç kimə deməyin</b> — nə həmkarlara, nə İT-yə. İT heç vaxt soruşmur.</li>\n<li><b>Şifrələri göndərməyin</b> — e-poçt, Chat və ya WhatsApp ilə. Kiməsə giriş vermək lazımdır? <a href="https://helpdesk.example.com">Helpdesk</a>.</li>\n<li><b>Naməlum fleşkaları</b> taxmayın. Faylları ötürmək üçün Cloud.</li>\n<li><b>Ezamiyyət və obyekt</b>: noutbuku yanınızda saxlayın, oteldə / ictimai Wi-Fi-da VPN ilə işləyin, maşında qoymayın.</li>\n<li><b>Noutbuk və ya telefon itib</b>: elə həmin gün İT-yə xəbər verin.</li>\n<li><b>Şübhəli məktub</b>: bax <a href="/help/phishing">Şübhəli məktub? Bildirin</a>.</li>\n<li><b>Yeniləmələr</b>: Windows yenidən başlatmağı istəyəndə həmin gün edin.</li></ul>'}},
    {'slug': 'guest-wifi', 'category': 'devices', 'sort': 30, 'title': {'en': 'Wi-Fi for guests', 'ru': 'Wi-Fi для гостей', 'az': 'Qonaqlar üçün Wi-Fi'}, 'body': {'en': '<ul><li>Guests and private phones use the <b>guest Wi-Fi</b>, not the office network.</li>\n<li>Access for a visitor or a meeting: ask IT (<a href="https://helpdesk.example.com">Helpdesk</a> or phone) with the date and the number of guests — IT gives a guest login.</li>\n<li><b>Never</b> give your own user name and password to a guest or let them connect with your account.</li>\n<li>Company laptops connect to the office Wi-Fi automatically — no action needed.</li></ul>', 'ru': '<ul><li>Гости и личные телефоны подключаются к <b>гостевому Wi-Fi</b>, а не к офисной сети.</li>\n<li>Доступ для посетителя или встречи: обратитесь в ИТ (<a href="https://helpdesk.example.com">Helpdesk</a> или телефон), укажите дату и число гостей — ИТ выдаст гостевой вход.</li>\n<li><b>Никогда</b> не давайте гостям свой логин и пароль и не подключайте их под своей учётной записью.</li>\n<li>Рабочие ноутбуки подключаются к офисному Wi-Fi автоматически.</li></ul>', 'az': '<ul><li>Qonaqlar və şəxsi telefonlar ofis şəbəkəsinə deyil, <b>qonaq Wi-Fi</b>-na qoşulur.</li>\n<li>Ziyarətçi və ya görüş üçün giriş: İT-yə müraciət edin (<a href="https://helpdesk.example.com">Helpdesk</a> və ya telefon), tarixi və qonaq sayını yazın — İT qonaq girişi verir.</li>\n<li>Öz istifadəçi adınızı və şifrənizi qonağa <b>heç vaxt</b> verməyin və onu öz hesabınızla qoşmayın.</li>\n<li>İş noutbukları ofis Wi-Fi-na avtomatik qoşulur.</li></ul>'}},
]

# ---- Admin guides: category "admin", shown only to people with an editor role (AD groups) ----
ARTICLES += [
    {"slug": "admin-news", "category": "admin", "sort": 10,
     "title": {"en": "News: how to write and format a post", "ru": "Новости: как написать и оформить публикацию",
               "az": "Xəbərlər: yazını necə yazmaq və tərtib etmək"},
     "body": {
         "en": """<h3>Languages</h3><ul>
<li>Tabs <b>EN · RU · AZ</b> above the title. <b>★</b> marks the main language; write <b>English first</b> (the site default).</li>
<li>Fill the other tabs with the translation. An empty tab shows the main version.</li></ul>
<h3>Text styles (the “Paragraph” list)</h3><ul>
<li><b>Heading</b> for sections (“New colleague”, “Role changes”, “The offer”).</li>
<li><b>Subheading</b> is used for person cards (see below) - don't use it for other text.</li>
<li>Lists for dates, conditions and steps; <b>bold</b> for the key fact (a deadline, a discount).</li>
<li>Pasting from Word works; then press <b>Clear formatting</b> (T̶x) on odd fonts and colours.</li></ul>
<h3>Introducing people: the Colleague button</h3><ol>
<li>Put the cursor where the person should go and press <b>👤 Colleague</b>.</li>
<li>Type 2+ letters of the name and click the person. A card with photo, job title and department is inserted.</li>
<li>Edit the line under the name if needed (“Reports to …”). On RU/AZ tabs translate it.</li></ol>
<p>Put new people under a heading <b>New colleague</b> and promotions under <b>Role changes</b> (in RU/AZ: “Новый сотрудник” / “Назначение”, “Yeni əməkdaş” / “Vəzifə dəyişikliyi”). The <b>People</b> panel on the News page reads these headings and shows each person for 60 days with the label <b>New</b> or <b>New role</b>.</p>
<h3>Pictures and files</h3><ul>
<li><b>Image</b> button or paste a picture into the text; it stays where you put it.</li>
<li><b>Cover picture</b> (right) is the small picture in the news list. Empty = the first picture in the text; with no picture the list shows the faces of the people in the post.</li>
<li><b>Attachments</b>: PDF, Word, Excel, PowerPoint, pictures - up to 15 MB each, 20 MB in total. They appear under the post and go with the e-mail.</li></ul>
<h3>Publishing</h3><ul>
<li><b>News date</b>: empty = today. Choose an earlier date for an announcement that was sent earlier. Future dates are not possible.</li>
<li><b>Summary</b>: 1-2 sentences for the list. Empty = the start of the text.</li>
<li><b>Pin to top</b> keeps the post first until you untick it.</li>
<li><b>E-mail to all staff</b> + Publish/Update sends the post (all languages, pictures inside, files attached) from hrnews@. Use <b>Send a test to me</b> first - it sends the saved version.</li>
<li><b>Unpublish</b> hides the post and keeps its date.</li></ul>""",
         "ru": """<h3>Языки</h3><ul>
<li>Вкладки <b>EN · RU · AZ</b> над заголовком. <b>★</b> - основной язык; пишите <b>сначала по-английски</b> (язык сайта по умолчанию).</li>
<li>В остальные вкладки вставьте перевод. Пустая вкладка показывает основную версию.</li></ul>
<h3>Стили текста (список «Абзац»)</h3><ul>
<li><b>Заголовок</b> - для разделов («Новый сотрудник», «Назначение», «Предложение»).</li>
<li><b>Подзаголовок</b> используется для карточек сотрудников (см. ниже) - не применяйте его для другого текста.</li>
<li>Списки - для дат, условий и шагов; <b>жирный</b> - для главного (срок, скидка).</li>
<li>Текст из Word вставляется; затем нажмите <b>Очистить формат</b> (T̶x) для лишних шрифтов и цветов.</li></ul>
<h3>Представление сотрудников: кнопка «Сотрудник»</h3><ol>
<li>Поставьте курсор и нажмите <b>👤 Сотрудник</b>.</li>
<li>Введите 2+ буквы имени и выберите человека. Вставится карточка с фото, должностью и отделом.</li>
<li>При необходимости дополните строку под именем («Подчиняется …»). Во вкладках RU/AZ переведите её.</li></ol>
<p>Новых сотрудников ставьте под заголовок <b>Новый сотрудник</b>, назначения - под <b>Назначение</b> (в EN/AZ: “New colleague” / “Role changes”, “Yeni əməkdaş” / “Vəzifə dəyişikliyi”). Панель <b>Люди</b> на странице новостей читает эти заголовки и 60 дней показывает человека с меткой <b>Новый</b> или <b>Новая должность</b>.</p>
<h3>Картинки и файлы</h3><ul>
<li>Кнопка <b>Изображение</b> или вставка картинки в текст - она остаётся на своём месте.</li>
<li><b>Обложка</b> (справа) - маленькая картинка в списке новостей. Пусто = первая картинка из текста; без картинок список покажет лица сотрудников из публикации.</li>
<li><b>Вложения</b>: PDF, Word, Excel, PowerPoint, картинки - до 15 МБ каждый, 20 МБ всего. Показываются под публикацией и уходят с письмом.</li></ul>
<h3>Публикация</h3><ul>
<li><b>Дата новости</b>: пусто = сегодня. Для объявления, разосланного раньше, выберите прошлую дату. Будущие даты нельзя.</li>
<li><b>Краткое описание</b>: 1-2 предложения для списка. Пусто = начало текста.</li>
<li><b>Закрепить</b> - публикация остаётся первой, пока не снимете галочку.</li>
<li><b>Отправить всем по почте</b> + Опубликовать/Обновить - письмо от hrnews@ (все языки, картинки внутри, файлы вложены). Сначала нажмите <b>Отправить тест мне</b> - уходит сохранённая версия.</li>
<li><b>Снять с публикации</b> скрывает публикацию и сохраняет её дату.</li></ul>""",
         "az": """<h3>Dillər</h3><ul>
<li>Başlığın üstündə <b>EN · RU · AZ</b> tabları. <b>★</b> əsas dildir; <b>əvvəlcə ingiliscə</b> yazın (saytın əsas dili).</li>
<li>Digər tablara tərcüməni yazın. Boş tab əsas versiyanı göstərir.</li></ul>
<h3>Mətn üslubları (“Mətn” siyahısı)</h3><ul>
<li><b>Başlıq</b> - bölmələr üçün (“Yeni əməkdaş”, “Vəzifə dəyişikliyi”, “Təklif”).</li>
<li><b>Alt başlıq</b> əməkdaş kartları üçündür (aşağıya baxın) - başqa mətn üçün istifadə etməyin.</li>
<li>Tarixlər, şərtlər və addımlar üçün siyahı; əsas fakt üçün <b>qalın</b> (son tarix, endirim).</li>
<li>Word-dən yapışdırmaq olar; sonra artıq şrift və rənglər üçün <b>Formatı təmizlə</b> (T̶x) düyməsini basın.</li></ul>
<h3>Əməkdaşları təqdim etmək: “Əməkdaş” düyməsi</h3><ol>
<li>Kursoru qoyun və <b>👤 Əməkdaş</b> düyməsini basın.</li>
<li>Adın 2+ hərfini yazın və şəxsi seçin. Foto, vəzifə və şöbə ilə kart əlavə olunur.</li>
<li>Lazım olsa addan aşağıdakı sətri tamamlayın (“Rəhbəri: …”). RU/AZ tablarında onu tərcümə edin.</li></ol>
<p>Yeni əməkdaşları <b>Yeni əməkdaş</b>, təyinatları <b>Vəzifə dəyişikliyi</b> başlığı altına qoyun (EN/RU: “New colleague” / “Role changes”, “Новый сотрудник” / “Назначение”). Xəbərlər səhifəsindəki <b>İnsanlar</b> paneli bu başlıqları oxuyur və şəxsi 60 gün <b>Yeni</b> və ya <b>Yeni vəzifə</b> nişanı ilə göstərir.</p>
<h3>Şəkillər və fayllar</h3><ul>
<li><b>Şəkil</b> düyməsi və ya şəkli mətnə yapışdırın - qoyduğunuz yerdə qalır.</li>
<li><b>Üz şəkli</b> (sağda) xəbər siyahısındakı kiçik şəkildir. Boş = mətndəki ilk şəkil; şəkil yoxdursa, siyahı yazıdakı əməkdaşların üzlərini göstərir.</li>
<li><b>Əlavələr</b>: PDF, Word, Excel, PowerPoint, şəkillər - hər biri 15 MB-a qədər, cəmi 20 MB. Yazının altında görünür və məktubla gedir.</li></ul>
<h3>Dərc etmək</h3><ul>
<li><b>Xəbərin tarixi</b>: boş = bu gün. Əvvəl göndərilmiş elan üçün keçmiş tarixi seçin. Gələcək tarix olmaz.</li>
<li><b>Qısa məzmun</b>: siyahı üçün 1-2 cümlə. Boş = mətnin əvvəli.</li>
<li><b>Yuxarıda sabitlə</b> - işarəni götürənə qədər yazı birinci qalır.</li>
<li><b>Bütün əməkdaşlara e-poçtla göndər</b> + Dərc et/Yenilə - hrnews@ ünvanından məktub (bütün dillər, şəkillər içində, fayllar əlavədə). Əvvəlcə <b>Mənə test göndər</b> - saxlanmış versiya gedir.</li>
<li><b>Dərcdən çıxar</b> yazını gizlədir və tarixini saxlayır.</li></ul>"""}},

    {"slug": "admin-hr", "category": "admin", "sort": 20,
     "title": {"en": "Birthdays, emergency banner, weekly e-mail", "ru": "Дни рождения, экстренный баннер, еженедельное письмо",
               "az": "Ad günləri, təcili banner, həftəlik məktub"},
     "body": {
         "en": """<h3>Birthdays</h3><ul>
<li>The year is optional and visible only to HR here; staff and the Home page see day and month only.</li>
<li><b>Paste from Excel</b>: two columns - user name, e-mail or full name, and the date (15.03 or 15.03.1990).</li>
<li>Or set day and month in the list - it saves at once. <b>Only missing</b> shows who has no date; set both to “—” to remove a birthday (for people who don't want it shown).</li></ul>
<h3>Emergency banner</h3><ul>
<li>A coloured bar on top of every intranet page, plus a push notification to phones and browsers that allowed it.</li>
<li>Type: <b>Info</b> (blue), <b>Warning</b> (amber), <b>Emergency</b> (red). Keep the text to one sentence with the action (“Office closed today - work from home”).</li>
<li><b>Until</b>: the banner switches off by itself; empty = until you untick <b>Show the banner</b>.</li></ul>
<h3>Weekly e-mail</h3><ul>
<li>A digest of the news published since the last one, to all staff. Nothing is sent in a week without news.</li>
<li>It is currently <b>off</b>; use <b>E-mail to all staff</b> on a single post instead. <b>Preview</b> and <b>Send a test to me</b> show it without sending to everyone.</li></ul>""",
         "ru": """<h3>Дни рождения</h3><ul>
<li>Год необязателен и виден только HR здесь; сотрудники и главная страница видят только день и месяц.</li>
<li><b>Вставить из Excel</b>: два столбца - логин, e-mail или полное имя, и дата (15.03 или 15.03.1990).</li>
<li>Или выберите день и месяц в списке - сохраняется сразу. <b>Только незаполненные</b> показывает, у кого даты нет; поставьте «—» в обоих полях, чтобы убрать день рождения (если человек не хочет его показывать).</li></ul>
<h3>Экстренный баннер</h3><ul>
<li>Цветная полоса вверху каждой страницы интранета и push-уведомление на телефоны и браузеры, где оно разрешено.</li>
<li>Тип: <b>Инфо</b> (синий), <b>Внимание</b> (жёлтый), <b>Экстренно</b> (красный). Одно предложение с действием («Офис сегодня закрыт - работаем из дома»).</li>
<li><b>До</b>: баннер выключится сам; пусто = пока не снимете галочку <b>Показывать баннер</b>.</li></ul>
<h3>Еженедельное письмо</h3><ul>
<li>Подборка новостей с прошлого письма для всех сотрудников. Если новостей нет, письмо не уходит.</li>
<li>Сейчас <b>выключено</b>; вместо него используйте <b>Отправить всем по почте</b> у отдельной новости. <b>Просмотр</b> и <b>Отправить тест мне</b> показывают письмо без рассылки.</li></ul>""",
         "az": """<h3>Ad günləri</h3><ul>
<li>İl könüllüdür və yalnız burada HR-a görünür; əməkdaşlar və ana səhifə yalnız gün və ayı görür.</li>
<li><b>Excel-dən yapışdır</b>: iki sütun - istifadəçi adı, e-poçt və ya tam ad, və tarix (15.03 və ya 15.03.1990).</li>
<li>Və ya siyahıda gün və ayı seçin - dərhal saxlanılır. <b>Yalnız boş olanlar</b> tarixi olmayanları göstərir; ad gününü silmək üçün hər iki sahədə “—” seçin (göstərilməsini istəməyənlər üçün).</li></ul>
<h3>Təcili banner</h3><ul>
<li>İntranetin hər səhifəsinin yuxarısında rəngli zolaq və icazə verilmiş telefon və brauzerlərə push bildiriş.</li>
<li>Növ: <b>Məlumat</b> (göy), <b>Xəbərdarlıq</b> (sarı), <b>Təcili</b> (qırmızı). Hərəkəti göstərən bir cümlə yazın (“Ofis bu gün bağlıdır - evdən işləyirik”).</li>
<li><b>Bitmə vaxtı</b>: banner özü sönür; boş = <b>Banneri göstər</b> işarəsini götürənə qədər.</li></ul>
<h3>Həftəlik məktub</h3><ul>
<li>Son məktubdan bəri dərc olunan xəbərlərin icmalı, bütün əməkdaşlara. Xəbər olmayan həftə göndərilmir.</li>
<li>Hazırda <b>söndürülüb</b>; əvəzinə ayrıca xəbərdə <b>Bütün əməkdaşlara e-poçtla göndər</b> seçin. <b>Önbaxış</b> və <b>Mənə test göndər</b> hamıya göndərmədən göstərir.</li></ul>"""}},

    {"slug": "admin-hse", "category": "admin", "sort": 30,
     "title": {"en": "HSE: hazard reports and the board", "ru": "ОТиПБ: сообщения об опасностях и табло", "az": "SƏTƏM: təhlükə bildirişləri və lövhə"},
     "body": {
         "en": """<h3>Hazard reports</h3><ul>
<li>Staff report a <b>near miss</b>, <b>unsafe act</b>, <b>unsafe condition</b> or <b>good practice</b>, with an optional photo. Anonymous reports carry no name.</li>
<li>Work through them with the filter: <b>New → In review → Closed</b>. Set the status and press <b>Save</b>.</li>
<li><b>Comment for the reporter</b> is shown to the person who reported it (under “My reports”) - say what was done.</li></ul>
<h3>HSE board (Home page strip and the HSE page)</h3><ul>
<li><b>Date of the last lost-time incident</b>: the “days without LTI” counter is calculated from it every day.</li>
<li><b>Best record, days</b> and <b>Man-hours this year</b>: update monthly.</li>
<li><b>Target / message of the month</b>: one line.</li>
<li><b>Safety moment</b>: a title and a short text with a picture - change it weekly or monthly.</li></ul>""",
         "ru": """<h3>Сообщения об опасностях</h3><ul>
<li>Сотрудники сообщают о <b>потенциально опасном происшествии</b>, <b>опасном действии</b>, <b>опасном условии</b> или <b>хорошей практике</b>, можно с фото. Анонимные сообщения без имени.</li>
<li>Работайте по фильтру: <b>Новое → На рассмотрении → Закрыто</b>. Выберите статус и нажмите <b>Сохранить</b>.</li>
<li><b>Комментарий для автора</b> видит автор сообщения («Мои сообщения») - напишите, что сделано.</li></ul>
<h3>Табло ОТиПБ (полоса на главной и страница HSE)</h3><ul>
<li><b>Дата последнего происшествия с потерей рабочего времени</b>: счётчик «дней без LTI» считается от неё каждый день.</li>
<li><b>Лучший рекорд, дней</b> и <b>Человеко-часы за год</b>: обновляйте ежемесячно.</li>
<li><b>Цель / сообщение месяца</b>: одна строка.</li>
<li><b>Момент безопасности</b>: заголовок и короткий текст с картинкой - меняйте раз в неделю или месяц.</li></ul>""",
         "az": """<h3>Təhlükə bildirişləri</h3><ul>
<li>Əməkdaşlar <b>təhlükəli hadisə (az qala)</b>, <b>təhlükəli hərəkət</b>, <b>təhlükəli şərait</b> və ya <b>yaxşı təcrübə</b> barədə bildirir, istəsə foto ilə. Anonim bildirişlərdə ad olmur.</li>
<li>Filtrlə işləyin: <b>Yeni → Baxılır → Bağlanıb</b>. Statusu seçin və <b>Saxla</b> basın.</li>
<li><b>Bildirən üçün şərh</b> bildirən şəxsə görünür (“Mənim bildirişlərim”) - nə edildiyini yazın.</li></ul>
<h3>SƏTƏM lövhəsi (ana səhifədəki zolaq və HSE səhifəsi)</h3><ul>
<li><b>Son iş vaxtı itkisi ilə hadisənin tarixi</b>: “LTI-siz günlər” sayğacı hər gün ondan hesablanır.</li>
<li><b>Ən yaxşı rekord, gün</b> və <b>Bu il adam-saat</b>: ayda bir yeniləyin.</li>
<li><b>Ayın hədəfi / mesajı</b>: bir sətir.</li>
<li><b>Təhlükəsizlik anı</b>: başlıq və şəkilli qısa mətn - həftədə və ya ayda bir dəyişin.</li></ul>"""}},

    {"slug": "admin-training", "category": "admin", "sort": 40,
     "title": {"en": "Certificates, types and the training matrix", "ru": "Сертификаты, типы и матрица обучения", "az": "Sertifikatlar, növlər və təlim matrisi"},
     "body": {
         "en": """<h3>Certificate types first</h3><ul>
<li>Add each certificate once in <b>Certificate types</b> with its <b>validity in months</b> (e.g. BOSIET 48).</li>
<li>Then the expiry date is filled automatically from the issue date - leave <b>Expires</b> empty.</li></ul>
<h3>Adding certificates</h3><ul>
<li><b>+ Add certificate</b>: choose the person from the list, the type, the issue date, number, provider; attach the scan (PDF or photo).</li>
<li><b>Import from Excel</b>: copy rows with 5 columns - person (user name, e-mail or full name), certificate type (exact name), issued, expires (may be empty), number. Dates as 15.03.2026 or 2026-03-15. Rows that can't be matched are listed as “not imported”.</li></ul>
<h3>Dashboard and matrix</h3><ul>
<li>Tiles: <b>Expired</b>, due in ≤30/60/90 days, valid - click a tile to filter.</li>
<li><b>Training matrix</b>: people × certificate types, coloured by status - use it to plan renewals.</li>
<li>Each employee sees their own certificates under <b>Training</b>.</li></ul>""",
         "ru": """<h3>Сначала типы сертификатов</h3><ul>
<li>Добавьте каждый сертификат один раз в <b>Типы сертификатов</b> со <b>сроком действия в месяцах</b> (например, BOSIET 48).</li>
<li>Тогда дата окончания заполняется автоматически от даты выдачи - оставьте <b>Действует до</b> пустым.</li></ul>
<h3>Добавление сертификатов</h3><ul>
<li><b>+ Добавить сертификат</b>: выберите сотрудника из списка, тип, дату выдачи, номер, организацию; приложите скан (PDF или фото).</li>
<li><b>Импорт из Excel</b>: скопируйте строки с 5 столбцами - сотрудник (логин, e-mail или полное имя), тип сертификата (точное название), выдан, действует до (можно пусто), номер. Даты 15.03.2026 или 2026-03-15. Нераспознанные строки покажутся как «не импортировано».</li></ul>
<h3>Панель и матрица</h3><ul>
<li>Плитки: <b>Просрочен</b>, истекает через ≤30/60/90 дней, действует - нажмите плитку для фильтра.</li>
<li><b>Матрица обучения</b>: сотрудники × типы сертификатов по цвету статуса - для планирования продлений.</li>
<li>Каждый сотрудник видит свои сертификаты в разделе <b>Обучение</b>.</li></ul>""",
         "az": """<h3>Əvvəlcə sertifikat növləri</h3><ul>
<li>Hər sertifikatı bir dəfə <b>Sertifikat növləri</b> bölməsində <b>aylarla etibarlılıq müddəti</b> ilə əlavə edin (məs. BOSIET 48).</li>
<li>Onda bitmə tarixi verilmə tarixindən avtomatik hesablanır - <b>Bitmə tarixi</b> sahəsini boş saxlayın.</li></ul>
<h3>Sertifikat əlavə etmək</h3><ul>
<li><b>+ Sertifikat əlavə et</b>: siyahıdan şəxsi, növü, verilmə tarixini, nömrəni, təlimçi təşkilatı seçin; skanı əlavə edin (PDF və ya foto).</li>
<li><b>Excel-dən idxal</b>: 5 sütunlu sətirləri kopyalayın - şəxs (istifadəçi adı, e-poçt və ya tam ad), sertifikat növü (dəqiq ad), verilib, bitir (boş ola bilər), nömrə. Tarixlər 15.03.2026 və ya 2026-03-15. Tanınmayan sətirlər “idxal olunmadı” kimi göstərilir.</li></ul>
<h3>Panel və matris</h3><ul>
<li>Plitələr: <b>Vaxtı keçib</b>, ≤30/60/90 gün qalıb, etibarlıdır - filtr üçün plitəyə basın.</li>
<li><b>Təlim matrisi</b>: əməkdaşlar × sertifikat növləri, statusa görə rəngli - yeniləmələri planlamaq üçün.</li>
<li>Hər əməkdaş öz sertifikatlarını <b>Təlim</b> bölməsində görür.</li></ul>"""}},

    {"slug": "admin-it", "category": "admin", "sort": 50,
     "title": {"en": "Help Center articles, usage analytics and audit log", "ru": "Статьи справочного центра, аналитика и журнал изменений", "az": "Kömək mərkəzi məqalələri, analitika və dəyişikliklər jurnalı"},
     "body": {
         "en": """<h3>Writing a Help Center article</h3><ul>
<li><b>Address</b> (slug): short, lower-case, with dashes (book-meeting-room). It is the link: /help/book-meeting-room - don't change it later, “?” buttons point to it.</li>
<li>Fill <b>EN, RU and AZ</b>; staff read the article in their own language.</li>
<li>Write steps as a numbered list, one action per step, with the button names in <b>bold</b>.</li>
<li>Category <b>Admin guides</b> is visible only to editors (these cheat sheets).</li>
<li><b>Order</b>: smaller numbers come first in the category.</li></ul>
<h3>Usage analytics</h3><ul>
<li><b>Usage analytics</b>: visits per page and per day, by department and language (no names stored).</li>
<li>The <b>Help Center articles</b> list shows each article's “Was this helpful?” votes and the searches that found nothing - a hint for a new article.</li></ul>
<h3>Audit log</h3><ul>
<li><b>Audit log</b>: every change made by an editor - news, banner, people, HSE, certificates, help articles - with the name, time and address. Filter by section, period or person. Kept for 2 years.</li>
<li>IT also gets a morning e-mail when there were failed sign-ins or admin changes the day before. No e-mail means a quiet day.</li></ul>""",
         "ru": """<h3>Как написать статью справочного центра</h3><ul>
<li><b>Адрес</b> (slug): коротко, строчными, через дефис (book-meeting-room). Это ссылка /help/book-meeting-room - не меняйте её потом, на неё ведут кнопки «?».</li>
<li>Заполните <b>EN, RU и AZ</b>; сотрудники читают статью на своём языке.</li>
<li>Шаги - нумерованным списком, одно действие на шаг, названия кнопок <b>жирным</b>.</li>
<li>Категория <b>Для редакторов</b> видна только редакторам (эти памятки).</li>
<li><b>Порядок</b>: меньшие числа выше в категории.</li></ul>
<h3>Аналитика</h3><ul>
<li><b>Аналитика</b>: посещения по страницам и дням, по отделам и языкам (имена не хранятся).</li>
<li>Список <b>статей справочного центра</b> показывает оценки «Это помогло?» и поиски без результата - подсказку для новой статьи.</li></ul>
<h3>Журнал изменений</h3><ul>
<li><b>Журнал изменений</b>: каждое изменение редактора - новости, баннер, сотрудники, HSE, сертификаты, статьи - с именем, временем и адресом. Фильтр по разделу, периоду или человеку. Хранится 2 года.</li>
<li>ИТ также получает утреннее письмо, если накануне были неудачные входы или изменения редакторов. Нет письма - день был спокойным.</li></ul>""",
         "az": """<h3>Kömək mərkəzi məqaləsi yazmaq</h3><ul>
<li><b>Ünvan</b> (slug): qısa, kiçik hərflərlə, defislə (book-meeting-room). Bu, keçiddir: /help/book-meeting-room - sonra dəyişməyin, “?” düymələri ona aparır.</li>
<li><b>EN, RU və AZ</b> doldurun; əməkdaşlar məqaləni öz dilində oxuyur.</li>
<li>Addımları nömrəli siyahı ilə yazın, hər addımda bir hərəkət, düymə adları <b>qalın</b>.</li>
<li><b>Redaktorlar üçün</b> kateqoriyası yalnız redaktorlara görünür (bu yaddaş kartları).</li>
<li><b>Sıra</b>: kiçik rəqəmlər kateqoriyada yuxarıda olur.</li></ul>
<h3>İstifadə analitikası</h3><ul>
<li><b>İstifadə analitikası</b>: səhifələr və günlər, şöbələr və dillər üzrə ziyarətlər (adlar saxlanılmır).</li>
<li><b>Kömək mərkəzi məqalələri</b> siyahısı “Faydalı oldu?” rəylərini və nəticəsiz axtarışları göstərir - yeni məqalə üçün ipucu.</li></ul>
<h3>Dəyişikliklər jurnalı</h3><ul>
<li><b>Dəyişikliklər jurnalı</b>: redaktorun hər dəyişikliyi - xəbərlər, banner, əməkdaşlar, HSE, sertifikatlar, məqalələr - ad, vaxt və ünvanla. Bölmə, dövr və ya şəxs üzrə süzün. 2 il saxlanılır.</li>
<li>Ötən gün uğursuz girişlər və ya redaktor dəyişiklikləri olubsa, İT səhər e-məktub alır. Məktub yoxdursa, gün sakit keçib.</li></ul>"""}},
]

ARTICLES += [
    {"slug": "admin-people", "category": "admin", "sort": 15,
     "title": {"en": "People: job title, department and manager", "ru": "Сотрудники: должность, отдел и руководитель",
               "az": "Əməkdaşlar: vəzifə, şöbə və rəhbər"},
     "body": {
         "en": """<ul>
<li>The list comes from Active Directory - the same data as the Directory, Outlook's address book and the org chart.</li>
<li><b>Needs attention</b> shows people with no job title, department or manager. Fill those first.</li>
<li><b>Edit</b> → change the fields → <b>Save to AD</b>. The change shows everywhere within a minute.</li>
<li><b>Manager</b>: start typing and pick the name from the list. Clear the field to remove the manager.</li>
<li><b>Department</b>: pick an existing name from the list so the same department is not spelled two ways.</li>
<li>Write job titles in English, in the same style (“Human capital manager”, “Senior accountant”).</li>
<li>Names, e-mail addresses, new accounts and leavers stay with IT - send them a request.</li>
<li><b>History</b> in the edit window shows who changed what and when.</li></ul>""",
         "ru": """<ul>
<li>Список берётся из Active Directory - это те же данные, что в справочнике, адресной книге Outlook и оргструктуре.</li>
<li><b>Требует внимания</b> показывает сотрудников без должности, отдела или руководителя. Заполните их в первую очередь.</li>
<li><b>Изменить</b> → поправьте поля → <b>Сохранить в AD</b>. Изменение везде появится через минуту.</li>
<li><b>Руководитель</b>: начните вводить и выберите имя из списка. Очистите поле, чтобы убрать руководителя.</li>
<li><b>Отдел</b>: выбирайте существующее название из списка, чтобы один отдел не писался по-разному.</li>
<li>Должности пишите по-английски в одном стиле («Human capital manager», «Senior accountant»).</li>
<li>Имена, адреса e-mail, новые учётные записи и уволившиеся - через IT, отправьте заявку.</li>
<li><b>История</b> в окне редактирования показывает, кто и когда что менял.</li></ul>""",
         "az": """<ul>
<li>Siyahı Active Directory-dən gəlir - Ünvan kitabı, Outlook ünvan kitabı və struktur sxemi ilə eyni məlumatdır.</li>
<li><b>Diqqət tələb edir</b> vəzifəsi, şöbəsi və ya rəhbəri olmayan əməkdaşları göstərir. Əvvəlcə onları doldurun.</li>
<li><b>Redaktə</b> → sahələri dəyişin → <b>AD-də saxla</b>. Dəyişiklik bir dəqiqəyə hər yerdə görünür.</li>
<li><b>Rəhbər</b>: yazmağa başlayın və adı siyahıdan seçin. Rəhbəri silmək üçün sahəni boşaldın.</li>
<li><b>Şöbə</b>: eyni şöbə iki cür yazılmasın deyə siyahıdakı mövcud adı seçin.</li>
<li>Vəzifələri ingiliscə, eyni üslubda yazın (“Human capital manager”, “Senior accountant”).</li>
<li>Adlar, e-poçt ünvanları, yeni hesablar və işdən çıxanlar IT ilə qalır - sorğu göndərin.</li>
<li>Redaktə pəncərəsindəki <b>Tarixçə</b> kimin nəyi nə vaxt dəyişdiyini göstərir.</li></ul>"""}},
]
