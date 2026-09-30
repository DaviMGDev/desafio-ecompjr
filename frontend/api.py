"""Cliente HTTP da API de estoque — a única saída de rede do painel.

O painel consome a API pública por HTTP (ADR-0014); nada aqui importa models,
services ou sessão do banco. Em testes, `TRANSPORTE` é trocado por um adaptador
do app ASGI da API, então a suíte roda sem servidor de verdade.
"""

from typing import Any

import httpx2

from frontend.config import settings

# Preenchido pelos testes com um transporte que aponta para o app ASGI da API.
TRANSPORTE: httpx2.BaseTransport | None = None


def requisitar(
    metodo: str,
    caminho: str,
    *,
    token: str | None = None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    """Chama a API e devolve `(status, corpo)`; corpo JSON ou `None`."""
    cabecalhos = {"Authorization": f"Bearer {token}"} if token else {}
    with httpx2.Client(
        base_url=settings.api_url,
        timeout=settings.timeout_api,
        transport=TRANSPORTE,
    ) as cliente:
        resposta = cliente.request(metodo, caminho, params=params, json=json, headers=cabecalhos)
    try:
        corpo = resposta.json()
    except ValueError:
        corpo = None
    return resposta.status_code, corpo


def detail_do_corpo(corpo: Any) -> Any:
    """Extrai o `detail` do envelope de erro da API (o corpo inteiro se não houver)."""
    if isinstance(corpo, dict) and "detail" in corpo:
        return corpo["detail"]
    return corpo


def mensagem_do_detail(detail: Any) -> str:
    """Texto exibível do envelope `detail` (string ou lista do 422)."""
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "; ".join(str(item.get("msg", "")) for item in detail if isinstance(item, dict))
    return "Não foi possível concluir a operação."


def erros_por_campo(detail: Any) -> dict[str, str]:
    """Mensagens do 422 mapeadas pelo último componente de `loc`."""
    if not isinstance(detail, list):
        return {}

    erros: dict[str, str] = {}
    for item in detail:
        if not isinstance(item, dict):
            continue
        local = [parte for parte in item.get("loc", []) if parte not in ("body", "query", "path")]
        if local:
            erros[str(local[-1])] = str(item.get("msg", "Valor inválido"))
    return erros


# --- Endpoints da API ---------------------------------------------------------


def login(email: str, senha: str) -> tuple[int, Any]:
    """`POST /auth/login` — devolve o token de acesso."""
    return requisitar("POST", "/auth/login", json={"email": email, "senha": senha})


def listar_fornecedores(token: str, **filtros: Any) -> tuple[int, Any]:
    """`GET /fornecedores` com os filtros repassados como query string."""
    return requisitar("GET", "/fornecedores", token=token, params=filtros)


def obter_fornecedor(token: str, fornecedor_id: int) -> tuple[int, Any]:
    """`GET /fornecedores/{id}`."""
    return requisitar("GET", f"/fornecedores/{fornecedor_id}", token=token)


def criar_fornecedor(token: str, dados: dict[str, Any]) -> tuple[int, Any]:
    """`POST /fornecedores`."""
    return requisitar("POST", "/fornecedores", token=token, json=dados)


def atualizar_fornecedor(token: str, fornecedor_id: int, dados: dict[str, Any]) -> tuple[int, Any]:
    """`PUT /fornecedores/{id}`."""
    return requisitar("PUT", f"/fornecedores/{fornecedor_id}", token=token, json=dados)


def excluir_fornecedor(token: str, fornecedor_id: int) -> tuple[int, Any]:
    """`DELETE /fornecedores/{id}`."""
    return requisitar("DELETE", f"/fornecedores/{fornecedor_id}", token=token)


def listar_categorias(token: str, **filtros: Any) -> tuple[int, Any]:
    """`GET /categorias`."""
    return requisitar("GET", "/categorias", token=token, params=filtros)


def obter_categoria(token: str, categoria_id: int) -> tuple[int, Any]:
    """`GET /categorias/{id}`."""
    return requisitar("GET", f"/categorias/{categoria_id}", token=token)


def criar_categoria(token: str, dados: dict[str, Any]) -> tuple[int, Any]:
    """`POST /categorias`."""
    return requisitar("POST", "/categorias", token=token, json=dados)


def atualizar_categoria(token: str, categoria_id: int, dados: dict[str, Any]) -> tuple[int, Any]:
    """`PUT /categorias/{id}`."""
    return requisitar("PUT", f"/categorias/{categoria_id}", token=token, json=dados)


def excluir_categoria(token: str, categoria_id: int) -> tuple[int, Any]:
    """`DELETE /categorias/{id}`."""
    return requisitar("DELETE", f"/categorias/{categoria_id}", token=token)


def listar_produtos(token: str, **filtros: Any) -> tuple[int, Any]:
    """`GET /produtos` (filtros: nome, categoria_id, fornecedor_id, limit, offset)."""
    return requisitar("GET", "/produtos", token=token, params=filtros)


def produtos_estoque_baixo(token: str, **filtros: Any) -> tuple[int, Any]:
    """`GET /produtos/estoque-baixo`."""
    return requisitar("GET", "/produtos/estoque-baixo", token=token, params=filtros)


def obter_produto(token: str, produto_id: int) -> tuple[int, Any]:
    """`GET /produtos/{id}` — usado para refrescar o saldo exibido."""
    return requisitar("GET", f"/produtos/{produto_id}", token=token)


def criar_produto(token: str, dados: dict[str, Any]) -> tuple[int, Any]:
    """`POST /produtos`."""
    return requisitar("POST", "/produtos", token=token, json=dados)


def atualizar_produto(token: str, produto_id: int, dados: dict[str, Any]) -> tuple[int, Any]:
    """`PUT /produtos/{id}`."""
    return requisitar("PUT", f"/produtos/{produto_id}", token=token, json=dados)


def excluir_produto(token: str, produto_id: int) -> tuple[int, Any]:
    """`DELETE /produtos/{id}`."""
    return requisitar("DELETE", f"/produtos/{produto_id}", token=token)


def listar_movimentacoes(token: str, **filtros: Any) -> tuple[int, Any]:
    """`GET /movimentacoes` (produto, tipo, fornecedor, período, limit, offset)."""
    return requisitar("GET", "/movimentacoes", token=token, params=filtros)


def criar_movimentacao(token: str, dados: dict[str, Any]) -> tuple[int, Any]:
    """`POST /movimentacoes` — entrada/saída atômica na API."""
    return requisitar("POST", "/movimentacoes", token=token, json=dados)
