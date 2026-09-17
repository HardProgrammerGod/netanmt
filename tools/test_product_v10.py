"""Offline behavioral tests. No outbound requests."""
import sys, unittest
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.methods import SendMessage
from bot.retention import TIPS, reminder_message, send_reminder_batch

class DeliveryTests(unittest.IsolatedAsyncioTestCase):
    def batch(self,n=1):
        rows=[dict(id=str(uuid4()),user_id=i+1,tip_index=i,quiet=False) for i in range(n)]
        db=AsyncMock(); db.claim_reminders.return_value=rows; db.can_send_reminder.return_value=True
        return rows,db,AsyncMock()
    async def test_success(self):
        rows,db,bot=self.batch(); await send_reminder_batch(bot,db)
        bot.send_message.assert_awaited_once(); db.finish_reminder.assert_awaited_once_with(rows[0]['id'],'sent')
    async def test_optout_or_completion_after_claim(self):
        rows,db,bot=self.batch(); db.can_send_reminder.return_value=False
        await send_reminder_batch(bot,db); bot.send_message.assert_not_awaited()
        db.finish_reminder.assert_awaited_once_with(rows[0]['id'],'skipped')
    async def test_forbidden(self):
        rows,db,bot=self.batch(2)
        bot.send_message.side_effect=[TelegramForbiddenError(method=SendMessage(chat_id=1,text='x'),message='Forbidden'),None]
        await send_reminder_batch(bot,db); db.set_user_inactive.assert_awaited_once_with(1)
        self.assertEqual(bot.send_message.await_count,2)
    async def test_rate_limit(self):
        rows,db,bot=self.batch(2)
        bot.send_message.side_effect=TelegramRetryAfter(method=SendMessage(chat_id=1,text='x'),message='wait',retry_after=120)
        self.assertEqual(await send_reminder_batch(bot,db),120); bot.send_message.assert_awaited_once()
    async def test_ambiguous_timeout_no_retry(self):
        rows,db,bot=self.batch(); bot.send_message.side_effect=TimeoutError()
        with self.assertLogs('bot.retention',level='ERROR'): await send_reminder_batch(bot,db)
        bot.send_message.assert_awaited_once(); db.set_user_inactive.assert_not_awaited()
    async def test_db_write_failure_no_resend(self):
        rows,db,bot=self.batch(); db.finish_reminder.side_effect=ConnectionError()
        with self.assertRaises(ConnectionError): await send_reminder_batch(bot,db)
        bot.send_message.assert_awaited_once()
    def test_content_and_callbacks(self):
        self.assertEqual(len(TIPS),30); self.assertEqual(len(set(TIPS)),30)
        for i in range(61):
            text,kb=reminder_message(dict(id=str(uuid4()),tip_index=i,quiet=i>3))
            self.assertLess(len(text),1000)
            for row in kb.inline_keyboard:
                for b in row: self.assertLessEqual(len(b.callback_data.encode()),64)
            self.assertIn('reminder_off',str(kb))
if __name__=='__main__': unittest.main(verbosity=2)
