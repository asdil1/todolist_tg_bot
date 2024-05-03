from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    task: State = State()
    description: State = State()
    task_number_for_remove: State = State()
    task_number_for_done: State = State()