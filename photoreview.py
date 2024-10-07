# -*- coding: utf-8 -*-

import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
# ID вашего канала
CHANNEL_ID = -1002249882445
# Укажите ваш Telegram ID
ADMIN_ID = 1238802718  # Замените на ваш реальный Telegram ID

# Цены на квадратный метр для каждого типа уборки
CLEANING_PRICES = {
    'Ген.Уборка🧼': 125,
    'Повседневная🧹': 75,
    'Послестрой🛠': 190,
    'Мытье окон🧴': 350
}

# Получаем путь к директории, где находится текущий файл
base_dir = os.path.dirname(os.path.abspath(__file__))

# Пути к изображениям и текст для каждого тарифа
CLEANING_DETAILS = {
    'Ген.Уборка🧼': {
        'image_path': os.path.join(base_dir, 'img', 'general.jpg'),
        'details_text': [
            'Стоимость по тарифу "Генеральная уборка" расчитывается по 125р. за кв.М',
            'Перечень услуг для генеральной уборки:\n\n1. Уборка полов:\n- Влажная уборка всех типов полов.\n- Глубокая очистка труднодоступных мест, включая углы и пространства под мебелью.\n\n2. Мойка зеркал:\n- Очистка зеркал и стеклянных поверхностей до блеска.\n- Удаление налета и загрязнений.\n\n3. Уборка кухни:\n- Очищение настенного фартука от следов готовки.\n- Чистка и дезинфекция кухонных поверхностей внутри гарнитура и снаружи.\n- Мытье и полировка кухонной техники (духовка, микроволновка, холодильник).',
            '4. Уборка ванной комнаты и туалета:\n- Мытье стен от известкового налета в санузлах.\n- Чистка и дезинфекция сантехники (унитаз, раковина, ванна, душ).\n- Удаление известкового налета и плесени.\n- Полировка смесителей и зеркал.\n\n5. Удаление пыли:\n- Протирание и очистка всех поверхностей от пыли (мебель, полки, техника).\n- Очистка плинтусов, карнизов, дверей и подоконников.\n- Уборка пыли с осветительных приборов и элементов декора.\n\n6. Обработка поверхностей антибактериальными средствами:\n- Обработка ручек дверей, выключателей и других часто трогаемых мест.',
            '7. Организация пространства:\n- Раскладка вещей и организация хранения.\n- Разбор и сортировка вещей, книг, одежды.\n\n8. Дополнительные услуги:\n- Мытье жалюзи.\n- Чистка и уход за комнатными растениями.'
        ]
    },
    'Повседневная🧹': {
        'image_path': os.path.join(base_dir, 'img', 'vacuumcat.png'),
        'details_text': [
            'Стоимость по тарифу "Повседневна уборка" расчитывается по 75р. за кв.М',
            'Перечень услуг для тарифа "Повседневная уборка":\n\n1. Легкая уборка полов:\n- Влажная уборка всех видов напольных покрытий.\n- Очистка труднодоступных мест, включая углы и пространства под мебелью.\n\n2. Протирка пыли:\n- Удаление пыли с открытых поверхностей мебели, подоконников, и техники.\n- Легкая очистка плинтусов и дверных ручек.',
            '3. Уборка кухни:\n- Протирка кухонных столешниц, стола и рабочих поверхностей.\n- Очистка варочной панели и внешней части кухонного гарнитура.\n\n4. Уборка ванной комнаты и туалета:\n- Чистка и дезинфекция сантехники (раковина, унитаз, душевая кабина).\n- Очистка зеркал и полок.\n\n5. Мойка зеркал и стеклянных поверхностей от отпечатков пальцев и загрязнений.\n\n6. Вынос мусора.',
            '7. Наведение порядка:\n- Организация вещей и устранение мелкого беспорядка.\n- Замена постельного белья по договоренности.'
        ]
    },
    'Послестрой🛠': {
        'image_path': os.path.join(base_dir, 'img', 'build.jpg'),
        'details_text': [
            'Стоимость по тарифу "Послестрой" расчитывается по 190р. за кв.М',
            'Перечень услуг для тарифа "Послестрой":\n\n1. Вынос строительного мусора:\n- Сбор и вынос не крупного строительного мусора.\n\n2. Мойка окон:\n- Тщательная мойка окон со всех сторон, включая рамы и подоконники.\n- Удаление следов строительных материалов, пыли и грязи.',
            '3. Обеспыливание поверхностей:\n- Влажная и сухая уборка стен, мебели, люстр, плинтусов, светильников и розеток для удаления строительной пыли.\n\n4. Мойка дверей и дверных рам:\n- Очистка дверей и рам от пыли, следов строительных материалов и загрязнений.\n- Протирка и полировка для восстановления чистоты и блеска.\n\n5. Мойка стен в санузлах:\n- Удаление затирки и следов строительных смесей с плитки в ванных комнатах и санузлах.',
            '6. Полировка зеркал и стеклянных поверхностей:\n- Удаление пятен, налета и загрязнений.\n- Натирание зеркал и всех стеклянных поверхностей до блеска.\n\n7. Очистка и полировка сантехники:\n- Удаление остатков строительных материалов, грязи и пятен.\n- Натирание и дезинфекция всех сантехнических приборов (унитазы, раковины, ванны).\n\n8. Мытье и дезинфекция полов:\n- Глубокая очистка полов от строительной пыли и грязи.\n- Дезинфекция напольных покрытий для полного устранения загрязнений.'
        ]
    },
    'Мытье окон🧴': {
        'image_path': os.path.join(base_dir, 'img', 'window.jpg'),
        'details_text': [
            'Стоимость по тарифу "Мытье окон" расчитывается по 350р. за створку',
            'Перечень услуг для мытья окон:\n\n- Мойка рам с двух сторон.\n- Очистка стекол от наклеек и следов клея.\n- Полировка стекол с двух сторон.\n-Мойка подоконников.\n- Обеспечение чистоты и порядка в помещении после завершения работы.'
        ]
    }
}

