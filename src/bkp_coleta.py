import flet as ft
import requests
from typing import Dict, Optional
import logging
from functools import partial

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações da aplicação
class AppConfig:
    API_BASE = "http://94550ac37bb5.sn.mynetname.net:58244"
    DEFAULT_CARD_WIDTH = 260.0
    MOBILE_BREAKPOINT = 500.0
    MIN_CARD_WIDTH = 200.0
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8500
    ASSETS_DIR = "assets"

class ResponsiveCard(ft.Container):
    """Componente de card responsivo com tratamento robusto de erros"""
    
    def __init__(self, item_data: Dict, page: ft.Page):
        self.page = page
        self.item_data = item_data or {}
        super().__init__(
            padding=12,
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            content=self._build_content(),
            width=self._calculate_safe_width(),
            on_hover=self._on_card_hover
        )

    def _calculate_safe_width(self) -> float:
        """Calcula largura com tratamento completo de erros"""
        try:
            if not hasattr(self, 'page') or not hasattr(self.page, 'width'):
                return AppConfig.DEFAULT_CARD_WIDTH
                
            page_width = getattr(self.page, 'width', None)
            if page_width is None:
                return AppConfig.DEFAULT_CARD_WIDTH
                
            try:
                width = float(page_width)
                if width >= AppConfig.MOBILE_BREAKPOINT:
                    return AppConfig.DEFAULT_CARD_WIDTH
                calculated = width * 0.85
                return max(calculated, AppConfig.MIN_CARD_WIDTH)
            except (TypeError, ValueError):
                return AppConfig.DEFAULT_CARD_WIDTH
                
        except Exception as e:
            logger.error(f"Erro ao calcular largura: {str(e)}")
            return AppConfig.DEFAULT_CARD_WIDTH

    def _build_content(self) -> ft.Column:
        """Constrói conteúdo do card de forma segura"""
        try:
            fields = [
                ("Produto", self._get_data('Produto')),
                ("Cor", self._get_data('Cor')),
                ("Qtde Item", self._get_data('Qtde_Item')),
                ("Qtde Saldo", self._get_data('Qtde_Saldo')),
                ("SubLote", self._get_data('Sublote', self._get_data('SubLote', '---'))),
                ("Gavetas", self._get_data('Gavetas')),
                ("Qtde Peças", self._get_data('Qtde_Pecas')),
                ("Total Metros", self._get_data('Total_Metros')),
                ("Rolos", f"{self._get_data('Rolos')}")
            ]
            
            return ft.Column(
                controls=[
                    ft.Text(f"{label}: {value}", 
                          weight=ft.FontWeight.BOLD if idx == 0 else None)
                    for idx, (label, value) in enumerate(fields)
                ],
                spacing=4
            )
        except Exception as e:
            logger.error(f"Erro ao construir card: {str(e)}")
            return ft.Column(controls=[ft.Text("Erro ao carregar dados")])

    def _get_data(self, key: str, default: str = "") -> str:
        """Método seguro para obter dados do item"""
        return str(self.item_data.get(key, default)).strip()

    def _on_card_hover(self, e: ft.ControlEvent):
        """Efeito hover no card"""
        self.bgcolor = ft.Colors.SURFACE if not e.data == "true" else ft.Colors.SECONDARY_CONTAINER
        self.update()

