from decimal import Decimal

from modeslos import Item, Pedido, Produto, formatar, quantidade
from pagamento import (
    FATORES,
    calcular_pagamento,
    preco_para_centavos,
    valor_monetario,
)


def _esperar_erro(funcao, mensagem: str) -> None:
    try:
        funcao()
    except (TypeError, ValueError):
        return
    raise AssertionError(mensagem)


def verificar() -> bool:
    assert quantidade("3") == 3
    assert quantidade(2) == 2
    for entrada in ("", "0", "-1", "1.5", "abc"):
        _esperar_erro(
            lambda entrada=entrada: quantidade(entrada),
            f"A quantidade {entrada!r} deveria ser rejeitada.",
        )

    assert formatar(0) == "R$ 0,00"
    assert formatar(123456) == "R$ 1.234,56"
    _esperar_erro(lambda: formatar(-1), "Centavos negativos deveriam ser rejeitados.")

    produto = Produto("A1", "Café", 1250)
    item = Item(produto, "2")
    assert item.subtotal() == 2500

    pedido = Pedido()
    pedido.adicionar(produto, "2")
    pedido.adicionar(produto, "1")
    assert len(pedido.itens) == 1
    assert pedido.itens[0].quantidade == 3
    assert pedido.total_centavos() == 3750
    assert "R$ 37,50" in pedido.linhas()[0]

    _esperar_erro(
        lambda: pedido.adicionar(produto, "invalida"),
        "Uma quantidade inválida deveria ser rejeitada.",
    )
    assert pedido.total_centavos() == 3750
    pedido.atualizar("A1", "4")
    assert pedido.total_centavos() == 5000

    _esperar_erro(
        lambda: pedido.atualizar("A1", "0"),
        "A quantidade zero deveria ser rejeitada.",
    )
    assert pedido.total_centavos() == 5000
    pedido.atualizar("A1", "1")
    assert pedido.total_centavos() == 1250

    _esperar_erro(lambda: pedido.remover("inexistente"), "Código inexistente deveria falhar.")
    assert pedido.total_centavos() == 1250
    pedido.remover("A1")
    assert pedido.total_centavos() == 0
    _esperar_erro(lambda: pedido.finalizar(), "Pedido vazio não deveria ser finalizado.")

    pedido.adicionar(produto, "1")
    pedido.finalizar()
    assert pedido.aberto is False
    _esperar_erro(
        lambda: pedido.adicionar(produto, "1"),
        "Não deveria ser possível alterar um pedido finalizado.",
    )

    assert valor_monetario("R$ 1.234,56") == Decimal("1234.56")
    assert valor_monetario("1234.56") == Decimal("1234.56")
    assert preco_para_centavos("12,35") == 1235
    _esperar_erro(
        lambda: valor_monetario("-1,00"),
        "Valores monetários negativos deveriam ser rejeitados.",
    )
    _esperar_erro(
        lambda: valor_monetario("0", permitir_zero=False),
        "Zero deveria ser rejeitado quando não permitido.",
    )

    for forma, fator in FATORES.items():
        resultado = calcular_pagamento("100,00", forma)
        total_esperado = (Decimal("100.00") * fator).quantize(Decimal("0.01"))
        assert resultado["subtotal"] == Decimal("100.00")
        assert resultado["total"] == total_esperado
        assert resultado["desconto"] == Decimal("100.00") - total_esperado

    _esperar_erro(
        lambda: calcular_pagamento("100,00", "forma inexistente"),
        "Forma de pagamento desconhecida deveria ser rejeitada.",
    )
    return True


if __name__ == "__main__":
    if verificar():
        print("Verificações concluídas: modelo, validações e pagamentos conferem.")
