from aiohttp import web

from url_shortener import UrlShortener


async def make_url(request):
    url_shortener: UrlShortener = request.app['url_shortener']
    params = request.rel_url.query.copy()
    if 'url' not in params:
        raise web.HTTPBadRequest(reason='No url param presented')

    url: str = params.pop('url')
    force = params.pop('force', None) is not None
    try:
        result = await url_shortener.short_url(url, force=force, **params)
        return web.Response(text=result)
    except ValueError as e:
        raise web.HTTPBadRequest(reason=str(e))


async def get_url(request):
    url_shortener: UrlShortener = request.app['url_shortener']
    params = request.rel_url.query
    if 'short_url' not in params:
        raise web.HTTPBadRequest(reason='No short_url param presented')

    short_url: str = params['short_url']
    try:
        result = await url_shortener.get_url(short_url)
        return web.Response(text=result)
    except RuntimeError as e:
        raise web.HTTPBadRequest(reason=str(e))
    except ValueError as e:
        raise web.HTTPNotFound(reason=str(e))
