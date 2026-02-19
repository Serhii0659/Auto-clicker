# pyright: reportUnknownMemberType=false
import ctypes
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

import customtkinter as ctk  # type: ignore
import win32api
import win32con
import win32event
import win32gui
import win32process
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController

# --- Мова ---
CurrentLanguage: Optional[str] = None

# --- Константи програми ---
APP_VERSION: str = "1.2"
APP_YEAR: str = "2025"

# --- Переклади ---
translations = {
    "UA": {
        "window_title": "AutoClicker Pro",
        "app_title": "Auto Clicker",
        "target_label": "Кнопка дії:",
        "trigger_label": "Кнопка активації:",
        "delay_label": "Затримка (мс):",
        "window_label": "Вікно (опційно):",
        "select_button": "Обрати кнопку",
        "not_selected": "Не обрано",
        "press_any_key": "Натисніть будь-яку кнопку...",
        "selected": "Обрано",
        "status_waiting": "СТАТУС: ОЧІКУВАННЯ",
        "status_running": "СТАТУС: ПРАЦЮЄ",
        "status_stopped": "СТАТУС: ЗУПИНЕНО",
        "status_window_waiting": "СТАТУС: ОЧІКУВАННЯ ВІКНА",
        "status_window_inactive": "СТАТУС: ВІКНО НЕ АКТИВНО",
        "status_window_closed": "СТАТУС: ВІКНО ЗАКРИТО",
        "status_window_error": "СТАТУС: ПОМИЛКА ВІКНА",
        "status_no_support": "СТАТУС: НЕМАЄ ПІДТРИМКИ ВІКОН",
        "author": "Автор: Serhii0659",
        "mouse_left": "ЛКМ",
        "mouse_right": "ПКМ",
        "mouse_middle": "СКМ",
        "error_pywin32": "pywin32 не встановлено. Оновлення списку вікон неможливе.",
        "error_process_access": "Помилка доступу до процесу",
        "error_class_access": "Помилка отримання класу",
        "error_window_processing": "Помилка обробки вікна",
        "error_window_refresh": "Помилка при оновленні списку вікон",
        "msg_hwnd_obtained": "HWND власного вікна",
        "msg_hwnd_failed": "Не вдалося отримати HWND власного вікна",
        "msg_window_closed": "Обране вікно більше не існує",
        "msg_window_check_error": "Помилка перевірки вікна",
        "msg_config_loaded": "Налаштування завантажено з",
        "msg_config_load_error": "Помилка завантаження налаштувань",
        "msg_config_saved": "Налаштування збережено у",
        "msg_config_save_error": "Помилка збереження налаштувань",
        "msg_key_restore_error": "Помилка відновлення кнопки",
        "msg_refresh_failed": "Не вдалося оновити список вікон або список порожній",
        "msg_windows_found": "Оновлено список вікон: знайдено",
        "msg_windows_word": "вікон",
        "msg_started_window": "Started - Очікування активації обраного вікна",
        "msg_started_any": "Started - Кліки працюють у будь-якому вікні",
        "msg_stopped": "Stopped",
        "msg_already_running": "Інший екземпляр програми вже відкритий",
        "msg_already_running_title": "Програма вже запущена",
        "config_file_content": """

" ═══════════════════════════════════════════════════════════════════════
"  				AutoClicker Pro - Configuration File
" ═══════════════════════════════════════════════════════════════════════
" 
"  Автор: Serhii0659
"  GitHub: {github_link}
"  Версія: {app_version}
"  Дата створення: {app_year}
"  Ліцензія: MIT License (https://opensource.org/licenses/MIT)
" 
"  ─────────────────────────────────────────────────────────────────────
"  💡 ПОРАДА ДНЯ: Не лізь куди не треба 😏
"  ─────────────────────────────────────────────────────────────────────
" 
"  Слава Україні!
" 
═══════════════════════════════════════════════════════════════════════
"""
    },
    "EN": {
        "window_title": "AutoClicker Pro",
        "app_title": "Auto Clicker",
        "target_label": "Action Button:",
        "trigger_label": "Activation Button:",
        "delay_label": "Delay (ms):",
        "window_label": "Window (optional):",
        "select_button": "Select Button",
        "not_selected": "Not Selected",
        "press_any_key": "Press any key...",
        "selected": "Selected",
        "status_waiting": "STATUS: WAITING",
        "status_running": "STATUS: RUNNING",
        "status_stopped": "STATUS: STOPPED",
        "status_window_waiting": "STATUS: WAITING FOR WINDOW",
        "status_window_inactive": "STATUS: WINDOW INACTIVE",
        "status_window_closed": "STATUS: WINDOW CLOSED",
        "status_window_error": "STATUS: WINDOW ERROR",
        "status_no_support": "STATUS: NO WINDOW SUPPORT",
        "author": "Author: Serhii0659",
        "mouse_left": "LMB",
        "mouse_right": "RMB",
        "mouse_middle": "MMB",
        "error_pywin32": "pywin32 not installed. Window list update unavailable.",
        "error_process_access": "Process access error",
        "error_class_access": "Class retrieval error",
        "error_window_processing": "Window processing error",
        "error_window_refresh": "Error updating window list",
        "msg_hwnd_obtained": "App window HWND",
        "msg_hwnd_failed": "Failed to obtain app window HWND",
        "msg_window_closed": "Selected window no longer exists",
        "msg_window_check_error": "Window check error",
        "msg_config_loaded": "Configuration loaded from",
        "msg_config_load_error": "Configuration load error",
        "msg_config_saved": "Configuration saved to",
        "msg_config_save_error": "Configuration save error",
        "msg_key_restore_error": "Key restore error",
        "msg_refresh_failed": "Failed to update window list or list is empty",
        "msg_windows_found": "Window list updated: found",
        "msg_windows_word": "windows",
        "msg_started_window": "Started - Waiting for selected window activation",
        "msg_started_any": "Started - Clicks work in any window",
        "msg_stopped": "Stopped",
        "msg_already_running": "Another instance of the program is already running",
        "msg_already_running_title": "Program Already Running",
        "config_file_content": """

" ═══════════════════════════════════════════════════════════════════════
"  				AutoClicker Pro - Configuration File
" ═══════════════════════════════════════════════════════════════════════
" 
"  Author: Serhii0659
"  GitHub: {github_link}
"  Version: {app_version}
"  Date Created: {app_year}
"  License: MIT License (https://opensource.org/licenses/MIT)
" 
═══════════════════════════════════════════════════════════════════════
"""
    }
}

