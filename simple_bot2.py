# -*- coding: utf-8 -*-
import uuid
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
CHANNEL_ID = -1002249882445  # Замените на ваш реальный CHANNEL_ID

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

def add_review(context, user_name, review_text, photo_file_ids):
    reviews = context.bot_data.get('reviews', [])
    review_id = str(uuid.uuid4())  # Генерация уникального идентификатора
    review = {
        'id': review_id,  # Присваиваем уникальный ID
        'user_name': user_name,
        'review': review_text,
        'photo_file_ids': photo_file_ids,
        'approved': False
    }
    reviews.append(review)
    context.bot_data['reviews'] = reviews

def extract_review_id(data: str) -> int:
    try:
        # Пример: извлечение ID отзыва из строки данных
        return int(data.split('_')[1])
    except (IndexError, ValueError) as e:
        logging.error(f"Ошибка при извлечении ID отзыва из строки '{data}': {e}")
        return None


def get_review_by_id(review_id: int, reviews: list) -> dict:
    # Поиск отзыва по ID в списке отзывов
    for review in reviews:
        if review.get('id') == review_id:
            return review
    return None

def mark_review_as_published(review_id: int, reviews: list) -> bool:
    for review in reviews:
        if review.get('id') == review_id:
            review['approved'] = True
            logger.debug(f"Отзыв с ID {review_id} помечен как опубликованный.")
            return True
    logger.debug(f"Не удалось пометить отзыв с ID {review_id} как опубликованный.")
    return False
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


# Универсальная функция для обработки отзывов
# Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id  # Добавьте эту строку
    user_state = context.user_data.get('state', 'main_menu')

    # Если состояние 'write_review', используем объединённую функцию для обработки отзывов
    if user_state == 'write_review':
        await handle_review(update, context)
        return

    # Обработка состояния 'admin_menu', когда администратор взаимодействует с меню
    elif user_id == ADMIN_ID and user_state == 'admin_menu':
        if update.message.text.strip() == 'Модерация':
            # Получаем все отзывы, которые еще не были одобрены
            reviews = context.application.bot_data.get('reviews', [])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]

            if not pending_reviews:
                # Если нет отзывов для модерации, отправляем сообщение и возвращаем в админ-меню
                await send_message(update, context, "Нет отзывов для модерации.", MENU_TREE['admin_menu']['options'])
                context.user_data['state'] = 'admin_menu'
                return

            # Перебираем и отображаем отзывы для модерации
            for i, review in enumerate(pending_reviews):
                review_text = (
                    f"Отзыв №{i + 1}:\n"
                    f"{review['review']}\n\n"
                    f"Автор: {review['user_name']} (ID: {review['user_id']})"
                )
                logger.info(f"Отображаем отзыв для модерации: {review_text}")

                # Создаем кнопки для публикации или удаления отзыва
                buttons = [
                    [InlineKeyboardButton("Опубликовать✅", callback_data=f'publish_{i}'),
                     InlineKeyboardButton("Удалить🗑️", callback_data=f'delete_{i}')]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                await update.message.reply_text(review_text, reply_markup=reply_markup)

            # Обновляем состояние на 'moderation_menu' после отображения отзывов
            context.user_data['state'] = 'moderation_menu'

    # Обработка любого другого состояния или неизвестной команды
    else:
        # Возвращаем пользователя в главное меню и сбрасываем состояние
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
        context.user_data['state'] = 'main_menu'


# Функция для публикации отзывов в канал
async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        if review.get('review'):
            await context.bot.send_message(chat_id=CHANNEL_ID, text=review['review'])

        if review.get('photo_file_ids'):
            media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
            await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)

        logger.info(f"Отзыв от {review['user_name']} успешно опубликован в канал.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")

