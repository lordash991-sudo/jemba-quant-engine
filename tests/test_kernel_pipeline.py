from unittest.mock import MagicMock

from jemba_core.kernel.kernel import JembaKernel
from jemba_core.pipeline.pipeline_engine import PipelineEngine


def test_kernel_creates_pipeline():
    kernel = JembaKernel()

    kernel.start()

    assert isinstance(kernel.pipeline, PipelineEngine)


def test_kernel_run_passes_market_data_to_pipeline():
    kernel = JembaKernel()

    kernel.start()

    kernel.market = MagicMock()
    kernel.pipeline = MagicMock()

    kernel.market.update.return_value = "market_data"

    kernel.run(cycles=2, delay=0)

    assert kernel.market.update.call_count == 2
    assert kernel.pipeline.execute.call_count == 2
    kernel.pipeline.execute.assert_called_with("market_data")
