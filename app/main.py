import os
import yaml

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine

from schema import Base
from routes import setup_routes
from url_shortener import get_url_shortener

DSN = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


def read_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


async def setup(app):
    conf = app['db_config']['postgres']
    db_url = DSN.format(**conf)
    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    app['url_shortener'] = get_url_shortener(db=engine, **app['url_shortener_config'])

    yield

    await app['url_shortener'].db.dispose()


if __name__ == '__main__':
    app = web.Application()
    app['url_shortener_config'] = read_config(os.environ['SHORTENER_CONFIG'])
    app['db_config'] = read_config(os.environ['DB_CONFIG'])
    setup_routes(app)
    app.cleanup_ctx.append(setup)
    web.run_app(app)
