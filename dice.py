import random


def validate_probabilities(probabilities):
    if not isinstance(probabilities, list):
        return False, "Probabilities must be a list."

    if len(probabilities) != 6:
        return False, "Probabilities must contain exactly 6 entries."

    for i, p in enumerate(probabilities):
        if not isinstance(p, (int, float)):
            return False, f"Probability at index {i} is not numeric."
        if p < 0:
            return False, f"Probability at index {i} is negative."

    total = sum(probabilities)
    if not abs(total - 1.0) < 1e-9:
        return False, f"Probabilities must sum to 1.0, got {total}."

    return True, None


def generate_biased_rolls(probabilities, number_of_random):
    if not isinstance(number_of_random, int) or number_of_random < 1:
        raise ValueError("number_of_random must be a positive integer.")

    cumulative = []
    cumsum = 0.0
    for p in probabilities:
        cumsum += p
        cumulative.append(cumsum)

    cumulative[-1] = 1.0

    results = []
    for _ in range(number_of_random):
        r = random.random()  
        for face, threshold in enumerate(cumulative):
            if r < threshold:
                results.append(face + 1)  
                break
    return results


def process_request(payload):
    if not isinstance(payload, dict):
        return {"status": "error", "message": "Invalid JSON payload."}, 400

    if "probabilities" not in payload:
        return {"status": "error", "message": "Missing 'probabilities' field."}, 400

    if "number_of_random" not in payload:
        return {"status": "error", "message": "Missing 'number_of_random' field."}, 400

    probabilities = payload["probabilities"]
    number_of_random = payload.get("number_of_random", 1)

    is_valid, error_msg = validate_probabilities(probabilities)
    if not is_valid:
        return {"status": "error", "message": error_msg}, 400

    if not isinstance(number_of_random, int) or number_of_random < 1:
        return {"status": "error", "message": "number_of_random must be a positive integer."}, 400

    dices = generate_biased_rolls(probabilities, number_of_random)

    return {
        "status": "success",
        "probabilities": probabilities,
        "dices": dices
    }, 200
