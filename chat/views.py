from .utils import (
    normalize_text,
    similarity_ratio,
    find_page_with_highest_similarity,
    process_sources_with_pages,
    create_thread
)
from LeadTech1.settings import MACHINE_SLUGS, MEDIA_FOLDER
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from memories.utils import summarize_conversation
from memories.models import Memory
from django.conf import settings
import os

API_KEY = settings.API_KEY
BASE_URL = settings.BASE_URL


def search_source_page(request):
    """
    Handle the request to search for the page associated with a specific source.
    """
    if request.method == "POST":
        source_text = request.POST.get("source_text", "").strip()
        source_title = request.POST.get("source_title", "").strip()

        if not source_text or not source_title:
            return JsonResponse({"error": "Invalid source data provided."}, status=400)

        # Locate the PDF file
        pdf_path = os.path.join(MEDIA_FOLDER, source_title)
        if not os.path.exists(pdf_path):
            return JsonResponse({"error": "Document not found on the server."}, status=404)

        # Search for the page containing the source text
        page_number = find_page_with_highest_similarity(pdf_path, source_text)
        if page_number:
            page_url = f"/media/{source_title}#page={page_number}"
            return JsonResponse({
                "success": True,
                "page_number": page_number,
                "page_url": page_url
            })
        else:
            return JsonResponse({"error": "No matching page found in the document."}, status=404)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def chat_view(request):
    # Retrieve workspace slug from session
    workspace_slug = request.session.get("workspace_slug")
    if not workspace_slug:
        return redirect("select_machine")

    request.session.set_expiry(3600)  # Set session to expire in 1 hour for debugging

    # Retrieve or create thread_slug
    thread_slug = request.session.get("thread_slug")
    if not thread_slug:
        thread_slug = create_thread(request, workspace_slug)
        if thread_slug:
            request.session["thread_slug"] = thread_slug
        else:
            print(f"Failed to create thread for workspace_slug: {workspace_slug}")
            return render(request, "chat/chat.html", {"error": "Failed to create a new thread."})

    # Initialize or retrieve session data
    if "messages" not in request.session:
        request.session["messages"] = []
    if "sources" not in request.session:
        request.session["sources"] = []

    messages = request.session["messages"]
    sources = request.session["sources"]

    if request.method == "POST":
        user_message = request.POST.get("message", "")
        messages.append({"sender": "user", "text": user_message})

        # API call to get AI response
        api_url = f"{BASE_URL}/v1/workspace/{workspace_slug}/thread/{thread_slug}/chat"
        payload = {"message": user_message, "mode": "chat"}
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json()
            ai_response = response_data.get("textResponse", "No response available")
            messages.append({"sender": "ai", "text": ai_response})

            # Process sources if available
            response_sources = response_data.get("sources", [])
            sources = []  # Reset sources to avoid duplicates
            for source in response_sources:
                sources.append({
                    "title": source.get("title", "Unknown Title"),
                    "chunk": source.get("chunkSource", "No Chunk Source Available"),
                    "text": source.get("text", "No text available"),
                    "url": source.get("url"),
                })

            sources = process_sources_with_pages(sources, MEDIA_FOLDER)  # Add page numbers to sources
            request.session["sources"] = sources

            print("DEBUG: Sources Data:", sources)

        except Exception as e:
            messages.append({"sender": "ai", "text": f"An error occurred: {str(e)}"})

        # Save session data
        request.session["messages"] = messages
        request.session.modified = True

    return render(request, "chat/chat.html", {"messages": messages, "sources": sources})

def end_conversation(request):
    # Retrieve messages and workspace_slug
    messages = request.session.get("messages", [])
    workspace_slug = request.session.get("workspace_slug")

    if messages and workspace_slug:
        # Summarize the conversation
        summary = summarize_conversation(messages)

        if summary:
            # Save the summary to the database
            Memory.objects.create(
                workspace_slug=workspace_slug,
                summary=summary
            )
            # Clear the session
            request.session.pop("messages", None)
            request.session.pop("thread_slug", None)
            request.session.pop("sources", None)

    # Redirect to machine selection
    return redirect("select_machine")

def machine_selection_view(request):
    if request.method == "POST":
        selected_machine = request.POST.get("machine")

        # Use the key directly
        workspace_slug = MACHINE_SLUGS.get(selected_machine)

        if workspace_slug:
            # Clear existing session data
            request.session.flush()

            # Store the workspace key (not the slug name)
            request.session["workspace_slug"] = selected_machine
            request.session.set_expiry(3600)  # Optional: Set session expiry time

            return redirect("chat")
        else:
            return render(request, "chat/machine_selection.html", {"error": "Invalid machine selected."})

    return render(request, "chat/machine_selection.html")



