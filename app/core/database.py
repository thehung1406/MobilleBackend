from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

# 1. Tạo engine (kết nối DB)
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,         # log SQL ra console, để debug
    pool_pre_ping=True # check connection trước khi dùng
)

# 2. Hàm tạo DB schema (migration cơ bản)
def init_db() -> None:
    SQLModel.metadata.create_all(engine)

# 3. Dependency cho FastAPI
def get_session():
    with Session(engine) as session:
        yield session
