import pytest
import re

from sqlalchemy.ext.asyncio import create_async_engine

from schema import Base
from url_shortener import get_url_shortener

TEST_DB = 'postgresql+asyncpg://aiohttpdemo_user:aiohttpdemo_pass@localhost:5432/aiohttpdemo_polls'


class TestUrlShortener:
    @pytest.fixture(autouse=True)
    async def init_db(self):
        engine = create_async_engine(TEST_DB)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        return engine

    @pytest.mark.asyncio
    @pytest.mark.parametrize(['url', 'short_id', 'force'], [('https://a', 'b', True), ('https://b', 'a', False)])
    async def test_url_shortener_id(self, init_db, url, short_id, force):
        shortener = get_url_shortener(domain='domain', shortener_type='by_id', db=await init_db)
        short_url = await shortener.short_url(url, id=short_id)
        assert short_url == f'domain/{short_id}'
        assert await shortener.get_url(short_url) == url

        if force:
            short_url = await shortener.short_url(url, force, id=short_id)
            assert await shortener.get_url(short_url) == url
        else:
            with pytest.raises(ValueError):
                await shortener.short_url(url, force, id=short_id)

    @pytest.mark.asyncio
    async def test_url_shortener_uuid(self, init_db):
        url = 'https://a'
        shortener = get_url_shortener(domain='domain', shortener_type='uuid', db=await init_db)
        short_url = await shortener.short_url(url)
        assert re.match(r'domain/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', short_url)
        assert await shortener.get_url(short_url) == url

    @pytest.mark.asyncio
    @pytest.mark.parametrize('initial_id', [None, 42, 69])
    async def test_incremental_url_shortener(self, init_db, initial_id):
        params = {'initial_value': initial_id} if initial_id else None
        initial_id = initial_id or 1

        shortener = get_url_shortener(domain='domain', shortener_type='incremental', params=params, db=await init_db)
        short_url_1 = await shortener.short_url('a')
        assert short_url_1 == f'domain/{initial_id}'
        assert await shortener.get_url(short_url_1) == 'a'

        short_url_2 = await shortener.short_url('b')
        assert short_url_2 == f'domain/{initial_id + 1}'
        assert await shortener.get_url(short_url_2) == 'b'
