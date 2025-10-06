import requests

def test_equipment_database_api():
    """
    This test verifies that the /api/equipment-database/ endpoint is active
    and returns a successful response.
    """
    # 1. Arrange: Define the API endpoint URL.
    url = "http://127.0.0.1:8000/api/equipment-database/"

    try:
        # 2. Act: Make a GET request to the endpoint.
        response = requests.get(url)

        # 3. Assert: Check for a successful status code (200 OK).
        assert response.status_code == 200
        print(f"Success: The endpoint {url} is active and returned a status code of 200.")

        # 4. Assert: Check if the response content is valid JSON.
        data = response.json()
        print(f"Success: The endpoint returned valid JSON data.")

        # 5. Print a sample of the data for review.
        print("Sample data:", data[:1] if isinstance(data, list) and data else "No data found")

    except requests.exceptions.RequestException as e:
        print(f"Error: The request to {url} failed: {e}")
        assert False, f"API request failed: {e}"
    except ValueError:
        print(f"Error: The endpoint did not return valid JSON.")
        assert False, "Invalid JSON response"

# Run the test
if __name__ == "__main__":
    test_equipment_database_api()