def t(key: str) -> str:
    """Отримати переклад за ключем"""
    lang: str = CurrentLanguage if CurrentLanguage and CurrentLanguage in translations else "UA"
    return translations[lang].get(key, key)

# --- Налаштування інтерфейсу ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Константи ---
WINDOW_WIDTH: int = 400
WINDOW_HEIGHT: int = 600
DEFAULT_DELAY_MS: int = 100
DEFAULT_EMPTY_DELAY_MS: int = 1000
POPUP_MENU_WIDTH: int = 340
POPUP_ITEM_HEIGHT: int = 32
MAX_VISIBLE_POPUP_ITEMS: int = 10
MIN_VISIBLE_POPUP_ITEMS: int = 1
LISTENING_READY_DELAY_MS: int = 1
GLOBAL_CLICK_BIND_DELAY_MS: int = 100
GITHUB_LINK: str = "https://github.com/Serhii0659"

# VK коди клавіш
VK_A_TO_Z_START: int = 65
VK_A_TO_Z_END: int = 90
VK_0_TO_9_START: int = 48
VK_0_TO_9_END: int = 57
VK_NUMPAD_0_TO_9_START: int = 96
VK_NUMPAD_0_TO_9_END: int = 105
VK_NUMPAD_OPS_START: int = 106
VK_NUMPAD_OPS_END: int = 111

def resource_path(relative_path: str) -> Path:
    """ Отримує абсолютний шлях до ресурсу. Працює для dev-середовища і для PyInstaller. """
    try:
        base_path = Path(getattr(sys, '_MEIPASS'))
    except AttributeError:
        base_path = Path.cwd()

    return base_path / relative_path

class AutoClickerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # Оголошення атрибутів для Strict Pylance
        self.popup_frame: Optional[Union[ctk.CTkFrame, ctk.CTkScrollableFrame]] = None
        self._popup_clicked: bool = False

        # Налаштування вікна
        self.title(t("window_title"))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Центрування вікна на екрані
        self.update_idletasks()
        screen_width: int = self.winfo_screenwidth()
        screen_height: int = self.winfo_screenheight()
        x: int = (screen_width - WINDOW_WIDTH) // 2
        y: int = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Встановлення іконки програми
        icon_file = resource_path("icon.ico")
        if icon_file.exists():
            self.iconbitmap(str(icon_file))
        else:
            logging.warning("Іконку %s не знайдено", icon_file)

        # Контролери введення
        self.keyboard_controller: KeyboardController = KeyboardController()
        self.mouse_controller: MouseController = MouseController()

        # Дозволені клавіші (whitelist) - використовуємо набори для швидкої перевірки
        self.allowed_special_keys: Set[keyboard.Key] = {
            keyboard.Key.space,
            # Функціональні клавіші
            keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4,
            keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
            keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12,
            # Спеціальні клавіші
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
            keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
            keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
            keyboard.Key.tab, keyboard.Key.caps_lock, keyboard.Key.enter,
            keyboard.Key.backspace, keyboard.Key.delete, keyboard.Key.esc,
            keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up, keyboard.Key.page_down,
            keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right,
        }

        # Дозволені кнопки миші
        self.allowed_mouse_buttons: Set[Button] = {Button.left, Button.right, Button.middle}

        # Змінні стану
        self.target_key: Optional[Tuple[Any, bool]] = None  # Кнопка 1 (Дія)
        self.trigger_key: Optional[Tuple[Any, bool]] = None  # Кнопка 2 (Тригер)
        self.is_running: bool = False
        self.listening_mode: Optional[str] = None  # 'target' або 'trigger'
        self.listening_ready: bool = False  # Чи готовий режим прослуховування (для захисту від першого кліку)
        self.delay_ms: int = DEFAULT_DELAY_MS
        self.selected_window_hwnd: Optional[int] = None  # HWND обраного вікна
        self.window_list: List[Tuple[int, str]] = []  # Список вікон
        self.last_window_status: Optional[str] = None  # Останній статус вікна для відображення
        self.app_hwnd: Optional[int] = None  # HWND власного вікна програми

        # Лістенери (слухачі)
        self.kb_listener: Optional[keyboard.Listener] = None
        self.mouse_listener: Optional[mouse.Listener] = None

        # Потік для клікера
        self.clicker_thread: threading.Thread = threading.Thread(target=self.clicker_logic, daemon=True)
        self.clicker_thread.start()

        # Глобальний слухач для тригера
        self.start_global_listeners()

        # Створення UI віджетів
        self.create_widgets()

        # Завантажуємо налаштування ПІСЛЯ створення віджетів
        self.load_config()

        # Зберігаємо налаштування при закритті
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_config_path(self) -> Path:
        """Отримати шлях до файлу конфігурації у AppData"""
        # Зберігаємо у %APPDATA%\AutoClickerPro\config.json
        appdata: Optional[str] = os.getenv('APPDATA')
        if not appdata:
            # Fallback для систем без APPDATA
            appdata = str(Path.home() / 'AppData' / 'Roaming')

        config_dir: Path = Path(appdata) / 'AutoClickerPro'
        config_dir.mkdir(parents=True, exist_ok=True)  # Створюємо папку якщо не існує
        return config_dir / 'config.json'

    def load_config(self) -> None:
        """Завантажити налаштування з файлу"""
        global CurrentLanguage
        try:
            config_path: Path = self.get_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content: str = f.read()

                    # Видаляємо секцію після закриваючої дужки JSON
                    # Шукаємо останню закриваючу дужку JSON
                    last_brace: int = content.rfind('}')
                    if last_brace != -1:
                        json_content: str = content[:last_brace + 1].strip()
                    else:
                        json_content = content.strip()

                    config: Dict[str, Any] = json.loads(json_content)

                # Відновлюємо затримку
                if 'delay' in config:
                    self.entry_delay.delete(0, "end")
                    self.entry_delay.insert(0, str(config['delay']))

                # Відновлюємо мову
                if 'language' in config:
                    CurrentLanguage = str(config['language'])
                    self.language_var.set(CurrentLanguage)
                    self.update_ui_language()
                else:
                    CurrentLanguage = "UA"  # За замовчуванням українська
                    self.language_var.set(CurrentLanguage)

                # Відновлюємо кнопку дії
                if 'target_key' in config:
                    key_data: Optional[Dict[str, Any]] = config['target_key']
                    self.target_key = self._deserialize_key(key_data)
                    if self.target_key:
                        display_name: str = self.get_key_display_name(self.target_key[0])
                        self.lbl_target_val.configure(text=f"{t('selected')}: {display_name}", text_color="green")

                # Відновлюємо кнопку тригера
                if 'trigger_key' in config:
                    key_data = config['trigger_key']
                    self.trigger_key = self._deserialize_key(key_data)
                    if self.trigger_key:
                        display_name = self.get_key_display_name(self.trigger_key[0])
                        self.lbl_trigger_val.configure(text=f"{t('selected')}: {display_name}", text_color="green")

                print(f"{t('msg_config_loaded')} {config_path}")
            else:
                # Файл конфігурації не існує - перший запуск
                # Встановлюємо UA за замовчуванням
                CurrentLanguage = "UA"
                self.language_var.set(CurrentLanguage)
                print("Перший запуск - мова встановлена на UA за замовчуванням")
        except Exception as e:
            print(f"{t('msg_config_load_error')}: {e}")
            # У випадку помилки також встановлюємо UA за замовчуванням
            CurrentLanguage = "UA"
            self.language_var.set(CurrentLanguage)
            self.language_menu.set(CurrentLanguage)

    def save_config(self) -> None:
        """Зберегти налаштування у файл"""
        try:
            config: Dict[str, Any] = {
                'language': CurrentLanguage,
                'delay': self.entry_delay.get(),
                'target_key': self._serialize_key(self.target_key) if self.target_key else None,
                'trigger_key': self._serialize_key(self.trigger_key) if self.trigger_key else None
            }

            config_path: Path = self.get_config_path()

            # Формуємо JSON з відступами
            json_str: str = json.dumps(config, indent=2, ensure_ascii=False)

            # Додаємо секцію для інформації про автора
            info_section: str = t("config_file_content").format(
                github_link=GITHUB_LINK,
                app_version=APP_VERSION,
                app_year=APP_YEAR
            )

            final_content: str = json_str + info_section

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            print(f"{t('msg_config_saved')} {config_path}")
        except Exception as e:
            print(f"{t('msg_config_save_error')}: {e}")

    def _serialize_key(self, key_tuple: Optional[Tuple[Any, bool]]) -> Optional[Dict[str, Any]]:
        """Перетворити кнопку у JSON-сумісний формат"""
        if not key_tuple:
            return None

        key, is_mouse = key_tuple

        # Для миші
        if is_mouse:
            if key == Button.left:
                return {'type': 'mouse', 'button': 'left'}
            elif key == Button.right:
                return {'type': 'mouse', 'button': 'right'}
            elif key == Button.middle:
                return {'type': 'mouse', 'button': 'middle'}

        # Для клавіатури
        else:
            # Спеціальні клавіші
            if hasattr(key, 'name'):
                return {'type': 'keyboard', 'name': key.name}

            # KeyCode (літери, цифри, numpad)
            if hasattr(key, 'vk'):
                return {'type': 'keyboard', 'vk': key.vk}

            # Fallback для char
            if hasattr(key, 'char') and key.char:
                return {'type': 'keyboard', 'char': key.char}

        return None

    def _deserialize_key(self, key_data: Optional[Dict[str, Any]]) -> Optional[Tuple[Any, bool]]:
        """Відновити кнопку з JSON формату"""
        if not key_data:
            return None

        try:
            # Миша
            if key_data['type'] == 'mouse':
                button_map: Dict[str, Button] = {
                    'left': Button.left,
                    'right': Button.right,
                    'middle': Button.middle
                }
                button: Optional[Button] = button_map.get(key_data['button'])
                if button:
                    return (button, True)

            # Клавіатура
            elif key_data['type'] == 'keyboard':
                # Спеціальні клавіші
                if 'name' in key_data:
                    try:
                        key_val = getattr(keyboard.Key, key_data['name'])
                        return (key_val, False)
                    except AttributeError:
                        pass

                # KeyCode (VK коди)
                if 'vk' in key_data:
                    from pynput.keyboard import KeyCode
                    key_val = KeyCode.from_vk(key_data['vk'])
                    return (key_val, False)

                # Char (літери)
                if 'char' in key_data:
                    from pynput.keyboard import KeyCode
                    key_val = KeyCode.from_char(key_data['char'])
                    return (key_val, False)

        except Exception as e:
            print(f"{t('msg_key_restore_error')}: {e}")

        return None

    def on_closing(self) -> None:
        """Обробник закриття вікна"""
        self.save_config()
        self.destroy()

    def get_app_hwnd(self) -> None:
        """Отримати HWND власного вікна програми"""

        try:
            # Отримуємо HWND через tkinter
            self.app_hwnd = int(self.wm_frame(), 16)
            print(f"{t('msg_hwnd_obtained')}: {self.app_hwnd}")
        except Exception as e:
            print(f"{t('msg_hwnd_failed')}: {e}")
            self.app_hwnd = None

    def open_github(self) -> None:
        """Відкрити GitHub профіль у браузері"""
        import webbrowser
        webbrowser.open(GITHUB_LINK)

    def change_language(self, value: str) -> None:
        """Змінити мову інтерфейсу"""
        global CurrentLanguage
        CurrentLanguage = value
        self.update_ui_language()

    def update_ui_language(self) -> None:
        """Оновити всі текстові елементи UI після зміни мови"""
        # Оновлюємо заголовок вікна
        self.title(t("window_title"))

        # Оновлюємо заголовок додатку
        self.label_title.configure(text=t("app_title"))

        # Оновлюємо лейбли секцій
        self.lbl_target.configure(text=t("target_label"))
        self.lbl_trigger.configure(text=t("trigger_label"))
        self.lbl_delay.configure(text=t("delay_label"))
        self.lbl_window.configure(text=t("window_label"))

        # Оновлюємо кнопки
        self.btn_set_target.configure(text=t("select_button"))
        self.btn_set_trigger.configure(text=t("select_button"))

        # Оновлюємо статус якщо він не в процесі прослуховування
        if not self.listening_mode:
            if not self.is_running:
                self.lbl_status.configure(text=t("status_waiting"))
            elif self.selected_window_hwnd:
                if self.last_window_status:
                    # Залишаємо поточний статус вікна
                    pass
                else:
                    self.lbl_status.configure(text=t("status_window_waiting"))
            else:
                self.lbl_status.configure(text=t("status_running"))

        # Оновлюємо автора
        self.lbl_author.configure(text=t("author"))

        # Оновлюємо кнопку вибору вікна якщо вибрано "Не обрано"
        if self.selected_window_hwnd is None:
            self.selected_window_name = t("not_selected")
            self.window_select_btn.configure(text=self.selected_window_name)

        # Оновлюємо значення обраних кнопок якщо вони є
        if self.target_key and not self.listening_mode:
            display_name: str = self.get_key_display_name(self.target_key[0])
            self.lbl_target_val.configure(text=f"{t('selected')}: {display_name}")
        elif not self.listening_mode:
            self.lbl_target_val.configure(text=t("not_selected"))

        if self.trigger_key and not self.listening_mode:
            display_name = self.get_key_display_name(self.trigger_key[0])
            self.lbl_trigger_val.configure(text=f"{t('selected')}: {display_name}")
        elif not self.listening_mode:
            self.lbl_trigger_val.configure(text=t("not_selected"))

    def show_error(self, error_text: str) -> None:
        """Показати повідомлення про помилку"""
        self.lbl_error.configure(text=error_text)
        self.lbl_error.pack(pady=5)

    def hide_error(self) -> None:
        """Приховати повідомлення про помилку"""
        self.lbl_error.pack_forget()

    def create_widgets(self) -> None:
        # Заголовок
        self.label_title = ctk.CTkLabel(self, text=t("app_title"), font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=10)

        # Секція Кнопки 1 (Дія)
        self.frame_1 = ctk.CTkFrame(self)
        self.frame_1.pack(pady=8, padx=20, fill="x")

        self.lbl_target = ctk.CTkLabel(self.frame_1, text=t("target_label"))
        self.lbl_target.pack(pady=3)
        def make_click_handler(button: Any, mode: str):
            def handler(e: Any) -> Optional[str]:
                return self.on_button_mouse_click(e, button, mode)
            return handler

        def handle_target_binding() -> None:
            self.start_binding('target')

        self.btn_set_target = ctk.CTkButton(self.frame_1, text=t("select_button"),
                                            command=handle_target_binding)
        self.btn_set_target.pack(pady=3)
        
        # Використовуємо генератор замість lambda
        self.btn_set_target.bind("<Button-1>", make_click_handler(Button.left, 'target'))
        self.btn_set_target.bind("<Button-2>", make_click_handler(Button.middle, 'target'))
        self.btn_set_target.bind("<Button-3>", make_click_handler(Button.right, 'target'))

        self.lbl_target_val = ctk.CTkLabel(self.frame_1, text=t("not_selected"), text_color="gray")
        self.lbl_target_val.pack(pady=3)

        # Секція Кнопки 2 (Тригер)
        self.frame_2 = ctk.CTkFrame(self)
        self.frame_2.pack(pady=8, padx=20, fill="x")

        self.lbl_trigger = ctk.CTkLabel(self.frame_2, text=t("trigger_label"))
        self.lbl_trigger.pack(pady=3)

        def handle_trigger_binding() -> None:
            self.start_binding('trigger')

        self.btn_set_trigger = ctk.CTkButton(self.frame_2, text=t("select_button"),
                                                command=handle_trigger_binding)
        self.btn_set_trigger.pack(pady=3)
        
        # Використовуємо генератор замість lambda
        self.btn_set_trigger.bind("<Button-1>", make_click_handler(Button.left, 'trigger'))
        self.btn_set_trigger.bind("<Button-2>", make_click_handler(Button.middle, 'trigger'))
        self.btn_set_trigger.bind("<Button-3>", make_click_handler(Button.right, 'trigger'))

        self.lbl_trigger_val = ctk.CTkLabel(self.frame_2, text=t("not_selected"), text_color="gray")
        self.lbl_trigger_val.pack(pady=3)

        # Секція затримки
        self.frame_3 = ctk.CTkFrame(self)
        self.frame_3.pack(pady=8, padx=20, fill="x")

        self.lbl_delay = ctk.CTkLabel(self.frame_3, text=t("delay_label"))
        self.lbl_delay.pack(pady=3)

        # Валідація введення (тільки цифри)
        vcmd: Tuple[str, str] = (self.register(self.validate_digit), '%P')
        self.entry_delay = ctk.CTkEntry(self.frame_3, placeholder_text=str(DEFAULT_DELAY_MS),
                                        validate="key", validatecommand=vcmd)
        self.entry_delay.pack(pady=3)
        self.entry_delay.insert(0, str(DEFAULT_DELAY_MS))
        self.entry_delay.bind("<FocusOut>", self.on_delay_focus_out)

        # Секція вибору вікна
        self.frame_4 = ctk.CTkFrame(self)
        self.frame_4.pack(pady=8, padx=20, fill="x")

        self.lbl_window = ctk.CTkLabel(self.frame_4, text=t("window_label"))
        self.lbl_window.pack(pady=3)

        # Кастомна кнопка для вибору вікна
        self.selected_window_name: str = t("not_selected")
        self.window_select_btn = ctk.CTkButton(
            self.frame_4,
            text=self.selected_window_name,
            command=self.open_window_menu,
            width=POPUP_MENU_WIDTH,
            anchor="w"
        )
        self.window_select_btn.pack(pady=3)

        # Popup меню для вибору вікна (створюється динамічно)
        self.window_popup: Optional[ctk.CTkToplevel] = None

        # Статус
        self.lbl_status = ctk.CTkLabel(self, text=t("status_waiting"), font=("Roboto", 16, "bold"), text_color="red")
        self.lbl_status.pack(pady=10)

        # Помилки (показується тільки коли є помилка)
        self.lbl_error = ctk.CTkLabel(self, text="", font=("Roboto", 10), text_color="#FF6B6B", wraplength=360)
        self.lbl_error.pack(pady=0)
        self.lbl_error.pack_forget()  

        # Вибір мови
        self.frame_language = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_language.pack(pady=5)

        self.lbl_language = ctk.CTkLabel(self.frame_language, text="Language:", font=("Roboto", 10))
        self.lbl_language.pack(side="left", padx=(0, 5))

        self.language_var = ctk.StringVar(value=CurrentLanguage)
        self.language_menu = ctk.CTkSegmentedButton(
            self.frame_language,
            values=["UA", "EN"],
            variable=self.language_var,
            command=self.change_language,
            width=100,
            height=24
        )
        self.language_menu.pack(side="left")

        # Автор
        self.lbl_author = ctk.CTkLabel(self, text=t("author"), font=("Arial", 11),
                                        text_color="#4A9EFF", cursor="hand2")
        self.lbl_author.pack(pady=(5, 10))
        
        def handle_github_open(e: Any) -> None:
            self.open_github()
            
        self.lbl_author.bind("<Button-1>", handle_github_open)

        # Отримуємо HWND власного вікна після створення UI
        def deferred_get_hwnd() -> None:
            self.get_app_hwnd()
            
        self.after(100, deferred_get_hwnd)

        # Прив'язка кліків до елементів для зняття фокусу з entry_delay
        self.label_title.bind("<Button-1>", self.on_window_click)
        self.frame_1.bind("<Button-1>", self.on_window_click)
        self.frame_2.bind("<Button-1>", self.on_window_click)
        self.frame_4.bind("<Button-1>", self.on_window_click)
        self.lbl_target.bind("<Button-1>", self.on_window_click)
        self.lbl_trigger.bind("<Button-1>", self.on_window_click)
        self.lbl_delay.bind("<Button-1>", self.on_window_click)
        self.lbl_window.bind("<Button-1>", self.on_window_click)
        self.lbl_status.bind("<Button-1>", self.on_window_click)
        self.lbl_target_val.bind("<Button-1>", self.on_window_click)
        self.lbl_trigger_val.bind("<Button-1>", self.on_window_click)

    def validate_digit(self, P: str) -> bool:
        if P == "" or P.isdigit():
            # Перевірка на unsigned int (приблизно 4 млрд)
            if P != "" and int(P) > 4294967295:
                return False
            return True
        return False

    def on_window_click(self, event: Any) -> None:
        """Знімає фокус з поля вводу при кліку на інші елементи"""
        self.focus_set()

    def on_button_mouse_click(self, event: Any, button: Button, mode: str) -> Optional[str]:
        """Обробка кліків миші на кнопках вибору"""
        # Перевіряємо чи режим прослуховування активний І готовий приймати введення
        if self.listening_mode == mode and self.listening_ready:
            # Зберігаємо цю кнопку миші
            self.on_input_event(button, is_mouse=True)
            return "break"  # Зупиняємо подальшу обробку події
        return None

    def on_delay_focus_out(self, event: Any) -> None:
        """Auto-fill 1000ms when delay field is empty"""
        if self.entry_delay.get().strip() == "":
            self.entry_delay.delete(0, "end")
            self.entry_delay.insert(0, str(DEFAULT_EMPTY_DELAY_MS))
            # Зупиняємо авто-кліки при зміні затримки
            if self.is_running:
                self.is_running = False
                self.lbl_status.configure(text=t("status_stopped"), text_color="red")

    def open_window_menu(self) -> None:
        """Відкриває меню вибору вікна ТІЛЬКИ після оновлення списку"""
        # Спочатку оновлюємо список
        success: bool = self.refresh_window_list()

        if not success or not self.window_list:
            print(t("msg_refresh_failed"))
            return

        # ТІЛЬКИ ПІСЛЯ успішного оновлення створюємо і показуємо меню
        self.show_window_popup()

    def show_window_popup(self) -> None:
        """Показує popup меню з списком вікон"""
        # Закриваємо попереднє меню якщо воно існує
        if self.window_popup is not None:
            try:
                self.window_popup.destroy()
            except:
                pass

        # Створюємо нове Toplevel вікно для меню
        self.window_popup = ctk.CTkToplevel(self)
        self.window_popup.title("")
        self.window_popup.overrideredirect(True)  # Прибираємо рамку вікна
        self.window_popup.attributes('-topmost', True)

        # Вимикаємо взаємодію з батьківським вікном
        self.window_popup.transient(self)

        # Розміщуємо popup під кнопкою
        btn_x: int = self.window_select_btn.winfo_rootx()
        btn_y: int = self.window_select_btn.winfo_rooty()
        btn_height: int = self.window_select_btn.winfo_height()

        # Розраховуємо висоту на основі кількості вікон
        # +1 для кнопки "Не обрано"
        num_items: int = len(self.window_list) + 1
        # Мінімум 2 елементи, максимум 10 елементів
        visible_items: int = max(MIN_VISIBLE_POPUP_ITEMS, min(num_items, MAX_VISIBLE_POPUP_ITEMS))
        menu_height: int = visible_items * POPUP_ITEM_HEIGHT + 10  # +10 для paddings

        # Фіксована ширина для консистентності
        menu_width: int = POPUP_MENU_WIDTH

        self.window_popup.geometry(f"{menu_width}x{menu_height}+{btn_x}+{btn_y + btn_height}")

        # Фрейм зі скролом (тільки якщо потрібно)
        if num_items <= MAX_VISIBLE_POPUP_ITEMS:
            # Якщо елементів мало, використовуємо звичайний фрейм без скролу
            self.popup_frame = ctk.CTkFrame(self.window_popup, width=menu_width-20, height=menu_height-10)
            self.popup_frame.pack_propagate(False)  # Забороняємо зміну розміру
        else:
            # Якщо елементів багато, використовуємо ScrollableFrame
            self.popup_frame = ctk.CTkScrollableFrame(self.window_popup, width=menu_width-20, height=menu_height-10)

        self.popup_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Додаємо кнопку "Не обрано"
        btn_none = ctk.CTkButton(
            self.popup_frame,
            text=t("not_selected"),
            command=lambda: self.select_window(None, t("not_selected")),
            width=menu_width-30,
            height=28,
            anchor="w"
        )
        btn_none.pack(pady=2, fill="x")

        # Додаємо кнопки для кожного вікна
        for hwnd, window_name in self.window_list:
            # Обрізаємо довгі назви але залишаємо фіксовану ширину кнопки
            display_name: str = window_name if len(window_name) <= 45 else window_name[:42] + "..."
            btn = ctk.CTkButton(
                self.popup_frame,
                text=display_name,
                command=lambda h=hwnd, n=window_name: self.select_window(h, n),
                width=menu_width-30,
                height=28,
                anchor="w"
            )
            btn.pack(pady=2, fill="x")

        # Прив'язуємо закриття меню при кліку поза ним
        self.window_popup.bind("<FocusOut>", lambda e: self.close_window_popup())

        # Додаємо глобальний обробник кліків для закриття при кліку поза вікном
        self.window_popup.bind("<Button-1>", self._popup_click_inside)
        self.after(GLOBAL_CLICK_BIND_DELAY_MS, self._bind_global_click)

        self.window_popup.focus_set()

    def select_window(self, hwnd: Optional[int], name: str) -> None:
        """Вибирає вікно зі списку"""
        self.selected_window_hwnd = hwnd
        self.selected_window_name = name
        self.window_select_btn.configure(text=name[:40] + ("..." if len(name) > 40 else ""))
        self.close_window_popup()

    def _popup_click_inside(self, event: Any) -> None:
        """Помічає що клік був всередині popup"""
        self._popup_clicked = True

    def _bind_global_click(self) -> None:
        """Прив'язує глобальний обробник кліків"""
        if self.window_popup:
            self._popup_clicked = False
            self.bind("<Button-1>", self._check_click_outside)

    def _check_click_outside(self, event: Any) -> None:
        """Перевіряє чи клік був поза popup і закриває його"""
        if not self._popup_clicked and self.window_popup:
            self.close_window_popup()
        self._popup_clicked = False
        self.unbind("<Button-1>")

    def close_window_popup(self) -> None:
        if self.window_popup is not None:
            try:
                self.window_popup.destroy()
            except Exception:
                pass
            self.window_popup = None
            
        try:
            self.unbind("<Button-1>")
        except Exception:
            pass

    def refresh_window_list(self) -> bool:
        """Оновлює список відкритих вікон. Повертає True якщо успішно."""
        try:
            self.hide_error()
            self.window_list = []
            errors: List[str] = []

            def enum_windows_callback(hwnd: int, _: Any) -> bool:
                try:
                    if self.app_hwnd and hwnd == self.app_hwnd:
                        return True
                    if not win32gui.IsWindowVisible(hwnd):
                        return True
                        
                    raw_window_text = win32gui.GetWindowText(hwnd)
                    if not raw_window_text:
                        return True
                    window_text: str = str(raw_window_text)
                    
                    process_handle = None
                    try:
                        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                        process_handle = win32api.OpenProcess(
                            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                            False,
                            process_id
                        )
                        
                        if process_handle:
                            raw_process_name = cast(Optional[str], win32process.GetModuleFileNameEx(process_handle, 0))
                            process_name: str = str(raw_process_name).lower() if raw_process_name else ""
                            
                            if 'explorer.exe' in process_name:
                                return True
                    except Exception as e:
                        if len(errors) < 3:
                            errors.append(f"{t('error_process_access')}: {window_text[:30]}")
                    finally:
                        if process_handle:
                            win32api.CloseHandle(process_handle)
                    try:
                        raw_class_name = win32gui.GetClassName(hwnd)
                        class_name: str = str(raw_class_name) if raw_class_name else ""
                        
                        excluded_classes: List[str] = [
                            'IME', 'MSCTFIME UI', 'Windows.UI.Core.CoreWindow', 'ApplicationFrameWindow',
                        ]
                        if any(excluded in class_name for excluded in excluded_classes):
                            return True
                    except Exception as e:
                        if len(errors) < 3:
                            errors.append(f"{t('error_class_access')}: {window_text[:30]}")
                    
                    ex_style = cast(int, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE))
                    if ex_style & win32con.WS_EX_TOOLWINDOW:
                        return True
                    if not (ex_style & win32con.WS_EX_APPWINDOW):
                        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
                            return True
                            
                    style = cast(int, win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE))
                    if not (style & win32con.WS_VISIBLE):
                        return True
                        
                    self.window_list.append((hwnd, window_text))
                except Exception as e:
                    if len(errors) < 3:
                        errors.append(f"{t('error_window_processing')}: {str(e)[:50]}")
                return True

            win32gui.EnumWindows(enum_windows_callback, None)

            # Типізована функція замість lambda
            def sort_key(item: Tuple[int, str]) -> str:
                return item[1].lower()

            self.window_list.sort(key=sort_key)

            if errors:
                self.show_error(" | ".join(errors))

            print(f"{t('msg_windows_found')} {len(self.window_list)} {t('msg_windows_word')}")
            return True

        except Exception as e:
            error_msg = f"{t('error_window_refresh')}: {e}"
            print(error_msg)
            self.show_error(error_msg)
            return False

    def start_binding(self, mode: str) -> None:
        # Зупиняємо авто-кліки при зміні кнопки
        if self.is_running:
            self.is_running = False
            self.lbl_status.configure(text=t("status_stopped"), text_color="red")

        # Скидаємо прапорець готовності
        self.listening_ready = False

        # Активуємо режим прослуховування ОДРАЗУ
        self.listening_mode = mode

        self.btn_set_target.configure(state="disabled")
        self.btn_set_trigger.configure(state="disabled")

        msg: str = t("press_any_key")
        if mode == 'target':
            self.lbl_target_val.configure(text=msg, text_color="yellow")
        else:
            self.lbl_trigger_val.configure(text=msg, text_color="yellow")

        # Встановлюємо готовність через мінімальну затримку (1мс)
        # Це дозволяє уникнути запису першого кліку на кнопці UI
        self.after(LISTENING_READY_DELAY_MS, lambda: setattr(self, 'listening_ready', True))


    def on_input_event(self, key: Any, is_mouse: bool = False) -> None:
        # Ця функція викликається з потоків слухачів
        if self.listening_mode:
            # Перевірка на дозволені клавіші
            if not self.is_key_allowed(key):
                # Скидаємо режим прослуховування
                self.listening_mode = None
                self.listening_ready = False
                self.btn_set_target.configure(state="normal")
                self.btn_set_trigger.configure(state="normal")
                return

            # Зберігаємо кнопку з читабельною назвою
            display_text: str = self.get_key_display_name(key)

            if self.listening_mode == 'target':
                self.target_key = (key, is_mouse)
                self.lbl_target_val.configure(text=f"{t('selected')}: {display_text}", text_color="green")
            elif self.listening_mode == 'trigger':
                self.trigger_key = (key, is_mouse)
                self.lbl_trigger_val.configure(text=f"{t('selected')}: {display_text}", text_color="green")

            # Скидаємо режим прослуховування та готовність
            self.listening_mode = None
            self.listening_ready = False
            self.btn_set_target.configure(state="normal")
            self.btn_set_trigger.configure(state="normal")

    def get_key_display_name(self, key: Any) -> str:
        """Отримати читабельну назву клавіші"""
        # Для кнопок миші
        if key == Button.left:
            return t("mouse_left")
        elif key == Button.right:
            return t("mouse_right")
        elif key == Button.middle:
            return t("mouse_middle")

        # Для клавіш з VK кодами (NumPad)
        if hasattr(key, 'vk'):
            vk: int = key.vk
            # NumPad цифри 0-9
            if VK_NUMPAD_0_TO_9_START <= vk <= VK_NUMPAD_0_TO_9_END:
                return f"NUMPAD{vk - VK_NUMPAD_0_TO_9_START}"
            # NumPad операції
            numpad_ops: Dict[int, str] = {
                106: "NUMPAD*", 107: "NUMPAD+", 108: "NUMPAD_SEP",
                109: "NUMPAD-", 110: "NUMPAD.", 111: "NUMPAD/"
            }
            if vk in numpad_ops:
                return numpad_ops[vk]

        # Стандартне відображення
        return str(key).replace("Key.", "").replace("Button.", "").replace("'", "").upper()

    def is_key_allowed(self, key: Any) -> bool:
        """Перевірка чи клавіша в списку дозволених"""
        # Для кнопок миші
        if key in self.allowed_mouse_buttons:
            return True

        # Для спеціальних клавіш клавіатури
        if key in self.allowed_special_keys:
            return True

        # Для KeyCode (літери, цифри, numpad) - дозволяємо всі що мають vk або char
        if hasattr(key, 'vk'):
            vk: int = key.vk
            # Літери A-Z (будь-яка розкладка)
            if VK_A_TO_Z_START <= vk <= VK_A_TO_Z_END:
                return True
            # Цифри 0-9 (верхній ряд)
            if VK_0_TO_9_START <= vk <= VK_0_TO_9_END:
                return True
            # NumPad цифри 0-9
            if VK_NUMPAD_0_TO_9_START <= vk <= VK_NUMPAD_0_TO_9_END:
                return True
            # NumPad операції (*, +, separator, -, ., /)
            if VK_NUMPAD_OPS_START <= vk <= VK_NUMPAD_OPS_END:
                return True

        # Якщо це KeyCode з char (для сумісності)
        if hasattr(key, 'char') and key.char:
            char: str = key.char.lower()
            # Літери a-z
            if 'a' <= char <= 'z':
                return True
            # Цифри 0-9
            if '0' <= char <= '9':
                return True

        return False

    # --- Логіка клікера ---
    def clicker_logic(self) -> None:
        while True:
            if self.is_running and self.target_key:
                key: Any
                is_mouse: bool
                key, is_mouse = self.target_key

                # Оновлюємо інтервал з поля вводу
                try:
                    delay: int = int(self.entry_delay.get())
                    if delay < 1: delay = 1
                except ValueError:
                    delay = 100

                # Якщо вибрано вікно, перевіряємо чи воно активне
                if self.selected_window_hwnd:
                    try:
                        # Перевіряємо чи вікно ще існує
                        if not win32gui.IsWindow(self.selected_window_hwnd):
                            new_status: str = t("status_window_closed")
                            if self.last_window_status != new_status:
                                self.last_window_status = new_status
                                self.after(0, lambda: self.lbl_status.configure(
                                    text=new_status, text_color="red"))
                            print(t("msg_window_closed"))
                            time.sleep(delay / 1000.0)
                            continue

                        # Отримуємо поточне активне вікно
                        current_hwnd: int = win32gui.GetForegroundWindow()

                        # Якщо обране вікно НЕ активне, пропускаємо клік
                        if current_hwnd != self.selected_window_hwnd:
                            new_status = t("status_window_inactive")
                            if self.last_window_status != new_status:
                                self.last_window_status = new_status
                                self.after(0, lambda: self.lbl_status.configure(
                                    text=new_status, text_color="orange"))
                            # Не виконуємо клік, просто чекаємо
                            time.sleep(delay / 1000.0)
                            continue
                        else:
                            # Вікно активне, оновлюємо статус якщо він змінився
                            new_status = t("status_running")
                            if self.last_window_status != new_status:
                                self.last_window_status = new_status
                                self.after(0, lambda: self.lbl_status.configure(
                                    text=new_status, text_color="green"))

                    except Exception as e:
                        new_status = t("status_window_error")
                        if self.last_window_status != new_status:
                            self.last_window_status = new_status
                            self.after(0, lambda: self.lbl_status.configure(
                                text=new_status, text_color="red"))
                        print(f"{t('msg_window_check_error')}: {e}")
                        time.sleep(delay / 1000.0)
                        continue

                # Виконуємо натискання (тільки якщо вікно активне або не вибране)
                if is_mouse:
                    self.mouse_controller.click(key)
                else:
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)

                time.sleep(delay / 1000.0)
            else:
                time.sleep(0.01)  # Економія ресурсів процесора

    # --- Глобальні слухачі ---
    def start_global_listeners(self) -> None:
        """Запускає глобальні слухачі для клавіатури та миші"""

        def on_press(key: Any) -> None:
            """Обробник натискання клавіш"""
            if self.listening_mode:
                self.after(0, lambda: self.on_input_event(key, is_mouse=False))
                return

            # Логіка тригера (перемикання on/off)
            if self.trigger_key:
                stored_key: Any
                is_mouse_trigger: bool
                stored_key, is_mouse_trigger = self.trigger_key
                if not is_mouse_trigger and key == stored_key:
                    self.toggle_running()

        def on_click(x: int, y: int, button: Button, pressed: bool) -> None:
            """Обробник кліків миші"""
            if not pressed:
                return

            if self.listening_mode:
                self.after(0, lambda b=button: self.on_input_event(b, is_mouse=True))
                return

            # Логіка тригера для миші
            if self.trigger_key:
                stored_key: Any
                is_mouse_trigger: bool
                stored_key, is_mouse_trigger = self.trigger_key
                if is_mouse_trigger and button == stored_key:
                    self.toggle_running()

        self.kb_listener = keyboard.Listener(on_press=on_press)
        self.mouse_listener = mouse.Listener(on_click=on_click)

        self.kb_listener.start()
        self.mouse_listener.start()

    def toggle_running(self) -> None:
        """Перемикає стан роботи авто-клікера"""
        self.is_running = not self.is_running

        if self.is_running:
            self._start_autoclicker()
        else:
            self._stop_autoclicker()

    def _start_autoclicker(self) -> None:
        self.last_window_status = None

        if self.selected_window_hwnd:
            self.after(0, lambda: self.lbl_status.configure(text=t("status_window_waiting"), text_color="yellow"))
            print(t("msg_started_window"))
        else:
            self.after(0, lambda: self.lbl_status.configure(text=t("status_running"), text_color="green"))
            print(t("msg_started_any"))

    def _stop_autoclicker(self) -> None:
        self.last_window_status = None
        self.after(0, lambda: self.lbl_status.configure(text=t("status_stopped"), text_color="red"))
        print(t("msg_stopped"))


