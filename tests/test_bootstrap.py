from jemba_core.kernel.bootstrap import Bootstrap
from jemba_core.providers.bingx_provider import BingXProvider


def test_bootstrap_build():
    bootstrap = Bootstrap()

    container = bootstrap.build()

    assert container is not None
    assert container.config is not None
    assert container.provider is not None
    assert isinstance(container.provider, BingXProvider)
    assert container.config["broker"] == "bingx"
