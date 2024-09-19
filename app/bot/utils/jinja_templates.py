from jinja2 import Template


user_main_menu_tm = Template("""
Этот бот - ваш спасательный круг в нашем море рунета

📱 Доступ ко всем сайтам и соц. сетям
🤫 Устойчивость к блокировкам
🚀 Без ограничения по скорости
💳 Оплата через сервис электронных платежей Юmoney
🌐 Доступ к российским сервисам с активированным VPN
💬 Оперативная поддержка 24/7 в любом вопросе.

/info для более подробной информации
""")


buy_subscription_tm = """
Выберите количество месяцев* на которое вы хотите купить или продлить подписку

<i>*Месяцем считается 30-дневный период</i>
"""


error_message = "Что-то пошло не так, обратитесь в поддержку"

sub_activity_info = Template("""
Подписка будет активна до {{ stop_date }} МСК
""")


success_payment = """
Оплата прошла успешно! 🎉🎉🎉
"""


sub_renew_msg = """
• Вы продлили подписку, дополнительно делать ничего не нужно
• Ключ-ссылку вы всегда можете посмотреть в вашем профиле в главном меню бота
"""


first_sub_activated_msg = """
• Скопируйте полученную ключ-ссылку ⏫⏫⏫ и следуйте инструкции для настройки
• Инструкции находятся в главном меню бота
• Количество устройств на ключ-ссылку не ограничено, но действует лимит трафика 200 гигабайт в месяц
• Вы можете посмотреть вашу ключ-ссылку и текущий расход трафика в вашем профиле в главном меню бота
"""


ios_foxray_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем из applestore программу foXray
3. В программе нажимаем значок планшета 📋
4. Нажимаем разрешить вставку и потом ОК
5. Готово! Что бы включить нажимаем на значок ▶️
"""


ios_v2box_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем из applestore программу V2Box
3. В программе сверху справа значок ➕
4. Нажимаем "Import V2Ray URI from clipboard"
5. Нажимаем разрешить вставку
6. Готово! Что бы выключить нажимаем на строку добавленного профиля
"""


ios_streisand_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем из applestore программу Streisand
3. В программе сверху справа нажимаем значок ➕
4. Выбираем "Вставить из буфера"
5. Готово! Что бы включить нажимаем значок ▶️
"""


macos_v2box_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем из applestore программу V2Box
3. Открываем приложение V2Box и нажимаем значок ➕
4. Выбираем опцию "Import url from clipboard"
5. Вернуться на главный экран (Значок дом)
6. Нажать кнопку "Connect" и разрешить приложению добавить конфигурацию VPN на устройство
"""


macos_nekoray_instruction_tm = """
1. Скачать архив с программой и распаковать его в любом месте
2. Запустить программу от <u>рута</u>
3. Скопировать ключ-ссылку в буфер обмена
4. В программе нажать на "Программа" в левом верхнем углу
5. Выбрать "Добавить профиль из буфера обмена"
6. В правом верхнем углу поставить галочку на режим TUN 
"""


android_v2ray_instruction_tm = Template("""
1. Копируем ключ-ссылку
2. Скачиваем из google play программу v2rayNG
3. Нажимаем сверху значок ➕
4. Выбираем "Импорт из буфера"
5. Готово! Что бы включить нажимаем снизу на значок ✔️
""")


android_nekobox_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем из google play программу nekobox (ярлык после установки может называться "MiProxy VPN")
3. Нажимаем сверху значок листа с ➕ внутри
4. Выбираем "Импорт из буфера обмена"
5. Готово! Что бы включить нажимаем снизу на значок самолетика
"""


windows_invisible_man_instruction_tm = """
1. Копируем ключ-ссылку
2. Скачиваем архив и распаковываем в любом удобном месте
3. Выбираем "Manage server configuration"
4. Нажимаем значок плюса
5. Выбираем "Import from link", вставляем скопированную ключ-ссылку и нажимаем "Import"
6. Закрываем меню выбора профиля и нажимаем RUN
"""


windows_nekoray_instruction_tm = """
1. Скачать программу и распаковать ее в любом месте
2. Запустить файл nekoray.exe из папки программы
3. Скопировать ключ-ссылку в буфер обмена
4. В программе нажать на "Программа" в левом верхнем углу
5. Выбрать "Добавить профиль из буфера обмена"
6. В правом верхнем углу поставить галочку на режим TUN
"""


linux_nekoray_instruction_tm = """
1. Скачиваем устанавливаем программу через ваш пакетный менеджер
2. Скопировать ключ-ссылку в буфер обмена
3. В программе нажать на "Программа" в левом верхнем углу
4. Выбрать "Добавить профиль из буфера обмена"
5. В правом верхнем углу поставить галочку на режим TUN
"""


xray_url = Template("<pre>"
                    "vless://{{ xray_uuid }}@"
                    "{{ host }}:{{ port }}?"
                    "type=tcp&"
                    "security=reality&"
                    "pbk={{ pbk }}&"
                    "fp=chrome&sni={{ mask_host }}&"
                    "sid={{ sid }}&"
                    "spx=/&"
                    "flow=xtls-rprx-vision#"
                    "{{ profile_name }}"
                    "</pre>")

profile_stat_unsub = Template("""
<b>Мой Telegram ID</b>
{{ telegram_id }}

Нет подписки
""")


profile_stat = Template("""
<b>Мой Telegram ID</b>
{{ telegram_id }}

<b>Подписка</b>
• Время оформления
{{ sub_created_at }}
• Время окончания
{{ sub_end_datetime }}
• Осталось
{{ days_to_end }} дней

<b>Трафик</b>
• Расход за период
{{ period_value }}/{{ traffic_limit }} Гб.
• Следующий сброс
{{ next_traffic_reset }}
""")

