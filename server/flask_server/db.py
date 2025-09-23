import os
from datetime import datetime
from typing import Optional
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

    name: Mapped[Optional[str]]
    symbol: Mapped[Optional[str]]

    score_normalised: Mapped[Optional[int]]
    risk_level: Mapped[Optional[str]]

    price: Mapped[Optional[float]]
    holders: Mapped[Optional[int]]
    liquidity: Mapped[Optional[float]]
    market_cap: Mapped[Optional[float]]
    creator_holdings_pct: Mapped[Optional[float]]

    detected_at: Mapped[Optional[str]]  # store original string from API
    fetched_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    raw_json: Mapped[Optional[str]]  # full API payload as JSON string


# Composite index to speed up latest-by-token lookups
Index(
    "ix_token_reports_token_id_fetched_at",
    TokenReport.token_id,
    TokenReport.fetched_at,
)


def init_db():
    Base.metadata.create_all(engine)
