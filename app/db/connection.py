from sqlalchemy import create_engine


def get_engine(connection_uri: str):
    engine = create_engine(
        connection_uri,
        pool_pre_ping=True,
        future=True
    )
    return engine