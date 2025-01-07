import openai
import requests
from django.conf import settings

API_KEY = settings.API_KEY
BASE_URL = settings.BASE_URL
openai.api_key = settings.OPENAI_KEY

def summarize_conversation(conversation):
    """Summarize a given conversation using the ChatGPT API."""
    # Format the conversation into a single text block
    formatted_conversation = "\n".join(
        [f"{'User' if msg['sender'] == 'user' else 'AI'}: {msg['text']}" for msg in conversation]
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize the conversation concisely in a way that highlights information that may be useful for future inquiries."},
                {"role": "user", "content": formatted_conversation},
            ],
        )
        summary = response.choices[0].message['content']
        return summary
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        return None


def upload_memory_to_workspace(slug, filename, content, api_key):
    base_url = "http://localhost:3001/api"

    # Step 1: Upload the document
    upload_url = f"{base_url}/v1/document/raw-text"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "textContent": content,
        "metadata": {
            "title": filename
        }
    }

    try:
        upload_response = requests.post(upload_url, json=payload, headers=headers)

        if upload_response.status_code == 200:
            print("Memory successfully uploaded.")
            upload_data = upload_response.json()

            # Extract document location
            document_location = upload_data["documents"][0]["location"]

            # Step 2: Add the document to the workspace
            update_workspace_url = f"{base_url}/v1/workspace/{slug}/update-embeddings"
            workspace_payload = {
                "adds": [document_location],
                "deletes": []
            }

            workspace_response = requests.post(update_workspace_url, json=workspace_payload, headers=headers)

            if workspace_response.status_code == 200:
                print(f"Memory successfully associated with workspace '{slug}'.")
                return workspace_response.json()
            else:
                print(f"Failed to associate memory with workspace. Status code: {workspace_response.status_code}")
                print("Response:", workspace_response.text)
                return None
        else:
            print(f"Failed to upload memory. Status code: {upload_response.status_code}")
            print("Response:", upload_response.text)
            return None

    except Exception as e:
        print(f"Error uploading memory to workspace: {e}")
        return None
