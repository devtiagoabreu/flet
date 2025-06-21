import flet as ft

def main(page: ft.Page):
  page.bgcolor = "#d6b108"

  page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
  page.vertical_alignment = ft.MainAxisAlignment.CENTER

  page.padding = ft.padding.all(100)
  page.spacing = 100
  page.title = 'Flet App'

  page.add(
    ft.Text(value = 'Olá mundo!'),
    ft.Container(ft.Text(value='Olá Mundo'), bgcolor='black')
  )





  page.update()

ft.app(target = main)  