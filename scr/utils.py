from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMediaPhoto
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

import logging

logger = logging.getLogger(__name__)

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    # Проверяем, что `options` это список списков
    if isinstance(options[0], list):
        reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    else:
        # Если `options` - это просто список, преобразуем его в список списков
        reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

    # Логируем отправку сообщения и состояние
    logger.info(f"Отправка сообщения с текстом: {message} и состоянием: {context.user_data.get('state', 'main_menu')}")

    await update.message.reply_text(message, reply_markup=reply_markup)

async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info("Отправлено сообщение с кнопками: %s", message)

def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость вашей уборки: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость вашей уборки: {total_cost:.2f} руб.'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

def calculate_windows(price_per_panel, num_panels):
    total_cost = price_per_panel * num_panels

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость мытья окон: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость мытья окон: {total_cost:.2f} руб. за {num_panels} створок(и).'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }