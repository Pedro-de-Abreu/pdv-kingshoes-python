import flet as ft
from datetime import datetime
import csv
import json
import os

# --- MAPEAMENTO DE MESES PARA O FILTRO ---
meses_map = {
    "01": "Jan",
    "02": "Fev",
    "03": "Mar",
    "04": "Abr",
    "05": "Mai",
    "06": "Jun",
    "07": "Jul",
    "08": "Ago",
    "09": "Set",
    "10": "Out",
    "11": "Nov",
    "12": "Dez",
}


# --- FUNÇÕES DE ARMAZENAMENTO LOCAL (ALÉRGICO A CRASH) ---
def carregar_dados_locais():
    catalogo = {}
    vendas = []

    # Carrega o catálogo de produtos local
    if os.path.exists("catalogo.json"):
        try:
            with open("catalogo.json", "r", encoding="utf-8") as f:
                catalogo = json.load(f)
        except Exception:
            catalogo = {}
    else:
        # Itens padrão de inicialização se o app for novo
        catalogo = {"Tênis Exemplo": 199.90}
        with open("catalogo.json", "w", encoding="utf-8") as f:
            json.dump(catalogo, f, ensure_ascii=False, indent=4)

    # Carrega o histórico de vendas local
    if os.path.exists("vendas.json"):
        try:
            with open("vendas.json", "r", encoding="utf-8") as f:
                vendas = json.load(f)
        except Exception:
            vendas = []

    return catalogo, vendas


