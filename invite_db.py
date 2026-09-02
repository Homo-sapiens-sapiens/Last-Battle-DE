from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import BigInteger, DateTime, String, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DB_PATH = Path(__file__).with_name("invites.db")

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH.as_posix()}")
Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True)
    inviter_id: Mapped[int] = mapped_column(BigInteger, index=True)
    target_id: Mapped[int] = mapped_column(BigInteger, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_invite(inviter_id: int, target_id: int) -> Invite:
    async with Session() as session:
        invite = Invite(inviter_id=inviter_id, target_id=target_id)
        session.add(invite)
        await session.commit()
        return invite


async def get_pending_by_inviter(inviter_id: int) -> Invite | None:
    async with Session() as session:
        result = await session.execute(
            select(Invite).where(
                Invite.inviter_id == inviter_id,
                Invite.status == "pending",
            )
        )
        return result.scalars().first()


async def set_invite_status(invite_id: int, status: str):
    async with Session() as session:
        await session.execute(
            update(Invite).where(Invite.id == invite_id).values(status=status)
        )
        await session.commit()


async def expire_all_pending():
    async with Session() as session:
        await session.execute(
            update(Invite).where(Invite.status == "pending").values(status="expired")
        )
        await session.commit()
