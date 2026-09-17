"""UI and result-handler tests, no network or real credentials."""
import os,sys,unittest
from pathlib import Path
from unittest.mock import AsyncMock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('BOT_TOKEN','12345:'+('a'*35))
os.environ.setdefault('SUPABASE_URL','https://example.supabase.co')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY','test-key')
os.environ.setdefault('WEBHOOK_BASE_URL','https://example.test')
with patch('supabase.create_client'):
    from bot.handlers import _send_session_result,_level_line,LearningDB
from bot.keyboards import get_daily_result_keyboard,get_practice_result_keyboard

class UI(unittest.IsolatedAsyncioTestCase):
    def test_conditional_invite_and_menu(self):
        for factory in [get_daily_result_keyboard,get_practice_result_keyboard]:
            for had_errors in [False,True]:
                for joined in [False,True,None]:
                    buttons=[b for row in factory(had_errors,joined).inline_keyboard for b in row]
                    callbacks=[b.callback_data for b in buttons]
                    self.assertEqual('leaderboard_on' in callbacks,joined is False)
                    self.assertEqual(callbacks[-1],'back_to_main')
                    self.assertEqual(buttons[-1].text,'🏠 Меню')
                    self.assertIn('start_practice:full:10',callbacks)
                    self.assertIn('start_practice:focus:5' if had_errors else 'start_practice:challenge:5',callbacks)
    def test_level_boundaries(self):
        for xp,level,remaining in [(0,1,100),(99,1,1),(100,2,100),(245,3,55)]:
            line=_level_line({'xp':xp})
            self.assertIn(f'<b>{level}</b>',line)
            self.assertIn(f'наступного: {remaining} XP',line)
    async def test_result_uses_persisted_membership(self):
        for kind in ['daily','practice']:
            for joined in [False,True]:
                msg=AsyncMock()
                s={'id':'test','user_id':4,'question_ids':[1,2,3,4],'correct_count':3,'session_type':kind}
                with patch.object(LearningDB,'get_session_insights',AsyncMock(return_value={})),patch.object(LearningDB,'get_session_xp',AsyncMock(return_value=5)),patch.object(LearningDB,'get_motivation',AsyncMock(return_value={'xp':245,'leaderboard_opt_in':joined})),patch.object(LearningDB,'get_streak',AsyncMock(return_value=1)):
                    await _send_session_result(msg,s)
                args=msg.answer.await_args
                self.assertIn('Ігровий рівень <b>3</b>',args.args[0])
                buttons=[b.callback_data for row in args.kwargs['reply_markup'].inline_keyboard for b in row]
                self.assertEqual('leaderboard_on' in buttons,not joined)
if __name__=='__main__': unittest.main(verbosity=2)
