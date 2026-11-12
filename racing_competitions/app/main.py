from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import get_db
from .models import Team, Driver, Race, Result
from .schemas import (TeamCreate, TeamPatch, TeamOut, DriverCreate, DriverPatch, DriverOut,
                      RaceCreate, RacePatch, RaceOut, ResultCreate, ResultPatch, ResultOut)
from .rules import ensure_unique_driver, ensure_unique_position, ensure_team_has_no_drivers

app = FastAPI(title="Racing Competitions API", version="1.0.0")

def find(db: Session, model, item_id: int):
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return item

def save(db: Session, item):
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Database constraint violation (duplicate or invalid reference)")

def patch(db: Session, item, data):
    changes = data.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(422, "Fields cannot be null")
    for key, value in changes.items():
        setattr(item, key, value)
    return save(db, item)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/teams", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return db.scalars(select(Team).order_by(Team.id)).all()
@app.get("/teams/{item_id}", response_model=TeamOut)
def get_team(item_id: int, db: Session = Depends(get_db)):
    return find(db, Team, item_id)
@app.post("/teams", response_model=TeamOut, status_code=201)
def create_team(data: TeamCreate, db: Session = Depends(get_db)):
    return save(db, Team(**data.model_dump()))
@app.patch("/teams/{item_id}", response_model=TeamOut)
def update_team(item_id: int, data: TeamPatch, db: Session = Depends(get_db)):
    return patch(db, find(db, Team, item_id), data)
@app.delete("/teams/{item_id}", status_code=204)
def delete_team(item_id: int, db: Session = Depends(get_db)):
    item = find(db, Team, item_id)
    count = db.scalar(select(func.count()).select_from(Driver).where(Driver.team_id == item_id))
    ensure_team_has_no_drivers(count)
    db.delete(item)
    db.commit()

@app.get("/drivers", response_model=list[DriverOut])
def list_drivers(db: Session = Depends(get_db)):
    return db.scalars(select(Driver).order_by(Driver.id)).all()
@app.get("/drivers/{item_id}", response_model=DriverOut)
def get_driver(item_id: int, db: Session = Depends(get_db)):
    return find(db, Driver, item_id)
@app.get("/teams/{team_id}/drivers", response_model=list[DriverOut])
def team_drivers(team_id: int, db: Session = Depends(get_db)):
    find(db, Team, team_id)
    return db.scalars(select(Driver).where(Driver.team_id == team_id).order_by(Driver.id)).all()
@app.post("/drivers", response_model=DriverOut, status_code=201)
def create_driver(data: DriverCreate, db: Session = Depends(get_db)):
    find(db, Team, data.team_id)
    return save(db, Driver(**data.model_dump()))
@app.patch("/drivers/{item_id}", response_model=DriverOut)
def update_driver(item_id: int, data: DriverPatch, db: Session = Depends(get_db)):
    if data.team_id is not None:
        find(db, Team, data.team_id)
    return patch(db, find(db, Driver, item_id), data)
@app.delete("/drivers/{item_id}", status_code=204)
def delete_driver(item_id: int, db: Session = Depends(get_db)):
    db.delete(find(db, Driver, item_id))
    db.commit()

@app.get("/races", response_model=list[RaceOut])
def list_races(db: Session = Depends(get_db)):
    return db.scalars(select(Race).order_by(Race.id)).all()
@app.get("/races/{item_id}", response_model=RaceOut)
def get_race(item_id: int, db: Session = Depends(get_db)):
    return find(db, Race, item_id)
@app.post("/races", response_model=RaceOut, status_code=201)
def create_race(data: RaceCreate, db: Session = Depends(get_db)):
    return save(db, Race(**data.model_dump()))
@app.patch("/races/{item_id}", response_model=RaceOut)
def update_race(item_id: int, data: RacePatch, db: Session = Depends(get_db)):
    return patch(db, find(db, Race, item_id), data)
@app.delete("/races/{item_id}", status_code=204)
def delete_race(item_id: int, db: Session = Depends(get_db)):
    db.delete(find(db, Race, item_id))
    db.commit()

@app.get("/results", response_model=list[ResultOut])
def list_results(db: Session = Depends(get_db)):
    return db.scalars(select(Result).order_by(Result.id)).all()
@app.get("/results/{item_id}", response_model=ResultOut)
def get_result(item_id: int, db: Session = Depends(get_db)):
    return find(db, Result, item_id)
@app.get("/races/{race_id}/results", response_model=list[ResultOut])
def race_results(race_id: int, db: Session = Depends(get_db)):
    find(db, Race, race_id)
    return db.scalars(select(Result).where(Result.race_id == race_id).order_by(Result.position)).all()
@app.post("/results", response_model=ResultOut, status_code=201)
def create_result(data: ResultCreate, db: Session = Depends(get_db)):
    # Lock race row: prevents simultaneous result inserts from bypassing business checks.
    race = db.scalar(select(Race).where(Race.id == data.race_id).with_for_update())
    if race is None:
        raise HTTPException(404, "Race not found")
    find(db, Driver, data.driver_id)
    ensure_unique_driver(db.scalar(select(Result.id).where(Result.race_id == data.race_id, Result.driver_id == data.driver_id)) is not None)
    ensure_unique_position(db.scalar(select(Result.id).where(Result.race_id == data.race_id, Result.position == data.position)) is not None)
    return save(db, Result(**data.model_dump()))
@app.patch("/results/{item_id}", response_model=ResultOut)
def update_result(item_id: int, data: ResultPatch, db: Session = Depends(get_db)):
    item = find(db, Result, item_id)
    if data.position is not None:
        db.scalar(select(Race).where(Race.id == item.race_id).with_for_update())
        occupied = db.scalar(select(Result.id).where(Result.race_id == item.race_id, Result.position == data.position, Result.id != item_id)) is not None
        ensure_unique_position(occupied)
    return patch(db, item, data)
@app.delete("/results/{item_id}", status_code=204)
def delete_result(item_id: int, db: Session = Depends(get_db)):
    db.delete(find(db, Result, item_id))
    db.commit()
