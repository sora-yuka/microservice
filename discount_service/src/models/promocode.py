from datetime import datetime
from enum import Enum

from sqlalchemy import String, Numeric, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base, UTCDateTime


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    discount_type: Mapped[DiscountType] = mapped_column(String(20))
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    min_cart_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    valid_from: Mapped[datetime] = mapped_column(UTCDateTime)
    valid_until: Mapped[datetime] = mapped_column(UTCDateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
