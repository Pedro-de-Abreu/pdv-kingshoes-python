# 👟 PDV Local - KingShoes (Edge Computing)

Sistema de Ponto de Venda (PDV) mobile desenvolvido nativamente em Python para otimizar o fluxo de caixa de uma loja física, operando 100% offline.

## 🚀 O Problema
A operação da loja precisava de agilidade no balcão, sem depender da latência de internet ou de planilhas complexas pelo celular, garantindo que nenhuma venda deixasse de ser registrada por falha de conexão.

## 💡 A Solução
Desenvolvimento de um aplicativo Android autônomo. O sistema utiliza a memória interna do dispositivo (armazenamento em JSON) para garantir velocidade de resposta instantânea (zero latência). No fim do mês, o sistema compila os dados e gera relatórios analíticos em `.csv` para a contabilidade.

## 🛠️ Tecnologias Utilizadas
* **Python** (Linguagem base)
* **Flet** (Framework UI e compilação mobile nativa)
* **JSON/CSV** (Persistência de dados local e exportação)
* **Android NDK** (Compilação do pacote `.apk`)

## ⚙️ Funcionalidades
- [x] Catálogo de produtos dinâmico.
- [x] Registro rápido de vendas no balcão.
- [x] Funcionamento 100% offline (Edge Computing).
- [x] Filtro temporal de faturamento em tempo real.
- [x] Geração e exportação automática de relatórios CSV.
