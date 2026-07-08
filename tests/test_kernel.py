from jemba_core.kernel.kernel import JembaKernel


def test_kernel_start():
    kernel = JembaKernel()

    container = kernel.start()

    assert kernel.running is True
    assert container is not None
    assert kernel.provider is not None
    assert kernel.config is not None


def test_kernel_stop():
    kernel = JembaKernel()

    kernel.start()
    kernel.stop()

    assert kernel.running is False
    assert kernel.container is None
    assert kernel.provider is None
    assert kernel.config is None
