# -------------------------------
# WEATHERAPP HOMEPAGE VIEW
# -------------------------------
# This file defines the main interface of the "WeatherApp" application,
# built with the Flet framework (similar to Flutter, but for Python).
# It allows the user to input a city, fetch weather data
# from the OpenWeatherMap API, and visualize the information in a dashboard.
# -------------------------------

# Import necessary libraries
import flet as ft
import json
import sys
from datetime import datetime

# Depending on the operating system, import modules to make secure HTTP requests
if sys.platform in ["android", "ios", "emscripten"]:
    import urllib.request
    import ssl
elif sys.platform in ["linux", "win32", "darwin"]:
    import urllib.request
    import ssl


# -------------------- MAIN CLASS: HOMEPAGEVIEW --------------------
# This class represents the main screen of the app.
# It inherits from ft.Column to organize the elements in a column format.
class HomepageView(ft.Column):
    """
    HomepageView defines the layout and behavior for the main weather dashboard.
    It manages the UI state, user preferences (API key, language, units), and fetches
    data from the OpenWeatherMap API.

    Attributes:
        page (ft.Page): The main Flet page instance used to add overlays, update UI, and access client storage.
        _default_units (str): The default measurement unit ("Metric" or "Imperial").
        _default_lang (str): The default language code for API responses (e.g., "En").
        data (dict | None): The JSON response payload from the OpenWeatherMap API.
    """
    def __init__(self, page):
        super().__init__()
        self.page = page
        self._default_units = "Metric"  # Default units: metric or imperial
        self._default_lang = "En"       # Default language: English
        self.data = None                # Variable where weather data is stored

    # ---------- DIALOGS ----------
    # Opens a dialog to input or view the API key
    async def open_dlg(self, e):
        """
        Opens the dialog for the user to view or enter their OpenWeatherMap API key.

        Args:
            e (ft.ControlEvent): The event object triggered by clicking the FAB.
        """
        self.api_key_field.value = await self.page.client_storage.get_async("api_key")
        self.page.overlay.append(self.dlg)
        self.dlg.open = True
        self.page.update()

    # Saves the API key introduced by the user
    async def save_api_key(self, e):
        """
        Saves the provided API key to the client's local storage and closes the dialog.

        Args:
            e (ft.ControlEvent): The event object triggered by the save button.
        """
        await self.page.client_storage.set_async("api_key", self.api_key_field.value)
        self.dlg.open = False
        self.page.update()

    # Deletes the stored API key
    async def delete_api_key(self, e):
        """
        Removes the API key from the client's local storage and clears the input field.

        Args:
            e (ft.ControlEvent): The event object triggered by the delete button.
        """
        await self.page.client_storage.remove_async("api_key")
        self.api_key_field.value = ""
        self.page.update()

    # ---------- PREFERENCES ----------
    # Executes when the user changes language, units or city.
    # Saves changes and updates the weather view.
    async def on_pref_change(self, e):
        """
        Event handler for preference changes (dropdowns for units or language).
        Saves the new preferences to client storage and triggers a weather data refresh.

        Args:
            e (ft.ControlEvent): The event object triggered by changing a dropdown value.
        """
        if self.dd_units.value:
            await self.page.client_storage.set_async("units", self.dd_units.value)
        if self.dd_lang.value:
            await self.page.client_storage.set_async("lang", self.dd_lang.value)
        if (self.city_field.value or "").strip():
            await self.get_weather(None)

    # ---------- FETCH AND SHOW WEATHER DATA ----------
    # Performs the API call to OpenWeatherMap to get the weather data.
    async def get_weather(self, e):
        """
        Fetches the current weather data from OpenWeatherMap using the stored API key and city.
        Updates the UI elements with the parsed data.

        Args:
            e (ft.ControlEvent | None): The event object triggered by button click or enter key, or None if called programmatically.
        
        Input: 
            Reads 'api_key' from client storage.
            Reads 'city_field.value' from the UI input.
            Reads preferences ('units', 'lang') from UI dropdowns.
            
        Output:
            Updates the UI text labels (temperature, weather description, pressure, wind_speed, humidity, last_update).
            Updates the weather icon image.
        """
        try:
            # Retrieve API key and inputted city
            api_key = await self.page.client_storage.get_async("api_key")
            city_raw = (self.city_field.value or "").strip()

            # Validate that both fields are present
            if not api_key and not city_raw:
                self.error_dlg.content = ft.Text("Please provide BOTH City and API key.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return
            if not api_key:
                self.error_dlg.content = ft.Text("Please provide the API key.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return
            if not city_raw:
                self.error_dlg.content = ft.Text("Please provide a City.", size=18)
                self.page.overlay.append(self.error_dlg); self.error_dlg.open = True; self.page.update(); return

            # Read user preferences or use defaults
            units = self.dd_units.value or self._default_units
            lang  = self.dd_lang.value  or self._default_lang

            # Show a loading spinner while the request is being made
            spinner = ft.ProgressRing()
            self.page.overlay.append(spinner); self.page.update()

            # Prepare the city for URL inclusion (replaces spaces and special characters)
            city_q = city_raw.replace(" ", "+").translate(
                str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "β": "ss"})
            )

            # Build the API URL with the appropriate parameters
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?q={city_q}&appid={api_key}&lang={lang}&units={units}"
            )

            # Make the API request using HTTPS
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(url, context=ctx) as response:
                self.data = json.loads(response.read())

            # Check if there was an error in the response (e.g., city not found)
            cod = self.data.get("cod", 200)
            if (isinstance(cod, str) and cod != "200") or (isinstance(cod, int) and cod != 200):
                msg = self.data.get("message", "Unknown error")
                raise RuntimeError(f"OpenWeather error: {msg}")

            # Process and convert the received values
            temp_val  = round(self.data["main"]["temp"], 1)
            temp_unit = "°C" if units == "Metric" else "°F"

            # Convert wind speed according to the selected units
            wind_raw = self.data["wind"]["speed"]
            if units == "Metric":
                wind_val, wind_unit = round(wind_raw * 3.6, 1), "km/h"   # API returns m/s
            else:
                wind_val, wind_unit = round(wind_raw, 1), "mph"

            # Update the UI labels with the current values
            self.temperature.value = f"{temp_val} {temp_unit}"
            self.weather.value     = f"{self.data['weather'][0]['description']}"
            self.pressure.value    = f"{self.data['main']['pressure']} hPa"
            self.wind_speed.value  = f"{wind_val} {wind_unit}"
            self.humidity.value    = f"{self.data['main']['humidity']} %"
            self.last_update.value = datetime.fromtimestamp(self.data["dt"]).strftime("%d/%m/%Y %H:%M:%S")

            # Load the icon corresponding to the weather status
            try:
                icon_code = self.data["weather"][0]["icon"]
                self.image.src = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            except Exception:
                pass

            # Save the last searched city
            await self.page.client_storage.set_async("last_city", city_raw)

            # Hide the loading spinner and update the interface
            if spinner in self.page.overlay:
                self.page.overlay.remove(spinner)
            self.page.update()

        except Exception as ex:
            # If an error occurs, remove any visible spinner and show notification
            for ctrl in list(self.page.overlay):
                if isinstance(ctrl, ft.ProgressRing):
                    self.page.overlay.remove(ctrl)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
            self.page.overlay.append(self.error_dlg)
            self.error_dlg.content = ft.Text("Failed to fetch weather. Check API key & City.", size=18)
            self.error_dlg.open = True
            self.page.update()
    
    # --- THEME MANAGEMENT (LIGHT / DARK) ---
    # Synchronizes the button icon with the current theme
    def _sync_theme_button(self):
        """
        Updates the theme toggle button icon to reflect the opposite of the current theme.
        """
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.theme_button.tooltip = "Switch to Light mode"
        else:
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.theme_button.tooltip = "Switch to Dark mode"

    # Loads the saved theme from local storage
    async def _load_theme(self):
        """
        Loads the user's previously saved theme mode (light or dark) from client storage
        and applies it to the app.
        """
        saved = await self.page.client_storage.get_async("theme_mode")
        if saved == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif saved == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self._sync_theme_button()
        self.page.update()

    # Toggles between light and dark mode, and saves the preference
    async def toggle_theme(self, e):
        """
        Toggles the application theme between Light and Dark mode, updates the button icon,
        and saves the new preference to client storage.

        Args:
            e (ft.ControlEvent): The event object triggered by the theme toggle button.
        """
        cur = self.page.theme_mode
        new_mode = ft.ThemeMode.DARK if cur != ft.ThemeMode.DARK else ft.ThemeMode.LIGHT
        self.page.theme_mode = new_mode
        self._sync_theme_button()
        await self.page.client_storage.set_async(
            "theme_mode", "dark" if new_mode == ft.ThemeMode.DARK else "light"
        )
        self.page.update()

    # ---------- INTERFACE BUILD ----------
    def build(self):
        """
        Constructs and returns the UI layout for the homepage.
        This method initializes all controls (buttons, text fields, dialogs, cards) 
        and arranges them in a central column layout.
        
        Returns:
            None (It modifies the self.controls list to append the UI tree).
        """
        # Configures the title, theme and alignment of the main page
        self.page.title = "WeatherApp"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Theme toggle button (dark / light)
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Switch to Dark mode",
            on_click=self.toggle_theme,
        )

        # Top app bar with the title and theme button
        self.page.appbar = ft.AppBar(
            title=ft.Text("WeatherApp"),
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.BLUE_900,
            actions=[self.theme_button],
            center_title=True
        )

        self._sync_theme_button()
        self.page.run_task(self._load_theme)

        # Floating action button to manage the API key
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.BLUE_900,
            text="API key",
            shape=ft.RoundedRectangleBorder(radius=40),
            height=45,
            tooltip="Provide API key",
            on_click=self.open_dlg,
        )

        # ---------- DIALOGS ----------
        # Dialog box to input the API key
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

        # Generic dialog to show errors
        self.error_dlg = ft.AlertDialog(
            content=ft.Text("Please provide City and API key.", size=18),
            actions=[
                ft.Row(
                    controls=[ft.TextButton("OK", on_click=lambda _: self.page.close(self.error_dlg))],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
        )

        # ---------- PREFERENCES ----------
        # Dropdowns for language and units
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

        # ---------- MAIN SECTION ----------
        # Image, city field and query button
        self.image = ft.Image(src="weatherapp_icon.png", width=100, height=100)
        self.headline = ft.Text("Current Weather", weight=ft.FontWeight.BOLD, size=24, text_align=ft.TextAlign.CENTER)
        self.city_field = ft.TextField(hint_text="Please choose a City", label="City", on_submit=self.get_weather, width=300)
        self.button = ft.ElevatedButton("Show weather", height=35, on_click=self.get_weather, bgcolor=ft.Colors.BLUE_900)

        # Labels to show data (filled when querying the API)
        self.temperature = ft.Text("-", size=18)
        self.weather     = ft.Text("-", size=18)
        self.pressure    = ft.Text("-", size=18)
        self.wind_speed  = ft.Text("-", size=18)
        self.humidity    = ft.Text("-", size=18)
        self.last_update = ft.Text("-", size=18)

        # ---------- DASHBOARD UI ----------
        def create_card(title, content, icon=None):
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([ft.Icon(icon, size=20, color=ft.Colors.BLUE_500), ft.Text(title, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER) if icon else ft.Text(title, weight=ft.FontWeight.BOLD),
                            content,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    padding=20,
                    width=160,
                    height=100,
                    alignment=ft.alignment.center,
                ),
                elevation=4,
            )

        dashboard = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Temperature & Weather", weight=ft.FontWeight.BOLD, size=16),
                                        ft.Row([self.temperature, self.weather], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=20,
                                width=340,
                                alignment=ft.alignment.center,
                            ),
                            elevation=6,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        create_card("Humidity", self.humidity, ft.Icons.WATER_DROP),
                        create_card("Wind", self.wind_speed, ft.Icons.AIR),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        create_card("Pressure", self.pressure, ft.Icons.SPEED),
                        create_card("Updated at", self.last_update, ft.Icons.UPDATE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # ---------- FINAL STRUCTURE ----------
        # All page elements are organized in a central column
        self.controls.append(
            ft.Column(
                controls=[
                    ft.ResponsiveRow([self.image, self.headline], alignment=ft.MainAxisAlignment.CENTER),
                    prefs_row,
                    ft.Row([self.city_field, self.button], alignment=ft.MainAxisAlignment.CENTER),
                    dashboard,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
