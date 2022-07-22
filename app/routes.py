from handlers import make_url, get_url


def setup_routes(app):
    app.router.add_get('/make_url', make_url)
    app.router.add_get('/get_url', get_url)
