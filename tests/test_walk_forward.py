import pytest

from jemba_core.walkforward import (
    WalkForwardWindow,
    generate_walk_forward_windows,
)


def test_generates_expected_windows():
    windows = generate_walk_forward_windows(
        length=1000,
        train_size=300,
        test_size=100,
    )

    assert len(windows) == 7
    assert all(isinstance(window, WalkForwardWindow) for window in windows)


def test_first_window_boundaries():
    window = generate_walk_forward_windows(
        length=1000,
        train_size=300,
        test_size=100,
    )[0]

    assert window.train_start == 0
    assert window.train_end == 300
    assert window.test_start == 300
    assert window.test_end == 400


def test_uses_custom_step_size():
    windows = generate_walk_forward_windows(
        length=600,
        train_size=300,
        test_size=100,
        step_size=50,
    )

    assert windows[1].train_start == 50
    assert windows[1].test_start == 350


def test_returns_empty_when_data_is_insufficient():
    windows = generate_walk_forward_windows(
        length=300,
        train_size=250,
        test_size=100,
    )

    assert windows == []


@pytest.mark.parametrize(
    ("field", "kwargs", "message"),
    [
        (
            "length",
            {
                "length": 0,
                "train_size": 10,
                "test_size": 5,
            },
            "LENGTH_MUST_BE_POSITIVE",
        ),
        (
            "train_size",
            {
                "length": 100,
                "train_size": 0,
                "test_size": 5,
            },
            "TRAIN_SIZE_MUST_BE_POSITIVE",
        ),
        (
            "test_size",
            {
                "length": 100,
                "train_size": 10,
                "test_size": 0,
            },
            "TEST_SIZE_MUST_BE_POSITIVE",
        ),
    ],
)
def test_rejects_invalid_sizes(
    field,
    kwargs,
    message,
):
    del field

    with pytest.raises(
        ValueError,
        match=message,
    ):
        generate_walk_forward_windows(**kwargs)
