import os
import tempfile

# Must run before any `app.*` module is imported, since app.db.session builds
# the SQLAlchemy engine from settings at import time.
_tmp_dir = tempfile.mkdtemp(prefix="part2-test-")
os.environ["PART2_DATABASE_URL"] = f"sqlite+aiosqlite:///{os.path.join(_tmp_dir, 'test.db')}"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.api import routes_config  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.db.models import Base  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_config_override():
    # routes_config._runtime_override is module-level, in-memory-only state
    # (D-11) shared across the whole test session — reset it around every
    # test so PUT /config tests can't leak state into unrelated tests.
    original = dict(routes_config._runtime_override)
    yield
    routes_config._runtime_override.clear()
    routes_config._runtime_override.update(original)


@pytest_asyncio.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
