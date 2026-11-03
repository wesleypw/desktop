import tkinter as tk
from tkinter import messagebox, ttk

from modeslos import Pedido, Produto, formatar
from pagamento import FATORES, calcular_pagamento, preco_para_centavos


class Aplicacao:
    def __init__(self, janela: tk.Tk):
        self.janela = janela
        self.janela.title("Controle de pedidos")
        self.janela.geometry("760x620")
        self.janela.minsize(620, 500)
        self.janela.columnconfigure(0, weight=1)
        self.janela.rowconfigure(2, weight=1)

        self.produtos: dict[str, Produto] = {}
        self.produtos_por_opcao: dict[str, Produto] = {}
        self.pedido = Pedido()
        self._criar_interface()

    def _criar_interface(self) -> None:
        cadastro = ttk.LabelFrame(self.janela, text="Cadastrar produto", padding=10)
        cadastro.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        for coluna in (1, 3):
            cadastro.columnconfigure(coluna, weight=1)

        ttk.Label(cadastro, text="Código").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.codigo = ttk.Entry(cadastro)
        self.codigo.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Label(cadastro, text="Nome").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.nome = ttk.Entry(cadastro)
        self.nome.grid(row=0, column=3, sticky="ew", padx=(0, 12))
        ttk.Label(cadastro, text="Preço").grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.preco = ttk.Entry(cadastro, width=14)
        self.preco.grid(row=0, column=5, sticky="ew")
        self.botao_cadastrar = ttk.Button(
            cadastro, text="Cadastrar", command=self.cadastrar_produto
        )
        self.botao_cadastrar.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(8, 0))

        itens = ttk.LabelFrame(self.janela, text="Adicionar item", padding=10)
        itens.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        itens.columnconfigure(1, weight=1)
        ttk.Label(itens, text="Produto").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.produto_escolhido = tk.StringVar()
        self.seletor_produtos = ttk.Combobox(
            itens, textvariable=self.produto_escolhido, state="readonly"
        )
        self.seletor_produtos.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Label(itens, text="Quantidade").grid(
            row=0, column=2, sticky="w", padx=(0, 6)
        )
        self.quantidade = ttk.Entry(itens, width=10)
        self.quantidade.grid(row=0, column=3, sticky="ew")
        self.quantidade.insert(0, "1")
        self.botao_adicionar = ttk.Button(
            itens, text="Adicionar", command=self.adicionar_item
        )
        self.botao_adicionar.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(8, 0))

        cesta = ttk.LabelFrame(self.janela, text="Pedido", padding=10)
        cesta.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        cesta.columnconfigure(0, weight=1)
        cesta.rowconfigure(0, weight=1)
        colunas = ("codigo", "nome", "quantidade", "subtotal")
        self.lista = ttk.Treeview(cesta, columns=colunas, show="headings", height=10)
        self.lista.heading("codigo", text="Código")
        self.lista.heading("nome", text="Produto")
        self.lista.heading("quantidade", text="Quantidade")
        self.lista.heading("subtotal", text="Subtotal")
        self.lista.column("codigo", width=90, anchor="center")
        self.lista.column("nome", width=260)
        self.lista.column("quantidade", width=100, anchor="center")
        self.lista.column("subtotal", width=130, anchor="e")
        self.lista.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(cesta, orient="vertical", command=self.lista.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=barra.set)

        acoes = ttk.Frame(cesta)
        acoes.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.botao_atualizar = ttk.Button(
            acoes, text="Atualizar quantidade", command=self.atualizar_item
        )
        self.botao_atualizar.pack(side="left", padx=(0, 6))
        self.botao_remover = ttk.Button(acoes, text="Remover", command=self.remover_item)
        self.botao_remover.pack(side="left")
        self.total = ttk.Label(acoes, text="Total: R$ 0,00")
        self.total.pack(side="right")

        pagamento = ttk.LabelFrame(self.janela, text="Pagamento", padding=10)
        pagamento.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        pagamento.columnconfigure(1, weight=1)
        ttk.Label(pagamento, text="Forma").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.forma = tk.StringVar(value="PIX")
        self.seletor_forma = ttk.Combobox(
            pagamento,
            textvariable=self.forma,
            values=tuple(FATORES),
            state="readonly",
        )
        self.seletor_forma.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.botao_pagar = ttk.Button(pagamento, text="Finalizar pedido", command=self.pagar)
        self.botao_pagar.grid(row=0, column=2, padx=(0, 6))
        self.botao_novo = ttk.Button(
            pagamento, text="Novo pedido", command=self.novo_pedido, state="disabled"
        )
        self.botao_novo.grid(row=0, column=3)

        self.aviso = ttk.Label(self.janela, text="Cadastre produtos para começar.")
        self.aviso.grid(row=4, column=0, sticky="w", padx=14, pady=(0, 12))

    def cadastrar_produto(self) -> None:
        try:
            codigo = self.codigo.get().strip()
            if codigo in self.produtos:
                raise ValueError(f"O código {codigo} já está cadastrado.")
            produto = Produto(
                codigo,
                self.nome.get(),
                preco_para_centavos(self.preco.get()),
            )
        except ValueError as erro:
            messagebox.showerror("Produto inválido", str(erro), parent=self.janela)
            return

        self.produtos[produto.codigo] = produto
        opcoes = [f"{item.codigo} — {item.nome}" for item in self.produtos.values()]
        self.produtos_por_opcao = {
            f"{item.codigo} — {item.nome}": item for item in self.produtos.values()
        }
        self.seletor_produtos.configure(values=opcoes)
        self.produto_escolhido.set(opcoes[-1])
        self.codigo.delete(0, tk.END)
        self.nome.delete(0, tk.END)
        self.preco.delete(0, tk.END)
        self.aviso.configure(text=f"Produto {produto.nome} cadastrado.")

    def _produto_atual(self) -> Produto:
        selecionado = self.produto_escolhido.get()
        try:
            return self.produtos_por_opcao[selecionado]
        except KeyError as erro:
            raise ValueError("Selecione um produto cadastrado.") from erro

    def adicionar_item(self) -> None:
        try:
            produto = self._produto_atual()
            self.pedido.adicionar(produto, self.quantidade.get())
        except ValueError as erro:
            messagebox.showerror("Não foi possível adicionar", str(erro), parent=self.janela)
            return
        self._atualizar_pedido()
        self.aviso.configure(text=f"{produto.nome} adicionado ao pedido.")

    def _codigo_selecionado(self) -> str:
        selecao = self.lista.selection()
        if not selecao:
            raise ValueError("Selecione um item do pedido.")
        return str(self.lista.item(selecao[0], "values")[0])

    def atualizar_item(self) -> None:
        try:
            codigo = self._codigo_selecionado()
            self.pedido.atualizar(codigo, self.quantidade.get())
        except ValueError as erro:
            messagebox.showerror("Não foi possível atualizar", str(erro), parent=self.janela)
            return
        self._atualizar_pedido()
        self.aviso.configure(text="Quantidade atualizada.")

    def remover_item(self) -> None:
        try:
            codigo = self._codigo_selecionado()
            produto = self.pedido.remover(codigo)
        except ValueError as erro:
            messagebox.showerror("Não foi possível remover", str(erro), parent=self.janela)
            return
        self._atualizar_pedido()
        self.aviso.configure(text=f"{produto.produto.nome} removido do pedido.")

    def _atualizar_pedido(self) -> None:
        for identificador in self.lista.get_children():
            self.lista.delete(identificador)
        for indice, item in enumerate(self.pedido.itens):
            self.lista.insert(
                "",
                "end",
                iid=f"item-{indice}",
                values=(
                    item.produto.codigo,
                    item.produto.nome,
                    item.quantidade,
                    formatar(item.subtotal()),
                ),
            )
        self.total.configure(text=f"Total: {formatar(self.pedido.total_centavos())}")

    def pagar(self) -> None:
        try:
            resultado = calcular_pagamento(
                formatar(self.pedido.total_centavos()), self.forma.get()
            )
            self.pedido.finalizar()
        except ValueError as erro:
            messagebox.showerror("Não foi possível finalizar", str(erro), parent=self.janela)
            return

        self._atualizar_estado()
        resumo = (
            f"Subtotal: {formatar(int(resultado['subtotal'] * 100))}\n"
            f"Desconto: {formatar(int(resultado['desconto'] * 100))}\n"
            f"Total: {formatar(int(resultado['total'] * 100))}"
        )
        messagebox.showinfo("Pedido finalizado", resumo, parent=self.janela)
        self.aviso.configure(text="Pedido finalizado. Inicie um novo pedido para continuar.")

    def novo_pedido(self) -> None:
        self.pedido = Pedido()
        self._atualizar_pedido()
        self._atualizar_estado()
        self.aviso.configure(text="Novo pedido aberto.")

    def _atualizar_estado(self) -> None:
        estado = "normal" if self.pedido.aberto else "disabled"
        for botao in (
            self.botao_cadastrar,
            self.botao_adicionar,
            self.botao_atualizar,
            self.botao_remover,
            self.botao_pagar,
        ):
            botao.configure(state=estado)
        self.botao_novo.configure(state="disabled" if self.pedido.aberto else "normal")


def criar_janela() -> tk.Tk:
    janela = tk.Tk()
    Aplicacao(janela)
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
