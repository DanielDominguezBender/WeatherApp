#Import needed
import flet as ft
import json
import sys

from datetime import datetime

if sys.platform =="android" or sys.platform == "ios" or sys.platform == "emscripten":
    import urllib.request
    import ssl
elif sys.platform == "linux" or sys.platform == "win32" or sys.platform == "darwin":
    import urllib.request
    import ssl


# Class dedicated to show the Home Page (with multiple expansion panels)
class HomepageView(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self._default_units = "Metric"  # "metric" or "imperial"
        self._default_lang = "En"       # "en","es","de","fr", ...
        self.data = None

    # ---------- Dialogs ----------
    async def open_dlg(self, e):
        self.api_key_field.value = await self.page.client_storage.get_async("api_key")
        self.page.overlay.append(self.dlg)
        self.dlg.open = True
        self.page.update()

    async def save_api_key(self, e):
        await self.page.client_storage.set_async("api_key", self.api_key_field.value)
        self.dlg.open = False
        self.page.update()

    async def delete_api_key(self, e):
        await self.page.client_storage.remove_async("api_key")
        self.api_key_field.value = ""
        self.page.update()

    # ---------- Preferences ----------
    async def on_pref_change(self, e):
        if self.dd_units.value:
            await self.page.client_storage.set_async("units", self.dd_units.value)
        if self.dd_lang.value:
            await self.page.client_storage.set_async("lang", self.dd_lang.value)
        if (self.city_field.value or "").strip():
            await self.get_weather(None)

    # ---------- Weather fetch & render ----------
    async def get_weather(self, e):
        try:
            api_key = await self.page.client_storage.get_async("api_key")
            city_raw = (self.city_field.value or "").strip()

            if not api_key and not city_raw:
                self.error_dlg.content = ft.Text("Please provide BOTH City and API key.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return
            if not api_key:
                self.error_dlg.content = ft.Text("Please provide the API key.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return
            if not city_raw:
                self.error_dlg.content = ft.Text("Please provide a City.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return

            units = self.dd_units.value or self._default_units
            lang  = self.dd_lang.value  or self._default_lang

            spinner = ft.ProgressRing()
            self.page.overlay.append(spinner); self.page.update()

            city_q = city_raw.replace(" ", "+").translate(
                str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "β": "ss"})
            )
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?q={city_q}&appid={api_key}&lang={lang}&units={units}"
            )

            ctx = ssl.create_default_context()
            with urllib.request.urlopen(url, context=ctx) as response:
                self.data = json.loads(response.read())

            cod = self.data.get("cod", 200)
            if (isinstance(cod, str) and cod != "200") or (isinstance(cod, int) and cod != 200):
                msg = self.data.get("message", "Unknown error")
                raise RuntimeError(f"OpenWeather error: {msg}")

            # Values & units
            temp_val  = round(self.data["main"]["temp"], 1)
            temp_unit = "°C" if units == "Metric" else "°F"

            wind_raw = self.data["wind"]["speed"]
            if units == "Metric":
                wind_val, wind_unit = round(wind_raw * 3.6, 1), "km/h"   # API gives m/s
            else:
                wind_val, wind_unit = round(wind_raw, 1), "mph"          # API gives mph

            # Update labels
            self.temperature.value = f"{temp_val} {temp_unit}"
            self.weather.value     = f"{self.data['weather'][0]['description']}"
            self.pressure.value    = f"{self.data['main']['pressure']} hPa"
            self.wind_speed.value  = f"{wind_val} {wind_unit}"
            self.humidity.value    = f"{self.data['main']['humidity']} %"
            self.last_update.value = datetime.fromtimestamp(self.data["dt"]).strftime("%d/%m/%Y %H:%M:%S")

            # Icon
            try:
                icon_code = self.data["weather"][0]["icon"]
                self.image.src = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            except Exception:
                pass

            await self.page.client_storage.set_async("last_city", city_raw)

            if spinner in self.page.overlay:
                self.page.overlay.remove(spinner)
            self.page.update()

        except Exception as ex:
            for ctrl in list(self.page.overlay):
                if isinstance(ctrl, ft.ProgressRing):
                    self.page.overlay.remove(ctrl)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
            self.page.overlay.append(self.error_dlg)
            self.error_dlg.content = ft.Text("Failed to fetch weather. Check API key & City.", size=18)
            self.error_dlg.open = True
            self.page.update()
    
    # --- Theme Dark / Light ---
    def _sync_theme_button(self):
        # Show the icon for the *target* mode
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.theme_button.tooltip = "Switch to Light mode"
        else:
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.theme_button.tooltip = "Switch to Dark mode"

    async def _load_theme(self):
        saved = await self.page.client_storage.get_async("theme_mode")
        if saved == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif saved == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        # If none or unknown -> keep whatever you set by default (SYSTEM)
        self._sync_theme_button()
        self.page.update()

    async def toggle_theme(self, e):
        # Toggle Light <-> Dark (if SYSTEM, go to DARK first)
        cur = self.page.theme_mode
        new_mode = ft.ThemeMode.DARK if cur != ft.ThemeMode.DARK else ft.ThemeMode.LIGHT
        self.page.theme_mode = new_mode
        self._sync_theme_button()
        await self.page.client_storage.set_async(
            "theme_mode", "dark" if new_mode == ft.ThemeMode.DARK else "light"
        )
        self.page.update()


    # ---------- UI ----------
    def build(self):
        self.page.title = "WeatherApp"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Create the theme toggle button (icon/tooltip will be synced below)
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,              # placeholder; will be updated by _sync_theme_button()
            tooltip="Switch to Dark mode",
            on_click=self.toggle_theme,           # async handler is fine
        )

        self.page.appbar = ft.AppBar(
            title=ft.Text("WeatherApp"),
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.BLUE_900,
            actions=[self.theme_button],          # <-- puts the button on the upper-right
            center_title=True
        )

        # Make the button reflect the current mode,
        # then load any saved preference from client storage.
        self._sync_theme_button()
        self.page.run_task(self._load_theme)

        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.BLUE_900,
            text="API key",
            shape=ft.RoundedRectangleBorder(radius=40),
            height=45,
            tooltip="Provide API key",
            on_click=self.open_dlg,
        )

        # Dialogs
        self.api_key_field = ft.TextField(hint_text="Please provide API key")
        self.dlg = ft.AlertDialog(
            title=ft.Text("Provide API key"),
            bgcolor=ft.Colors.BLUE_900,
            content=self.api_key_field,
            actions=[
                ft.Row(
                    controls=[
                        ft.TextButton(on_click=self.save_api_key, icon=ft.Icons.CHECK_CIRCLE),
                        ft.TextButton(on_click=lambda _: self.page.close(self.dlg), icon=ft.Icons.CANCEL),
                        ft.TextButton(on_click=self.delete_api_key, icon=ft.Icons.DELETE),
                    ]
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=40)
        )
        self.error_dlg = ft.AlertDialog(
            content=ft.Text("Please provide City and API key.", size=18),
            actions=[
                ft.Row(
                    controls=[ft.TextButton("OK", on_click=lambda _: self.page.close(self.error_dlg))],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
        )

        # Preferences
        self.dd_units = ft.Dropdown(
            label="Units",
            value=self._default_units,
            options=[ft.dropdown.Option("Metric"), ft.dropdown.Option("Imperial")],
            on_change=self.on_pref_change,
            width=220,
        )
        self.dd_lang = ft.Dropdown(
            label="Language",
            value=self._default_lang,
            options=[
                ft.dropdown.Option("En"),
                ft.dropdown.Option("Es"),
                ft.dropdown.Option("De"),
                ft.dropdown.Option("Fr"),
            ],
            on_change=self.on_pref_change,
            width=220,
        )
        prefs_row = ft.Row([self.dd_units, self.dd_lang], alignment=ft.MainAxisAlignment.CENTER)

        # Image & inputs
        self.image = ft.Image(src="weatherapp_icon.png", width=100, height=100)
        self.headline = ft.Text("Current Weather", weight=ft.FontWeight.BOLD, size=24, text_align=ft.TextAlign.CENTER)
        self.city_field = ft.TextField(hint_text="Please choose a City", label="City", on_submit=self.get_weather, width=300)
        self.button = ft.ElevatedButton("Show weather", height=35, on_click=self.get_weather, bgcolor=ft.Colors.BLUE_900)

        # Data labels (values only; headers are handled by panels)
        self.temperature = ft.Text("-", size=18)
        self.weather     = ft.Text("-", size=18)
        self.pressure    = ft.Text("-", size=18)
        self.wind_speed  = ft.Text("-", size=18)
        self.humidity    = ft.Text("-", size=18)
        self.last_update = ft.Text("-", size=18)

        # Multiple Expansion Panels — one per metric
        panels = ft.ExpansionPanelList(
            controls=[
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Temperature")),
                    content=ft.Container(content=self.temperature, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Weather")),
                    content=ft.Container(content=self.weather, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Humidity")),
                    content=ft.Container(content=self.humidity, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Wind Speed")),
                    content=ft.Container(content=self.wind_speed, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Pressure")),
                    content=ft.Container(content=self.pressure, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Updated at")),
                    content=ft.Container(content=self.last_update, padding=10),
                    expanded=True,
                    can_tap_header=True,
                ),
            ],
            elevation=2,
        )

        # Layout
        self.controls.append(
            ft.Column(
                controls=[
                    ft.ResponsiveRow([self.image, self.headline], alignment=ft.MainAxisAlignment.CENTER),
                    prefs_row,
                    ft.Row([self.city_field, self.button], alignment=ft.MainAxisAlignment.CENTER),
                    panels,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            )
        )
