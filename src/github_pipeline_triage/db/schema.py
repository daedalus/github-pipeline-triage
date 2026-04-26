"""SQLAlchemy database models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Maintainer(Base):
    __tablename__ = "maintainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    github_login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TriageItem(Base):
    __tablename__ = "triage_items"

    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)

    github_state: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    branch: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[str] = mapped_column(String(50))
    closed_at: Mapped[str | None] = mapped_column(String(50))
    merged_at: Mapped[str | None] = mapped_column(String(50))

    labels: Mapped[list] = mapped_column(JSON, default=list)
    files: Mapped[list] = mapped_column(JSON, default=list)

    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    priority: Mapped[int | None] = mapped_column(Integer)
    triage_status: Mapped[str] = mapped_column(String(50), default="untriaged")

    severity_heuristic: Mapped[str] = mapped_column(String(20), default="normal")
    is_noise: Mapped[bool] = mapped_column(Boolean, default=False)
    noise_reason: Mapped[str] = mapped_column(Text, default="")

    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    suspicion_level: Mapped[str] = mapped_column(String(20), default="none")
    suspicious_flags: Mapped[list] = mapped_column(JSON, default=list)

    first_time_author: Mapped[bool] = mapped_column(Boolean, default=False)
    modules: Mapped[list] = mapped_column(JSON, default=list)
    linked_issues: Mapped[list] = mapped_column(JSON, default=list)

    cluster_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clusters.id"))

    created_at_db: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at_db: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claims: Mapped[list[Claim]] = relationship("Claim", back_populates="item")
    tags: Mapped[list[Tag]] = relationship("Tag", back_populates="item")
    notes: Mapped[list[Note]] = relationship("Note", back_populates="item")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_number: Mapped[int] = mapped_column(Integer, ForeignKey("triage_items.number"))
    maintainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("maintainers.id"))
    intent: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[TriageItem] = relationship("TriageItem", back_populates="claims")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_number: Mapped[int] = mapped_column(Integer, ForeignKey("triage_items.number"))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[TriageItem] = relationship("TriageItem", back_populates="tags")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_number: Mapped[int] = mapped_column(Integer, ForeignKey("triage_items.number"))
    maintainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("maintainers.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[TriageItem] = relationship("TriageItem", back_populates="notes")


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    representative_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(50))
    item_number: Mapped[int | None] = mapped_column(Integer)
    maintainer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("maintainers.id"))
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
