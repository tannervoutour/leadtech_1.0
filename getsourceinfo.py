import requests
import time

# Replace with your actual API Key and Base URL
API_KEY = "GYWHV6F-RM64JQN-QB7GHRW-4RVBJG8"
BASE_URL = "http://localhost:3001/api"
WORKSPACE_SLUG = "powertrans"  # Replace with the desired workspace slug
USER_MESSAGE = "I'm having an issue with the loading sensor"  # Example message to trigger a response


def create_thread(workspace_slug):
    """
    Create a new thread for the given workspace slug with a unique slug.
    """
    api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/new"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    # Generate a unique slug using timestamp
    unique_slug = f"new-thread-{int(time.time())}"
    payload = {
        "userId": 1,  # Optional user ID, update as necessary
        "name": "New Thread",  # Replace with the desired thread name
        "slug": unique_slug,  # Ensure the slug is unique
    }

    try:
        print(f"API URL: {api_url}")  # Log the endpoint being called
        print(f"Payload: {payload}")  # Log the payload being sent
        response = requests.post(api_url, headers=headers, json=payload)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        if response.status_code in [200, 201]:  # HTTP OK or Created
            response_data = response.json()
            thread_slug = response_data.get("thread", {}).get("slug")
            if thread_slug:
                print(f"Thread created successfully with slug: {thread_slug}")
                return thread_slug
            else:
                print(f"Thread creation response missing 'slug': {response_data}")
                return None
        else:
            print(f"Failed to create thread: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def get_source_information(workspace_slug, thread_slug):
    """
    Retrieve and print all source information for the given thread.
    """
    # API Endpoint for the chat
    api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/{thread_slug}/chat"

    # Payload and headers for the API call
    payload = {"message": USER_MESSAGE, "mode": "chat"}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        # Make the API request
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code not in [200, 201]:
            print(f"Failed to fetch sources. Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            return

        response_data = response.json()

        # Check if sources are available in the response
        response_sources = response_data.get("sources", [])
        if not response_sources:
            print("No sources available in the response.")
            return

        # Print all available metadata for each source
        for i, source in enumerate(response_sources, 1):
            print(f"Source {i}:")
            for key, value in source.items():
                print(f"  {key}: {value}")
            print("\n")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An error occurred while fetching sources: {e}")


# Main function to orchestrate the workflow
def main():
    # Create a new thread
    thread_slug = create_thread(WORKSPACE_SLUG)
    if not thread_slug:
        print("Failed to create thread. Exiting.")
        return

    # Retrieve and display source information
    get_source_information(WORKSPACE_SLUG, thread_slug)


# Run the script
if __name__ == "__main__":
    main()
