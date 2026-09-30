"""Validadores e normalizadores de campos do domínio."""

import re

_NAO_DIGITOS = re.compile(r"\D")


def _digito_verificador(digitos: str, pesos: list[int]) -> str:
    soma = sum(int(digito) * peso for digito, peso in zip(digitos, pesos, strict=True))
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def normalizar_cnpj(valor: str) -> str:
    """Remove a máscara e valida os dígitos verificadores do CNPJ.

    O CNPJ é armazenado sem máscara, para que a unicidade no banco não dependa
    do formato enviado pelo cliente (ADR-0001 e § 2.b do enunciado).
    """
    digitos = _NAO_DIGITOS.sub("", valor)
    if len(digitos) != 14 or len(set(digitos)) == 1:
        raise ValueError("CNPJ inválido")

    primeiro = _digito_verificador(digitos[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    segundo = _digito_verificador(digitos[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    if digitos[12] != primeiro or digitos[13] != segundo:
        raise ValueError("CNPJ inválido")

    return digitos
