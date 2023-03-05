from typing import Any

import flet as ft

from todo_app.todo_app.models import TaskModel
from todo_app.todo_app.settings import TASKS_FILE


class TaskControl(ft.UserControl):
    def __init__(self, parent: ft.Control, task_model: TaskModel):
        super().__init__()
        self.parent: ft.Control = parent
        self.task_model: TaskModel = task_model

        self.display_task = ft.Checkbox(
            value=self.task_model.completed,
            label=self.task_model.name,
            on_change=self.status_changed,
        )
        self.display_view: ft.Row | None = None
        self.edit_text = ft.TextField(value=self.task_model.name, expand=1)
        self.edit_view: ft.Row | None = None

    def build(self) -> ft.Control | list[ft.Control]:
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.task_delete,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_text,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    def status_changed(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        self.task_model.completed = self.display_task.value
        self.parent.task_updated()

    def edit_clicked(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        self.edit_text.value = self.task_model.name

        if self.display_view is not None:
            self.display_view.visible = False

        if self.edit_view is not None:
            self.edit_view.visible = True

        self.update()

    def save_clicked(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        self.task_model.name = self.edit_text.value

        if self.display_view is not None:
            self.display_view.visible = True

        if self.edit_view is not None:
            self.edit_view.visible = False

        self.update()
        self.parent.update()

    def task_delete(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        self.parent.task_delete(self)


class TodoApp(ft.UserControl):
    def __init__(self, task_models_data: list[dict[Any, Any]]):
        super().__init__()

        task_models = [TaskModel(**task_model_data) for task_model_data in task_models_data]
        self.task_models = {task_model.task_id: task_model for task_model in task_models}
        self.filter = ft.Tabs(
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )
        self.new_task: ft.TextField | None = None
        self.tasks_view: ft.Column | None = None
        self.items_left = ft.Text("0 items left")

    def build(self) -> ft.Control | list[ft.Control]:
        self.new_task = ft.TextField(hint_text="Whats needs to be done?", expand=True)
        self.tasks_view = ft.Column()

        view = ft.Column(
            width=600,
            controls=[
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks_view,
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.items_left,
                        ft.OutlinedButton(text="Clear completed", on_click=self.clear_clicked),
                    ],
                ),
            ],
        )

        self.sync_task_list()
        return view

    def clear_clicked(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        completed_task_controls = list(
            filter(lambda task: task.task_model.completed, self.tasks_view.controls)  # type: ignore [arg-type, union-attr]  # noqa  # pylint: disable=line-too-long
        )

        for task_control in completed_task_controls:
            del self.task_models[task_control.task_model.task_id]

        self.save_tasks_to_file()
        self.update()

    def tabs_changed(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        self.update()

    def task_updated(self) -> None:
        self.save_tasks_to_file()
        self.update()

    def update(self) -> None:
        self.sync_task_list()
        super().update()

    def sync_task_list(self) -> None:
        # update/sync tasks list
        if self.tasks_view is not None:
            self.tasks_view.controls.clear()

            for task_model in self.task_models.values():
                task = TaskControl(parent=self, task_model=task_model)
                self.tasks_view.controls.append(task)

        status = self.filter.tabs[self.filter.selected_index].text
        count = 0

        for task_control in self.tasks_view.controls:
            task_control.visible = (
                status == "all"
                or (status == "active" and not task_control.task_model.completed)
                or (status == "completed" and task_control.task_model.completed)
            )

            if not task_control.task_model.completed:
                count += 1

        self.items_left.value = f"{count} active item(s) left"

    def add_clicked(
        self,
        event: ft.ControlEvent,  # pylint: disable=unused-argument
    ) -> None:
        if self.new_task is not None and self.new_task.value:
            task = TaskModel(
                name=self.new_task.value,
            )
            self.task_models[task.task_id] = task
            self.new_task.value = ""

            self.save_tasks_to_file()
            self.update()

    def save_tasks_to_file(self) -> None:
        with open(TASKS_FILE, mode="w", encoding="utf-8") as file:
            for task_model in self.task_models.values():
                file.write(task_model.json() + "\n")

    def task_delete(self, task_control: TaskControl) -> None:
        del self.task_models[task_control.task_model.task_id]

        if self.tasks_view is not None:
            self.tasks_view.controls.remove(task_control)

        self.save_tasks_to_file()
        self.update()