def check_single_instance() -> bool:
    """Перевіряє чи вже запущений екземпляр програми"""
    global mutex

    # Унікальний ідентифікатор для mutex
    mutex_name: str = "Global\\AutoClickerPro_SingleInstance_Mutex"

    try:
        # Спробуємо створити mutex
        mutex = win32event.CreateMutex(cast(Any, None), False, mutex_name)
        last_error: int = win32api.GetLastError()

        # Якщо mutex вже існує, програма вже запущена
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            return False

        return True
    except Exception as e:
        logging.error(f"Error checking single instance: {e}")
        # У випадку помилки дозволяємо запуск
        return True


def show_already_running_dialog() -> None:
    """Показує повідомлення про вже запущений екземпляр"""
    # Завантажуємо мову з конфігурації
    global CurrentLanguage
    try:
        appdata: Optional[str] = os.getenv('APPDATA')
        if appdata:
            config_path: Path = Path(appdata) / 'AutoClickerPro' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content: str = f.read()
                    last_brace: int = content.rfind('}')
                    if last_brace != -1:
                        json_content: str = content[:last_brace + 1].strip()
                    else:
                        json_content = content.strip()
                    config: Dict[str, Any] = json.loads(json_content)
                    CurrentLanguage = config.get('language', 'UA')
            else:
                CurrentLanguage = 'UA'
        else:
            CurrentLanguage = 'UA'
    except:
        CurrentLanguage = 'UA'

    # Створюємо просте вікно попередження
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root: ctk.CTk = ctk.CTk()
    root.title(t("msg_already_running_title"))
    root.geometry("400x150")
    root.resizable(False, False)

    # Встановлюємо іконку
    icon_file = resource_path("icon.ico")
    if icon_file.exists():
        root.iconbitmap(str(icon_file))

    # Центруємо вікно
    root.update_idletasks()
    screen_width: int = root.winfo_screenwidth()
    screen_height: int = root.winfo_screenheight()
    x: int = (screen_width - 400) // 2
    y: int = (screen_height - 150) // 2
    root.geometry(f"400x150+{x}+{y}")

    # Повідомлення
    label: ctk.CTkLabel = ctk.CTkLabel(
        root,
        text=t("msg_already_running"),
        font=("Arial", 14),
        wraplength=350
    )
    label.pack(pady=30)

    # Кнопка OK
    btn: ctk.CTkButton = ctk.CTkButton(
        root,
        text="OK",
        command=root.destroy,
        width=100
    )
    btn.pack(pady=10)

    root.mainloop()


# Глобальна змінна для збереження mutex
mutex: Any = None

if __name__ == "__main__":
    if os.name == 'nt':
        myappid: str = f"serhii0659.autoclickerpro.{APP_VERSION}"
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logging.warning("Не вдалося встановити AppUserModelID: %s", e)

    if not check_single_instance():
        show_already_running_dialog()
    else:
        app: AutoClickerApp = AutoClickerApp()
        app.mainloop()