# Обработчик нажатий на inline-кнопки
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()

        user_state = context.user_data.get('state', 'main_menu')
        reviews = context.application.bot_data.get('reviews', [])

        if query.data == "show_phone_number":
            phone_number = "+7 (995) 612-45-81"  # Укажите нужный номер телефона

            if query.message and query.message.chat_id:
                await query.edit_message_text(text=f"Номер телефона: {phone_number}")
            else:
                logger.error("Отсутствуют данные message или chat_id")
            return

        if user_state == 'moderation_menu' and query.data.startswith('publish_'):
            review_index = int(query.data.split('_')[1])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]
            if 0 <= review_index < len(pending_reviews):
                review = pending_reviews[review_index]
                review['approved'] = True  # Отмечаем отзыв как одобренный

                await publish_review(context, review)  # Публикуем отзыв через функцию publish_review
                await query.edit_message_text(text="Отзыв успешно опубликован.")

        elif query.data.startswith('delete_'):
            review_index = int(query.data.split('_')[1])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]
            if 0 <= review_index < len(pending_reviews):
                reviews.remove(pending_reviews[review_index])
                await query.edit_message_text(text="Отзыв безвозвратно удален.")

        pending_reviews = [review for review in reviews if not review.get('approved', False)]
        if not pending_reviews:
            if query.message:
                await context.bot.send_message(chat_id=query.message.chat_id, text="Все отзывы обработаны.")
                reply_keyboard = [['Админ меню']]
                reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
                await context.bot.send_message(chat_id=query.message.chat_id, text="Вернуться в админ меню:",
                                               reply_markup=reply_markup)
        else:
            for i, review in enumerate(pending_reviews):
                review_text = f"{i + 1}. {review['review']} - На рассмотрении"
                buttons = [
                    [InlineKeyboardButton("Опубликовать✅", callback_data=f'publish_{i}'),
                     InlineKeyboardButton("Удалить🗑️", callback_data=f'delete_{i}')]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                await context.bot.send_message(chat_id=query.message.chat_id, text=review_text,
                                               reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Произошла ошибка в обработке нажатия кнопки: {e}")


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    menu = MENU_TREE['admin_menu'] if user_id == ADMIN_ID else MENU_TREE['main_menu']
    context.user_data['state'] = 'admin_menu' if user_id == ADMIN_ID else 'main_menu'
    await send_message(update, context, menu['message'], menu['options'])
# Объединённая функция для обработки отзывов (текста и фотографий)
async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.message.from_user
        user_id = user.id
        user_name = user.full_name
        message_id = update.message.message_id

        # Если это фото, обрабатываем его
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            if 'photo_file_ids' not in context.user_data:
                context.user_data['photo_file_ids'] = []
            context.user_data['photo_file_ids'].append(photo_file_id)
            logger.info(f"Получено фото от {user_name} (ID: {user_id}). File ID: {photo_file_id}")

        # Если это текст, обрабатываем его
        review_text = update.message.text.strip() if update.message.text else ""

        # Если текст и/или фото переданы, сохраняем отзыв
        if review_text or 'photo_file_ids' in context.user_data:
            review_data = {
                'user_name': user_name,
                'user_id': user_id,
                'review': review_text,
                'message_id': message_id,
                'approved': False,
                'photo_file_ids': context.user_data.get('photo_file_ids', [])
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            context.user_data.pop('photo_file_ids', None)  # Очищаем временные данные о фото

            logger.info(f"Отзыв сохранен: {review_text} от {user_name} (ID: {user_id}, Message ID: {message_id}, Photos: {len(review_data['photo_file_ids'])})")

            await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.",
                               MENU_TREE['main_menu']['options'])
            context.user_data['state'] = 'main_menu'
            return

        # Если есть фото, но нет текста, продолжаем ожидать текст
        if 'photo_file_ids' in context.user_data:
            await update.message.reply_text("Фото получено. Пожалуйста, введите текст отзыва.")
            return

    except Exception as e:
        logging.error(f"Ошибка при обработке отзыва: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего отзыва. Попробуйте еще раз.")


# Основная функция для запуска бота
def main():
    logger.info("Запуск бота")

    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(CallbackQueryHandler(button_click))

    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
