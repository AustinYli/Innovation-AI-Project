from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_address: Mapped[str] = mapped_column(String(42), nullable=False)
    normalized_wallet_address: Mapped[str] = mapped_column(
        String(42),
        unique=True,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    feature_snapshots: Mapped[list["WalletFeatureSnapshot"]] = relationship(
        back_populates="wallet"
    )
    score_snapshots: Mapped[list["WalletScoreSnapshot"]] = relationship(
        back_populates="wallet"
    )
    proofs: Mapped[list["WalletProofSnapshot"]] = relationship(
        back_populates="wallet"
    )


class WalletFeatureSnapshot(Base):
    __tablename__ = "wallet_feature_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        index=True,
        nullable=False,
    )
    provider_profile: Mapped[dict] = mapped_column(JSON, nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    wallet: Mapped[Wallet] = relationship(back_populates="feature_snapshots")


class WalletScoreSnapshot(Base):
    __tablename__ = "wallet_score_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        index=True,
        nullable=False,
    )
    human_likelihood: Mapped[str] = mapped_column(String(20), nullable=False)
    trust_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_flags: Mapped[list] = mapped_column(JSON, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    wallet: Mapped[Wallet] = relationship(back_populates="score_snapshots")


class WalletProofSnapshot(Base):
    __tablename__ = "wallet_proof_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        index=True,
        nullable=False,
    )
    proof_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    behavior_fingerprint_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    proof_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    wallet: Mapped[Wallet] = relationship(back_populates="proofs")
