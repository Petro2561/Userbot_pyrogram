## Описание

Реализован ЮзерБот, который эмитирует воронку продаж.
После того, как пользователь написал Юзерботу, юзербот отправляет ему три сообщения, через определенный промежуток времени.
Также юзербот проверят наличие слов триггеров, а также статус пользователя.

## Запуск

1. Клонируем репозиторий на локальный компьютер 

```
git clone https://github.com/Petro2561/Userbot_pyrogram.git
```

2. Создаем .env файл в директории src. Пример находить в .env.example

3. Создаем образ и запускаем контейнер (Предполагается, что у вас установлен докер)
```
docker build -t userbot .
```
```
docker run userbot
```

Без использования докера необходимо: создать виртуальное окружение, запустить его, установить зависимости, запустить файл main.py.

Приложение готово к работе!

## Использованные технологии:
- Python 3.11
- Pyrogram
- SQLAlchemy
- Docker
- sqlite+aiosqlite
