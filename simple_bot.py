# -*- coding: utf-8 -*-
import requests
import httpx
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler


import telegram.error  # Добавляем этот импорт для доступа к telegram.error.Forbidden

# Настраиваем логирование на уровне DEBUG
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Укажите ваш Telegram ID
ADMIN_ID = 1238802718  # Замените на ваш реальный Telegram ID

# Цены на квадратный метр для каждого типа уборки
CLEANING_PRICES = {
    'Ген.Уборка🧼': 125,
    'Повседневная🧹': 75,
    'Послестрой🛠': 190,
    'Мытье окон🧴': 350
}

# Пути к изображениям и текст для каждого тарифа
CLEANING_DETAILS = {
    'Ген.Уборка🧼': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\img\general.jpg',
        'details_text': [
            'Стоимость по тарифу "Генеральная уборка" расчитывается по 125р. за кв.М',
            'Перечень услуг для генеральной уборки:\n\n1. Уборка полов:\n- Влажная уборка всех типов полов.\n- Глубокая очистка труднодоступных мест, включая углы и пространства под мебелью.\n\n2. Мойка зеркал:\n- Очистка зеркал и стеклянных поверхностей до блеска.\n- Удаление налета и загрязнений.\n\n3. Уборка кухни:\n- Очищение настенного фартука от следов готовки.\n- Чистка и дезинфекция кухонных поверхностей внутри гарнитура и снаружи.\n- Мытье и полировка кухонной техники (духовка, микроволновка, холодильник).',
            '4. Уборка ванной комнаты и туалета:\n- Мытье стен от известкового налета в санузлах.\n- Чистка и дезинфекция сантехники (унитаз, раковина, ванна, душ).\n- Удаление известкового налета и плесени.\n- Полировка смесителей и зеркал.\n\n5. Удаление пыли:\n- Протирание и очистка всех поверхностей от пыли (мебель, полки, техника).\n- Очистка плинтусов, карнизов, дверей и подоконников.\n- Уборка пыли с осветительных приборов и элементов декора.\n\n6. Обработка поверхностей антибактериальными средствами:\n- Обработка ручек дверей, выключателей и других часто трогаемых мест.',
            '7. Организация пространства:\n- Раскладка вещей и организация хранения.\n- Разбор и сортировка вещей, книг, одежды.\n\n8. Дополнительные услуги:\n- Мытье жалюзи.\n- Чистка и уход за комнатными растениями.'
        ]
    },
    'Повседневная🧹': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\img\vacuumcat.png',
        'details_text': [
            'Стоимость по тарифу "Повседневна уборка" расчитывается по 75р. за кв.М',
            'Перечень услуг для тарифа "Повседневная уборка":\n\n1. Легкая уборка полов:\n- Влажная уборка всех видов напольных покрытий.\n- Очистка труднодоступных мест, включая углы и пространства под мебелью.\n\n2. Протирка пыли:\n- Удаление пыли с открытых поверхностей мебели, подоконников, и техники.\n- Легкая очистка плинтусов и дверных ручек.',
            '3. Уборка кухни:\n- Протирка кухонных столешниц, стола и рабочих поверхностей.\n- Очистка варочной панели и внешней части кухонного гарнитура.\n\n4. Уборка ванной комнаты и туалета:\n- Чистка и дезинфекция сантехники (раковина, унитаз, душевая кабина).\n- Очистка зеркал и полок.\n\n5. Мойка зеркал и стеклянных поверхностей от отпечатков пальцев и загрязнений.\n\n6. Вынос мусора.',
            '7. Наведение порядка:\n- Организация вещей и устранение мелкого беспорядка.\n- Замена постельного белья по договоренности.'
        ]
    },
    'Послестрой🛠': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\img\build.jpg',
        'details_text': [
            'Стоимость по тарифу "Послестрой" расчитывается по 190р. за кв.М',
            'Перечень услуг для тарифа "Послестрой":\n\n1. Вынос строительного мусора:\n- Сбор и вынос не крупного строительного мусора.\n\n2. Мойка окон:\n- Тщательная мойка окон со всех сторон, включая рамы и подоконники.\n- Удаление следов строительных материалов, пыли и грязи.',
            '3. Обеспыливание поверхностей:\n- Влажная и сухая уборка стен, мебели, люстр, плинтусов, светильников и розеток для удаления строительной пыли.\n\n4. Мойка дверей и дверных рам:\n- Очистка дверей и рам от пыли, следов строительных материалов и загрязнений.\n- Протирка и полировка для восстановления чистоты и блеска.\n\n5. Мойка стен в санузлах:\n- Удаление затирки и следов строительных смесей с плитки в ванных комнатах и санузлах.',
            '6. Полировка зеркал и стеклянных поверхностей:\n- Удаление пятен, налета и загрязнений.\n- Натирание зеркал и всех стеклянных поверхностей до блеска.\n\n7. Очистка и полировка сантехники:\n- Удаление остатков строительных материалов, грязи и пятен.\n- Натирание и дезинфекция всех сантехнических приборов (унитазы, раковины, ванны).\n\n8. Мытье и дезинфекция полов:\n- Глубокая очистка полов от строительной пыли и грязи.\n- Дезинфекция напольных покрытий для полного устранения загрязнений.'
        ]
    },
    'Мытье окон🧴': {
        'image_path': r'C:\Users\travo\Desktop\tg_bot\img\window.jpg',
        'details_text': [
            'Стоимость по тарифу "Мытье окон" расчитывается по 350р. за створку',
            'Перечень услуг для мытья окон:\n\n- Мойка рам с двух сторон.\n- Очистка стекол от наклеек и следов клея.\n- Полировка стекол с двух сторон.\n-Мойка подоконников.\n- Обеспечение чистоты и порядка в помещении после завершения работы.'
        ]
    }
}

