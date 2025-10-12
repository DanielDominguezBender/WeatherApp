import flet as ft
from homepage import HomepageView

def main(page: ft.Page):
    home = HomepageView(page)
    page.add(home)
    page.update()

ft.app(target=main)
