from backend.auth import init_auth_db


def init_db():
    """Initialize the database."""
    init_auth_db()


if __name__ == "__main__":
    init_db()
