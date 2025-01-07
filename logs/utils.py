import requests
from django.conf import settings
from .models import Log

def get_machine_list():
    """
    Get the list of machines from the centralized machine mapping.
    """
    from LeadTech1.settings import MACHINE_SLUGS
    return [(slug, name) for slug, name in MACHINE_SLUGS.items()]


def create_log_entry(log_text, machine_slug):
    """
    Create and save a new log entry.
    """
    log = Log.objects.create(log_text=log_text, machine=machine_slug)
    log.save()
    return log


def upload_log_to_workspace(content, filename, machine_slug, api_key, base_url):
    """
    Upload a log as raw text and associate it with a machine's workspace.
    """
    try:
        # Step 1: Upload the log as a raw-text document
        upload_url = f"{base_url}/v1/document/raw-text"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        upload_payload = {
            "textContent": content,
            "metadata": {"title": filename},
        }
        upload_response = requests.post(upload_url, json=upload_payload, headers=headers)

        if upload_response.status_code != 200:
            return False, f"Failed to upload log: {upload_response.text}"

        # Extract document location
        upload_data = upload_response.json()
        document_location = upload_data["documents"][0]["location"]

        # Step 2: Add the document to the machine's workspace
        update_workspace_url = f"{base_url}/v1/workspace/{machine_slug}/update-embeddings"
        workspace_payload = {
            "adds": [document_location],
            "deletes": [],
        }
        workspace_response = requests.post(update_workspace_url, json=workspace_payload, headers=headers)

        if workspace_response.status_code != 200:
            return False, f"Failed to associate log with machine: {workspace_response.text}"

        return True, None
    except Exception as e:
        return False, str(e)
