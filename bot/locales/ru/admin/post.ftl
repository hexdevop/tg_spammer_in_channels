posts-list =
    <i><b>💭 Список постов канала {$mention}</>

    Тут можно Добавить/Посмотреть/Изменить порядок/Удалить пост</>

post-settings =
    <i><b>⚙️ Настройки поста для канала {$mention}</>

    ⬜️ Тип - {$media_type}
    ⏹️ Кнопки - {$keyboard}
    💭 Текст - {$text}

    🕓 Интервал - {$interval}
    ☑️ Прогресс - {$sent}/{$limit ->
[0] ♾️
*[other] {$limit}
}
    🔘 Статус - {$status}</>

add-the-post =
    <i><b>➕ Отправьте мне ваш готовый пост вместе с кнопками (Не обязательно)</>

    <blockquote expandable>Поддерживаю только эти типы
    👇
    {$types}</></>

unsupported-post-type = <i><b>💢 Я не поддерживаю этот тип</>

    <blockquote expandable>Поддерживаю только эти типы
    👇
    {$types}</></>

post-add-successfully = <i><b>✅ Пост успешно добавлен</></>

confirm-deleting-post = <i><b>😭 Подтвердите удаление поста канала {$mention}</></>

