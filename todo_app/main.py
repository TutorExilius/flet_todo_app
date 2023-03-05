import json

import flet as ft

from todo_app.custom_controls import TodoApp
from todo_app.settings import TASKS_FILE


def main(page: ft.Page) -> None:
    with open(TASKS_FILE, mode="r", encoding="utf-8") as file:
        lines = [stripped_line for line in file if (stripped_line := line.strip())]
        task_models_data = [json.loads(line) for line in lines]

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    todo_app_1 = TodoApp(task_models_data=task_models_data)

    page.add(todo_app_1)


ft.app(target=main, view=ft.FLET_APP)
