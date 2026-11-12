from fastapi import HTTPException

def ensure_unique_driver(existing: bool):
    if existing:
        raise HTTPException(409, "Driver already has a result in this race")

def ensure_unique_position(existing: bool):
    if existing:
        raise HTTPException(409, "Finish position is already taken in this race")

def ensure_valid_points(points: int):
    if not 0 <= points <= 1000:
        raise HTTPException(422, "Points must be between 0 and 1000")

def ensure_team_has_no_drivers(count: int):
    if count:
        raise HTTPException(409, "Cannot delete a team with drivers")