# Определение дерева меню
MENU_TREE = {
    'main_menu': {
        'message': 'Привет! Я Вера, твоя фея чистоты.\n\nМой робот-уборщик поможет:\n\n🔍Ознакомиться с моими '
                   'услугами\n\n🧮Рассчитать стоимость уборки\n\n🚗Заказать клининг на дом\n\n📞Связаться со мной.',
        'options': [
            ['Тарифы🏷️', 'Калькулятор🧮'],  # Первая строка
            ['Связаться📞', 'Отзывы💬'],  # Вторая строка
            ['Полезная информация📢']  # Третья строка
        ],
        'next_state': {
            'Тарифы🏷️': 'show_tariffs',
            'Калькулятор🧮': 'calculator_menu',
            'Связаться📞': 'contact',
            'Отзывы💬': 'reviews_menu',
            'Полезная информация📢': 'useful_info'  # Добавлено состояние useful_info
        }
    },
    'useful_info': {  # Новое состояние useful_info
        'message': 'Посетите наш канал для получения последних новостей, акций и розыгрышей!',
        'options': ['Главное меню🔙'],  # Кнопка для возврата в главное меню
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    },
    'admin_menu': {
        'message': 'Админ-панель:\nВыберите действие:',
        'options': ['Модерация'],
        'next_state': {
            'Модерация': 'moderation_menu',
        }
    },
    'moderation_menu': {
        'message': 'Вы всегда можете вернуться в админ меню :)',
        'options': ['Админ меню'],
        'next_state': {
            'Админ меню': 'admin_menu'
        }
    },
    'reviews_menu': {
        'message': 'Что вы хотите сделать?',
        'options': ['Написать отзыв', 'Посмотреть Отзывы💬', 'Главное меню🔙'],
        'next_state': {
            'Написать отзыв': 'write_review',
            'Посмотреть Отзывы💬': 'view_reviews',
            'Главное меню🔙': 'main_menu'
        }
    },
    'view_reviews': {
        'message': 'Просмотрите все отзывы на нашем канале:',
        'options': ['Перейти к каналу', 'Главное меню🔙'],
        'next_state': {
            'Перейти к каналу': 'open_channel',
            'Главное меню🔙': 'reviews_menu'
        }
    },
    'write_review': {
        'message': 'Пожалуйста, напишите ваш отзыв💬:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    },

    'show_tariffs': {
        'message': 'Выберите тариф для получения подробностей:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],
            ['Послестрой🛠', 'Мытье окон🧴'],
            ['Главное меню🔙']
        ],
        'next_state': {
            'Ген.Уборка🧼': 'detail_Ген.Уборка🧼',
            'Повседневная🧹': 'detail_Повседневная🧹',
            'Послестрой🛠': 'detail_Послестрой🛠',
            'Мытье окон🧴': 'detail_Мытье окон🧴',
            'Главное меню🔙': 'main_menu'
        }
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки🧺:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],
            ['Послестрой🛠', 'Мытье окон🧴'],
            ['Главное меню🔙']
        ],
        'next_state': {
            'Ген.Уборка🧼': 'enter_square_meters',
            'Повседневная🧹': 'enter_square_meters',
            'Послестрой🛠': 'enter_square_meters',
            'Мытье окон🧴': 'enter_square_meters',
            'Главное меню🔙': 'main_menu'
        }
    },
    'enter_square_meters': {
        'message': 'Введите количество квадратных метров,\nкоторые нужно убрать.',
        'options': ['Главное меню🔙'],
        'next_state': {
            'add_extras': 'add_extras'  # Переход к выбору дополнительных услуг
        }
    },
    'enter_window_panels': {
        'message': 'Введите количество оконных створок:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'calculate_result': 'calculate_result'
        }
    },
    'add_extras': {  # Новое состояние для добавления допуслуг
        'message': 'Выберите дополнительные услуги или завершите расчет:',
        'options': [
            ['Глажка белья', 'Стирка белья'],
            ['Почистить лоток', 'Уход за цветами'],
            ['Мытье окон(1 створка)🧴'],
            ['Связаться📞'],
            ['Главное меню🔙'],
        ],
        'next_state': {
            'Глажка белья': 'add_extras',
            'Стирка белья': 'add_extras',
            'Почистить лоток': 'add_extras',
            'Уход за цветами': 'add_extras',
            'Мытье окон🧴': 'add_extras',
            'Связаться📞': 'contact',  # Переход в состояние 'contact' для контактов
            'Главное меню🔙': 'main_menu'
        }
    },
    'extras_options': {  # Добавляем состояние для хранения кнопок допуслуг
        'options': [
            ['Глажка белья', 'Стирка белья'],
            ['Почистить лоток', 'Уход за цветами'],
            ['Мытье окон🧴(1 створка)'],
            ['Главное меню🔙', 'Связаться📞']
        ]
    },
    'calculate_result': {
        'options': ['Главное меню🔙', 'Связаться📞'],
        'next_state': {
            'Главное меню🔙': 'main_menu',
            'Связаться📞': 'contact'
        }
    },
    'contact': {
        'message': 'Связаться📞 со мной вы можете через следующие каналы:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    }
}

