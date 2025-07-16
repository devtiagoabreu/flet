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
    SERVER_HOST = "LOCALHOST"
    SERVER_PORT = 57244
    ASSETS_DIR = "assets"
    CARD_HEIGHT = 300.0  # Altura fixa para os cards
    ROLOS_HEIGHT = 120.0  # Altura aumentada para o campo Rolos

class ResponsiveCard(ft.Container):
    """Componente de card responsivo com altura fixa e rolagem no campo Rolos"""
    
    def __init__(self, item_data: Dict, page: ft.Page):
        self.page = page
        self.item_data = item_data or {}
        super().__init__(
            padding=12,
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            content=self._build_content(),
            width=self._calculate_safe_width(),
            height=AppConfig.CARD_HEIGHT,  # Altura fixa para todos os cards
            on_hover=self._on_card_hover
        )

    def _calculate_safe_width(self) -> float:
        """Calcula largura com tratamento completo de erros"""
        try:
            if not hasattr(self, 'page') or not hasattr(self.page, 'window'):
                return AppConfig.DEFAULT_CARD_WIDTH
                
            page_width = getattr(self.page.window, 'width', None)
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
        """Constrói conteúdo do card com rolagem no campo Rolos"""
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
            ]
            
            # Campo Rolos com rolagem interna usando ListView
            rolos_content = self._get_data('Rolos')
            rolos_container = ft.ListView(
                controls=[ft.Text(rolos_content, selectable=True)],
                height=AppConfig.ROLOS_HEIGHT,  # Altura aumentada para melhor interação
                auto_scroll=True,  # Melhora rolagem em dispositivos móveis
                padding=5,
                expand=False  # Evita expansão desnecessária
            )
            
            return ft.Column(
                controls=[
                    ft.Text(f"{label}: {value}", 
                           weight=ft.FontWeight.BOLD if idx == 0 else None)
                    for idx, (label, value) in enumerate(fields)
                ] + [
                    ft.Text("Rolos:", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=rolos_container,
                        padding=5,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5
                    )
                ],
                spacing=4,
                expand=True,
                scroll=ft.ScrollMode.HIDDEN  # Desativa rolagem no Column externo
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
    """View de sugestão de rolos com rolagem corrigida"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_ui()
        self._setup_event_handlers()

    def _setup_ui(self):
        """Configura componentes UI com rolagem adequada"""
        self.pedido_input = ft.TextField(
            label="Número do Pedido",
            width=300,
            autofocus=True,
            value=""
        )
        
        self.resultado_info = ft.Text()
        
        self.lista_resultados = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=False
        )
        
        self.painel_resultado = ft.Container(
            content=self.lista_resultados,
            visible=False,
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=10,
        )

    def _setup_event_handlers(self):
        """Configura handlers de eventos"""
        self.buscar_handler = partial(self._buscar_pedido)
        self.pdf_handler = partial(self._abrir_pdf)
        self.page.on_resize = self._on_resize

    def _on_resize(self, e: ft.ControlEvent):
        """Atualiza dimensões do painel ao redimensionar"""
        try:
            self.painel_resultado.height = self.page.window.height * 0.7 if self.page.window.height else 500
            self.page.update()
        except Exception as e:
            logger.error(f"Erro ao redimensionar: {str(e)}")

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
        """Exibe os resultados na UI com rolagem adequada"""
        try:
            self.lista_resultados.controls.clear()
            
            grid = ft.GridView(
                expand=True,
                runs_count=1 if self.page.window.width < AppConfig.MOBILE_BREAKPOINT else 3,  # Ajusta colunas em telas pequenas
                max_extent=300,
                child_aspect_ratio=0.8,
                spacing=20,  # Espaço horizontal
                run_spacing=20,  # Espaço vertical
                padding=10
            )

            for item in dados:
                if isinstance(item, dict):
                    grid.controls.append(ResponsiveCard(item, self.page))

            self.lista_resultados.controls.append(grid)
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
        """Retorna a view configurada com rolagem adequada"""
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
                ft.Container(
                    content=self.painel_resultado,
                    expand=True,
                    height=self.page.window.height * 0.7 if self.page.window.height else 500
                )
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

def main(page: ft.Page) -> None:
    """Configuração principal da aplicação"""
    try:
        # Configurações da página
        page.title = "Oráculo Coleta - Produção"
        page.scroll = ft.ScrollMode.AUTO
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

        # Log da plataforma para depuração
        logger.info(f"Plataforma em execução: {page.platform}")

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
    # Configuração para deploy em produção (modo web)
    try:
        ft.app(
            target=main,
            view=ft.WEB_BROWSER,  # Configurado para modo web
            host=AppConfig.SERVER_HOST,
            port=AppConfig.SERVER_PORT,
            assets_dir=AppConfig.ASSETS_DIR
        )
    except Exception as ex:
        logger.critical(f"Erro ao iniciar ft.app: {str(ex)}")
        raise