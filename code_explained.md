#🧩Step-by-Step Explanation: main.py

```python
import flet as ft
from homepage import HomepageView
````

🔹Step 1: Import Required Modules

- flet as ft: This imports the Flet UI framework, which lets you build modern apps with Python.
- from homepage import HomepageView: Imports the main view class of your app, which defines the whole interface and logic, from the homepage.py file.

```python
def main(page: ft.Page):
    home = HomepageView(page)
    page.add(home)
    page.update()
```

🔹Step 2: Define the Main Function

This function gets called when the app starts. Let’s break it down:

- def main(page: ft.Page): Flet passes the main page object to this function. It's like the canvas where your app will be drawn.
- home = HomepageView(page): Creates an instance of the HomepageView class (the UI and logic) and pass it the page.
- page.add(home): Adds the HomepageView to the current page — this renders it visually.
- page.update(): to refresh the UI.

🔹Step 3: Launch the App

- This tells Flet: “Run the app, and start by calling the main() function.”
- It works whether you’re running on desktop or in the browser.

```python
ft.app(target=main)
```

✅ What main.py does in simple terms:

It loads Flet, grabs the custom homepage layout, and tells Flet to render it inside a new app window or browser tab.


#🧩Step-by-Step Explanation: homepage.py

🔹Step 1: Class Definition

```python
class HomepageView(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        ...
```

- Defines a custom component (HomepageView) that acts as a main layout.
- It extends ft.Column, so it stacks UI elements vertically.
- self.page allows interaction with the global app (theme, storage, dialogs, etc.)


🔹Step 2: Dialog Boxes

```python
async def open_dlg(self, e):
    ...
async def save_api_key(self, e):
    ...
async def delete_api_key(self, e):
    ...
```

These methods manage the API key dialog:

-Open the dialog
-Save the key in local storage
-Delete the stored key


🔹Step 3: Preferences Handling

```python
async def on_pref_change(self, e):
    ...
````
- Called when the user changes the language or units dropdown.
- Stores preferences locally and fetches weather again if a city is set.


🔹Step 4: Fetch Weather Data

```python
async def get_weather(self, e):
    ...
```

This is the heart of the app:

1. Reads API key, city, language, units from UI and local storage.
2. Builds the API URL:

```python
url = f\"https://api.openweathermap.org/data/2.5/weather?q=...&appid=...&units=...&lang=...\"
```

3. Makes HTTPS request to OpenWeatherMap.
4. Parses JSON response and extracts:
- Temperature
- Weather condition
- Humidity
- Pressure
- Wind speed
- Timestamp

5. Updates the UI elements (self.temperature, etc.).
6. Handles and shows errors gracefully if the API fails.


🔹Step 5: Theme Toggle

```python
def _sync_theme_button(self):
    ...
async def _load_theme(self):
    ...
async def toggle_theme(self, e):
    ...
````

- Handles switching between dark/light mode
- Saves the preference in local storage
- Syncs the icon in the top bar to reflect the current theme


🔹Step 6: Visual Layout with build()

```python
def build(self):
    ...
```

This is where your UI gets constructed:

- AppBar with title and theme switcher
- Floating button to set API key
- Dropdowns to choose language and units
- City input field + “Show weather” button
- Icon image + headline
- Expansion Panels for each metric (temperature, humidity, etc.)
- All controls are organized inside ft.Column and ft.ResponsiveRow


🔹Step 7: Panel Content

```python
self.temperature = ft.Text(\"-\")
self.humidity = ft.Text(\"-\")
...
```


## To summarize
homepage.py is the app’s UI + logic core. It builds the interface, handles input, fetches data from the API, manages theme, local storage, and shows the final weather result — all inside a single class.