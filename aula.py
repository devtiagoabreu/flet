import flet as ft

def main(page: ft.Page):
  mensagem = ft.Text(value='Olá Mundo!')
  page.add(mensagem)

ft.app(target = main)  