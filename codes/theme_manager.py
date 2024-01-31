import re
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from tkinter import colorchooser, messagebox

SETTINGS_FOLDER = Path('~/AppData/Local/SumatraPDF').expanduser()
THEME_APP_SIZE = '200x50'


class SumatraThemeException(Exception):
    """Exception for errors regarding sumatra color settings."""


class SumatraThemeSetting:
    COLOR_SETTINGS = [
        "TextColor",
        "BackgroundColor",
        "MainWindowBackground",
        "SelectionColor",
        "GradientColors",  # Must be added in advanced settings first.
    ]

    def __init__(self, settings_file, settings_db):
        self.settings_file = settings_file
        self._settings_db = settings_db

    @property
    def available_themes(self):
        return self._get_database()['themes']

    def _get_database(self):
        with open(self._settings_db, 'r') as db:
            return json.load(db)

    def add_theme(self, new_theme_color, new_theme):
        database = self._get_database()
        database['themes'][new_theme_color] = new_theme
        self.update_db(database)

    def update_db(self, data):
        with open(self._settings_db, 'w') as db:
            json.dump(data, db, indent=4)

    def get_current_theme(self):
        current_theme = {}
        with open(self.settings_file, "r") as f:
            self.currentSettings = f.read()
            for color_setting in self.COLOR_SETTINGS:
                try:
                    color = re.findall(r"%s = (.*)" % (color_setting), self.currentSettings)[0]
                    if not color:
                        raise ValueError(f'No color found for {color_setting}.')
                    current_theme[color_setting] = color
                except IndexError as e:
                    raise SumatraThemeException(f'"{color_setting}" is not defined in settings.') from e
                except ValueError as e:
                    raise SumatraThemeException(f'No color found for {color_setting} in settings.') from e
        return current_theme

    def change_theme(self, theme_color=None):
        if not theme_color:
            return
        new_theme = self.available_themes.get(theme_color)
        if not new_theme:
            return
        current_theme = self.get_current_theme()
        updated_theme = []
        with open(self.settings_file, "r+") as f:
            for line in f.readlines():
                for color_setting in self.COLOR_SETTINGS:
                    current_color = current_theme[color_setting]
                    new_color = new_theme[color_setting]
                    line = re.sub(current_color, new_color, line)
                updated_theme.append(line)
            f.seek(0)
            f.writelines(updated_theme)
            f.truncate()


class CustomThemeDialog(tk.Toplevel):
    def __init__(self, master, current_theme, apply_callback):
        super().__init__(master)
        self.title("Custom Theme")
        self.geometry("390x200")

        self.current_theme = current_theme
        self.color_entries = []

        self.color_pick_label = ttk.Label(self, text='Color picker')
        self.color_radio = ttk.Radiobutton(self, command=self.pick_color, state=tk.DISABLED)

        self.color_pick_label.grid(row=0, column=3)
        self.color_radio.grid(row=0, column=4)

        for i, color_setting in enumerate(SumatraThemeSetting.COLOR_SETTINGS):
            setting_label = ttk.Label(self, text=f"{color_setting}:")
            entry = ttk.Entry(self)
            entry.bind("<FocusIn>", lambda event, entry=entry: self.enable_radio(entry))

            entry.insert(0, current_theme.get(color_setting, ""))

            setting_label.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")

            self.color_entries.append(entry)

        apply_button = ttk.Button(self, text="Apply", command=self.apply_custom_theme)
        apply_button.grid(row=len(SumatraThemeSetting.COLOR_SETTINGS), column=0, columnspan=2, pady=10)

        self.apply_callback = apply_callback

    def apply_custom_theme(self):
        custom_theme = {}
        for i, color_setting in enumerate(SumatraThemeSetting.COLOR_SETTINGS):
            custom_theme[color_setting] = self.color_entries[i].get()

        self.apply_callback(custom_theme)
        self.destroy()

    def enable_radio(self, entry):
        self.color_radio.configure(state=tk.NORMAL)
        self.color_entry = entry

    def pick_color(self):
        if self.color_entry == self.color_entries[-1]:
            new_gradient_colors = []
            for i in range(3):
                color = colorchooser.askcolor(title=f'Pick Gradient Color {i+1}')
                if color[1] is not None:
                    new_gradient_colors.append(color[1])

            new_gradient_colors = ' '.join(new_gradient_colors)
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, new_gradient_colors)
        else:
            color = colorchooser.askcolor(title='Pick a color')
            self.color_radio.configure(state=tk.DISABLED)
            if color[1] is not None:
                self.color_entry.delete(0, tk.END)
                self.color_entry.insert(0, color[1])


class SumatraThemeApp:
    def __init__(self, master, theme_setting):
        # window setup
        self.master = master
        self.theme_setting = theme_setting
        self.master.geometry(THEME_APP_SIZE)
        self.master.resizable(0, 0)
        self.master.title('Sumatra Advance Settings')

        self.theme_color_string = tk.StringVar()

        # Theme options
        self.all_themes = list(self.theme_setting.available_themes)
        self.theme_options_label = ttk.Label(text='Choose Theme:', font='Arial 10 bold')
        self.theme_option_menu = ttk.OptionMenu(
            self.master,
            self.theme_color_string,
            'Themes',
            *(self.all_themes),
            direction='flush',
            command=self.apply_theme
        )
        self.theme_options_label.grid(row=0, column=0, pady=5)
        self.theme_option_menu.grid(row=0, column=1, padx=5, pady=5)

    def apply_theme(self, theme_color):
        if theme_color == 'Custom':
            self.show_custom_theme_dialog()
            return
        try:
            self.theme_setting.change_theme(theme_color)
        except SumatraThemeException as e:
            self.display_error_message(e)

    def show_custom_theme_dialog(self):
        current_theme = self.theme_setting.get_current_theme()
        custom_dialog = CustomThemeDialog(self.master, current_theme, self.apply_custom_theme)
        self.master.wait_window(custom_dialog)

    def apply_custom_theme(self, custom_theme):
        try:
            self.theme_setting.add_theme('Custom', custom_theme)
            self.theme_setting.change_theme('Custom')
        except SumatraThemeException as e:
            self.display_error_message(e)

    def display_error_message(self, message):
        messagebox.showinfo("An error occured", message)


def main():
    settings_file = SETTINGS_FOLDER / 'SumatraPDF-settings.txt'
    settings_db = SETTINGS_FOLDER / 'backup_db.json'

    theme_setting = SumatraThemeSetting(settings_file, settings_db)

    app = SumatraThemeApp(tk.Tk(), theme_setting)
    app.master.mainloop()


if __name__ == '__main__':
    main()
