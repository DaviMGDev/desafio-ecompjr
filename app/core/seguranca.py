"""Hash de senha (e, na fase de login, verificação de credenciais)."""

from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()


def gerar_hash(senha: str) -> str:
    """Gera o hash argon2 da senha — a senha em claro nunca é armazenada."""
    return _hasher.hash(senha)


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere a senha contra o hash armazenado."""
    return _hasher.verify(senha, hash_armazenado)