# Определение дерева меню
MENU_TREE = {
    'main_menu': {
        'message': 'Привет! Я Вера, твоя фея чистоты.\n\nМой робот-уборщик поможет:\n\n🔍Ознакомиться с моими услугами\n\n🧮Рассчитать стоимость уборки\n\n🚗Заказать клининг на дом\n\n📞Связаться со мной.',
        'options': [
            ['Тарифы🏷️', 'Калькулятор🧮'],  # Первая строка
            ['Связаться📞', 'Отзывы💬']     # Вторая строка
        ],
        'next_state': {
            'Тарифы🏷️': 'show_tariffs',
            'Калькулятор🧮': 'calculator_menu',
            'Связаться📞': 'contact',
            'Отзывы💬': 'reviews_menu'
        }
    },
    'admin_menu': {
        'message': 'Админ-панель:\nВыберите действие:',
        'options': ['Модерация'],  # Убираем кнопку "В начало🔙"
        'next_state': {
            'Модерация': 'moderation_menu',
        }
    },
    'moderation_menu': {
        'message': 'Вы всегда можете вернуться в админ меню:)',
        'options': ['Админ меню'],  # Добавляем кнопку "Админ меню"
        'next_state': {
            'Админ меню': 'admin_menu'
        }
    },
    'reviews_menu': {
        'message': 'Что вы хотите сделать?',
        'options': ['Написать отзыв', 'Посмотреть Отзывы💬', 'В начало🔙'],
        'next_state': {
            'Написать отзыв': 'write_review',
            'Посмотреть Отзывы💬': 'view_reviews',
            'В начало🔙': 'main_menu'
        }
    },
    'view_reviews': {
        'message': 'Просмотрите все отзывы на нашем канале:',
        'options': ['Перейти к каналу', 'В начало🔙'],
        'next_state': {
            'Перейти к каналу': 'open_channel',
            'В начало🔙': 'reviews_menu'
        }
    },
    'write_review': {
        'message': 'Пожалуйста, напишите ваш отзыв💬:',
        'options': ['В начало🔙'],
        'next_state': {
            'В начало🔙': 'main_menu'
        }
    },

    'show_tariffs': {
        'message': 'Выберите тариф для получения подробностей:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],  # Первая строка
            ['Послестрой🛠', 'Мытье окон🧴'],   # Вторая строка
            ['В начало🔙']                      # Третья строка с одной кнопкой
        ],
        'next_state': {
            'Ген.Уборка🧼': 'detail_Ген.Уборка🧼',
            'Повседневная🧹': 'detail_Повседневная🧹',
            'Послестрой🛠': 'detail_Послестрой🛠',
            'Мытье окон🧴': 'detail_Мытье окон🧴',
            'В начало🔙': 'main_menu'
        }
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки🧺:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],  # Первая строка
            ['Послестрой🛠', 'Мытье окон🧴'],   # Вторая строка
            ['В начало🔙']                      # Третья строка с одной кнопкой
        ],
        'next_state': {
            'Ген.Уборка🧼': 'enter_square_meters',
            'Повседневная🧹': 'enter_square_meters',
            'Послестрой🛠': 'enter_square_meters',
            'Мытье окон🧴': 'enter_square_meters',
            'В начало🔙': 'main_menu'
        }
    },
    'enter_square_meters': {
        'message': 'Введите количество квадратных метров,\nкоторые нужно убрать.',
        'options': ['В начало🔙'],
        'next_state': {
            'calculate_result': 'calculate_result'
        }
    },
    'enter_window_panels': {  # Новое состояние для ввода створок окон
        'message': 'Введите количество оконных створок:',
        'options': ['В начало🔙'],
        'next_state': {
            'calculate_result': 'calculate_result'
        }
    },
    'calculate_result': {
        'options': ['В начало🔙', 'Связаться📞'],
        'next_state': {
            'В начало🔙': 'main_menu',
            'Связаться📞': 'contact'
        }
    },
    'contact': {
        'message': 'Связаться📞 со мной вы можете через следующие каналы:',
        'options': ['В начало🔙'],
        'next_state': {
            'В начало🔙': 'main_menu'
        }
    }
}

