import os
import sys
from typing import Any, Callable, Iterable, List

import cutie
from docx2pdf import convert as convert_to_pdf
from pdf2docx import Converter as ToDocxConverter
from PIL import Image

# COMPONENTS


def main_menu():
    menu_head()
    while True:
        select(
            on_render=lambda: None,
            buttons=[
                Button("Сменить рабочий каталог", lambda: change_dir()),
                Button("Преобразовать PDF в DOCX", lambda: pdf_to_docx()),
                Button("Преобразовать DOCX в PDF", lambda: docx_to_pdf()),
                Button("Произвести сжатие изображений", lambda: compress_images()),
                Button("Удалить группу файлов", lambda: rm_files_group()),
                Button("Выход", lambda: sys.exit()),
            ],
            print_selected_option=True,
        )


class Button:
    """
    Класс кнопки. (Пункт в списке, который возможно выбрать нажатием Enter)
    При нажатии на кнопку выполняется метод press, который вызывает функцию
    действия, которая была передана при создании объекта кнопки.
    """

    def __init__(self, name: str, action: Callable = lambda: None):
        self.set_name(name)
        self._action = action

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def press(self):
        self._action()


def validated_input(
    input_name: str,
    validators: Iterable[Callable[[str], None]] = [],
    on_successful_confirm: Callable = lambda: None,
) -> str:
    """
    Инпут с возможностью валидации.
    Отображает строку input_name и запрашивает ввод пользователя.
    Не возвращает введенное пользователем значение, пока каждый из
    валидаторов из списка validators не пройдет без ошибок.

    Args:
        input_name (str): Текст, отображаемый перед инпутом
        validators (Iterable[Callable[[str], None]]): Список функций-валидаторов вводимого значения
        on_sucessful_confirm (_type_, optional): Функция, выполняемая после успешного ввода. Defaults to lambda:None.

    Returns:
        str: Значение, которое ввел пользователь
    """
    while True:
        value = input(f"{input_name}: ")

        errors: list[str]
        errors = []
        for validator in validators:
            try:
                validator(value)
            except ValidationError as e:
                errors.append(str(e))

        if len(errors) > 0:
            [print(error) for error in errors]
        else:
            on_successful_confirm()
            return value


def select(
    buttons: list[Button] = [],
    non_selectable_buttons: list[Button] | None = None,
    on_render: Callable = lambda: os.system("cls||clear"),
    print_selected_option: bool = False,
) -> None:
    """
    Отображение списка из кнопок с возможностью отключить выбор кнопок, указав их
    в non_selectable_buttons.

    Args:
        buttons (list[Button]): Список кнопок для отображения
        non_selectable_buttons (list[Button] | None, optional): Кнопки, которые нельзя будет выбрать. Defaults to None.
    """
    on_render()
    button_names = [button.get_name() for button in buttons]
    if non_selectable_buttons is not None:
        non_selectable_button_names = [
            button.get_name() for button in non_selectable_buttons
        ]
        non_selectable_button_indices = [
            button_names.index(non_selectable_name)
            for non_selectable_name in non_selectable_button_names
        ]
        pressed_button_index = cutie.select(button_names, non_selectable_button_indices)
    else:
        pressed_button_index = cutie.select(button_names)
    if print_selected_option:
        print("Ваш выбор: ", button_names[pressed_button_index])
    buttons[pressed_button_index].press()


def menu_head() -> None:
    os.system("cls||clear")
    print(f"Текущий каталог: {os.getcwd()}")
    print()
    print("Выберите действие: ")
    print()


def confirmation_prompt(
    question: str,
    on_confirm: Callable = lambda: None,
    on_reject: Callable = lambda: None,
    confirm_text: str = "Да",
    reject_text: str = "Нет",
) -> Any:
    """
    Запрашивает у пользователя подтверждение действия, обозначенного в question.
    В зависимости от согласия или отказа пользователя возвращает значение функции
    из on_confirm или on_reject.

    Args:
        question (str): Описание действия для соглашения/отказа пользователя
        on_confirm (_type_, optional): Функция, выполняемая при согласии. Defaults to lambda:None.
        on_reject (_type_, optional): Функция, выполняемая при отклонении. Defaults to lambda:None.
        confirm_text (str, optional): Текст кнопки подтверждения. Defaults to "Да".
        reject_text (str, optional): Текст кнопки отклонения. Defaults to "Нет".

    Returns:
        Any: Значение функции из on_confirm или on_reject
    """
    if cutie.prompt_yes_or_no(
        question,
        yes_text=confirm_text,
        no_text=reject_text,
        char_prompt=False,
        default_is_yes=True,
    ):
        return on_confirm()
    else:
        return on_reject()


def file_list(exts: List[str] = []) -> List[str]:
    if len(exts) == 0:
        print(f"Список файлов в данном каталоге")
        print()
        return [f for f in os.listdir(os.getcwd()) if os.path.isfile(f)]
    print(
        f"Список файлов с расширением {'; '.join(exts) if len(exts)> 1 else exts[0]} в данном каталоге"
    )
    print()
    return files_in_cwd_with_exts(exts)


# END COMPONENTS


# ERRORS
class ValidationError(Exception):
    """
    Исключение, выбрасываемое при ошибке валидации
    """

    pass


# END ERRORS


# VALIDATORS
def not_empty(value: str) -> None:
    if len(value) == 0 or value.isspace():
        raise ValidationError("Значение не должно быть пустым.")


def list_len_validator(length: int = 3, sep: str = " ") -> Callable[[str], None]:
    def validate(value: str) -> None:
        if len(value.split(sep)) != length:
            raise ValidationError(
                f"Количество элементов должно равняться {length}. Сейчас {len(value.split(sep))}."
            )

    return validate


