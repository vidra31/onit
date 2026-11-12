def seed(client):
    team = client.post("/teams", json={"name": "Silver Arrow", "country": "Germany"})
    assert team.status_code == 201
    tid = team.json()["id"]
    driver = client.post("/drivers", json={"name": "Alex Speed", "number": 44, "team_id": tid})
    race = client.post("/races", json={"name": "Grand Prix", "circuit": "Monza", "laps": 53})
    assert driver.status_code == 201 and race.status_code == 201
    return tid, driver.json()["id"], race.json()["id"]

def test_crud_teams(client):
    tid, did, rid = seed(client)
    assert client.get(f"/teams/{tid}").json()["country"] == "Germany"
    assert client.patch(f"/teams/{tid}", json={"country": "Italy"}).json()["country"] == "Italy"
    assert client.delete(f"/teams/{tid}").status_code == 409
    assert client.delete(f"/drivers/{did}").status_code == 204
    assert client.delete(f"/teams/{tid}").status_code == 204
    assert client.get(f"/teams/{tid}").status_code == 404

def test_results_and_duplicate_driver(client):
    tid, did, rid = seed(client)
    data = {"race_id": rid, "driver_id": did, "position": 1, "points": 25}
    response = client.post("/results", json=data)
    assert response.status_code == 201
    assert client.post("/results", json={**data, "position": 2}).status_code == 409
    result_id = response.json()["id"]
    assert client.patch(f"/results/{result_id}", json={"points": 18}).json()["points"] == 18
    assert client.get(f"/races/{rid}/results").json()[0]["id"] == result_id

def test_position_cannot_be_reused(client):
    tid, did, rid = seed(client)
    second = client.post("/drivers", json={"name": "Sam Racer", "number": 55, "team_id": tid}).json()["id"]
    assert client.post("/results", json={"race_id": rid, "driver_id": did, "position": 1, "points": 25}).status_code == 201
    assert client.post("/results", json={"race_id": rid, "driver_id": second, "position": 1, "points": 18}).status_code == 409
    assert client.post("/results", json={"race_id": rid, "driver_id": second, "position": 2, "points": 18}).status_code == 201

def test_validation_and_missing_reference(client):
    tid, did, rid = seed(client)
    assert client.post("/teams", json={"name": "Silver Arrow", "country": "Germany"}).status_code == 409
    assert client.post("/races", json={"name": "Bad", "circuit": "Track", "laps": 0}).status_code == 422
    assert client.post("/drivers", json={"name": "Test Driver", "number": 2, "team_id": 9999}).status_code == 404
    assert client.post("/results", json={"race_id": rid, "driver_id": did, "position": 1, "points": -1}).status_code == 422

def test_race_and_result_deletion(client):
    tid, did, rid = seed(client)
    response = client.post("/results", json={"race_id": rid, "driver_id": did, "position": 1, "points": 25})
    assert response.status_code == 201
    assert client.delete(f"/races/{rid}").status_code == 204
    assert client.get(f"/results/{response.json()['id']}").status_code == 404
