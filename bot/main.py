import os
from io import BytesIO
from typing import Dict, Any

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

from .content import generate_question
from .images import render_time_of_day_card, render_text_card, render_clock
from .voice import synthesize_ru_speech_to_bytes


DEFAULT_LEVEL = 1


def _ensure_user_defaults(user_data: Dict[str, Any]) -> None:
    if "level" not in user_data:
        user_data["level"] = DEFAULT_LEVEL
    if "voice_enabled" not in user_data:
        user_data["voice_enabled"] = False


async def _send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    _ensure_user_defaults(user_data)

    level = int(user_data.get("level", DEFAULT_LEVEL))
    q = generate_question(level)

    if q.render_type == "time_of_day":
        image_bytes = render_time_of_day_card(q.render_params.get("label", ""))
    elif q.render_type == "text_card":
        image_bytes = render_text_card(q.render_params.get("text", ""))
    else:
        image_bytes = render_clock(
            int(q.render_params.get("hour", 12)), int(q.render_params.get("minute", 0))
        )

    keyboard = [[InlineKeyboardButton(text=c.capitalize(), callback_data=f"ans::{c}")] for c in q.choices]
    markup = InlineKeyboardMarkup(keyboard)

    user_data["current_correct"] = q.correct

    if update.effective_chat is not None:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(BytesIO(image_bytes), filename="card.png"),
            caption=q.question_text,
            reply_markup=markup,
        )

    if user_data.get("voice_enabled") and update.effective_chat is not None:
        audio_bytes = synthesize_ru_speech_to_bytes(q.question_text)
        if audio_bytes:
            await context.bot.send_voice(
                chat_id=update.effective_chat.id,
                voice=InputFile(BytesIO(audio_bytes), filename="q.mp3"),
                caption="Подсказка голосом",
            )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user_defaults(context.user_data)
    name = update.effective_user.first_name if update.effective_user else "друг"
    greeting = (
        f"Привет, {name}! Я помогу тебе разобраться со временем: временем суток, днями недели, месяцами и часами.\n"
        f"Начнём с простого. Можешь в любой момент сменить уровень: /level 1..5.\n"
        f"Голосовую озвучку можно включить командой /voice."
    )
    if update.message is not None:
        await update.message.reply_text(greeting)
    await _send_question(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Команды:\n"
        "/start — начать обучение\n"
        "/level 1..5 — выбрать уровень сложности\n"
        "/voice — включить/выключить голосовую озвучку"
    )
    if update.message is not None:
        await update.message.reply_text(text)


async def level_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user_defaults(context.user_data)
    if context.args:
        try:
            level = int(context.args[0])
            level = max(1, min(5, level))
            context.user_data["level"] = level
            if update.message is not None:
                await update.message.reply_text(f"Уровень установлен: {level}")
        except ValueError:
            if update.message is not None:
                await update.message.reply_text("Укажи уровень числом от 1 до 5, например: /level 3")
    else:
        if update.message is not None:
            await update.message.reply_text(f"Текущий уровень: {context.user_data.get('level', DEFAULT_LEVEL)}. Укажи: /level 1..5")
    await _send_question(update, context)


async def voice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user_defaults(context.user_data)
    context.user_data["voice_enabled"] = not context.user_data.get("voice_enabled")
    state = "включена" if context.user_data["voice_enabled"] else "выключена"
    if update.message is not None:
        await update.message.reply_text(f"Голосовая озвучка {state}.")
    await _send_question(update, context)


async def on_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    user_data = context.user_data
    _ensure_user_defaults(user_data)
    correct = user_data.get("current_correct")

    data = query.data or ""
    chosen = data.split("::", 1)[1] if data.startswith("ans::") else data

    feedback = "Верно! Молодец!" if chosen == correct else f"Пока нет. Правильный ответ: {correct}."

    if query.message is not None and query.message.caption:
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n{feedback}")

    await _send_question(Update(update.update_id, message=query.message), context)


def run() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN в окружении (.env)")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("level", level_cmd))
    app.add_handler(CommandHandler("voice", voice_cmd))
    app.add_handler(CallbackQueryHandler(on_answer))

    app.run_polling(close_loop=False)


if __name__ == "__main__":
    run()
