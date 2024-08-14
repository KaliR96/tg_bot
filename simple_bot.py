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

# Пути к изображениям и текст для каждого тарифа
CLEANING_DETAILS = {
    'Ген.уборка': {
        'image_path': 'path_to_general_cleaning_image.jpg',  # Укажите путь к изображению для Генеральной уборки
        'details_text': 'Генеральная уборка включает в себя полную уборку всей квартиры: удаление пыли, чистка полов, влажная уборка всех поверхностей и т.д.'
    },
    'Повседневная': {
        'image_path': 'path_to_daily_cleaning_image.jpg',  # Укажите путь к изображению для Повседневной уборки
        'details_text': 'Повседневная уборка включает поддержание чистоты: протирка пыли, мытье полов, уборка на кухне и в санузле.'
    },
    'Послестрой': {
        'image_path': 'path_to_post_construction_cleaning_image.jpg',  # Укажите путь к изображению для уборки после ремонта
        'details_text': 'Уборка после ремонта включает удаление строительной пыли, очистку окон и дверей, удаление следов краски и т.д.'
    },
    'Мытье окон': {
        'image_path': 'path_to_window_cleaning_image.jpg',  # Укажите путь к изображению для мытья окон
        'details_text': 'Мытье окон включает очистку стекол снаружи и изнутри, а также протирку рам и подоконников.'
    }
}

# Определение дерева меню
MENU_TREE = {
    'main_menu': {
        'message': 'Привет! Я Вера, твоя фея чистоты.\nМой робот-уборщик поможет:\n- рассчитать стоимость уборки\n- прислать клининг на дом\n- связаться со мной.',
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
        'message': 'Выберите тариф для получения подробностей:',
        'options': ['Ген.уборка', 'Повседневная', 'Послестрой', 'Мытье окон', 'В начало'],
        'next_state': {
            'Ген.уборка': 'detail_Ген.уборка',
            'Повседневная': 'detail_Повседневная',
            'Послестрой': 'detail_Послестрой',
            'Мытье окон': 'detail_Мытье окон',
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
        'fallback': 'Пожалуйста, выберите тип уборки из списка.'
    },
    'enter_square_meters': {
        'message': 'Введите количество квадратных метров:',
        'options': ['В начало'],
        'next_state': {
            'calculate_result': 'calculate_result'
        },
        'fallback': 'Пожалуйста, введите корректное количество квадратных метров.'
    },
    'calculate_result': {
        'message': '',  # Мы будем динамически формировать сообщение
        'options': ['В начало', 'Заказать клининг'],
        'next_state': {
            'В начало': 'main_menu',
            'Заказать клининг': 'order_cleaning_now'
        }
    },
    'order_cleaning_now': {
        'message': 'Заявка отправлена! Ожидайте звонка от нашего менеджера.',
        'options': ['В начало'],
        'run': 'order_cleaning_now_func',
        'next_state': {
            'В начало': 'main_menu'
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

# Динамическое добавление состояний для каждого тарифа
for tariff_name, details in CLEANING_DETAILS.items():
    MENU_TREE[f'detail_{tariff_name}'] = {
        'message': details['details_text'],
        'image_path': details['image_path'],
        'options': ['В начало'],
        'next_state': {
            'В начало': 'main_menu'
        }
    }

# Функция для отправки сообщения с заданной клавиатурой
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)
    logger.info("Отправлено сообщение: %s", message)

# Функция для расчета стоимости уборки
def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm
    formatted_message = f'Стоимость уборки: {total_cost:.2f} руб.'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для обработки заявки на клининг
async def order_cleaning_now_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Логика отправки сообщения владельцу бота
    await send_message(update, context, 'Ваша заявка принята и обрабатывается. Ожидайте!', ['В начало'])
    context.user_data['state'] = 'main_menu'

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['state'] = 'main_menu'
    menu = MENU_TREE['main_menu']
    await send_message(update, context, menu['message'], menu['options'])

# Универсальная функция для обработки переходов между состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text

    if user_state in [f'detail_{name}' for name in CLEANING_PRICES.keys()]:
        details = CLEANING_DETAILS.get(user_state.split('_')[1])
        if details:
            # Отправляем изображение
            with open(details['image_path'], 'rb') as image_file:
                await update.message.reply_photo(photo=image_file)
            # Отправляем текст
            await send_message(update, context, details['details_text'], ['В начало'])
        context.user_data['state'] = 'main_menu'
    elif user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu['fallback'], menu['options'])

# Основная функция для запуска бота
def main():
    logger.info("Запуск бота")

    # Ваш токен
    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'  # Вставьте ваш токен сюда

    # Создаем объект Application и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
