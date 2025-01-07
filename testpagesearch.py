import requests
import fitz  # PyMuPDF library
import os
import uuid
from difflib import SequenceMatcher

# Replace with your actual API Key and Base URL
API_KEY = "GYWHV6F-RM64JQN-QB7GHRW-4RVBJG8"
BASE_URL = "http://localhost:3001/api"
WORKSPACE_SLUG = "washer"  # Replace with the desired workspace slug
USER_MESSAGE = "I'm having an issue with the loading sensor"
MEDIA_FOLDER = r"C:\Users\Tanner Voutour\Desktop\ProjectFolder\LeadTech1\media"

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

def create_thread(workspace_slug):
    """
    Create a new thread for the given workspace slug with a unique slug.
    """
    api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/new"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    unique_slug = str(uuid.uuid4())

    payload = {
        "userId": 1,
        "name": "New Thread",
        "slug": unique_slug,
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        response_data = response.json()
        return response_data.get("thread", {}).get("slug")
    else:
        print(f"Failed to create thread: {response.text}")
        return None

def call_ai_api(workspace_slug, thread_slug, message):
    """
    Make a call to the AI API and return the sources.
    """
    api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/{thread_slug}/chat"
    payload = {"message": message, "mode": "chat"}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(api_url, json=payload, headers=headers)
    response_data = response.json()

    if response.status_code in [200, 201]:
        return response_data.get("sources", [])
    else:
        print(f"Failed to get sources: {response.text}")
        return None

def find_page_with_highest_similarity(pdf_path, text_to_search):
    """
    Search for the page with the highest similarity to the given input in a PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        normalized_search_text = normalize_text(text_to_search)
        print(f"Normalized Search Text: {normalized_search_text[:500]}...")

        best_page = None
        best_similarity = 0

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            page_text = normalize_text(page.get_text("text"))

            # Calculate similarity
            similarity = similarity_ratio(normalized_search_text, page_text)

            # Log similarity scores for debugging
            print(f"Page {page_number + 1}: Similarity Score = {similarity:.2f}")

            # Update the best match if this page has a higher similarity
            if similarity > best_similarity:
                best_similarity = similarity
                best_page = page_number + 1  # 1-indexed

        pdf_document.close()

        if best_page is not None:
            print(f"Highest similarity {best_similarity:.2f} found on page {best_page}")
            return best_page, best_similarity
        else:
            print("No similar text found in the document.")
            return None, 0
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None, 0

def process_sources_with_highest_similarity(sources):
    """
    Process the sources to extract document name and locate the page number with the highest similarity for the source text.
    """
    for source in sources:
        doc_path = source.get("url", "").replace("file://", "").strip()
        doc_name = os.path.basename(doc_path)
        text = source.get("text", "").strip()

        if not text:
            print(f"No text available for source: {doc_name}")
            continue

        pdf_path = os.path.join(MEDIA_FOLDER, doc_name)
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            continue

        print(f"Searching for text in document: {pdf_path}")
        print(f"Text to search: {text}")

        # Find the page with the highest similarity
        best_page, best_similarity = find_page_with_highest_similarity(pdf_path, text)
        if best_page:
            print(f"Best match for source '{doc_name}' is page {best_page} with similarity {best_similarity:.2f}")
        else:
            print(f"No matching text found in document: {doc_name}")

def main():
    # Create a new thread
    thread_slug = create_thread(WORKSPACE_SLUG)
    if not thread_slug:
        print("Failed to create thread. Exiting.")
        return

    # Call AI API and get sources
    sources = call_ai_api(WORKSPACE_SLUG, thread_slug, USER_MESSAGE)
    if not sources:
        print("No sources returned. Exiting.")
        return

    # Process the sources
    process_sources_with_highest_similarity(sources)

if __name__ == "__main__":
    main()


