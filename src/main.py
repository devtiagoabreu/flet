import flet as ft

def main(page: ft.Page):
  page.fonts = {
    'kanit': 'https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf',
    'blankScript': 'fonts/Blank_Script.otf',
  }

  t1 = ft.Text(
    value = "Teste de texto!!!",
    style = ft.TextThemeStyle.DISPLAY_LARGE,
    #bgcolor = ft.Colors.WHITE,
    color = ft.Colors.AMBER,
    font_family = 'blankScript',
    max_lines = 2,
    overflow = ft.TextOverflow.ELLIPSIS,
    selectable = True,
    size = 50,
    text_align = ft.TextAlign.JUSTIFY,
    weight = ft.FontWeight.BOLD,

  )

  link_style = ft.TextStyle(color = ft.Colors.BLUE)

  t2 = ft.Text(
    spans = [
      ft.TextSpan(text='wow ', style = link_style),
      ft.TextSpan(text='wow ', url='http://wow.com.br'),
      ft.TextSpan(text='wow '),
    ]

  )

  page.add(t1,t2)

  
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
  ft.app(target = main, assets_dir = 'assets')