# Динамическое добавление состояний для каждого тарифа с кнопкой "Калькулятор🧮"
for tariff_name, details in CLEANING_DETAILS.items():
    MENU_TREE[f'detail_{tariff_name}'] = {
        'message': details['details_text'],
        'image_path': details['image_path'],
        'options': ['Калькулятор🧮', 'Назад'],  # Заменяем "В начало🔙" на "Назад"
        'next_state': {
            'Калькулятор🧮': 'calculator_menu',
            'Назад': 'show_tariffs'  # Возвращаемся к списку тарифов
        }
    }

#Функция для возврата в главное меню.
async def go_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = 'main_menu'
    menu = MENU_TREE['main_menu']
    await send_message(update, context, menu['message'], menu['options'])
# Функция для отправки сообщения с клавиатурой
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    # Проверяем, что `options` это список списков
    if isinstance(options[0], list):
        reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    else:
        # Если `options` - это просто список, преобразуем его в список списков
        reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(message, reply_markup=reply_markup)
    logger.info("Отправлено сообщение: %s", message)

# Функция для отправки сообщения с inline-кнопками
async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info("Отправлено сообщение с кнопками: %s", message)

# Универсальная функция для обработки переходов между состояниями
# Функция для обработки текстовых сообщений и фотографий
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)

    # Обработка отзывов
    if user_state == 'write_review':
        review_text = update.message.text.strip() if update.message.text else None
        await handle_review_submission(update, context, review_text)
        return

    # Обработка переходов в главное меню
    if update.message.text.strip() == 'В начало🔙':
        await go_to_main_menu(update, context)
        return

    # Если сообщение пришло от администратора и он выбрал "Модерация"
    if user_id == ADMIN_ID and user_state == 'admin_menu':
        if update.message.text.strip() == 'Модерация':
            reviews = context.application.bot_data.get('reviews', [])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]

            if not pending_reviews:
                await send_message(update, context, "Нет отзывов для модерации.",
                                   MENU_TREE['admin_menu']['options'])
                context.user_data['state'] = 'admin_menu'
                return

            for i, review in enumerate(pending_reviews):
                review_text = (
                    f"Отзыв №{i + 1}:\n"
                    f"{review['review']}\n\n"
                    f"Автор: {review['user_name']} (ID: {review['user_id']})"
                )
                logger.info(f"Отображаем отзыв для модерации: {review_text}")

                buttons = [
                    [InlineKeyboardButton("Опубликовать✅", callback_data=f'publish_{i}'),
                     InlineKeyboardButton("Удалить🗑️", callback_data=f'delete_{i}')]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                await update.message.reply_text(review_text, reply_markup=reply_markup)

            context.user_data['state'] = 'moderation_menu'
            return

    # Обработка нажатия кнопки "Посмотреть Отзывы💬"
    if user_state == 'reviews_menu' and update.message.text.strip() == 'Посмотреть Отзывы💬':
        channel_url = "https://t.me/CleaningSphere"  # Замените на реальную ссылку на канал
        await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")

        reply_keyboard = [['В начало🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)

        context.user_data['state'] = 'main_menu'
        return

    # Обработка нажатия кнопки "Назад" при показе тарифов
    if user_state.startswith('detail_') and update.message.text.strip() == 'Назад':
        context.user_data['state'] = 'show_tariffs'
        await send_message(update, context, MENU_TREE['show_tariffs']['message'], MENU_TREE['show_tariffs']['options'])
        return

    # Обработка действий администратора
    if user_id == ADMIN_ID:
        if user_state == 'main_menu':
            context.user_data['state'] = 'admin_menu'
            menu = MENU_TREE['admin_menu']
            await send_message(update, context, menu['message'], menu['options'])
            return

        if user_state == 'admin_menu' and update.message.text.strip() == 'Модерация':
            reviews = context.application.bot_data.get('reviews', [])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]

            if not pending_reviews:
                await send_message(update, context, "Нет отзывов для модерации.",
                                   MENU_TREE['admin_menu']['options'])
                context.user_data['state'] = 'admin_menu'
                return

            for i, review in enumerate(pending_reviews):
                review_text = f"{i + 1}. {review['review']} - На рассмотрении"
                buttons = [
                    [InlineKeyboardButton("Опубликовать✅", callback_data=f'publish_{i}'),
                     InlineKeyboardButton("Удалить🗑️", callback_data=f'delete_{i}')]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                await update.message.reply_text(review_text, reply_markup=reply_markup)

            context.user_data['state'] = 'moderation_menu'
            return

    # Обработка модерации отзывов
    if user_state == 'moderation_menu':
        reviews = context.application.bot_data.get('reviews', [])
        pending_reviews = [review for review in reviews if not review.get('approved', False)]

        logger.info(f"Найдено {len(pending_reviews)} отзывов для модерации")

        if not pending_reviews:
            await send_message(update, context, "Нет отзывов для модерации.",
                               MENU_TREE['admin_menu']['options'])
            context.user_data['state'] = 'admin_menu'
            return

        for i, review in enumerate(pending_reviews):
            review_text = (
                f"{i + 1}. {review['review']} - {'Одобрено' if review.get('approved', False) else 'На рассмотрении'}\n"
                f"Автор: {review['user_name']} (ID: {review['user_id']})"
            )
            logger.info(f"Отображаем отзыв для модерации: {review_text}")

            if 'photo_file_ids' in review:
                logger.info(f"Отзыв содержит {len(review['photo_file_ids'])} фото")
                media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
                await context.bot.send_media_group(chat_id=ADMIN_ID, media=media_group)

            buttons = [
                [InlineKeyboardButton("Опубликовать✅", callback_data=f'publish_{i}'),
                 InlineKeyboardButton("Удалить🗑️", callback_data=f'delete_{i}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(review_text, reply_markup=reply_markup)

        context.user_data['state'] = 'moderation_menu'
        return

    # Обработка состояния "Отзывы💬"
    if user_state == 'reviews_menu':
        if update.message.text.strip() in MENU_TREE['reviews_menu']['next_state']:
            context.user_data['state'] = MENU_TREE['reviews_menu']['next_state'][update.message.text.strip()]
            next_menu = MENU_TREE.get(context.user_data['state'])
            await send_message(update, context, next_menu['message'], next_menu['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.",
                               MENU_TREE['reviews_menu']['options'])
        return

    # Если пользователь не администратор, обрабатываем обычные состояния
    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text.strip()

    # Переход в главное меню
    if user_choice == 'В начало🔙':
        await go_to_main_menu(update, context)
        return

    # Обработка выбора тарифа в Калькуляторе🧮
    if user_state == 'calculator_menu' and user_choice in CLEANING_PRICES:
        context.user_data['selected_tariff'] = user_choice
        if user_choice == 'Мытье окон🧴':
            context.user_data['state'] = 'enter_window_panels'
            await send_message(update, context, MENU_TREE['enter_window_panels']['message'],
                               MENU_TREE['enter_window_panels']['options'])
        else:
            context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, MENU_TREE['enter_square_meters']['message'],
                               MENU_TREE['enter_square_meters']['options'])
        return

    # Обработка выбора тарифа в меню "Тарифы🏷️"
    if user_state == 'show_tariffs' and user_choice in CLEANING_PRICES:
        details = CLEANING_DETAILS.get(user_choice)
        if details:
            try:
                with open(details['image_path'], 'rb') as image_file:
                    await update.message.reply_photo(photo=image_file)
            except FileNotFoundError:
                logger.error(f"Изображение не найдено: {details['image_path']}")
                await update.message.reply_text("Изображение для этого тарифа временно недоступно.")

            context.user_data['selected_tariff'] = user_choice
            context.user_data['state'] = f'detail_{user_choice}'

            for part in details['details_text']:
                await update.message.reply_text(part)

            await send_message(update, context, "Выберите дальнейшее действие:",
                               MENU_TREE[f'detail_{user_choice}']['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.",
                               MENU_TREE['show_tariffs']['options'])
        return

    # Обработка перехода в калькулятор внутри меню тарифа
    if user_state.startswith('detail_') and user_choice == 'Калькулятор🧮':
        tariff_name = user_state.split('_')[1]
        context.user_data['selected_tariff'] = tariff_name

        if tariff_name == 'Мытье окон🧴':
            context.user_data['state'] = 'enter_window_panels'
            await send_message(update, context, "Введите количество оконных створок:", ['В начало🔙'])
        else:
            context.user_data['price_per_sqm'] = CLEANING_PRICES[tariff_name]
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, MENU_TREE['enter_square_meters']['message'],
                               MENU_TREE['enter_square_meters']['options'])
        return

    # Обработка ввода квадратных метров или количества оконных створок
    if user_state == 'enter_square_meters':
        try:
            sqm = float(user_choice)
            price_per_sqm = context.user_data.get('price_per_sqm')
            if price_per_sqm is None:
                await send_message(update, context,
                                   'Произошла ошибка. Пожалуйста, вернитесь в главное меню и начните заново.',
                                   ['В начало🔙'])
                await go_to_main_menu(update, context)
                return

            result = calculate(price_per_sqm, sqm)
            await send_message(update, context, result['formatted_message'], MENU_TREE['calculate_result']['options'])
            context.user_data['state'] = 'calculate_result'  # Переход в состояние показа результата
        except ValueError:
            await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                               menu['options'])
        return

    # Обработка ввода количества оконных створок для тарифа "Мытье окон"
    if user_state == 'enter_window_panels':
        try:
            num_panels = int(user_choice)
            price_per_panel = CLEANING_PRICES['Мытье окон🧴']

            result = calculate_windows(price_per_panel, num_panels)

            await send_message(update, context, result['formatted_message'], MENU_TREE['calculate_result']['options'])
            context.user_data['state'] = 'calculate_result'  # Переход в состояние показа результата
        except ValueError:
            await send_message(update, context, 'Пожалуйста, введите корректное количество оконных створок.',
                               ['В начало🔙'])
        return

    # Обработка перехода в меню "Связаться📞"
    if user_state in ['main_menu', 'calculate_result'] and user_choice == 'Связаться📞':
        context.user_data['state'] = 'contact'

        buttons = [
            [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
            [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
            [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
        ]
        await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)

        reply_keyboard = [['В начало🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)
        return

    # Обработка выбора следующего состояния на основе выбора пользователя
    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        if next_state == 'enter_square_meters':
            context.user_data['selected_tariff'] = user_choice  # Запоминаем выбранный тариф
        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu.get('fallback', 'Пожалуйста, выберите опцию из меню.'), menu['options'])

# ID вашего канала
CHANNEL_ID = -1002249882445

#Функция для обработки отправки отзыва
async def handle_review_submission(update: Update, context: ContextTypes.DEFAULT_TYPE, review_text=None):
    if review_text:
        context.user_data['review_text'] = review_text

    if 'photo_file_ids' not in context.user_data and not context.user_data.get('review_text'):
        await update.message.reply_text("Пожалуйста, добавьте текст или фото к отзыву.")
        return

    # Сохраняем отзыв
    review_data = {
        'review': context.user_data.get('review_text', ''),
        'user_name': update.message.from_user.full_name,
        'user_id': update.message.from_user.id,
        'message_id': update.message.message_id,
        'approved': False,
        'photo_file_ids': context.user_data.get('photo_file_ids', [])
    }

    context.application.bot_data.setdefault('reviews', []).append(review_data)
    context.user_data.pop('photo_file_ids', None)
    context.user_data.pop('review_text', None)

    logger.info(f"Отзыв сохранен: {review_data['review']} от {review_data['user_name']} (ID: {review_data['user_id']})")
    await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.",
                       MENU_TREE['main_menu']['options'])
    await go_to_main_menu(update, context)

# Функция для публикации отзывов в канал
async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        # Отправляем текст отзыва в канал, если он есть
        if review.get('review'):
            await context.bot.send_message(chat_id=CHANNEL_ID, text=review['review'])

        # Отправляем фотографии отзыва в канал, если они есть
        photo_ids = review.get('photo_file_ids', [])
        if photo_ids:
            media_group = [InputMediaPhoto(photo_id) for photo_id in photo_ids]
            await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)

        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} успешно опубликован в канал.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")
        # Можно отправить сообщение администратору о неудачной публикации
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Не удалось опубликовать отзыв от {review['user_name']}. Ошибка: {e}")

# Обновленная функция для обработки нажатий на inline-кнопки
# Функция для обработки нажатий на inline-кнопки
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()

        user_state = context.user_data.get('state', 'main_menu')
        reviews = context.application.bot_data.get('reviews', [])

        if query.data == "show_phone_number":
            phone_number = "+7 (995) 612-45-81"  # Укажите нужный номер телефона
            await query.edit_message_text(text=f"Номер телефона: {phone_number}")
            return

        if query.data.startswith('publish_'):
            review_index = int(query.data.split('_')[1])
            await publish_review(context, reviews[review_index])
            await query.edit_message_text(text="Отзыв успешно опубликован.")
        elif query.data.startswith('delete_'):
            review_index = int(query.data.split('_')[1])
            reviews.pop(review_index)
            await query.edit_message_text(text="Отзыв удален.")
    except Exception as e:
        logger.error(f"Произошла ошибка в обработке нажатия кнопки: {e}")

# Пример функции для отправки сообщения с контактными кнопками
async def send_contact_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [InlineKeyboardButton("Связаться через WhatsApp", callback_data='contact_whatsapp')],
        [InlineKeyboardButton("Связаться через Telegram", callback_data='contact_telegram')],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("Выберите способ связи:", reply_markup=reply_markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        photo_file_id = update.message.photo[-1].file_id  # Получаем ID файла фото

        # Сохраняем ID файла фото в user_data
        if 'photo_file_ids' not in context.user_data:
            context.user_data['photo_file_ids'] = []
        context.user_data['photo_file_ids'].append(photo_file_id)

        logging.info(f"Получено фото от {user.first_name} (ID: {user.id}). File ID: {photo_file_id}")

        await update.message.reply_text("Фото получено! Пожалуйста, введите текст отзыва или подтвердите отправку.")
    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего отзыва. Попробуйте еще раз.")

def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm
    formatted_message = f'Стоимость вашей уборки: {total_cost:.2f} руб.'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }
# Функция для расчета стоимости мытья окон
def calculate_windows(price_per_panel, num_panels):
    total_cost = price_per_panel * num_panels
    formatted_message = f'Стоимость мытья окон: {total_cost:.2f} руб. за {num_panels} створок(и).'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        context.user_data['state'] = 'admin_menu'
        menu = MENU_TREE['admin_menu']
    else:
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']

    await send_message(update, context, menu['message'], menu['options'])


# Основная функция для запуска бота
def main():
    logger.info("Запуск бота")

    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'

    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавляем обработчик фотографий
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Добавляем обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_click))

    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()


if __name__ == '__main__':
    main()
