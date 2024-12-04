from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class SecurityTries(Base):
    __tablename__ = 'security_tries'

    id: Mapped[UUID] = mapped_column(as_uuid=True, primary_key=True)
    userId: Mapped[UUID]
    remainingTries: Mapped[int]
    isBlocked: Mapped[bool]
    startDate: Mapped[datetime]
    endDate: Mapped[datetime]
