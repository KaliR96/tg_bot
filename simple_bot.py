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
        'image_path': r'C:\Users\travo\Desktop\tg_bot\генералка.jpg',
        'details_text': 'Генеральная уборка включает в себя полную уборку всей квартиры: удаление пыли, чистка полов, влажная уборка всех поверхностей и т.д.'
    },
    'Повседневная': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\повседневка.jpg',
        'details_text': 'Повседневная уборка включает поддержание чистоты: протирка пыли, мытье полов, уборка на кухне и в санузле.'
    },
    'Послестрой': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\послестрой.jpg',
        'details_text': 'Уборка после ремонта включает удаление строительной пыли, очистку окон и дверей, удаление следов краски и т.д.'
    },
    'Мытье окон': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\окна.jpg',
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
        }
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
        }
    },
    'enter_square_meters': {
        'message': 'Введите количество квадратных метров:',
        'options': ['В начало'],
        'next_state': {
            'calculate_result': 'calculate_result'
        }
    },
    'calculate_result': {
        'options': ['В начало', 'Заказать клининг'],
        'next_state': {
            'В начало': 'main_menu',
            'Заказать клининг': 'order_cleaning_now'
        }
    },
    'order_cleaning_now': {
        'message': 'Заявка отправлена! Ожидайте звонка от нашего менеджера.',
        'options': ['В начало'],
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

# Универсальная функция для обработки переходов между состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text

    # Переход в главное меню
    if user_choice == 'В начало':
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
        await send_message(update, context, menu['message'], menu['options'])
        return

    # Обработка выбора тарифа в меню "Тарифы"
    if user_state == 'show_tariffs' and user_choice in CLEANING_PRICES:
        details = CLEANING_DETAILS.get(user_choice)
        if details:
            try:
                # Отправляем изображение
                with open(details['image_path'], 'rb') as image_file:
                    await update.message.reply_photo(photo=image_file)
            except FileNotFoundError:
                logger.error(f"Изображение не найдено: {details['image_path']}")
                await update.message.reply_text("Изображение для этого тарифа временно недоступно.")
            # Отправляем текст
            await send_message(update, context, details['details_text'], ['В начало'])
        return

    # Обработка выбора типа уборки в калькуляторе
    if user_state == 'calculator_menu' and user_choice in CLEANING_PRICES:
        context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]  # Сохранение цены в контексте
        context.user_data['state'] = 'enter_square_meters'
        await send_message(update, context, MENU_TREE['enter_square_meters']['message'], MENU_TREE['enter_square_meters']['options'])
        return

    # Обработка ввода квадратных метров
    if user_state == 'enter_square_meters':
        try:
            sqm = float(user_choice)
            price_per_sqm = context.user_data.get('price_per_sqm')
            if price_per_sqm is None:
                await send_message(update, context, 'Произошла ошибка. Пожалуйста, вернитесь в главное меню и начните заново.', ['В начало'])
                context.user_data['state'] = 'main_menu'
                return

            result = calculate(price_per_sqm, sqm)
            await send_message(update, context, result['formatted_message'], MENU_TREE['calculate_result']['options'])
            context.user_data['state'] = 'main_menu'
        except ValueError:
            await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.', menu['options'])
        return

    # Переходы между остальными состояниями
    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state
        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu.get('fallback', 'Пожалуйста, выберите опцию из меню.'), menu['options'])

# Функция для расчета стоимости уборки
def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm
    formatted_message = f'Стоимость уборки: {total_cost:.2f} руб.'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['state'] = 'main_menu'
    menu = MENU_TREE['main_menu']
    await send_message(update, context, menu['message'], menu['options'])

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
