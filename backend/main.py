from sqlalchemy import create_engine, text
from config import settings
from model import User, Base, UserRole


def init_db():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Create db with Modular structure")


def main():
    print(f"Connect to database {settings.DB_NAME} at port {settings.DB_HOST}")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"Connect successfull! Version : {result.fetchone()[0]}")
    except Exception as e:
        print(f"Connect Error : {e}")


if __name__ == "__main__":
    main()
    init_db()
