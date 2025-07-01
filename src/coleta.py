import flet as ft
import requests

API_BASE = "http://94550ac37bb5.sn.mynetname.net:58244"  # Altere para o endereço da sua API

# ========== TELA: Sugestão de Rolos ==========
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
            header_row = ft.Row(
                [ft.Text(h, weight=ft.FontWeight.BOLD, size=12) for h in headers],
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
            )

            tabela.controls.clear()
            tabela.controls.append(ft.Container(content=header_row, bgcolor=ft.Colors.GREY_200, padding=5))

            for item in dados:
                row = ft.Row(
                    [ft.Text(str(item[col]), size=11) for col in headers],
                    wrap=True,
                    alignment=ft.MainAxisAlignment.START,
                )
                tabela.controls.append(ft.Container(content=row, padding=5, border=ft.border.all(0.5, ft.Colors.GREY_300)))

            resultado_info.value = f"✅ {len(dados)} itens encontrados"
            painel_resultado.visible = True
            page.update()

        except Exception as ex:
            resultado_info.value = f"Erro na requisição: {ex}"
            painel_resultado.visible = False
            page.update()

    def imprimir(e):
        page.launch_url("javascript:window.print();")

    return ft.Column([
        ft.Text("📦 Sugestão de Rolos", size=24, weight=ft.FontWeight.BOLD),
        pedido_input,
        ft.Row([
            ft.ElevatedButton("🔍 Buscar", on_click=buscar),
            ft.ElevatedButton("🖨️ Imprimir", on_click=imprimir),
            ft.ElevatedButton("⬅ Voltar", on_click=lambda e: page.go("/")),
        ], alignment=ft.MainAxisAlignment.START),
        resultado_info,
        ft.Divider(),
        painel_resultado,
    ], spacing=12, expand=True)


# ========== TELA: Tela Inicial ==========
def home_view(page: ft.Page):
    return ft.Column([
        ft.Text("Oráculo Coleta", size=30, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Sugestão de Rolos", on_click=lambda e: page.go("/sugestao")),
        ft.ElevatedButton("Sair", on_click=lambda e: page.window_close())
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)


# ========== MAIN APP ==========
def main(page: ft.Page):
    page.title = "Oráculo Coleta"
    page.padding = 10
    page.scroll = ft.ScrollMode.ALWAYS

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", controls=[home_view(page)]))
        elif page.route == "/sugestao":
            page.views.append(ft.View("/sugestao", controls=[sugestao_rolos_view(page)]))
        page.update()

    page.on_route_change = route_change
    page.go("/")


# ========== EXECUTA ==========
ft.app(target=main, view=ft.WEB_BROWSER)
