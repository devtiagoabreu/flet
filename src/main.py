import flet as ft

def main(page: ft.Page):
  
  page.window.always_on_top = True
  page.window.title_bar_hidden = False
  page.window.frameless = False
  page.window.bgcolor = ft.Colors.TRANSPARENT
  page.window.full_screen = False
  page.window.height = 500
  page.window.max_height = 800
  page.window.min_height = 300
  page.window.width = 500
  page.window.max_width = 800
  page.window.min_width = 300
  page.window.resizable = True
  page.window.movable = False
  #page.window.top = 100
  #page.window.left = 100
  page.window.center()

  def page_resize(e):
    print("Tamanho:", page.window.height, page.window.width)

  page.on_resized = page_resize


  print(page.platform)


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