import requests


def call_api(base_url, payload):
    try:
        response = requests.get(base_url, json=payload)  # GET method
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None


if __name__ == "__main__":
    url = "http://127.0.0.1:8080/roll_dice"

    # Example payload
    data = {
        "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],  # sum to 1
        "number_of_random": 10
    }

    print("Calling the API with the following payload:")
    print(data)

    result = call_api(url, data)
    print(type(result))
    print(result)
    if result:
        for i in result:
            print(i, result[i])
