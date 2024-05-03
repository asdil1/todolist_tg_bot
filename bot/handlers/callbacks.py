from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline_keyboards import get_inline_kb_for_help
from bot.utils.states import States
from bot.database.db_utils import add_task_to_db, remove_task_from_db, get_task, get_task_status, mark_task_done


router = Router(name=__name__)


@router.callback_query(F.data == 'help')
async def callback_help_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer('Список доступных действий', reply_markup=await get_inline_kb_for_help())


@router.callback_query(F.data == 'add_task')
async def callback_add_task(callback: CallbackQuery, state: FSMContext) -> None:

    await callback.answer()

    await state.set_state(States.task)
    await callback.message.answer("Input task")


@router.message(States.task)
async def callback_add_task_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task=message.text)
    await state.set_state(States.description)
    await message.answer("Input description of task")


@router.message(States.description)
async def callback_add_description_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer("Task and task description added")

    user_id = message.from_user.id
    data = await state.get_data()

    add_task_to_db(user_id, data['task'], data['description'])

    await state.clear()


@router.callback_query(F.data == 'check_tasks')
async def callback_check_tasks(callback: CallbackQuery) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    tasks = get_task(user_id)
    msg = "Your tasks:\n"
    for index, task in enumerate(tasks, start=1):
        task_id = task[2]
        task_status = get_task_status(task_id)
        if task_status[0] == "done":
            status_emoji = "✅"
        else:
            status_emoji = "❌"
        msg += f"\n{index}) {task[0]}\n" \
               f"Description:\n{task[1]}\n" \
               f"\nStatus:\n{task_status[0]}" \
               f"{status_emoji}\n"
    await callback.message.answer(msg)


@router.callback_query(F.data == 'remove_task')
async def callback_remove_task(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(States.task_number_for_remove)
    await callback.message.answer("Input task number")


@router.message(States.task_number_for_remove)
async def callback_remove_task_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task_num=message.text)

    user_id = message.from_user.id
    data = await state.get_data()

    if data['task_num'].isdigit():
        remove_task_from_db(user_id, data['task_num'])
        await message.answer("Task removed")
    else:
        await message.answer("Not correct number")
    await state.clear()

@router.callback_query(F.data == 'done_task')
async def callback_done_task(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(States.task_number_for_done)
    await callback.message.answer("Input task number")


@router.message(States.task_number_for_done)
async def callback_done_task_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task_num=message.text)

    user_id = message.from_user.id
    data = await state.get_data()

    if data['task_num'].isdigit():
        mark_task_done(user_id, data['task_num'])
        await message.answer("Task done")
    else:
        await message.answer("Not correct number")
    await state.clear()