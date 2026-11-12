from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    drivers: Mapped[list["Driver"]] = relationship(back_populates="team")

class Driver(Base):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    team: Mapped[Team] = relationship(back_populates="drivers")
    results: Mapped[list["Result"]] = relationship(back_populates="driver", cascade="all, delete-orphan")

class Race(Base):
    __tablename__ = "races"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    circuit: Mapped[str] = mapped_column(String(150), nullable=False)
    laps: Mapped[int] = mapped_column(Integer, nullable=False)
    results: Mapped[list["Result"]] = relationship(back_populates="race", cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "results"
    __table_args__ = (
        UniqueConstraint("race_id", "driver_id", name="uq_race_driver"),
        UniqueConstraint("race_id", "position", name="uq_race_position"),
        CheckConstraint("position > 0", name="ck_result_position"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id", ondelete="CASCADE"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    race: Mapped[Race] = relationship(back_populates="results")
    driver: Mapped[Driver] = relationship(back_populates="results")
