import customtkinter as ctk
import threading
import time
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import logging
import json
import os
from pathlib import Path
import base64

try:
    import win32gui
    import win32con
    import win32process
    import win32api
except ImportError as e:
    win32gui = None
    win32con = None
    win32process = None
    win32api = None
    WINDOWS_SUPPORT = False
    logging.warning("pywin32 не встановлено. Функція вибору вікна недоступна: %s", e)
else:
    WINDOWS_SUPPORT = True

# --- Мова ---
CurrentLanguage = None # Буде встановлено при завантаженні конфігурації або за замовчуванням - "UA"

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
        "config_file_content": """

═══════════════════════════════════════════════════════════════════════
  AutoClicker Pro - Configuration File
═══════════════════════════════════════════════════════════════════════
" 
"  Автор: Serhii0659
"  GitHub: {github_link}
"  Версія: 1.0
"  Дата створення: 2025
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
        "config_file_content": """

═══════════════════════════════════════════════════════════════════════
  AutoClicker Pro - Configuration File
═══════════════════════════════════════════════════════════════════════
" 
"  Author: Serhii0659
"  GitHub: {github_link}
"  Version: 1.0
"  Date Created: 2025
" 
"  ─────────────────────────────────────────────────────────────────────
"  💡 TIP OF THE DAY: Don't poke where you shouldn't 😏
"  ─────────────────────────────────────────────────────────────────────
" 
═══════════════════════════════════════════════════════════════════════
"""
    }
}

def t(key):
    """Отримати переклад за ключем"""
    lang = CurrentLanguage if CurrentLanguage in translations else "UA"
    return translations[lang].get(key, key)

# --- Налаштування інтерфейсу ---
ctk.set_appearance_mode("Dark")  # Режим: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Теми: "blue" (standard), "green", "dark-blue"

# --- Константи ---
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
DEFAULT_DELAY_MS = 100
DEFAULT_EMPTY_DELAY_MS = 1000
POPUP_MENU_WIDTH = 340
POPUP_ITEM_HEIGHT = 32
MAX_VISIBLE_POPUP_ITEMS = 10
MIN_VISIBLE_POPUP_ITEMS = 1
LISTENING_READY_DELAY_MS = 1
GLOBAL_CLICK_BIND_DELAY_MS = 100
GITHUB_LINK = "https://github.com/Serhii0659"

# --- Вбудована іконка програми (Base64 encoded ICO) ---
ICON_BASE64 = """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"""

# VK коди клавіш
VK_A_TO_Z_START = 65
VK_A_TO_Z_END = 90
VK_0_TO_9_START = 48
VK_0_TO_9_END = 57
VK_NUMPAD_0_TO_9_START = 96
VK_NUMPAD_0_TO_9_END = 105
VK_NUMPAD_OPS_START = 106
VK_NUMPAD_OPS_END = 111


class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Налаштування вікна
        self.title(t("window_title"))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Центрування вікна на екрані
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Встановлюємо кастомну іконку програми
        self.set_app_icon()

        # Контролери введення
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()

        # Дозволені клавіші (whitelist) - використовуємо набори для швидкої перевірки
        self.allowed_special_keys = {
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
        self.allowed_mouse_buttons = {Button.left, Button.right, Button.middle}

        # Змінні стану
        self.target_key = None  # Кнопка 1 (Дія)
        self.trigger_key = None  # Кнопка 2 (Тригер)
        self.is_running = False
        self.listening_mode = None  # 'target' або 'trigger'
        self.listening_ready = False  # Чи готовий режим прослуховування (для захисту від першого кліку)
        self.delay_ms = DEFAULT_DELAY_MS
        self.selected_window_hwnd = None  # HWND обраного вікна
        self.window_list = []  # Список вікон
        self.last_window_status = None  # Останній статус вікна для відображення
        self.app_hwnd = None  # HWND власного вікна програми

        # Лістенери (слухачі)
        self.kb_listener = None
        self.mouse_listener = None

        # Потік для клікера
        self.clicker_thread = threading.Thread(target=self.clicker_logic, daemon=True)
        self.clicker_thread.start()

        # Глобальний слухач для тригера (запускаємо одразу)
        self.start_global_listeners()

        self.create_widgets()

        # Завантажуємо налаштування ПІСЛЯ створення віджетів
        self.load_config()

        # Зберігаємо налаштування при закритті
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_config_path(self):
        """Отримати шлях до файлу конфігурації у AppData"""
        # Зберігаємо у %APPDATA%\AutoClickerPro\config.json
        appdata = os.getenv('APPDATA')
        if not appdata:
            # Fallback для систем без APPDATA
            appdata = Path.home() / 'AppData' / 'Roaming'

        config_dir = Path(appdata) / 'AutoClickerPro'
        config_dir.mkdir(parents=True, exist_ok=True)  # Створюємо папку якщо не існує
        return config_dir / 'config.json'

    def load_config(self):
        """Завантажити налаштування з файлу"""
        global CurrentLanguage
        try:
            config_path = self.get_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Видаляємо секцію після закриваючої дужки JSON
                    # Шукаємо останню закриваючу дужку JSON
                    last_brace = content.rfind('}')
                    if last_brace != -1:
                        json_content = content[:last_brace + 1].strip()
                    else:
                        json_content = content.strip()

                    config = json.loads(json_content)

                # Відновлюємо затримку
                if 'delay' in config:
                    self.entry_delay.delete(0, "end")
                    self.entry_delay.insert(0, str(config['delay']))

                # Відновлюємо мову
                if 'language' in config:
                    CurrentLanguage = config['language']
                    self.language_var.set(CurrentLanguage)
                    self.update_ui_language()
                else:
                    CurrentLanguage = "UA"  # За замовчуванням українська
                    self.language_var.set(CurrentLanguage)

                # Відновлюємо кнопку дії
                if 'target_key' in config:
                    key_data = config['target_key']
                    self.target_key = self._deserialize_key(key_data)
                    if self.target_key:
                        display_name = self.get_key_display_name(self.target_key[0])
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

    def save_config(self):
        """Зберегти налаштування у файл"""
        try:
            config = {
                'language': CurrentLanguage,
                'delay': self.entry_delay.get(),
                'target_key': self._serialize_key(self.target_key) if self.target_key else None,
                'trigger_key': self._serialize_key(self.trigger_key) if self.trigger_key else None
            }

            config_path = self.get_config_path()

            # Формуємо JSON з відступами
            json_str = json.dumps(config, indent=2, ensure_ascii=False)

            # Додаємо секцію для інформації про автора
            info_section = t("config_file_content").format(github_link=GITHUB_LINK)

            final_content = json_str + info_section

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            print(f"{t('msg_config_saved')} {config_path}")
        except Exception as e:
            print(f"{t('msg_config_save_error')}: {e}")

    def _serialize_key(self, key_tuple):
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

    def _deserialize_key(self, key_data):
        """Відновити кнопку з JSON формату"""
        if not key_data:
            return None

        try:
            # Миша
            if key_data['type'] == 'mouse':
                button_map = {
                    'left': Button.left,
                    'right': Button.right,
                    'middle': Button.middle
                }
                button = button_map.get(key_data['button'])
                if button:
                    return (button, True)

            # Клавіатура
            elif key_data['type'] == 'keyboard':
                # Спеціальні клавіші
                if 'name' in key_data:
                    try:
                        key = getattr(keyboard.Key, key_data['name'])
                        return (key, False)
                    except AttributeError:
                        pass

                # KeyCode (VK коди)
                if 'vk' in key_data:
                    from pynput.keyboard import KeyCode
                    key = KeyCode.from_vk(key_data['vk'])
                    return (key, False)

                # Char (літери)
                if 'char' in key_data:
                    from pynput.keyboard import KeyCode
                    key = KeyCode.from_char(key_data['char'])
                    return (key, False)

        except Exception as e:
            print(f"{t('msg_key_restore_error')}: {e}")

        return None

    def on_closing(self):
        """Обробник закриття вікна"""
        self.save_config()
        self.destroy()

    def set_app_icon(self):
        """Встановити вбудовану іконку програми з Base64"""
        if not ICON_BASE64:
            # Якщо іконка не встановлена, пропускаємо
            return

        try:
            # Декодуємо Base64 → байти
            icon_data = base64.b64decode(ICON_BASE64)

            # Створюємо тимчасовий файл .ico
            temp_ico_path = Path.home() / 'AppData' / 'Local' / 'Temp' / 'autoclicker_icon.ico'
            temp_ico_path.parent.mkdir(parents=True, exist_ok=True)

            # Зберігаємо байти у файл
            with open(temp_ico_path, 'wb') as f:
                f.write(icon_data)

            # Встановлюємо іконку
            self.iconbitmap(str(temp_ico_path))
            print(f"Іконку встановлено успішно: {temp_ico_path}")

        except Exception as e:
            print(f"Помилка встановлення іконки: {e}")

    def get_app_hwnd(self):
        """Отримати HWND власного вікна програми"""
        if WINDOWS_SUPPORT:
            try:
                # Отримуємо HWND через tkinter
                self.app_hwnd = int(self.wm_frame(), 16)
                print(f"{t('msg_hwnd_obtained')}: {self.app_hwnd}")
            except Exception as e:
                print(f"{t('msg_hwnd_failed')}: {e}")
                self.app_hwnd = None

    def open_github(self):
        """Відкрити GitHub профіль у браузері"""
        import webbrowser
        webbrowser.open(GITHUB_LINK)

    def change_language(self, value):
        """Змінити мову інтерфейсу"""
        global CurrentLanguage
        CurrentLanguage = value
        self.update_ui_language()

    def update_ui_language(self):
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
            display_name = self.get_key_display_name(self.target_key[0])
            self.lbl_target_val.configure(text=f"{t('selected')}: {display_name}")
        elif not self.listening_mode:
            self.lbl_target_val.configure(text=t("not_selected"))

        if self.trigger_key and not self.listening_mode:
            display_name = self.get_key_display_name(self.trigger_key[0])
            self.lbl_trigger_val.configure(text=f"{t('selected')}: {display_name}")
        elif not self.listening_mode:
            self.lbl_trigger_val.configure(text=t("not_selected"))

    def show_error(self, error_text):
        """Показати повідомлення про помилку"""
        self.lbl_error.configure(text=error_text)
        self.lbl_error.pack(pady=5)

    def hide_error(self):
        """Приховати повідомлення про помилку"""
        self.lbl_error.pack_forget()

    def create_widgets(self):
        # Заголовок
        self.label_title = ctk.CTkLabel(self, text=t("app_title"), font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=10)

        # Секція Кнопки 1 (Дія)
        self.frame_1 = ctk.CTkFrame(self)
        self.frame_1.pack(pady=8, padx=20, fill="x")

        self.lbl_target = ctk.CTkLabel(self.frame_1, text=t("target_label"))
        self.lbl_target.pack(pady=3)

        self.btn_set_target = ctk.CTkButton(self.frame_1, text=t("select_button"),
                                            command=lambda: self.start_binding('target'))
        self.btn_set_target.pack(pady=3)
        # Додаємо обробку кліків миші на кнопці
        self.btn_set_target.bind("<Button-1>", lambda e: self.on_button_mouse_click(e, Button.left, 'target'))
        self.btn_set_target.bind("<Button-2>", lambda e: self.on_button_mouse_click(e, Button.middle, 'target'))
        self.btn_set_target.bind("<Button-3>", lambda e: self.on_button_mouse_click(e, Button.right, 'target'))

        self.lbl_target_val = ctk.CTkLabel(self.frame_1, text=t("not_selected"), text_color="gray")
        self.lbl_target_val.pack(pady=3)

        # Секція Кнопки 2 (Тригер)
        self.frame_2 = ctk.CTkFrame(self)
        self.frame_2.pack(pady=8, padx=20, fill="x")

        self.lbl_trigger = ctk.CTkLabel(self.frame_2, text=t("trigger_label"))
        self.lbl_trigger.pack(pady=3)

        self.btn_set_trigger = ctk.CTkButton(self.frame_2, text=t("select_button"),
                                             command=lambda: self.start_binding('trigger'))
        self.btn_set_trigger.pack(pady=3)
        # Додаємо обробку кліків миші на кнопці
        self.btn_set_trigger.bind("<Button-1>", lambda e: self.on_button_mouse_click(e, Button.left, 'trigger'))
        self.btn_set_trigger.bind("<Button-2>", lambda e: self.on_button_mouse_click(e, Button.middle, 'trigger'))
        self.btn_set_trigger.bind("<Button-3>", lambda e: self.on_button_mouse_click(e, Button.right, 'trigger'))

        self.lbl_trigger_val = ctk.CTkLabel(self.frame_2, text=t("not_selected"), text_color="gray")
        self.lbl_trigger_val.pack(pady=3)

        # Секція затримки
        self.frame_3 = ctk.CTkFrame(self)
        self.frame_3.pack(pady=8, padx=20, fill="x")

        self.lbl_delay = ctk.CTkLabel(self.frame_3, text=t("delay_label"))
        self.lbl_delay.pack(pady=3)

        # Валідація введення (тільки цифри)
        vcmd = (self.register(self.validate_digit), '%P')
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
        self.selected_window_name = t("not_selected")
        self.window_select_btn = ctk.CTkButton(
            self.frame_4,
            text=self.selected_window_name,
            command=self.open_window_menu,
            width=POPUP_MENU_WIDTH,
            anchor="w"
        )
        self.window_select_btn.pack(pady=3)

        # Popup меню для вибору вікна (створюється динамічно)
        self.window_popup = None

        # Статус
        self.lbl_status = ctk.CTkLabel(self, text=t("status_waiting"), font=("Roboto", 16, "bold"), text_color="red")
        self.lbl_status.pack(pady=10)

        # Помилки (показується тільки коли є помилка)
        self.lbl_error = ctk.CTkLabel(self, text="", font=("Roboto", 10), text_color="#FF6B6B", wraplength=360)
        self.lbl_error.pack(pady=0)
        self.lbl_error.pack_forget()  # Приховуємо за замовчуванням

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
        self.lbl_author.bind("<Button-1>", lambda e: self.open_github())

        # Отримуємо HWND власного вікна після створення UI
        self.after(100, self.get_app_hwnd)  # type: ignore

        # Прив'язка кліків до елементів для зняття фокусу з entry_delay
        # НЕ прив'язуємо до frame_3, щоб не блокувати клік на entry_delay
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

    def validate_digit(self, P):
        if P == "" or P.isdigit():
            # Перевірка на unsigned int (приблизно 4 млрд)
            if P != "" and int(P) > 4294967295:
                return False
            return True
        return False

    def on_window_click(self, event):
        """Знімає фокус з поля вводу при кліку на інші елементи"""
        self.focus_set()

    def on_button_mouse_click(self, event, button, mode):
        """Обробка кліків миші на кнопках вибору"""
        # Перевіряємо чи режим прослуховування активний І готовий приймати введення
        if self.listening_mode == mode and self.listening_ready:
            # Зберігаємо цю кнопку миші
            self.on_input_event(button, is_mouse=True)
            return "break"  # Зупиняємо подальшу обробку події

    def on_delay_focus_out(self, event):
        """Auto-fill 1000ms when delay field is empty"""
        if self.entry_delay.get().strip() == "":
            self.entry_delay.delete(0, "end")
            self.entry_delay.insert(0, str(DEFAULT_EMPTY_DELAY_MS))
            # Зупиняємо авто-кліки при зміні затримки
            if self.is_running:
                self.is_running = False
                self.lbl_status.configure(text=t("status_stopped"), text_color="red")

    def open_window_menu(self):
        """Відкриває меню вибору вікна ТІЛЬКИ після оновлення списку"""
        # Спочатку оновлюємо список
        success = self.refresh_window_list()

        if not success or not self.window_list:
            print(t("msg_refresh_failed"))
            return

        # ТІЛЬКИ ПІСЛЯ успішного оновлення створюємо і показуємо меню
        self.show_window_popup()

    def show_window_popup(self):
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
        btn_x = self.window_select_btn.winfo_rootx()
        btn_y = self.window_select_btn.winfo_rooty()
        btn_height = self.window_select_btn.winfo_height()

        # Розраховуємо висоту на основі кількості вікон
        # +1 для кнопки "Не обрано"
        num_items = len(self.window_list) + 1
        # Мінімум 2 елементи, максимум 10 елементів
        visible_items = max(MIN_VISIBLE_POPUP_ITEMS, min(num_items, MAX_VISIBLE_POPUP_ITEMS))
        menu_height = visible_items * POPUP_ITEM_HEIGHT + 10  # +10 для paddings

        # Фіксована ширина для консистентності
        menu_width = POPUP_MENU_WIDTH

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
            display_name = window_name if len(window_name) <= 45 else window_name[:42] + "..."
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
        self.after(GLOBAL_CLICK_BIND_DELAY_MS, self._bind_global_click)  # type: ignore

        self.window_popup.focus_set()

    def select_window(self, hwnd, name):
        """Вибирає вікно зі списку"""
        self.selected_window_hwnd = hwnd
        self.selected_window_name = name
        self.window_select_btn.configure(text=name[:40] + ("..." if len(name) > 40 else ""))
        self.close_window_popup()

    def _popup_click_inside(self, event):
        """Помічає що клік був всередині popup"""
        self._popup_clicked = True

    def _bind_global_click(self):
        """Прив'язує глобальний обробник кліків"""
        if self.window_popup:
            self._popup_clicked = False
            self.bind("<Button-1>", self._check_click_outside)

    def _check_click_outside(self, event):
        """Перевіряє чи клік був поза popup і закриває його"""
        if not self._popup_clicked and self.window_popup:
            self.close_window_popup()
        self._popup_clicked = False
        # Видаляємо обробник після використання
        self.unbind("<Button-1>")

    def close_window_popup(self):
        """Закриває popup меню"""
        if self.window_popup is not None:
            try:
                self.window_popup.destroy()
            except:
                pass
            self.window_popup = None
        # Видаляємо глобальний обробник якщо він був
        try:
            self.unbind("<Button-1>")
        except:
            pass

    def refresh_window_list(self):
        """Оновлює список відкритих вікон. Повертає True якщо успішно."""
        if not WINDOWS_SUPPORT:
            error_msg = t("error_pywin32")
            print(error_msg)
            self.show_error(error_msg)
            return False

        try:
            self.hide_error()  # Приховуємо попередні помилки
            self.window_list = []
            errors = []  # Збираємо помилки для відображення

            def enum_windows_callback(hwnd, _):
                try:
                    # Виключаємо власне вікно програми
                    if self.app_hwnd and hwnd == self.app_hwnd:
                        return True

                    # Перевіряємо чи вікно видиме
                    if not win32gui.IsWindowVisible(hwnd):
                        return True

                    # Отримуємо назву вікна
                    window_text = win32gui.GetWindowText(hwnd)
                    if not window_text:
                        return True

                    # Виключаємо вікна explorer.exe
                    if WINDOWS_SUPPORT:
                        try:
                            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                            process_handle = win32api.OpenProcess(
                                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                False,
                                process_id
                            )
                            process_name = win32process.GetModuleFileNameEx(process_handle, 0).lower()
                            win32api.CloseHandle(process_handle)

                            if 'explorer.exe' in process_name:
                                return True
                        except Exception as e:
                            # Записуємо помилку доступу до процесу
                            if len(errors) < 3:
                                errors.append(f"{t('error_process_access')}: {window_text[:30]}")

                    # Отримуємо клас вікна
                    try:
                        class_name = win32gui.GetClassName(hwnd)
                        excluded_classes = [
                            'IME', 'MSCTFIME UI', 'Windows.UI.Core.CoreWindow', 'ApplicationFrameWindow',
                        ]
                        if any(excluded in class_name for excluded in excluded_classes):
                            return True
                    except Exception as e:
                        # Записуємо помилку отримання класу
                        if len(errors) < 3:
                            errors.append(f"{t('error_class_access')}: {window_text[:30]}")

                    # Фільтруємо тільки звичайні вікна програм
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

                    # Виключаємо Tool Windows
                    if ex_style & win32con.WS_EX_TOOLWINDOW:
                        return True

                    # Виключаємо вікна без WS_EX_APPWINDOW якщо вони мають власника
                    if not (ex_style & win32con.WS_EX_APPWINDOW):
                        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
                            return True

                    # Перевіряємо стиль вікна
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

                    # Вікно має бути видимим
                    if not (style & win32con.WS_VISIBLE):
                        return True

                    # Додаємо вікно до списку
                    self.window_list.append((hwnd, window_text))

                except Exception as e:
                    # Записуємо загальну помилку
                    if len(errors) < 3:
                        errors.append(f"{t('error_window_processing')}: {str(e)[:50]}")
                return True

            win32gui.EnumWindows(enum_windows_callback, None)

            # Сортуємо за назвою
            self.window_list.sort(key=lambda x: x[1].lower())

            # Відображаємо помилки якщо вони є
            if errors:
                self.show_error(" | ".join(errors))

            print(f"{t('msg_windows_found')} {len(self.window_list)} {t('msg_windows_word')}")
            return True

        except Exception as e:
            error_msg = f"{t('error_window_refresh')}: {e}"
            print(error_msg)
            self.show_error(error_msg)
            return False

    def start_binding(self, mode):
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

        msg = t("press_any_key")
        if mode == 'target':
            self.lbl_target_val.configure(text=msg, text_color="yellow")
        else:
            self.lbl_trigger_val.configure(text=msg, text_color="yellow")

        # Встановлюємо готовність через мінімальну затримку (1мс)
        # Це дозволяє уникнути запису першого кліку на кнопці UI
        self.after(LISTENING_READY_DELAY_MS, lambda: setattr(self, 'listening_ready', True))  # type: ignore


    def on_input_event(self, key, is_mouse=False):
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
            display_text = self.get_key_display_name(key)

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

    def get_key_display_name(self, key):
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
            vk = key.vk
            # NumPad цифри 0-9
            if VK_NUMPAD_0_TO_9_START <= vk <= VK_NUMPAD_0_TO_9_END:
                return f"NUMPAD{vk - VK_NUMPAD_0_TO_9_START}"
            # NumPad операції
            numpad_ops = {
                106: "NUMPAD*", 107: "NUMPAD+", 108: "NUMPAD_SEP",
                109: "NUMPAD-", 110: "NUMPAD.", 111: "NUMPAD/"
            }
            if vk in numpad_ops:
                return numpad_ops[vk]

        # Стандартне відображення
        return str(key).replace("Key.", "").replace("Button.", "").replace("'", "").upper()

    def is_key_allowed(self, key):
        """Перевірка чи клавіша в списку дозволених"""
        # Для кнопок миші
        if key in self.allowed_mouse_buttons:
            return True

        # Для спеціальних клавіш клавіатури
        if key in self.allowed_special_keys:
            return True

        # Для KeyCode (літери, цифри, numpad) - дозволяємо всі що мають vk або char
        if hasattr(key, 'vk'):
            vk = key.vk
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
            char = key.char.lower()
            # Літери a-z
            if 'a' <= char <= 'z':
                return True
            # Цифри 0-9
            if '0' <= char <= '9':
                return True

        return False

    # --- Логіка клікера ---
    def clicker_logic(self):
        while True:
            if self.is_running and self.target_key:
                key, is_mouse = self.target_key

                # Оновлюємо інтервал з поля вводу
                try:
                    delay = int(self.entry_delay.get())
                    if delay < 1: delay = 1
                except ValueError:
                    delay = 100

                # Якщо вибрано вікно, перевіряємо чи воно активне
                if self.selected_window_hwnd:
                    if WINDOWS_SUPPORT:
                        try:
                            # Перевіряємо чи вікно ще існує
                            if not win32gui.IsWindow(self.selected_window_hwnd):
                                new_status = t("status_window_closed")
                                if self.last_window_status != new_status:
                                    self.last_window_status = new_status
                                    self.after(0, lambda: self.lbl_status.configure(
                                        text=new_status, text_color="red"))  # type: ignore
                                    print(t("msg_window_closed"))
                                time.sleep(delay / 1000.0)
                                continue

                            # Отримуємо поточне активне вікно
                            current_hwnd = win32gui.GetForegroundWindow()

                            # Якщо обране вікно НЕ активне, пропускаємо клік
                            if current_hwnd != self.selected_window_hwnd:
                                new_status = t("status_window_inactive")
                                if self.last_window_status != new_status:
                                    self.last_window_status = new_status
                                    self.after(0, lambda: self.lbl_status.configure(
                                        text=new_status, text_color="orange"))  # type: ignore
                                # Не виконуємо клік, просто чекаємо
                                time.sleep(delay / 1000.0)
                                continue
                            else:
                                # Вікно активне, оновлюємо статус якщо він змінився
                                new_status = t("status_running")
                                if self.last_window_status != new_status:
                                    self.last_window_status = new_status
                                    self.after(0, lambda: self.lbl_status.configure(
                                        text=new_status, text_color="green"))  # type: ignore

                        except Exception as e:
                            new_status = t("status_window_error")
                            if self.last_window_status != new_status:
                                self.last_window_status = new_status
                                self.after(0, lambda: self.lbl_status.configure(
                                    text=new_status, text_color="red"))  # type: ignore
                                print(f"{t('msg_window_check_error')}: {e}")
                            time.sleep(delay / 1000.0)
                            continue
                    else:
                        # Якщо немає підтримки Windows, не можемо перевірити - пропускаємо
                        new_status = t("status_no_support")
                        if self.last_window_status != new_status:
                            self.last_window_status = new_status
                            self.after(0, lambda: self.lbl_status.configure(
                                text=new_status, text_color="red"))  # type: ignore
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
    def start_global_listeners(self):
        """Запускає глобальні слухачі для клавіатури та миші"""

        def on_press(key):
            """Обробник натискання клавіш"""
            if self.listening_mode:
                self.after(0, lambda: self.on_input_event(key, is_mouse=False))  # type: ignore
                return

            # Логіка тригера (перемикання on/off)
            if self.trigger_key:
                stored_key, is_mouse_trigger = self.trigger_key
                if not is_mouse_trigger and key == stored_key:
                    self.toggle_running()

        def on_click(x, y, button, pressed):
            """Обробник кліків миші"""
            if not pressed:
                return

            if self.listening_mode:
                self.after(0, lambda b=button: self.on_input_event(b, is_mouse=True))  # type: ignore
                return

            # Логіка тригера для миші
            if self.trigger_key:
                stored_key, is_mouse_trigger = self.trigger_key
                if is_mouse_trigger and button == stored_key:
                    self.toggle_running()

        self.kb_listener = keyboard.Listener(on_press=on_press)
        self.mouse_listener = mouse.Listener(on_click=on_click)

        self.kb_listener.start()
        self.mouse_listener.start()

    def toggle_running(self):
        """Перемикає стан роботи авто-клікера"""
        self.is_running = not self.is_running

        if self.is_running:
            self._start_autoclicker()
        else:
            self._stop_autoclicker()

    def _start_autoclicker(self):
        """Запускає авто-клікер"""
        self.last_window_status = None

        if self.selected_window_hwnd:
            self.lbl_status.configure(text=t("status_window_waiting"), text_color="yellow")
            print(t("msg_started_window"))
        else:
            self.lbl_status.configure(text=t("status_running"), text_color="green")
            print(t("msg_started_any"))

    def _stop_autoclicker(self):
        """Зупиняє авто-клікер"""
        self.last_window_status = None
        self.lbl_status.configure(text=t("status_stopped"), text_color="red")
        print(t("msg_stopped"))


if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()