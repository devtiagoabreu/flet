import flet as ft
from flet import Icons
import pandas as pd

def main(page: ft.Page):
    page.title = "Gerador de SQL para CTE_peca"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 700
    page.window_height = 600
    page.padding = 20

    output_text = ft.Text()
    sql_preview = ft.TextField(
        label="Prévia do SQL gerado",
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=20,
        expand=True
    )

    download_button = ft.ElevatedButton(
        "Baixar SQL",
        icon=Icons.DOWNLOAD,
        visible=False
    )

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def gerar_update_sql(df: pd.DataFrame) -> str:
        df['NRO_ROLO'] = df['NRO_ROLO'].astype(str).str.zfill(10)
        df['NRO_PECA'] = df['NRO_PECA'].astype(int).astype(str).str.zfill(3)
        df['AVISO'] = df['AVISO'].astype(str).str.zfill(6)
        df['TEAR'] = df['TEAR'].astype(str).str.zfill(6)

        updates = []
        for _, row in df.iterrows():
            updates.append(
                f"""UPDATE CTE_peca
SET Tear = '{row['TEAR']}', Num_Etq_Aux = '{row['Num_Etq_Aux']}'
WHERE Nro_rolo = '{row['NRO_ROLO']}' AND Nro_peca = '{row['NRO_PECA']}' AND Sublote = '{row['LOTE']}' AND Aviso = '{row['AVISO']}';\n"""
            )
        return "\n".join(updates)

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal sql_path
        if not e.files:
            output_text.value = "Nenhum arquivo selecionado."
            page.update()
            return

        try:
            file = e.files[0]
            df = pd.read_csv(file.path, sep=';')
            sql_content = gerar_update_sql(df)

            sql_preview.value = sql_content[:3000]  # Mostra apenas os primeiros 3000 caracteres
            sql_path = "atualizar_CTE_peca.sql"
            with open(sql_path, "w") as f:
                f.write(sql_content)

            output_text.value = "Arquivo SQL gerado com sucesso!"
            download_button.visible = True
            page.update()

        except Exception as ex:
            output_text.value = f"Erro: {ex}"
            page.update()

    def selecionar_arquivo(e):
        file_picker.pick_files(allow_multiple=False)

    def baixar_sql(e):
        if sql_path:
            page.launch_url(sql_path)

    # Conecta eventos
    file_picker.on_result = on_file_selected
    download_button.on_click = baixar_sql

    sql_path = ""

    # Interface
    page.add(
        ft.Text("Gerador de UPDATEs para a tabela CTE_peca", size=22, weight="bold"),
        ft.ElevatedButton("Selecionar CSV", icon=Icons.UPLOAD_FILE, on_click=selecionar_arquivo),
        sql_preview,
        output_text,
        download_button,
    )

ft.app(target=main)
