import json

import requests


def main():
    login = requests.post(
        "http://127.0.0.1:5000/api/auth/login",
        json={"email": "admin@placement.edu", "password": "Admin@123"},
        timeout=10,
    )
    login.raise_for_status()
    token = login.json().get("access_token")
    if not token:
        raise RuntimeError("No access_token in login response")

    dash = requests.get(
        "http://127.0.0.1:5000/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if not dash.ok:
        print("STATUS:", dash.status_code)
        print(dash.text)
        return

    print(json.dumps(dash.json(), indent=2))


if __name__ == "__main__":
    main()