class SugestaoRolosView:
    """View de sugestão de rolos com gerenciamento de estado"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_ui()
        self._setup_event_handlers()

    def _setup_ui(self):
        """Configura componentes UI"""
        self.pedido_input = ft.TextField(
            label="Número do Pedido",
            width=300,
            autofocus=True,
            value=""
        )
        
        self.resultado_info = ft.Text()
        self.lista_resultados = ft.Column(expand=True, spacing=10)
        self.painel_resultado = ft.Container(
            content=self.lista_resultados,
            visible=False
        )

    def _setup_event_handlers(self):
        """Configura handlers de eventos"""
        self.buscar_handler = partial(self._buscar_pedido)
        self.pdf_handler = partial(self._abrir_pdf)

    def _buscar_pedido(self, e: ft.ControlEvent):
        """Busca dados do pedido na API"""
        try:
            pedido = self.pedido_input.value.strip()
            if not pedido:
                self._update_ui("❗ Informe o número do pedido.", False)
                return

            self._update_ui("🔍 Buscando dados...", False)
            
            response = requests.get(
                f"{AppConfig.API_BASE}/sugestao-rolos/{pedido}",
                timeout=10
            )
            response.raise_for_status()

            dados = response.json() or []
            self._exibir_resultados(dados)
            
        except requests.exceptions.RequestException as e:
            self._update_ui(f"⚠️ Erro na conexão: {str(e)}", False)
        except Exception as e:
            self._update_ui(f"❌ Erro inesperado: {str(e)}", False)

    def _exibir_resultados(self, dados: list):
        """Exibe os resultados na UI"""
        try:
            self.lista_resultados.controls.clear()
            
            row_cartoes = ft.Row(
                wrap=True,
                spacing=12,
                run_spacing=12,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            for item in dados:
                if isinstance(item, dict):
                    row_cartoes.controls.append(ResponsiveCard(item, self.page))

            self.lista_resultados.controls.append(row_cartoes)
            self._update_ui(f"✅ {len(dados)} itens encontrados", True)
            
        except Exception as e:
            self._update_ui(f"❌ Erro ao exibir resultados: {str(e)}", False)

    def _update_ui(self, mensagem: str, mostrar_resultados: bool):
        """Atualiza a UI de forma consistente"""
        self.resultado_info.value = mensagem
        self.painel_resultado.visible = mostrar_resultados
        self.page.update()

    def _abrir_pdf(self, e: ft.ControlEvent):
        """Abre PDF do pedido"""
        try:
            pedido = self.pedido_input.value.strip()
            if pedido:
                self.page.launch_url(f"{AppConfig.API_BASE}/pdf/sugestao-rolos/{pedido}")
        except Exception as e:
            logger.error(f"Erro ao abrir PDF: {str(e)}")

    def get_view(self) -> ft.Column:
        """Retorna a view configurada"""
        return ft.Column(
            controls=[
                ft.Text("📦 Sugestão de Rolos", size=22, weight=ft.FontWeight.BOLD),
                self.pedido_input,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("🔍 Buscar", on_click=self.buscar_handler),
                        ft.ElevatedButton("📄 Gerar PDF", on_click=self.pdf_handler),
                        ft.ElevatedButton("⬅ Voltar", on_click=lambda _: self.page.go("/")),
                    ],
                    spacing=10
                ),
                self.resultado_info,
                ft.Divider(),
                self.painel_resultado,
            ],
            spacing=12,
            expand=True
        )

def main(page: ft.Page) -> None:
    """Configuração principal da aplicação"""
    try:
        # Configurações da página
        page.title = "Oráculo Coleta - Produção"
        page.scroll = ft.ScrollMode.ADAPTIVE
        page.padding = 20
        page.theme_mode = ft.ThemeMode.LIGHT

        # Configuração de tema
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_700,
                secondary=ft.Colors.CYAN_600,
                surface=ft.Colors.GREY_100,
            )
        )
        
        page.dark_theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                surface=ft.Colors.GREY_900,
            )
        )

        def route_change(e: ft.RouteChangeEvent) -> None:
            """Gerencia navegação entre views"""
            try:
                page.views.clear()
                
                if e.route == "/":
                    page.views.append(ft.View("/", [home_view(page)]))
                elif e.route == "/sugestao":
                    view = SugestaoRolosView(page)
                    page.views.append(ft.View("/sugestao", [view.get_view()]))
                    
                page.update()
            except Exception as ex:
                logger.error(f"Erro na navegação: {str(ex)}")

        page.on_route_change = route_change
        page.go(page.route or "/")
        
    except Exception as ex:
        logger.critical(f"Falha na inicialização: {str(ex)}")
        raise

def home_view(page: ft.Page) -> ft.Column:
    """View inicial da aplicação"""
    def toggle_theme(e: ft.ControlEvent) -> None:
        """Alterna entre temas claro/escuro"""
        try:
            page.theme_mode = (
                ft.ThemeMode.DARK 
                if page.theme_mode == ft.ThemeMode.LIGHT 
                else ft.ThemeMode.LIGHT
            )
            page.update()
        except Exception as e:
            logger.error(f"Erro ao alternar tema: {str(e)}")

    return ft.Column(
        controls=[
            ft.Text("Oráculo Coleta", size=30, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "📦 Sugestão de Rolos", 
                on_click=lambda e: page.go("/sugestao")
            ),
            ft.ElevatedButton(
                "🌗 Alternar Tema", 
                on_click=toggle_theme
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

if __name__ == "__main__":
    # Configuração para deploy em produção
    ft.app(
        target=main,
        view=None,  # Sem abrir navegador automaticamente
        host=AppConfig.SERVER_HOST,
        port=AppConfig.SERVER_PORT,
        assets_dir=AppConfig.ASSETS_DIR,
        # upload_dir=AppConfig.ASSETS_DIR,  # Descomente se precisar de uploads
    )