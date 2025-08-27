import os
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Index,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Mapped,
    mapped_column,
)


Base = declarative_base()


def _default_db_url() -> str:
    here = os.path.dirname(__file__)
    db_path = os.path.join(here, "server.db")
    return f"sqlite:///{db_path}"


DATABASE_URL = os.getenv("DATABASE_URL", _default_db_url())

# For SQLite, future=True and check_same_thread=False to allow usage in Flask threads
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class TokenReport(Base):
    __tablename__ = "token_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[str] = mapped_column(index=True, nullable=False)

    name: Mapped[str | None]
    symbol: Mapped[str | None]

    score_normalised: Mapped[int | None]
    risk_level: Mapped[str | None]

    price: Mapped[float | None]
    holders: Mapped[int | None]
    liquidity: Mapped[float | None]
    market_cap: Mapped[float | None]
    creator_holdings_pct: Mapped[float | None]

    detected_at: Mapped[str | None]  # store original string from API
    fetched_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    raw_json: Mapped[str | None]  # full API payload as JSON string


# Composite index to speed up latest-by-token lookups
Index(
    "ix_token_reports_token_id_fetched_at",
    TokenReport.token_id,
    TokenReport.fetched_at,
)


def init_db():
    Base.metadata.create_all(engine)
