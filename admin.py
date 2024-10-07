from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils import send_message

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
