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
        },
        'fallback': 'Пожалуйста, выберите опцию из меню.'
    },
    'show_tariffs': {
        'message': '\n'.join([f"{name}: {price} руб./кв.м" for name, price in CLEANING_PRICES.items()]),
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        }
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки:',
        'options': ['Ген.уборка', 'Повседневная', 'Послестрой', 'Мытье окон', 'В начало'],
        'next_state': {
            'Ген.уборка': 'enter_square_meters',
            'Повседневная': 'enter_square_meters',
            'Послестрой': 'enter_square_meters',
            'Мытье окон': 'enter_square_meters',
            'В начало': 'main_menu'
        },
        'fallback': 'Пожалуйста, выберите тип уборки из списка.',
        'list': {
            'enter_square_meters': {
                'message': 'Введите количество квадратных метров:',
                'options': ['В начало'],
                'next_state': {
                    'calculate_result': 'calculate_result'
                },
                'fallback': 'Пожалуйста, введите корректное количество квадратных метров.',
                'list': {
                    'calculate_result': {
                        'message': 'Стоимость уборки: {total_cost:.2f} руб.',
                        'options': ['В начало', 'Заказать клининг'],
                        'run': 'calculate',
                        'next_state': {
                            'В начало': 'main_menu',
                            'Заказать клининг': 'order_cleaning_now'
                        },
                        'list': {
                            'order_cleaning_now': {
                                'message': 'Заявка отправлена! Ожидайте звонка от нашего менеджера.',
                                'options': ['В начало'],
                                'run': 'order_cleaning_now_func',
                                'next_state': {
                                    'В начало': 'main_menu'
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'order_cleaning': {
        'message': 'Для заказа клининга нажмите "Заказать сейчас" или свяжитесь с нами по телефону +7 (123) 456-78-90.',
        'options': ['Заказать сейчас', 'В начало'],
        'next_state': {
            'Заказать сейчас': 'order_cleaning_now',
            'В начало': 'main_menu'
        },
        'fallback': 'Пожалуйста, выберите опцию из меню.'
    },
    'contact': {
        'message': 'Связаться с нами вы можете по телефону +7 (123) 456-78-90 или через email: clean@example.com.',
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        },
        'fallback': 'Пожалуйста, выберите опцию из меню.'
    }
}


# Функция для отправки сообщения с заданной клавиатурой
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)
    logger.info("Отправлено сообщение: %s", message)


# Функция-фильтр для выполнения расчетов
def calculate(context: ContextTypes.DEFAULT_TYPE, **kwargs) -> dict:
    price_per_sqm = context.user_data.get('price_per_sqm')
    sqm = float(kwargs.get('user_choice'))
    total_cost = price_per_sqm * sqm
    return {
        'total_cost': total_cost,
        'formatted_message': f'Стоимость уборки: {total_cost:.2f} руб.'
    }


# Функция для обработки заявки на клининг
async def order_cleaning_now_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Логика отправки сообщения владельцу бота
    await send_message(update, context, 'Ваша заявка принята и обрабатывается. Ожидайте!', ['В начало'])
    context.user_data['state'] = 'main_menu'


# Универсальная функция для вызова действий
async def run_action(action_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    action_map = {
        'calculate': calculate,
        'order_cleaning_now_func': order_cleaning_now_func
    }

    if action_name in action_map:
        action = action_map[action_name]
        if action_name == 'calculate':
            result = action(context, **kwargs)
            message = MENU_TREE[context.user_data['state']]['message'].format(**result)
            await send_message(update, context, message, ['В начало'])
            context.user_data['state'] = 'main_menu'
        elif action_name == 'order_cleaning_now_func':
            await action(update, context)


# Функция обработки переходов между состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    # Получаем текущее меню
    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text

    # Проверяем наличие функции 'run' для выполнения
    if 'run' in menu:
        await run_action(menu['run'], update, context, user_choice=user_choice)
        return

    # Проверяем, есть ли следующий уровень меню
    if user_choice in CLEANING_PRICES and user_state == 'calculator_menu':
        context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
        next_state = 'enter_square_meters'
        context.user_data['state'] = next_state
        await send_message(update, context, MENU_TREE['calculator_menu']['list']['enter_square_meters']['message'],
                           MENU_TREE['calculator_menu']['list']['enter_square_meters']['options'])
    elif user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        next_menu = MENU_TREE['calculator_menu']['list'].get(next_state) or MENU_TREE.get(next_state)
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