def salvar_produto_local(catalogo):
    with open("catalogo.json", "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=4)


def salvar_venda_local(vendas):
    with open("vendas.json", "w", encoding="utf-8") as f:
        json.dump(vendas, f, ensure_ascii=False, indent=4)


def main(page: ft.Page):
    page.title = "KingShoes - Gestão PDV Local"
    page.window.width = 400
    page.window.height = 750
    page.theme_mode = ft.ThemeMode.DARK

    # Carrega os dados direto da memória do dispositivo
    catalogo_produtos, historico_mensal = carregar_dados_locais()

    total_geral = [0.0]
    totais_por_produto = {}

    # --- COMPONENTE DE FILTRAGEM POR MÊS ---
    dropdown_filtro_mes = ft.Dropdown(
        label="Mês",
        value="Todos",
        options=[ft.dropdown.Option("Todos")]
        + [ft.dropdown.Option(m) for m in meses_map.values()],
        width=110,
        on_change=lambda e: recalcular_tudo(),
    )

    # --- ELEMENTOS VISUAIS ---
    texto_total = ft.Text(
        "Total: R$ 0.00", size=30, weight="bold", color=ft.Colors.GREEN_400
    )

    dropdown_produto_caixa = ft.Dropdown(
        label="Selecione o Produto",
        icon=ft.Icons.SHOPPING_BAG,
        options=[ft.dropdown.Option(p) for p in catalogo_produtos.keys()],
        expand=True,
    )

    input_quantidade = ft.TextField(
        label="Qtd",
        value="1",
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=80,
    )

    linha_produto_qtd = ft.Row([dropdown_produto_caixa, input_quantidade])

    dropdown_pagamento = ft.Dropdown(
        label="Pagamento",
        value="Pix",
        options=[
            ft.dropdown.Option(x)
            for x in ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"]
        ],
    )

    input_novo_nome = ft.TextField(label="Nome do Produto", icon=ft.Icons.NEW_LABEL)
    input_novo_preco = ft.TextField(
        label="Preço (R$)",
        icon=ft.Icons.ATTACH_MONEY,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    lista_recentes = ft.ListView(expand=True, spacing=10)
    lista_catalogo_visual = ft.ListView(expand=True, spacing=10)
    lista_resumo_produtos = ft.ListView(expand=True, spacing=10)
    lista_historico = ft.ListView(expand=True, spacing=10)

    # --- MOTOR DE RECALCULAR COM FILTRO DINDÂMICO ---
    def recalcular_tudo():
        total_geral[0] = 0.0
        totais_por_produto.clear()

        mes_selecionado = dropdown_filtro_mes.value

        for v in historico_mensal:
            # Extrai o mês da string de data "dd/mm/aaaa hh:mm"
            try:
                mes_venda_num = v["data"].split("/")[1]
                mes_venda_nome = meses_map.get(mes_venda_num, "")
            except Exception:
                mes_venda_nome = ""

            # Se tiver filtro ativo e não bater, ignora a linha no cálculo
            if mes_selecionado != "Todos" and mes_venda_nome != mes_selecionado:
                continue

            total_geral[0] += v["valor_total"]
            p_nome = v["produto"]
            if p_nome in totais_por_produto:
                totais_por_produto[p_nome]["qtd"] += v["qtd"]
                totais_por_produto[p_nome]["valor"] += v["valor_total"]
            else:
                totais_por_produto[p_nome] = {
                    "qtd": v["qtd"],
                    "valor": v["valor_total"],
                }

        texto_total.value = f"Total: R$ {total_geral[0]:.2f}"
        atualizar_listas_visuais()

    def deletar_venda(venda_id):
        del historico_mensal[venda_id]
        salvar_venda_local(historico_mensal)
        recalcular_tudo()

    def atualizar_listas_visuais():
        lista_catalogo_visual.controls.clear()
        for prod, preco in catalogo_produtos.items():
            lista_catalogo_visual.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.STYLE, color=ft.Colors.ORANGE_400),
                    title=ft.Text(prod),
                    trailing=ft.Text(f"R$ {preco:.2f}", weight="bold"),
                )
            )

        lista_resumo_produtos.controls.clear()
        for prod, dados in totais_por_produto.items():
            lista_resumo_produtos.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2, color=ft.Colors.BLUE_400),
                    title=ft.Text(prod),
                    subtitle=ft.Text(f"{dados['qtd']} unid."),
                    trailing=ft.Text(f"R$ {dados['valor']:.2f}", weight="bold"),
                )
            )

        lista_historico.controls.clear()
        lista_recentes.controls.clear()

        mes_selecionado = dropdown_filtro_mes.value
        cont_recente = 0

        for i, venda in reversed(list(enumerate(historico_mensal))):
            try:
                mes_venda_num = venda["data"].split("/")[1]
                mes_venda_nome = meses_map.get(mes_venda_num, "")
            except Exception:
                mes_venda_nome = ""

            if mes_selecionado != "Todos" and mes_venda_nome != mes_selecionado:
                continue

            item_hist = ft.ListTile(
                leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.PURPLE_400),
                title=ft.Text(
                    f"{venda['qtd']}x {venda['produto']} - {venda['pagamento']}"
                ),
                subtitle=ft.Text(venda["data"]),
                trailing=ft.Row(
                    [
                        ft.Text(
                            f"R$ {venda['valor_total']:.2f}", color=ft.Colors.GREEN_400
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Excluir Venda",
                            on_click=lambda e, vid=i: deletar_venda(vid),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    tight=True,
                ),
            )
            lista_historico.controls.append(item_hist)

            if cont_recente < 5:
                item_recente = ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                    title=ft.Text(f"{venda['qtd']}x {venda['produto']}"),
                    subtitle=ft.Text(venda["data"]),
                    trailing=ft.Text(f"R$ {venda['valor_total']:.2f}"),
                )
                lista_recentes.controls.append(item_recente)
                cont_recente += 1

        page.update()

    # --- AÇÕES DOS BOTÕES (SALVAMENTO LOCAL AUTOMÁTICO) ---
    def cadastrar_novo_produto(e):
        nome = input_novo_nome.value.strip().title()
        if nome and input_novo_preco.value:
            try:
                preco = float(input_novo_preco.value.replace(",", "."))
                catalogo_produtos[nome] = preco

                salvar_produto_local(catalogo_produtos)

                dropdown_produto_caixa.options = [
                    ft.dropdown.Option(p) for p in catalogo_produtos.keys()
                ]
                input_novo_nome.value = ""
                input_novo_preco.value = ""
                atualizar_listas_visuais()

                page.snack_bar = ft.SnackBar(ft.Text("Produto adicionado com sucesso!"))
                page.snack_bar.open = True
                page.update()
            except ValueError:
                pass

    def registrar_venda(e):
        if dropdown_produto_caixa.value and input_quantidade.value:
            try:
                produto_nome = dropdown_produto_caixa.value
                qtd = int(input_quantidade.value)
                valor_total_item = catalogo_produtos[produto_nome] * qtd
                pagamento = dropdown_pagamento.value
                data_str = datetime.now().strftime("%d/%m/%Y %H:%M")

                historico_mensal.append(
                    {
                        "data": data_str,
                        "produto": produto_nome,
                        "qtd": qtd,
                        "valor_total": valor_total_item,
                        "pagamento": pagamento,
                    }
                )

                salvar_venda_local(historico_mensal)

                dropdown_produto_caixa.value = None
                input_quantidade.value = "1"
                recalcular_tudo()

                page.snack_bar = ft.SnackBar(ft.Text("Venda registrada localmente!"))
                page.snack_bar.open = True
                page.update()
            except ValueError:
                pass

    def exportar_csv(e):
        mes_selecionado = dropdown_filtro_mes.value
        nome_arquivo = (
            f"relatorio_vendas_{mes_selecionado}.csv"
            if mes_selecionado != "Todos"
            else "relatorio_vendas_completo.csv"
        )

        with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Data", "Produto", "Quantidade", "Valor Total", "Pagamento"]
            )

            for v in historico_mensal:
                try:
                    mes_venda_num = v["data"].split("/")[1]
                    mes_venda_nome = meses_map.get(mes_venda_num, "")
                except Exception:
                    mes_venda_nome = ""

                if mes_selecionado != "Todos" and mes_venda_nome != mes_selecionado:
                    continue

                writer.writerow(
                    [
                        v["data"],
                        v["produto"],
                        v["qtd"],
                        v["valor_total"],
                        v["pagamento"],
                    ]
                )

        page.snack_bar = ft.SnackBar(
            ft.Text(f"Arquivo {nome_arquivo} gerado com sucesso!")
        )
        page.snack_bar.open = True
        page.update()

    # --- INICIALIZAÇÃO DA INTERFACE ---
    recalcular_tudo()

    aba_registro = ft.Container(
        padding=10,
        content=ft.Column(
            [
                texto_total,
                ft.Divider(color=ft.Colors.TRANSPARENT),
                linha_produto_qtd,
                dropdown_pagamento,
                ft.ElevatedButton(
                    "REGISTRAR VENDA",
                    icon=ft.Icons.ADD,
                    on_click=registrar_venda,
                    width=400,
                    height=50,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Divider(),
                ft.Text("Últimas Vendas do Mês:", size=16),
                lista_recentes,
            ]
        ),
    )

    aba_catalogo = ft.Container(
        padding=10,
        content=ft.Column(
            [
                ft.Text("Cadastrar Item", size=20, weight="bold"),
                input_novo_nome,
                input_novo_preco,
                ft.ElevatedButton(
                    "ADICIONAR AO CATÁLOGO",
                    icon=ft.Icons.SAVE,
                    on_click=cadastrar_novo_produto,
                    width=400,
                    height=50,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Divider(),
                ft.Text("Itens Disponíveis:", size=16),
                lista_catalogo_visual,
            ]
        ),
    )

    aba_produtos = ft.Container(
        padding=10,
        content=ft.Column(
            [
                ft.Text("Vendas por Produto", size=20, weight="bold"),
                lista_resumo_produtos,
            ]
        ),
    )

    aba_historico = ft.Container(
        padding=10,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Histórico Filtrado", size=20, weight="bold"),
                        ft.ElevatedButton(
                            "Exportar Excel/CSV",
                            icon=ft.Icons.DOWNLOAD,
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                            on_click=exportar_csv,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                lista_historico,
            ]
        ),
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=1,
        tabs=[
            ft.Tab(text="Caixa", icon=ft.Icons.POINT_OF_SALE, content=aba_registro),
            ft.Tab(text="Catálogo", icon=ft.Icons.STYLE, content=aba_catalogo),
            ft.Tab(text="Produtos", icon=ft.Icons.INVENTORY_2, content=aba_produtos),
            ft.Tab(text="Histórico", icon=ft.Icons.HISTORY, content=aba_historico),
        ],
    )

    # Adiciona o cabeçalho com a logo da marca e o filtro de meses colado no topo
    page.add(
        ft.Row(
            [
                ft.Text(
                    "KingShoes PDV", size=22, weight="bold", color=ft.Colors.ORANGE_400
                ),
                dropdown_filtro_mes,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        tabs,
    )


ft.app(target=main)
