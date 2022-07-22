from uuid import uuid4
from dataclasses import dataclass
from typing import Callable, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from schema import UrlsTable


@dataclass
class UrlShortener:
    domain: str
    id_generator: Callable[..., str]
    db: AsyncEngine

    async def short_url(self, url: str, force: Optional[bool] = False, **kwargs):
        short_id = self.id_generator(**kwargs)
        async with AsyncSession(self.db) as session:
            async with session.begin():
                if not force:
                    cursor = await session.execute(select(UrlsTable).where(UrlsTable.id == short_id))
                    if cursor.first():
                        raise ValueError(f'{short_id} is already in the base; use force param to override')

                await session.execute(insert(UrlsTable).values(id=short_id, url=url).on_conflict_do_update(
                    constraint='Urls_pkey',
                    set_={'url': url},
                ))
                return f'{self.domain}/{short_id}'

    async def get_url(self, short_url: str):
        if not short_url.startswith(self.domain):
            raise RuntimeError('It\'s not a short url!')
        short_id = short_url[len(self.domain) + 1:]
        async with AsyncSession(self.db) as session:
            async with session.begin():
                cursor = await session.execute(select(UrlsTable).where(UrlsTable.id == short_id))
                record = cursor.first()
                if not record:
                    raise ValueError(f'No such id {short_id}')
                return record[0].url


@dataclass
class _IncrementalIds:
    cnt: int = 0

    def __call__(self, *args, **kwargs) -> str:
        self.cnt += 1
        return str(self.cnt)


def get_url_shortener(domain: str, db: AsyncEngine, shortener_type: str, params: Optional[dict] = None) -> UrlShortener:
    if shortener_type == 'by_id':
        return UrlShortener(domain=domain, id_generator=lambda id: id, db=db)
    elif shortener_type == 'uuid':
        return UrlShortener(domain=domain, id_generator=lambda: str(uuid4()), db=db)
    elif shortener_type == 'incremental':
        initial_id = params.get('initial_value', 1) - 1 if params else 0
        return UrlShortener(domain=domain, id_generator=_IncrementalIds(cnt=initial_id), db=db)
    else:
        raise ValueError(f'Unknown url shortener type {shortener_type}')
