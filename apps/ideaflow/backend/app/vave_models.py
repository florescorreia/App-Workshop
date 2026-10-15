"""Additive VAVE records. Existing ideas and their lifecycle are never rewritten."""
from sqlalchemy import String, ForeignKey, Integer, JSON, LargeBinary, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
from .models import uid

class Program(Base):
    __tablename__ = 'vave_program'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    record_version: Mapped[int] = mapped_column(Integer, default=1)
    data: Mapped[dict] = mapped_column(JSON)

class Case(Base):
    __tablename__ = 'vave_case'
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), primary_key=True)
    program_id: Mapped[str] = mapped_column(ForeignKey('vave_program.id'), index=True)
    maturity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='Draft')
    data: Mapped[dict] = mapped_column(JSON)
    reviews: Mapped[dict] = mapped_column(JSON, default=dict)
    approved: Mapped[dict | None] = mapped_column(JSON)
    actuals: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (CheckConstraint('maturity BETWEEN 0 AND 6'), CheckConstraint("status IN ('Draft','Active','On hold','Rejected','Cancelled','Superseded','Closed')"))

class ProgramEvent(Base):
    __tablename__ = 'vave_program_event'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    program_id: Mapped[str] = mapped_column(ForeignKey('vave_program.id'))
    actor_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    data: Mapped[dict] = mapped_column(JSON)

class Evidence(Base):
    __tablename__ = 'vave_evidence'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), index=True)
    name: Mapped[str] = mapped_column(String(240))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    sha256: Mapped[str] = mapped_column(String(64))
    shared: Mapped[bool] = mapped_column(default=False)

class Notice(Base):
    __tablename__ = 'vave_notice'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'), index=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'))
    data: Mapped[dict] = mapped_column(JSON)
    read: Mapped[bool] = mapped_column(default=False)

class Preference(Base):
    __tablename__ = 'vave_preference'
    user_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'), primary_key=True)
    record_version: Mapped[int] = mapped_column(Integer, default=1)
    data: Mapped[dict] = mapped_column(JSON)
