# Телеграм-бот: Время для детей (5+)

Запуск локально:
```
pip install -r requirements.txt
python -m bot.main
```
Создайте `.env` рядом с этим файлом и добавьте:
```
TELEGRAM_BOT_TOKEN=ваш_токен
```

Railway:
- Start command: `python -m bot.main`
- Vars: `TELEGRAM_BOT_TOKEN` (обязательно), опционально `PYTHONUNBUFFERED=1`, `TZ=Europe/Moscow`
- Тип — без веба (ничего не слушает), домен и порт не нужны

Команды: `/start`, `/level 1..5`, `/voice`, `/help`.
