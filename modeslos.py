import re


def quantidade(texto: str | int) -> int:
    """Converte uma quantidade inteira positiva ou informa que ela e invalida."""
    if isinstance(texto, bool):
        raise ValueError("A quantidade deve ser um numero inteiro positivo.")
    if isinstance(texto, int):
        valor = texto
    elif isinstance(texto, str) and re.fullmatch(r"[0-9]+", texto.strip()):
        valor = int(texto.strip())
    else:
        raise ValueError("A quantidade deve ser um numero inteiro positivo.")

    if valor <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    return valor


def formatar(centavos: int) -> str:
    """Formata um valor inteiro em centavos no padrao monetario brasileiro."""
    if isinstance(centavos, bool) or not isinstance(centavos, int) or centavos < 0:
        raise ValueError("O valor em centavos deve ser um inteiro nao negativo.")
    reais, centavos_restantes = divmod(centavos, 100)
    reais_formatados = f"{reais:,}".replace(",", ".")
    return f"R$ {reais_formatados},{centavos_restantes:02d}"


class Produto:
    def __init__(self, codigo: str, nome: str, preco_centavos: int):
        codigo = str(codigo).strip()
        nome = str(nome).strip()
        if not codigo:
            raise ValueError("Informe o codigo do produto.")
        if not nome:
            raise ValueError("Informe o nome do produto.")
        if (
            isinstance(preco_centavos, bool)
            or not isinstance(preco_centavos, int)
            or preco_centavos < 0
        ):
            raise ValueError("O preco deve ser um inteiro nao negativo em centavos.")

        self.codigo = codigo
        self.nome = nome
        self.preco_centavos = preco_centavos


class Item:
    def __init__(self, produto: Produto, texto_quantidade: str | int):
        if not isinstance(produto, Produto):
            raise TypeError("O item precisa estar associado a um produto.")
        self.produto = produto
        self.quantidade = quantidade(texto_quantidade)

    def subtotal(self) -> int:
        return self.produto.preco_centavos * self.quantidade


class Pedido:
    def __init__(self):
        self.itens: list[Item] = []
        self.aberto = True

    def exigir_aberto(self) -> None:
        if not self.aberto:
            raise ValueError("O pedido ja foi finalizado.")

    def adicionar(self, produto: Produto, texto_quantidade: str | int) -> Item:
        self.exigir_aberto()
        if not isinstance(produto, Produto):
            raise TypeError("O pedido so pode receber instancias de Produto.")
        nova_quantidade = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == produto.codigo:
                if (
                    item.produto.nome != produto.nome
                    or item.produto.preco_centavos != produto.preco_centavos
                ):
                    raise ValueError("O codigo ja esta associado a outro produto.")
                item.quantidade += nova_quantidade
                return item

        item = Item(produto, nova_quantidade)
        self.itens.append(item)
        return item

    def total_centavos(self) -> int:
        return sum(item.subtotal() for item in self.itens)

    def linhas(self) -> list[str]:
        return [
            f"{item.produto.codigo} | {item.produto.nome} | "
            f"{item.quantidade} x {formatar(item.produto.preco_centavos)} | "
            f"{formatar(item.subtotal())}"
            for item in self.itens
        ]

    def atualizar(self, codigo: str, texto_quantidade: str | int) -> Item:
        self.exigir_aberto()
        nova_quantidade = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == str(codigo).strip():
                item.quantidade = nova_quantidade
                return item
        raise ValueError(f"Nao existe item com o codigo {codigo}.")

    def remover(self, codigo: str) -> Item:
        self.exigir_aberto()
        for indice, item in enumerate(self.itens):
            if item.produto.codigo == str(codigo).strip():
                return self.itens.pop(indice)
        raise ValueError(f"Nao existe item com o codigo {codigo}.")

    def finalizar(self) -> None:
        self.exigir_aberto()
        if not self.itens:
            raise ValueError("Nao e possivel finalizar um pedido vazio.")
        self.aberto = False