def list_elems_validator(
    sep: str = " ",
    elem_validators: Iterable[Callable[[str], None]] = [lambda _: None],
) -> Callable[[str], None]:
    def validate(value: str) -> None:
        errors: Iterable[str] = []
        for i, elem in enumerate(value.split(sep)):
            for validator in elem_validators:
                try:
                    validator(elem)
                except Exception as e:
                    errors.append(
                        f"Ошибка для элемента '{elem}' под номером {i}: {str(e)}"
                    )
        if len(errors):
            raise ValidationError("\n".join(errors))

    return validate


def only_digit_validator(value: str) -> None:
    is_num = True
    try:
        float(value)
    except ValueError:
        is_num = False

    if not is_num:
        raise ValidationError(f"Значение '{value}' не является числом.")


def is_path_valid(v: str):
    if not (os.path.exists(v) and os.path.isdir(v)):
        raise ValidationError(f"Путь {v} некорректен.")


# END VALIDATORS


# ACTIONS
def files_in_cwd_with_exts(exts: List[str]) -> List[str]:
    filelist = []
    for ext in exts:
        filelist.extend(
            [
                f
                for f in os.listdir(os.getcwd())
                if os.path.isfile(f)
                if f.endswith(f".{ext}")
            ]
        )
    return filelist


def pdf_to_docx():
    os.system("cls||clear")
    select(
        [
            Button(
                file,
                lambda: ToDocxConverter(file).convert(
                    "docx_" + file.replace(".pdf", ".docx")
                ),
            )
            for file in file_list(["pdf"])
        ]
        + [Button("Выход", lambda: main_menu())],
        on_render=lambda: None,
    )


def docx_to_pdf():
    os.system("cls||clear")
    select(
        [
            Button(
                file,
                lambda: convert_to_pdf(file, "pdf_" + file.replace(".docx", ".pdf")),
            )
            for file in file_list(["docx"])
        ]
        + [Button("Выход", lambda: main_menu())],
        on_render=lambda: None,
    )


def change_dir():
    os.chdir(
        confirmation_prompt(
            "Вы действительно хотите сменить путь",
            on_confirm=lambda: validated_input(
                "Введите путь",
                validators=[is_path_valid],
            ),
            on_reject=lambda: os.getcwd(),
        )
    )
    main_menu()


def get_compression_value_and_apply_to(files: List[str]):
    compression_input_name = "Введите параметры сжатия (от 0 до 100%)"
    compression_input_validators = [only_digit_validator, not_empty]
    compression_value = validated_input(
        compression_input_name, compression_input_validators
    )
    for file in files:
        Image.open(file).save(
            "compressed_" + file,
            quality=int(compression_value),
            optimize=True,
        )


def compress_images():
    os.system("cls||clear")
    compression_input_name = "Введите параметры сжатия (от 0 до 100%)"
    compression_input_validators = [only_digit_validator, not_empty]
    files = file_list(["jpeg", "jpg", "png", "gif"])
    select(
        [
            Button(
                file,
                lambda f=file: Image.open(f).save(
                    "compressed_" + f,
                    quality=int(
                        validated_input(
                            compression_input_name,
                            validators=compression_input_validators,
                        )
                    ),
                    optimize=True,
                ),
            )
            for file in files
        ]
        + [
            Button(
                "Сжать все файлы в каталоге",
                lambda: get_compression_value_and_apply_to(files),
            ),
            Button("Выход", lambda: main_menu()),
        ],
        on_render=lambda: None,
    )


def rm_files(files: List[str]) -> List[str]:
    removed = []
    for file in files:
        os.remove(file)
    return removed


def successfully_removed_message_for_file(filename: str):
    print(f'Файл: "{filename}" успешно удален!')


def rm_files_startswith(s: str, files: List[str]):
    for f in rm_files(list(filter(lambda f: f.startswith(s), files))):
        successfully_removed_message_for_file(f)


def rm_files_endswith(s: str, files: List[str]):
    for f in rm_files(list(filter(lambda f: f.endswith(s), files))):
        successfully_removed_message_for_file(f)


def rm_files_contains(s: str, files: List[str]):
    for f in rm_files(list(filter(lambda f: s in f, files))):
        successfully_removed_message_for_file(f)


def rm_files_by_extension(ext: str):
    for f in rm_files(files_in_cwd_with_exts(["ext"])):
        successfully_removed_message_for_file(f)


def rm_files_group():
    files = file_list()
    substr_input_title = "Введите подстроку"
    substr_input_validators = [not_empty]
    select(
        [
            Button(
                "Удалить все файлы начинающиеся на определенную подстроку",
                lambda: rm_files_startswith(
                    validated_input(
                        substr_input_title, validators=substr_input_validators
                    ),
                    files,
                ),
            ),
            Button(
                "Удалить все файлы заканчивающиеся на определенную подстроку",
                lambda: rm_files_endswith(
                    validated_input(
                        substr_input_title, validators=substr_input_validators
                    ),
                    files,
                ),
            ),
            Button(
                "Удалить все файлы содержащие определенную подстроку",
                lambda: rm_files_contains(
                    validated_input(
                        substr_input_title, validators=substr_input_validators
                    ),
                    files,
                ),
            ),
            Button(
                "Удалить все файлы по расширению",
                lambda: rm_files_by_extension(
                    validated_input(
                        "Введите расширение", validators=substr_input_validators
                    )
                ),
            ),
            Button("Выход", lambda: main_menu()),
        ]
    )


# END ACTIONS
