from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_inline_kb_for_help() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Add Task', callback_data='add_task')
    kb.button(text='Remove Task', callback_data='remove_task')
    kb.button(text='Check Tasks', callback_data='check_tasks')
    kb.button(text='Done Task', callback_data='done_task')
    kb.adjust(1)
    return kb.as_markup()


async def get_inline_kb_for_start() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='help', callback_data='help')
    kb.adjust(1)
    return kb.as_markup()
