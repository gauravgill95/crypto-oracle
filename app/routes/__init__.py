def initialize_routes(app):
    from .health_router import router as health_router

    app.include_router(health_router)