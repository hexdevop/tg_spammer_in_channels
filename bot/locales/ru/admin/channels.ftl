channels-list =
    <i><b>🔊 Список каналов</>

    Добавьте/Выберите один из каналов для его настройки</>

forward-me-message-from-channel = <i><b>💬 Перешлите мне сообщение с канала который вы хотите добавить</></>

bot-is-a-not-member-of-the-channel = <i><b>💢 Бот не является участником канала! Повторите попытку когда добавите бота в канал</></>

bot-dont-have-enough-rights =
    <i><b>💢 У бота не достаточно прав</>

    Бот должен иметь право на <b>Публикацию сообщений</> и <b>Удаление публикаций</></>

channel-successfully-add = <i><b>✅ Канал {$mention} успешно добавлен</></>

channel-settings =
    <i><b>⚙️ Настройки канала</>

    ℹ️ ID: <code>{$chat_id}</>
    🔡 Название: {$mention}
    ➡️ Ссылка: {$username}

    🔢 Постов - {$count}
    🕓 Интервал - {$interval}
    ☑️ Кругов - {$sent}/{$limit ->
[0] ♾️
*[other] {$limit}
} (До конца круга {$to_the_end})
    🔘 Статус - {$status}

    Дата добавления: {$created_at}</>

confirm-deleting-channel = <i><b>😭 Подтвердите удаление канала {$mention}</></>

get-post-interval = <i><b>🕐 Введите интервал в секундах</>

    Например: 1, 2, 5, 10, 30, 60</>

get-post-limit = <i><b>☑️ Введите количество кругов постов которые должны быть отправлены</>

    1 круг - отправка всех добавленных постов 1 раз</>

select-spamming-type =
    <i><b>💬 Как начать спамить постами ?</>

    📢 Начать сейчас - Первый пост будет отправлен немедленно и будет отправлятся в заданном интервале

    🕐 С интервалом - Сначала бот подождет заданный интервал, а после, посты будут отправляться в заданном интервале</>

no-post-found = 💢 Сначала добавьте хотя бы один пост
