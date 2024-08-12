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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция start вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    # Основное меню
    keyboard = [
        ['Тарифы', 'Калькулятор'],
        ['Заказать клининг', 'Связаться']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    response_message = 'Привет!\nЯ Вера, твоя фея чистоты.\nМой робот-уборщик поможет:\n- рассчитать стоимость уборки\n- прислать клининг на дом\n- связаться со мной.'
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    logger.info("Отправлено сообщение: %s", response_message)


async def show_calculator_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция show_calculator_options вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    # Меню для выбора типа уборки с добавленной кнопкой "В начало"
    keyboard = [
        ['Ген.уборка', 'Повседневная'],
        ['Послестрой', 'Мытье окон'],
        ['В начало']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    response_message = 'Выберите тип уборки:'
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    logger.info("Отправлено сообщение: %s", response_message)


async def calculate_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция calculate_cost вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    user_choice = update.message.text
    if user_choice == 'В начало':
        logger.info("Пользователь вернулся в начало")
        await start(update, context)
    elif user_choice in CLEANING_PRICES:
        context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
        logger.info("Пользователь выбрал уборку: %s", user_choice)

        response_message = f'Вы выбрали {user_choice}. Введите количество квадратных метров:'
        await update.message.reply_text(response_message)
        logger.info("Отправлено сообщение: %s", response_message)
    else:
        try:
            logger.info("Попытка преобразования ввода в число")
            sqm = float(update.message.text)
            logger.info("Успешно преобразовано: %.2f кв.м", sqm)
            price_per_sqm = context.user_data.get('price_per_sqm')
            logger.info("Текущая цена за квадратный метр: %s", price_per_sqm)

            if price_per_sqm:
                total_cost = price_per_sqm * sqm
                logger.info("Рассчитанная стоимость: %.2f руб.", total_cost)
                # Формируем текст с результатом и кнопкой "В начало"
                keyboard = [['В начало']]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

                response_message = f'Стоимость уборки: {total_cost:.2f} руб.'
                await update.message.reply_text(response_message, reply_markup=reply_markup)

                logger.info("Рассчитана стоимость: %.2f руб. за %.2f кв.м", total_cost, sqm)
                logger.info("Отправлено сообщение: %s", response_message)
                # Очистка данных о цене, чтобы избежать ошибок при следующем вводе
                context.user_data['price_per_sqm'] = None
            else:
                response_message = 'Пожалуйста, выберите тип уборки.'
                await update.message.reply_text(response_message)
                logger.warning("Цена за квадратный метр не установлена.")
                logger.info("Отправлено сообщение: %s", response_message)
        except ValueError:
            response_message = 'Пожалуйста, введите корректное количество квадратных метров.'
            await update.message.reply_text(response_message)
            logger.error("Ошибка ввода: %s не является числом", update.message.text)
            logger.info("Отправлено сообщение: %s", response_message)


async def show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция show_tariffs вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    tariffs_text = "\n".join([f"{name}: {price} руб./кв.м" for name, price in CLEANING_PRICES.items()])
    keyboard = [['В начало']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    response_message = f'Вот наши тарифы:\n{tariffs_text}'
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    logger.info("Отправлено сообщение: %s", response_message)


async def order_cleaning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция order_cleaning вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    keyboard = [['В начало']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    response_message = 'Для заказа клининга свяжитесь с нами по телефону +7 (123) 456-78-90 или оставьте заявку на сайте.'
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    logger.info("Отправлено сообщение: %s", response_message)


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Функция contact вызвана пользователем %s", update.message.from_user.username)
    logger.info("Получено сообщение: %s", update.message.text)

    keyboard = [['В начало']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    response_message = 'Связаться с нами вы можете по телефону +7 (123) 456-78-90 или через email: clean@example.com.'
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    logger.info("Отправлено сообщение: %s", response_message)


def main():
    logger.info("Запуск бота")
    # Ваш токен
    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'

    # Создаем объект Application и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик нажатия кнопки "Калькулятор"
    application.add_handler(MessageHandler(filters.Text(['Калькулятор']), show_calculator_options))

    # Обработчик нажатия кнопки "Тарифы"
    application.add_handler(MessageHandler(filters.Text(['Тарифы']), show_tariffs))

    # Обработчик нажатия кнопки "Заказать клининг"
    application.add_handler(MessageHandler(filters.Text(['Заказать клининг']), order_cleaning))

    # Обработчик нажатия кнопки "Связаться"
    application.add_handler(MessageHandler(filters.Text(['Связаться']), contact))

    # Обработчик выбора типа уборки и ввода квадратных метров
    application.add_handler(MessageHandler(filters.Text(list(CLEANING_PRICES.keys())), calculate_cost))

    # Обработчик нажатия кнопки "В начало"
    application.add_handler(MessageHandler(filters.Text(['В начало']), start))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
