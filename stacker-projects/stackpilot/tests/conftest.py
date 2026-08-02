import pytest
import pytest_asyncio


@pytest.fixture
def anyio_backend():
    return "asyncio"
