"""
Main entry point for the WeatherApp application.

This script initializes the Flet application and loads the HomepageView.

Variables:
    page (ft.Page): The root application container provided by Flet, representing
                    the UI window or web page context.

Functions:
    main(page: ft.Page): Instantiates the main HomepageView and adds it to the page.
"""
import flet as ft
from homepage import HomepageView

def main(page: ft.Page):
    """
    Main function to configure the Flet application page.

    Input:
        page (ft.Page): The Flet page instance.

    Output:
        Adds the HomepageView to the page and triggers a UI update.
    """
    home = HomepageView(page)
    page.add(home)
    page.update()

# Start the application in a web browser view
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
