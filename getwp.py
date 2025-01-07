import requests

# Configuration
API_KEY = "GYWHV6F-RM64JQN-QB7GHRW-4RVBJG8"
BASE_URL = "http://localhost:3001/api"


def get_workspaces():
    """Fetches the list of workspaces and their slugs."""
    url = f"{BASE_URL}/v1/workspaces"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)

        # Debugging: Check the raw response
        print(f"Raw Response: {response.text}")

        # Parse the JSON response
        if response.headers.get("Content-Type", "").startswith("application/json"):
            data = response.json()
            if isinstance(data, list):  # Ensure we have a list of workspaces
                for workspace in data:
                    print(f"Name: {workspace.get('name', 'Unknown')}, Slug: {workspace.get('slug', 'Unknown')}")
                return data
            else:
                print(f"Unexpected JSON structure: {data}")
        else:
            print(f"Unexpected content type: {response.headers.get('Content-Type')}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    get_workspaces()

