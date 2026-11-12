from pydantic import BaseModel, ConfigDict, Field

class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    country: str = Field(min_length=2, max_length=80)
class TeamPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=80)
class TeamOut(TeamCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DriverCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    number: int = Field(ge=1, le=999)
    team_id: int = Field(gt=0)
class DriverPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    number: int | None = Field(default=None, ge=1, le=999)
    team_id: int | None = Field(default=None, gt=0)
class DriverOut(DriverCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    circuit: str = Field(min_length=2, max_length=150)
    laps: int = Field(ge=1, le=1000)
class RacePatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    circuit: str | None = Field(default=None, min_length=2, max_length=150)
    laps: int | None = Field(default=None, ge=1, le=1000)
class RaceOut(RaceCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ResultCreate(BaseModel):
    race_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    position: int = Field(gt=0)
    points: int = Field(ge=0, le=1000)
class ResultPatch(BaseModel):
    position: int | None = Field(default=None, gt=0)
    points: int | None = Field(default=None, ge=0, le=1000)
class ResultOut(ResultCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
