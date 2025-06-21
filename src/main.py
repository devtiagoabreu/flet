import flet as ft

def main(page: ft.Page):
  
  page.window.always_on_top = True
  page.window.title_bar_hidden = False
  page.window.frameless = False
  page.window.bgcolor = ft.Colors.TRANSPARENT
  
  page.bgcolor = ft.Colors.TRANSPARENT

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

if __name__ == '__main__':
  ft.app(target = main)