def test_pacote_app_importavel() -> None:
    """Fumaça: a raiz do projeto está no sys.path e o pacote `app` importa."""
    import app

    assert app is not None
