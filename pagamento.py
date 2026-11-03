import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


FATORES = {
    "Dinheiro": Decimal("0.87"),
    "PIX": Decimal("0.87"),
    "Débito": Decimal("0.92"),
    "Crédito 1x": Decimal("1.00"),
}
CENTAVO = Decimal("0.01")


def valor_monetario(texto: str | int | Decimal, permitir_zero: bool = True) -> Decimal:
    """Interpreta um valor em reais e devolve Decimal arredondado para centavos."""
    if isinstance(texto, bool):
        raise ValueError("Informe um valor monetario valido.")

    if isinstance(texto, Decimal):
        valor = texto
    elif isinstance(texto, int):
        valor = Decimal(texto)
    elif isinstance(texto, str):
        normalizado = texto.strip()
        if normalizado[:2].upper() == "R$":
            normalizado = normalizado[2:].strip()
        normalizado = normalizado.replace(" ", "")

        padrao_brasileiro = r"(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,[0-9]{1,2})?"
        padrao_americano = r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]{1,2})?"
        if re.fullmatch(padrao_brasileiro, normalizado):
            normalizado = normalizado.replace(".", "").replace(",", ".")
        elif re.fullmatch(padrao_americano, normalizado):
            normalizado = normalizado.replace(",", "")
        else:
            raise ValueError("Use um valor como 12,50 ou R$ 1.234,50.")
        try:
            valor = Decimal(normalizado)
        except InvalidOperation as erro:
            raise ValueError("Informe um valor monetario valido.") from erro
    else:
        raise ValueError("Informe um valor monetario valido.")

    if not valor.is_finite() or valor < 0 or (valor == 0 and not permitir_zero):
        if permitir_zero:
            raise ValueError("O valor deve ser maior ou igual a zero.")
        raise ValueError("O valor deve ser maior que zero.")
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def calcular_pagamento(subtotal_texto: str | int | Decimal, forma: str) -> dict[str, Decimal]:
    """Retorna subtotal, desconto e total como valores Decimal em reais."""
    try:
        fator = FATORES[forma]
    except KeyError as erro:
        raise ValueError(f"Forma de pagamento invalida: {forma}.") from erro

    subtotal = valor_monetario(subtotal_texto)
    total = (subtotal * fator).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return {
        "subtotal": subtotal,
        "desconto": (subtotal - total).quantize(CENTAVO),
        "total": total,
    }


def preco_para_centavos(texto: str | int | Decimal) -> int:
    """Converte um preco monetario para um numero inteiro de centavos."""
    return int(valor_monetario(texto) * 100)
