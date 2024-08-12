# -*- coding: utf-8 -*-
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
        }
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки:',
        'options': ['Ген.уборка', 'Повседневная', 'Послестрой', 'Мытье окон', 'В начало'],
        'next_state': {
            'Ген.уборка': 'calculate_cost',
            'Повседневная': 'calculate_cost',
            'Послестрой': 'calculate_cost',
            'Мытье окон': 'calculate_cost',
            'В начало': 'main_menu'
        }
    },
    'back_to_main': {
        'message': 'В начало',
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


# Функция обработки переходов между состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text

    # Проверка, если выбранная опция ведет на следующий уровень
    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        # Переход на следующий уровень меню
        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
        elif next_state == 'calculate_cost':
            # Обработка калькулятора отдельно, так как требуется ввод данных
            context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
            await send_message(update, context, f'Вы выбрали {user_choice}. Введите количество квадратных метров:', ['В начало'])
    else:
        # Обработка ввода квадратных метров для расчета стоимости
        if user_state == 'calculate_cost':
            try:
                sqm = float(user_choice)
                price_per_sqm = context.user_data.get('price_per_sqm')
                total_cost = price_per_sqm * sqm
                await send_message(update, context, f'Стоимость уборки: {total_cost:.2f} руб.', ['В начало'])
                context.user_data['state'] = 'main_menu'
            except ValueError:
                await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                                   ['В начало'])
        else:
            # Если выбрана некорректная опция
            await send_message(update, context, 'Пожалуйста, выберите опцию из меню.', menu['options'])


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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
