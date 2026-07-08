from unittest.mock import MagicMock

from jemba_core.kernel.kernel import JembaKernel


def test_kernel_run():
    kernel = JembaKernel()

    kernel.start()

    kernel.market = MagicMock()
    kernel.pipeline = MagicMock()

    kernel.run(cycles=2, delay=0)

    assert kernel.market.update.call_count == 2
    assert kernel.pipeline.execute.call_count == 2
