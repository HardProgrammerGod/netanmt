"""Useful, rotating reminder content; no AI/network dependency."""
import asyncio
import logging
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)
TIPS = (
    ('Interested in', 'Кажемо <b>interested in</b>, а не interested on.', 'I’m interested in learning English.'),
    ('Since чи for?', '<b>Since</b> — точка початку; <b>for</b> — тривалість.', 'since Monday · for three days'),
    ('Advice без -s', '<b>Advice</b> — незлічуване. Одна порада: a piece of advice.', 'That’s useful advice.'),
    ('Enjoy + -ing', 'Після <b>enjoy</b> ставимо дієслово з -ing.', 'I enjoy reading.'),
    ('Say чи tell?', '<b>Tell</b> зазвичай потребує адресата; say — ні.', 'Tell me the story. · Say hello.'),
    ('Although', 'Після <b>although</b> потрібна частина речення з підметом і присудком.', 'Although it was late, we continued.'),
    ('Despite', 'Після <b>despite</b> — іменник або -ing, без of.', 'Despite the rain, we went out.'),
    ('Too та enough', '<b>Too</b> стоїть перед прикметником; enough — після.', 'too difficult · easy enough'),
    ('Make чи do?', 'Запам’ятовуй цілі сполучення, а не окреме дієслово.', 'make a decision · do homework'),
    ('Less чи fewer?', '<b>Fewer</b> — зі злічуваними в множині; less — з незлічуваними.', 'fewer mistakes · less time'),
    ('Look forward to', 'Тут <b>to</b> — прийменник. Після нього ставимо -ing.', 'I look forward to seeing you.'),
    ('Used to', '<b>Used to + дієслово</b> описує минулу звичку або стан.', 'I used to walk to school.'),
    ('Be used to', '<b>Be used to + -ing</b> означає «бути звиклим».', 'I’m used to getting up early.'),
    ('Borrow чи lend?', '<b>Borrow</b> — позичити в когось; lend — дати комусь.', 'Can I borrow your pen?'),
    ('Actual — пастка', '<b>Actual</b> — фактичний, справжній; current — поточний.', 'the actual cost · the current situation'),
    ('Eventually', '<b>Eventually</b> означає «зрештою», а не «можливо».', 'Eventually, we found the answer.'),
    ('Present Perfect', 'Для завершеної дії з конкретним минулим часом зазвичай потрібен Past Simple.', 'I saw her yesterday.'),
    ('Passive Voice', 'Базова формула: <b>be + третя форма дієслова</b>. Час змінює be.', 'The book was written in English.'),
    ('First Conditional', 'Для реальної майбутньої умови: <b>if + Present Simple</b>.', 'If it rains, we will stay home.'),
    ('Second Conditional', 'Для уявної ситуації: <b>if + Past Simple, would + дієслово</b>.', 'If I had more time, I would read more.'),
    ('Neither … nor', 'Ця пара поєднує два заперечені варіанти.', 'The room was neither large nor bright.'),
    ('Good at', 'Кажемо <b>good at + іменник або -ing</b>.', 'She is good at solving problems.'),
    ('Depend on', 'У сполученні <b>depend on</b> потрібен саме on.', 'It depends on the weather.'),
    ('Avoid + -ing', 'Після <b>avoid</b> використовуємо -ing.', 'Avoid making the same mistake.'),
    ('A few чи few?', '<b>A few</b> — кілька; few підкреслює, що їх мало.', 'I have a few ideas.'),
    ('A little чи little?', '<b>A little</b> — трохи; little підкреслює нестачу.', 'We have a little time left.'),
    ('Reading: доказ', 'Вибирай відповідь, яку підтверджує текст. Правдоподібність сама по собі — не доказ.', 'Знайди речення, яке підтримує твій варіант.'),
    ('Reading: перефразування', 'Правильна відповідь часто передає думку іншими словами.', 'not expensive → affordable'),
    ('Reading: займенники', 'У завданні з пропусками перевір, до чого відсилають it, they і this.', 'They має узгоджуватися з попереднім контекстом.'),
    ('Перевір контекст', 'Якщо два слова здаються правильними, прочитай речення до і після пропуску.', 'Шукай логіку, час і сталі сполучення.'),
)


def reminder_message(delivery):
    index = int(delivery.get('tip_index') or 0) % len(TIPS)
    title, rule, example = TIPS[index]
    invitation = ('Можна повернутися без поспіху: коротке заняття вже готове.'
                  if delivery.get('quiet') else 'Закріпимо англійську? Daily — 4 питання на сьогодні.')
    text = f'<b>💡 {title}</b>\n\n{rule}\n<i>{example}</i>\n\n{invitation}'
    if int(delivery.get('tip_index') or 0) == 0:
        text += '\n\nЦе автоматична підказка Neta. Час можна змінити, нагадування — вимкнути нижче.'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⚡ Почати / продовжити', callback_data=f"reminder_go:{delivery['id']}")],
        [InlineKeyboardButton(text='⚙️ Час', callback_data='show_settings'),
         InlineKeyboardButton(text='Без нагадувань', callback_data='reminder_off')],
    ])
    return text, keyboard


async def send_reminder_batch(bot, db):
    """Persisted claims prevent duplicate sends across concurrent workers/restarts.

    Delivery uncertainty favors a missed message over a duplicate. Telegram does
    not support an idempotency key for sendMessage. Do not retry ambiguous sends.
    """
    deliveries = await db.claim_reminders()
    for delivery in deliveries:
        user_id, delivery_id = int(delivery['user_id']), str(delivery['id'])
        try:
            if not await db.can_send_reminder(delivery_id):
                await db.finish_reminder(delivery_id, 'skipped')
                continue
            text, keyboard = reminder_message(delivery)
            await bot.send_message(user_id, text, reply_markup=keyboard)
        except TelegramForbiddenError:
            await db.finish_reminder(delivery_id, 'blocked')
            await db.set_user_inactive(user_id)
        except TelegramRetryAfter as exc:
            await db.finish_reminder(delivery_id, 'failed')
            # Stop the batch; unprocessed claims stay reserved today.
            return max(60, int(exc.retry_after))
        except Exception:
            logger.exception('Reminder send uncertain/failed for %s', user_id)
            await db.finish_reminder(delivery_id, 'failed')
        else:
            # If this write fails, keep the claim; NEVER resend the Telegram message.
            await db.finish_reminder(delivery_id, 'sent')
        await asyncio.sleep(0.08)
    return 60
