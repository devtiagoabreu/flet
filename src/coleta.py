import flet as ft
import requests

API_BASE = "http://94550ac37bb5.sn.mynetname.net:58244"  # Altere se a porta da sua API for diferente

# Armazena o tema atual (persistente no app)
app_theme = {"mode": ft.ThemeMode.LIGHT}


def sugestao_rolos_view(page: ft.Page):
    pedido_input = ft.TextField(label="Número do Pedido", width=300)
    resultado_info = ft.Text()
    tabela = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    painel_resultado = ft.Container(content=tabela, visible=False)

    def buscar(e):
        pedido = (pedido_input.value or "").strip()
        if not pedido:
            resultado_info.value = "❗ Informe o número do pedido."
            painel_resultado.visible = False
            page.update()
            return

        try:
            response = requests.get(f"{API_BASE}/sugestao-rolos/{pedido}")
            if not response.ok:
                resultado_info.value = f"Erro ao buscar dados: {response.status_code}"
                painel_resultado.visible = False
                page.update()
                return

            dados = response.json()
            if not dados:
                resultado_info.value = "Nenhum item encontrado para este pedido."
                painel_resultado.visible = False
                page.update()
                return

            headers = list(dados[0].keys())
            tabela.controls.clear()

            header_row = ft.Row(
                [ft.Text(h, weight=ft.FontWeight.BOLD, size=12) for h in headers],
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
            )

            tabela.controls.append(
                ft.Container(
                    content=header_row,
                    bgcolor=ft.Colors.BLUE_GREY_100 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLUE_GREY_900,
                    padding=5,
                )
            )

            for item in dados:
                row = ft.Row(
                    [ft.Text(str(item[col]), size=11) for col in headers],
                    wrap=True,
                    alignment=ft.MainAxisAlignment.START,
                )
                tabela.controls.append(
                    ft.Container(
                        content=row,
                        padding=5,
                        border=ft.border.all(0.5, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
                        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                    )
                )

            resultado_info.value = f"✅ {len(dados)} itens encontrados"
            painel_resultado.visible = True
            page.update()

        except Exception as ex:
            resultado_info.value = f"Erro na requisição: {ex}"
            painel_resultado.visible = False
            page.update()

    def abrir_pdf(e):
        pedido = (pedido_input.value or "").strip()
        if pedido:
            page.launch_url(f"{API_BASE}/pdf/sugestao-rolos/{pedido}")

    return ft.Column([
        ft.Text("📦 Sugestão de Rolos", size=24, weight=ft.FontWeight.BOLD),
        pedido_input,
        ft.Row([
            ft.ElevatedButton("🔍 Buscar", on_click=buscar),
            ft.ElevatedButton("📄 PDF", on_click=abrir_pdf),
            ft.ElevatedButton("⬅ Voltar", on_click=lambda e: page.go("/")),
        ], alignment=ft.MainAxisAlignment.START),
        resultado_info,
        ft.Divider(),
        painel_resultado,
    ], spacing=12, expand=True)


def home_view(page: ft.Page):
    def toggle_theme(e):
        app_theme["mode"] = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        page.theme_mode = app_theme["mode"]
        page.update()

    return ft.Column([
        ft.Text("Oráculo Coleta", size=30, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Sugestão de Rolos", on_click=lambda e: page.go("/sugestao")),
        ft.ElevatedButton("🌙 Alternar Tema", on_click=toggle_theme),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)


def main(page: ft.Page):
    page.title = "Oráculo Coleta"
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme_mode = app_theme["mode"]

    # Paleta personalizada para tema escuro
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.CYAN,
            on_surface=ft.Colors.WHITE,
            background=ft.Colors.BLACK,
        )
    )

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", controls=[home_view(page)]))
        elif page.route == "/sugestao":
            page.views.append(ft.View("/sugestao", controls=[sugestao_rolos_view(page)]))
        page.update()

    page.on_route_change = route_change
    page.go("/")


ft.app(target=main, view="web_browser")
