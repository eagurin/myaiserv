from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Account(BaseModel):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    balance = Column(DECIMAL(precision=18, scale=8), default=0.0, nullable=False)
    currency_code = Column(
        String(10), nullable=False, default="USD"
    )  # Can be USD, EUR, etc.

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, balance={self.balance}, currency={self.currency_code})>"
