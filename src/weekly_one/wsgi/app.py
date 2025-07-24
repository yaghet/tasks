from wsgiref.simple_server import make_server
import requests
import json

HOST = "localhost"
PORT = 8000


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    currency = path.lstrip("/").upper()
    headers = [("Content-Type", "application/json")]

    if len(currency) != 3 or not currency.isalpha():
        status = "400 Bad Request"
        start_response(status, headers)
        body = json.dumps({"Error": "Invalid currency code"}).encode("utf-8")
        return [body]

    url = "https://api.exchangerate-api.com/v4/latest/{currency}".format(
        currency=currency
    )

    response = requests.get(url, timeout=10)

    try:
        if response.status_code == 200:
            result = response.json()
            status = "200 OK"
        else:
            status = "400 Bad Request"
            result = {"Error": "Failed to fetch rates"}

    except Exception as exp:
        status = "500 Internal Server Error"
        result = {"Error": str(exp)}

    start_response(status, headers)
    body = json.dumps(result).encode("utf-8")
    return [body]


if __name__ == "__main__":
    with make_server(HOST, PORT, application) as server:
        print(f"Serving on http://{HOST}:{PORT}")
        server.serve_forever()
