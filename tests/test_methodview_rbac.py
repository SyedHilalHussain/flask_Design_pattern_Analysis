import pytest
from flask import Flask, jsonify, request, session
from flask.views import MethodView
import traceback


def test_methodview_rbac():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"

    class ProductAPI(MethodView):
        roles = {
            "GET": ["user", "admin"],
            "POST": ["admin"],
            "PATCH": ["admin"]
        }

        def get(self, product_id):
            return jsonify({"product": "Laptop", "id": product_id})

        def post(self):
            data = request.get_json()
            return jsonify({"message": "Product created", "data": data})

        def patch(self, product_id):
            data = request.get_json()
            return jsonify({"message": f"Updated product {product_id} with {data}"})

    app.add_url_rule('/products', view_func=ProductAPI.as_view('product_api_post'), methods=["POST"])
    app.add_url_rule('/products/<int:product_id>', view_func=ProductAPI.as_view('product_api'), methods=["GET", "PATCH"])

    client = app.test_client()

    def run_assert(description, condition):
        if condition:
            print(f"[PASS] {description}")
        else:
            message = f"[FAIL] {description} -- Expected condition was False"
            print(message)
            raise AssertionError(message)

    # User Role
    with client.session_transaction() as sess:
        sess["user_role"] = "user"
    with client:
        response = client.get('/products/1')
        run_assert("User should access GET", response.status_code == 200)

        response = client.post('/products', json={"name": "Tablet"})
        run_assert("User should NOT access POST", response.status_code == 403)
        run_assert("User POST error message", response.json["error"] == "Forbidden: Insufficient role")

        response = client.patch('/products/1', json={"price": 999})
        run_assert("User should NOT access PATCH", response.status_code == 403)
        run_assert("User PATCH error message", response.json["error"] == "Forbidden: Insufficient role")

    # Admin Role (INTENTIONAL FAIL by setting as 'user')
    with client.session_transaction() as sess:
        sess["user_role"] = "user"  # should be admin to pass
    with client:
        response = client.get('/products/1')
        run_assert("Admin should access GET", response.status_code == 200)

        response = client.post('/products', json={"name": "Tablet"})
        run_assert("Admin should access POST", response.status_code == 200)
        run_assert("Admin POST success", response.json.get("message") == "Product created")

        response = client.patch('/products/1', json={"price": 999})
        run_assert("Admin should access PATCH", response.status_code == 200)
        run_assert("Admin PATCH success", response.json.get("message") == "Updated product 1 with {'price': 999}")

    # Guest Role
    with client.session_transaction() as sess:
        sess["user_role"] = "guest"
    with client:
        response = client.get('/products/1')
        run_assert("Guest should NOT access GET", response.status_code == 403)
        run_assert("Guest GET error message", response.json["error"] == "Forbidden: Insufficient role")


if __name__ == "__main__":
    pytest.main(["-v", "test_methodview_rbac.py", "-s"])













# import pytest
# from flask import Flask, jsonify, request, session
# from flask.views import MethodView


# def test_methodview_rbac():
#     app = Flask(__name__)
#     app.secret_key = "test_secret_key"

#     class ProductAPI(MethodView):
#         roles = {
#             "GET": ["user", "admin"],
#             "POST": ["admin"],
#             "PATCH": ["admin"]
#         }

#         def get(self, product_id):
#             return jsonify({"product": "Laptop", "id": product_id})

#         def post(self):
#             data = request.get_json()
#             return jsonify({"message": "Product created", "data": data})

#         def patch(self, product_id):
#             data = request.get_json()
#             return jsonify({"message": f"Updated product {product_id} with {data}"})

#     # Separate POST route
#     app.add_url_rule('/products', view_func=ProductAPI.as_view('product_api_post'), methods=["POST"])
#     app.add_url_rule('/products/<int:product_id>', view_func=ProductAPI.as_view('product_api'), methods=["GET", "PATCH"])

#     client = app.test_client()

#     # User Role
#     with client.session_transaction() as sess:
#         sess["user_role"] = "user"
#     with client:
#         response = client.get('/products/1')
#         assert response.status_code == 200
#         assert response.json == {"product": "Laptop", "id": 1}

#         response = client.post('/products', json={"name": "Tablet"})
#         assert response.status_code == 403
#         assert response.json["error"] == "Forbidden: Insufficient role"

#         response = client.patch('/products/1', json={"price": 999})
#         assert response.status_code == 403
#         assert response.json["error"] == "Forbidden: Insufficient role"

#     # Admin Role
#     with client.session_transaction() as sess:
#         sess["user_role"] = "admin"
#     with client:
#         response = client.get('/products/1')
#         assert response.status_code == 200
#         assert response.json == {"product": "Laptop", "id": 1}

#         response = client.post('/products', json={"name": "Tablet"})
#         assert response.status_code == 200
#         assert response.json["message"] == "Product created"

#         response = client.patch('/products/1', json={"price": 999})
#         assert response.status_code == 200
#         assert response.json["message"] == "Updated product 1 with {'price': 999}"

#     # Guest Role
#     with client.session_transaction() as sess:
#         sess["user_role"] = "guest"
#     with client:
#         response = client.get('/products/1')
#         assert response.status_code == 403
#         assert response.json["error"] == "Forbidden: Insufficient role"


# if __name__ == "__main__":
#     pytest.main(["-v", "test_methodview_rbac.py"])