# Динамическое добавление состояний для каждого тарифа с кнопкой "Калькулятор🧮"
for tariff_name, details in CLEANING_DETAILS.items():
    MENU_TREE[f'detail_{tariff_name}'] = {
        'message': details['details_text'],
        'image_path': details['image_path'],
        'options': ['Калькулятор🧮', 'Назад'],
        'next_state': {
            'Калькулятор🧮': 'calculator_menu',
            'Назад': 'show_tariffs'
        }
    }


# Пример отправки сообщения с логированием
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


# Функция для отправки сообщения с inline-кнопками
async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info("Отправлено сообщение с кнопками: %s", message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)
    user_choice = update.message.text.strip()

    # Переход на состояние "Полезная информация📢"
    if user_choice == 'Полезная информация📢':
        context.user_data['state'] = 'useful_info'
        await show_useful_info(update, context)
        return

    if user_state == 'write_review':
        # Сохраняем ID текущего сообщения с текстом и медиа
        review_text = update.message.caption or update.message.text or ""
        message_id = update.message.message_id
        user_name = update.message.from_user.full_name

        if review_text == MENU_TREE['write_review']['options'][0]:
            await send_message(update, context, "Главное меню", MENU_TREE['main_menu']['options'])
            context.user_data['state'] = 'main_menu'
            return
        elif review_text == '':
            # Сохраняем отзыв как единое сообщение
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,  # Сохраняем полный message_id для пересылки целого сообщения
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            logger.info("Отправка сообщения с благодарностью пользователю.")

            # await update.message.reply_text("Спасибо за ваш отзыв! Он будет добавлен через некоторое время.")
            # await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.", MENU_TREE['write_review']['options'])
            context.user_data['state'] = 'write_review'
            return
        else:
            # Сохраняем отзыв как единое сообщение
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,  # Сохраняем полный message_id для пересылки целого сообщения
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            logger.info("Отправка сообщения с благодарностью пользователю.")

            # await update.message.reply_text("Спасибо за ваш отзыв! Он будет добавлен через некоторое время.")
            await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.",
                               MENU_TREE['write_review']['options'])
            context.user_data['state'] = 'write_review'
            return

    # Обработка нажатия кнопки "Посмотреть Отзывы💬"
    if user_state == 'reviews_menu' and update.message.text and update.message.text.strip() == 'Посмотреть Отзывы💬':
        channel_url = "https://t.me/CleaningSphere"  # Замените на реальную ссылку на канал
        await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")

        reply_keyboard = [['Главное меню🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)

        context.user_data['state'] = 'main_menu'
        return

    # Обработка нажатия кнопки "Назад" при показе тарифов
    if user_state.startswith('detail_') and update.message.text.strip() == 'Назад':
        context.user_data['state'] = 'show_tariffs'
        await send_message(update, context, MENU_TREE['show_tariffs']['message'], MENU_TREE['show_tariffs']['options'])
        return

    if user_id == ADMIN_ID:
        if user_state == 'main_menu':
            context.user_data['state'] = 'admin_menu'
            menu = MENU_TREE['admin_menu']
            await send_message(update, context, menu['message'], menu['options'])
            return

        if user_state == 'admin_menu':
            if update.message.text.strip() == 'Модерация':
                reviews = context.application.bot_data.get('reviews', [])
                pending_reviews = [review for review in reviews if not review.get('approved', False)]

                if not pending_reviews:
                    await send_message(update, context, "Нет отзывов для модерации.",
                                       MENU_TREE['admin_menu']['options'])
                    context.user_data['state'] = 'admin_menu'
                    return

        elif user_state == 'moderation_menu':
            if update.message.text.strip() == 'Админ меню':
                context.user_data['state'] = 'admin_menu'
                menu = MENU_TREE['admin_menu']
                await send_message(update, context, menu['message'], menu['options'])
                return

    # Обработка модерации отзывов
    if user_id == ADMIN_ID and user_state == 'admin_menu':
        if update.message.text.strip() == 'Модерация':
            await moderate_reviews(update, context, user_state)
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
    user_choice = update.message.text.strip() if update.message.text else None

    if user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
        await send_message(update, context, menu['message'], menu['options'])
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
            await send_message(update, context, "Введите количество оконных створок:", ['Главное меню🔙'])
        else:
            context.user_data['price_per_sqm'] = CLEANING_PRICES[tariff_name]
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, MENU_TREE['enter_square_meters']['message'],
                               MENU_TREE['enter_square_meters']['options'])
        return
    # Обработка ввода квадратных метров
    if user_state == 'enter_square_meters':
        try:
            # Пробуем преобразовать введенные данные в число с плавающей точкой
            sqm = float(user_choice)
            logger.info(f"Введенное количество квадратных метров: {sqm}")

            price_per_sqm = context.user_data.get('price_per_sqm')
            if price_per_sqm is None:
                await send_message(update, context,
                                   'Произошла ошибка. Пожалуйста, вернитесь в главное меню и начните заново.',
                                   ['Главное меню🔙'])
                context.user_data['state'] = 'main_menu'
                return

            # Считаем итоговую стоимость
            total_cost = price_per_sqm * sqm

            # Проверка минимальной стоимости
            if total_cost < 1500:
                total_cost = 1500
                result_message = (
                    f'Стоимость вашей уборки: 1500.00 руб.\n'
                    'Это минимальная стоимость заказа.'
                )
            else:
                result_message = f'Стоимость вашей уборки: {total_cost:.2f} руб. за {sqm:.2f} кв.м.'

            # Отправляем результат пользователю
            await send_message(update, context, result_message, MENU_TREE['calculate_result']['options'])

            # Сохраняем площадь и стоимость для дальнейшего использования
            context.user_data['square_meters'] = sqm
            context.user_data['total_cost'] = total_cost

            # Проверяем выбранный тариф и предлагаем допуслуги только для "Ген.Уборка🧼" и "Повседневная🧹"
            selected_tariff = context.user_data.get('selected_tariff')
            if selected_tariff in ['Ген.Уборка🧼', 'Повседневная🧹']:
                # Переходим к предложению дополнительных услуг, задаем кнопки с допуслугами
                extras_options = [
                    ['Глажка белья', 'Стирка белья'],
                    ['Почистить лоток', 'Уход за цветами'],
                    ['Мытье окон🧴(1 створка)'],
                    ['Главное меню🔙', 'Связаться📞']
                ]
                await send_message(update, context, "Хотите добавить дополнительные услуги?", extras_options)
                context.user_data['state'] = 'add_extras'
            else:
                # Если выбран тариф без допуслуг (например, "Мытье окон" или "Послестрой"), завершаем расчет
                await send_message(update, context,
                                   "Расчет завершен. Вы можете заказать услугу нажав кнопку 'Связаться📞' !",
                                   MENU_TREE['calculate_result']['options'])
                context.user_data['state'] = 'main_menu'

            # Логирование состояния после отправки сообщения
            logger.info(f"Состояние после отправки сообщения: {context.user_data['state']}")

            return  # Завершаем выполнение функции

        except ValueError:
            # Логируем некорректный ввод и возвращаем пользователя к повторному вводу
            logger.error(f"Некорректное количество квадратных метров: {user_choice}")
            await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                               MENU_TREE['enter_square_meters']['options'])

    # Обработка выбора дополнительных услуг
    if user_state == 'add_extras':
        if user_choice in ['Глажка белья', 'Стирка белья', 'Почистить лоток', 'Уход за цветами', 'Мытье окон🧴(1 створка)']:
            # Добавляем стоимость за выбранную допуслугу
            if user_choice == 'Глажка белья':
                context.user_data['total_cost'] += 300  # Например, 300 руб за глажку
            elif user_choice == 'Стирка белья':
                context.user_data['total_cost'] += 250  # Например, 250 руб за стирку
            elif user_choice == 'Почистить лоток':
                context.user_data['total_cost'] += 150  # Например, 150 руб за чистку лотка
            elif user_choice == 'Уход за цветами':
                context.user_data['total_cost'] += 200  # Например, 200 руб за уход за цветами
            elif user_choice == 'Мытье окон🧴(1 створка)':
                context.user_data['total_cost'] += 350  # Например, 350 руб за одну створку окна

            # Сохраняем выбранные дополнительные услуги в user_data
            context.user_data.setdefault('selected_extras', []).append(user_choice)

            # Логируем текущее состояние для отладки
            logger.info(f"Текущее состояние перед отправкой сообщения: {context.user_data['state']}")

            # Продолжаем выбор допуслуг, всегда показываем кнопку "Главное меню🔙"
            await send_message(update, context,
                               f"Услуга {user_choice} добавлена. Общая стоимость: {context.user_data['total_cost']} руб.\nВыберите еще услуги или свяжитесь с нами.",
                               [['Глажка белья', 'Стирка белья'],
                                ['Почистить лоток', 'Уход за цветами'],
                                ['Мытье окон🧴(1 створка)'],
                                ['Главное меню🔙', 'Связаться📞']])  # Кнопка "Главное меню🔙" всегда включена

            # Остаемся в состоянии add_extras, чтобы пользователь мог выбрать другие услуги
            # После выбора услуги
            context.user_data['state'] = 'add_extras'
            logger.info(f"Состояние изменено на: {context.user_data['state']}")

            # Завершаем выполнение функции, чтобы избежать лишних действий и смены состояния
            return


        # Если пользователь выбрал "Связаться📞", завершаем расчет и переходим к контактам
        elif user_choice == 'Связаться📞':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            # Отправляем итоговую стоимость с выбранными допуслугами
            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            # Отправляем сообщение с результатом
            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в состояние "Связаться"
            context.user_data['state'] = 'contact'
            buttons = [
                [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
                [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
                [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
            ]
            await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)

        # Если пользователь выбрал "В начало", то сбрасываем процесс и возвращаемся в главное меню
        elif user_choice == 'Главное меню🔙':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            # Отправляем сообщение с результатом
            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в главное меню
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

        # Сбрасываем список дополнительных услуг, когда расчет закончен
        context.user_data.pop('selected_extras', None)

    # Обработка ввода количества оконных створок для тарифа "мытье окон"
    if user_state == 'enter_window_panels':
        try:
            num_panels = int(user_choice)
            price_per_panel = CLEANING_PRICES['Мытье окон🧴']

            result = calculate_windows(price_per_panel, num_panels)

            await send_message(update, context, result['formatted_message'], MENU_TREE['calculate_result']['options'])
            context.user_data['state'] = 'main_menu'
        except ValueError:
            await send_message(update, context, 'Пожалуйста, введите корректное количество оконных створок.',
                               ['Главное меню🔙'])
        return

    # Обработка перехода в меню "Связаться📞"
    if user_state == 'main_menu' and user_choice == 'Связаться📞':
        context.user_data['state'] = 'contact'

        buttons = [
            [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
            [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
            [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
        ]
        await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)

        reply_keyboard = [['Главное меню🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)
        return

    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        if next_state == 'enter_square_meters':
            context.user_data['selected_tariff'] = user_choice  # Запоминаем выбранный тариф
        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu.get('fallback', 'Пожалуйста, выберите опцию из меню.'),
                           menu['options'])


async def moderate_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: str) -> None:
    # Получаем все отзывы, которые ещё не обработаны
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", MENU_TREE['admin_menu']['options'])
        context.user_data['state'] = 'admin_menu'
        return

    for review in pending_reviews:
        try:
            # Пересылаем сообщение целиком, используя сохраненный message_id
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=review['user_id'],
                message_id=review['message_id']  # Используем `message_id` для пересылки всего сообщения
            )

            buttons = [
                [InlineKeyboardButton(f"Опубликовать✅", callback_data=f'publish_{review["message_id"]}'),
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения: {e}")

    context.user_data['state'] = 'moderation_menu'


# Обновленная функция для обработки нажатий на inline-кнопки
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем текущее состояние пользователя
    user_state = context.user_data.get('state', 'main_menu')

    # Проверяем нажатие на кнопку с номером телефона
    if query.data == "show_phone_number":
        # Отправляем сообщение с номером телефона
        await query.message.reply_text("Ваш номер телефона: +79956124581")
        return

    # Если состояние пользователя в модерации
    if user_state == 'moderation_menu':
        # Ищем действие и message_id в callback_data
        action, message_id = query.data.split('_')
        pending_reviews = context.application.bot_data.get('reviews', [])
        review = next((r for r in pending_reviews if str(r['message_id']) == message_id), None)

        if review:
            if action == 'delete':
                # Отмечаем отзыв как удаленный
                review['deleted'] = True
                await query.edit_message_text(text="Отзыв безвозвратно удален.")
                context.application.bot_data['reviews'].remove(review)

            elif action == 'publish':
                # Отмечаем отзыв как опубликованный
                review['approved'] = True
                await publish_review(context, review)
                await query.edit_message_text(text="Отзыв успешно опубликован.")
                for r in context.application.bot_data['reviews']:
                    if r['user_id'] == review['user_id'] and r['message_id'] == review['message_id']:
                        r['approved'] = True

        # Проверка оставшихся отзывов для модерации
        remaining_reviews = [r for r in pending_reviews if not r.get('approved', False) and not r.get('deleted', False)]
        if not remaining_reviews:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Все отзывы обработаны.")
            context.user_data.pop('pending_reviews', None)
            context.user_data['state'] = 'admin_menu'
            return

        context.user_data['state'] = 'moderation_menu'


async def show_useful_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ссылка на ваш канал
    channel_url = "https://t.me/+7YI7c3pWXhQwMTcy"  # Замените на вашу реальную ссылку

    # Создаем Inline-кнопку с ссылкой на канал
    buttons = [[InlineKeyboardButton("Перейти в канал", url=channel_url)]]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Отправляем сообщение с Inline-кнопкой
    await update.message.reply_text(
        "Посетите наш канал для получения последних новостей, акций и розыгрышей!",
        reply_markup=reply_markup
    )


# Функция для публикации отзывов в канал
async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        if review['photo_file_ids']:
            if len(review['photo_file_ids']) > 1:
                media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
                await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
            else:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=review['photo_file_ids'][0])

        await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=review['user_id'],
            message_id=review['message_id']
        )

        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} успешно опубликован в канал.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"Не удалось опубликовать отзыв от {review['user_name']}. Ошибка: {e}")


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


# Функция для расчета стоимости мытья окон
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
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))

    # Добавляем обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_click))

    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()


if __name__ == '__main__':
    main()
