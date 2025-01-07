import requests
from django.conf import settings
import fitz  # PyMuPDF library
from difflib import SequenceMatcher
import os



API_KEY = settings.API_KEY
BASE_URL = settings.BASE_URL

def create_thread(request, workspace_slug, thread_name="New Conversation"):
    """
    Creates a new thread in the workspace and stores its slug in the session.
    """
    api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/new"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"name": thread_name}

    print(f"API URL: {api_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        print(f"API Response Status Code: {response.status_code}")
        print(f"API Response Content: {response.text}")  # Log raw response content

        if response.status_code == 200:
            thread_data = response.json()["thread"]
            request.session["thread_slug"] = thread_data["slug"]
            return thread_data["slug"]
        else:
            print(f"API Error: {response.text}")
            return None
    except Exception as e:
        print(f"Failed to create thread: {e}")
        return None


def normalize_text(text):
    """
    Normalize text for comparison by removing extra whitespace and converting to lowercase.
    """
    import unicodedata
    return " ".join(unicodedata.normalize("NFKD", text).lower().split())


def similarity_ratio(text1, text2):
    """
    Compute the similarity ratio between two texts using SequenceMatcher.
    """
    return SequenceMatcher(None, text1, text2).ratio()


def find_page_with_highest_similarity(pdf_path, text_to_search):
    """
    Search for the page containing text with the highest similarity to the given input in a PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        normalized_search_text = normalize_text(text_to_search)

        highest_similarity = 0
        best_page = None

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            page_text = normalize_text(page.get_text("text"))
            similarity = similarity_ratio(normalized_search_text, page_text)

            print(f"Page {page_number + 1}: Similarity Score = {similarity:.2f}")  # Debug log

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_page = page_number + 1  # Page numbers are 1-indexed

        pdf_document.close()

        # Return the page with the highest similarity, even if it's very low
        print(f"Highest Similarity: {highest_similarity:.2f} on Page: {best_page}")
        return best_page
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None


def process_sources_with_pages(sources, media_folder):
    """
    Add page numbers and page URLs to sources based on the highest similarity in the document.
    """
    for source in sources:
        doc_path = source.get("url", "").replace("file://", "").strip()
        doc_name = os.path.basename(doc_path)
        text = source.get("text", "").strip()

        if not text:
            source["page"] = None
            source["page_url"] = None
            continue

        pdf_path = os.path.join(media_folder, doc_name)
        if not os.path.exists(pdf_path):
            source["page"] = None
            source["page_url"] = None
            continue

        # Find the page with the highest similarity
        page_number = find_page_with_highest_similarity(pdf_path, text)

        if page_number:
            source["page"] = page_number
            source["page_url"] = f"/media/{doc_name}#page={page_number}"  # Correct URL format
        else:
            source["page"] = None
            source["page_url"] = None

    return sources
