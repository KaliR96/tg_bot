# -*- coding: utf-8 -*-
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Цены на квадратный метр для каждого типа уборки
CLEANING_PRICES = {
    'Ген.уборка': 125,
    'Повседневная': 75,
    'Послестрой': 190,
    'Мытье окон': 100
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Основное меню
    keyboard = [
        ['Тарифы', 'Калькулятор'],
        ['Заказать клининг', 'Связаться']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        'Привет!\nЯ Вера, твоя фея чистоты.\nМой робот-уборщик поможет:\n- рассчитать стоимость уборки\n- прислать клининг на дом\n- связаться со мной.\n- Выберите нужное действие внизу.',
        reply_markup=reply_markup
    )

async def show_calculator_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Меню для выбора типа уборки
    keyboard = [
        ['Ген.уборка', 'Повседневная'],
        ['Послестрой', 'Мытье окон']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        'Выберите тип уборки:',
        reply_markup=reply_markup
    )

async def calculate_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_choice = update.message.text
    if user_choice in CLEANING_PRICES:
        context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
        await update.message.reply_text(f'Вы выбрали {user_choice}. Введите количество квадратных метров:')
    else:
        try:
            sqm = float(update.message.text)
            price_per_sqm = context.user_data.get('price_per_sqm')
            if price_per_sqm:
                total_cost = price_per_sqm * sqm
                await update.message.reply_text(f'Стоимость уборки: {total_cost:.2f} руб.')
                # Сброс значения после расчета
                context.user_data['price_per_sqm'] = None
            else:
                await update.message.reply_text('Пожалуйста, выберите тип уборки.')
        except ValueError:
            await update.message.reply_text('Пожалуйста, введите корректное количество квадратных метров.')

def main():
    # Ваш токен
    TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'
    
    # Создаем объект Application и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик нажатия кнопки "Калькулятор"
    application.add_handler(MessageHandler(filters.Text(['Калькулятор']), show_calculator_options))
    
    # Обработчик выбора типа уборки и ввода квадратных метров
    application.add_handler(MessageHandler(filters.Text(list(CLEANING_PRICES.keys())), calculate_cost))
    application.add_handler(MessageHandler(filters.TEXT, calculate_cost))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
