import re
import tkinter as tk
from enum import Enum
from tkinter import ttk
from pathlib import Path


class Themes(Enum):
    LIGHT = {
        "TextColor": "#000000",
        "BackgroundColor": "#ffffff",
        "MainWindowBackground": "#80fff200",
        "SelectionColor": "#f5fc0c",
        "GradientColors": "#2828aa #28aa28 #aa2828",
    }
    DARK = {
        "TextColor": "#dddddd",
        "BackgroundColor": "#111111",
        "MainWindowBackground": "#2e2e2e",
        "SelectionColor": "#f5fc0c",
        "GradientColors": "#2828aa #28aa28 #aa2828",
    }
    DRACULA = {
        "TextColor": "#f8f8f2",
        "BackgroundColor": "#21222c",
        "MainWindowBackground": "#282a36",
        "SelectionColor": "#f4f4f4",
        "GradientColors": "#2828aa #28aa28 #aa2828",
    }


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

    def __init__(self, settings_file, theme_source):
        self.settings_file = settings_file
        self.theme_source = theme_source

    @property
    def available_themes(self):
        available_themes = {
            "Light": self.theme_source.LIGHT.value,
            "Dark": self.theme_source.DARK.value,
            "Dracula": self.theme_source.DRACULA.value,
        }
        return available_themes

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

    def change_theme(self, new_theme):
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


APP_SIZE = '250x80'


class SumatraThemeApp:
    def __init__(self, master, theme_setting):
        self.master = master
        self.theme_setting = theme_setting
        self.master.geometry(APP_SIZE)
        self.master.resizable(0, 0)
        self.master.title('Sumatra Advance Settings')

        self.new_theme_var = tk.StringVar()

        # Theme buttons
        self.dark_theme_button = ttk.Button(text='Dark', command=lambda: self.get_theme('Dark'))
        self.dark_theme_button.grid(row=0, column=0, padx=5, pady=5)
        self.default_theme_button = ttk.Button(text='Light', command=lambda: self.get_theme('Light'))
        self.default_theme_button.grid(row=0, column=1)
        self.dracula_theme_button = ttk.Button(text='Dracula', command=lambda: self.get_theme('Dracula'))
        self.dracula_theme_button.grid(row=0, column=2, padx=5, pady=5)

        # Apply theme button
        self.apply_theme_button = ttk.Button(text='Apply', command=self.apply_theme)
        self.apply_theme_button.grid(row=3, column=1, pady=10)

    def get_theme(self, theme_color):
        self.new_theme_var.set(theme_color)
        return self.theme_setting.available_themes.get(theme_color)

    def apply_theme(self):
        new_theme = self.get_theme(self.new_theme_var.get())
        self.theme_setting.change_theme(new_theme)


def main():
    settings_file = Path("~/Appdata/Local/SumatraPDF/SumatraPDF-settings.txt").expanduser()
    theme_setting = SumatraThemeSetting(settings_file, Themes)
    root = tk.Tk()
    app = SumatraThemeApp(root, theme_setting)
    app.master.mainloop()


if __name__ == '__main__':
    main()
