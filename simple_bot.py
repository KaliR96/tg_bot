# -*- coding: utf-8 -*-
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Цены на квадратный метр для каждого типа уборки
CLEANING_PRICES = {
    'Ген.уборка': 125,
    'Повседневная': 75,
    'Послестрой': 190,
    'Мытье окон': 100
}

# Определение дерева меню
MENU_TREE = {
    'main_menu': {
        'message': 'Привет!\nЯ Вера, твоя фея чистоты.\nМой робот-уборщик поможет:\n- рассчитать стоимость уборки\n- прислать клининг на дом\n- связаться со мной.',
        'options': ['Тарифы', 'Калькулятор', 'Заказать клининг', 'Связаться'],
        'next_state': {
            'Тарифы': 'show_tariffs',
            'Калькулятор': 'calculator_menu',
            'Заказать клининг': 'order_cleaning',
            'Связаться': 'contact'
        },
        'fallback': 'Пожалуйста, выберите опцию из меню.'
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки:',
        'options': ['Ген.уборка', 'Повседневная', 'Послестрой', 'Мытье окон', 'В начало'],
        'next_state': {
            'Ген.уборка': 'calculator_menu.enter_square_meters',
            'Повседневная': 'calculator_menu.enter_square_meters',
            'Послестрой': 'calculator_menu.enter_square_meters',
            'Мытье окон': 'calculator_menu.enter_square_meters',
            'В начало': 'main_menu'
        },
        'fallback': 'Пожалуйста, выберите тип уборки из списка.',
        'enter_square_meters': {
            'message': 'Введите количество квадратных метров:',
            'options': ['В начало'],
            'run': 'calculate',
            'fallback': 'Пожалуйста, введите корректное количество квадратных метров.'
        }
    },
    'show_tariffs': {
        'message': '\n'.join([f"{name}: {price} руб./кв.м" for name, price in CLEANING_PRICES.items()]),
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        }
    },
    'order_cleaning': {
        'message': 'Для заказа клининга свяжитесь с нами по телефону +7 (123) 456-78-90 или оставьте заявку на сайте.',
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        }
    },
    'contact': {
        'message': 'Связаться с нами вы можете по телефону +7 (123) 456-78-90 или через email: clean@example.com.',
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        }
    }
}

# Функция для отправки сообщения с заданной клавиатурой
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)
    logger.info("Отправлено сообщение: %s", message)

# Функция для обработки калькуляции
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        sqm = float(update.message.text)
        price_per_sqm = context.user_data.get('price_per_sqm')
        total_cost = price_per_sqm * sqm
        await send_message(update, context, f'Стоимость уборки: {total_cost:.2f} руб.', ['В начало'])
        context.user_data['state'] = 'main_menu'
    except ValueError:
        fallback_message = MENU_TREE['calculator_menu']['enter_square_meters']['fallback']
        await send_message(update, context, fallback_message, ['В начало'])

# Функция обработки переходов между состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    menu_path = user_state.split('.')
    menu = MENU_TREE
    for key in menu_path:
        menu = menu.get(key)

    user_choice = update.message.text

    # Если в текущем меню есть 'run', то запускаем соответствующую функцию
    if 'run' in menu:
        handler = globals()[menu['run']]
        await handler(update, context)
    elif user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        next_menu = MENU_TREE
        for key in next_state.split('.'):
            next_menu = next_menu.get(key)

        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu['fallback'], menu['options'])

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['state'] = 'main_menu'
    menu = MENU_TREE['main_menu']
    await send_message(update, context, menu['message'], menu['options'])

# Основная функция, которая отвечает за запуск бота
def main():
    logger.info("Запуск бота")

    # Ваш токен
    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'

    # Создаем объект Application и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle
