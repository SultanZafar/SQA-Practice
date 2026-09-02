import random


def test_health_check(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")
    
    response = api_context.get("/api/health")
    assert response.status == 200

    response_json = response.json()
    assert response_json["status"] == "ok"

    api_context.dispose

def test_get_all_tasks(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")
    response = api_context.get("/api/tasks")
    assert response.status == 200
    api_context.dispose()

def test_create_task_via_api(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")
    random_id = random.randint(1000, 9999)

    response = api_context.post("/api/tasks", data={
        "title": f"API Task {random_id}",
        "priority": "High",
        "user_id":9
    })
    assert response.status ==201

    response_json = response.json()
    assert response_json["title"] == f"API Task {random_id}"
    api_context.dispose()

def test_update_task_via_api(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")

    create_response = api_context.post("/api/tasks", data={
        "title": "Task to update",
        "user_id": 9
    })
    task_id = create_response.json()["id"]

    update_response = api_context.put(f"/api/tasks/{task_id}", data={
        "title": "Updated Title",
        "status": "Completed"
    })
    assert update_response.status == 200
    assert update_response.json()["status"] == "Completed"
    api_context.dispose()


def test_delete_task_via_api(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")

    create_response = api_context.post("/api/tasks", data={
        "title": "Task to delete",
        "user_id": 9
    })
    task_id = create_response.json()["id"]

    delete_response = api_context.delete(f"/api/tasks/{task_id}")
    assert delete_response.status == 200

    get_response = api_context.get(f"/api/tasks/{task_id}")
    assert get_response.status == 404
    api_context.dispose()


def test_create_task_empty_title_via_api(playwright):
    api_context = playwright.request.new_context(base_url="http://localhost:5000")

    response = api_context.post("/api/tasks", data={
        "title": "",
        "user_id": 9
    })
    assert response.status == 400
    api_context.dispose()