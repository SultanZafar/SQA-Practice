import pytest


def test_get_user_details(playwright):
    api_context = playwright.request.new_context(base_url="http://reqres.in")
    
    response = api_context.get("/api/users/2")

    assert response.status == 200

    response_json = response.json()
    assert response_json["data"]["id"] == 2
    assert response_json["data"]["first_name"] == "Janet"

    print(f"/n[API Success]) Loaded User: {response_json['data']['first_name']}")
    api_context.dispose