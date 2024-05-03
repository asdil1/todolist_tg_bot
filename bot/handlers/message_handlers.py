from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline_keyboards import get_inline_kb_for_start, get_inline_kb_for_help
from bot.utils.states import States
from bot.database.db_utils import get_task, get_task_status

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f'Добро пожаловать {message.from_user.full_name}', reply_markup=await get_inline_kb_for_start()
    )


@router.message(Command('help'))
async def show_commands(message: Message) -> None:
    await message.answer("Список доступных действий: ", reply_markup=await get_inline_kb_for_help())


@router.message(Command('add_task'))
async def add_task(message: Message, state: FSMContext) -> None:
    await state.set_state(States.task)
    await message.answer("Input task")


@router.message(Command('remove_task'))
async def remove_task(message: Message, state: FSMContext) -> None:
    await state.set_state(States.task_number_for_remove)
    await message.answer('Input task number')


@router.message(Command('check_tasks'))
async def check_tasks(message: Message) -> None:
    user_id = message.from_user.id
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
    await message.answer(msg)


@router.message(Command('done_task'))
async def done_task(message: Message, state: FSMContext) -> None:
    await state.set_state(States.task_number_for_done)
    await message.answer("Input task number")