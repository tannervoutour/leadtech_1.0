from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Memory
from .utils import upload_memory_to_workspace
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

API_KEY = settings.API_KEY
BASE_URL = settings.BASE_URL


def memory_list(request):
    filter_type = request.GET.get("filter", "all")  # Get filter type from dropdown
    if filter_type == "pending":
        memories = Memory.objects.filter(verification_status="pending")
    elif filter_type == "verified":
        memories = Memory.objects.filter(verification_status="verified")
    else:
        memories = Memory.objects.all()

    return render(request, "memories/memory_list.html", {"memories": memories, "filter_type": filter_type})


def verify_memory(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id)

    # Update verification status
    memory.verified = True
    memory.verification_status = "verified"  # Ensure consistency with filtering
    memory.save()

    # Upload to AnythingLLM
    result = upload_memory_to_workspace(
        slug=memory.workspace_slug,
        filename=f"Memory_{memory.date_created.strftime('%Y-%m-%d_%H-%M-%S')}.txt",
        content=memory.summary,
        api_key=API_KEY
    )

    if result:
        # Add a success message
        messages.success(request, "Memory verified and uploaded successfully.")
    else:
        # Add an error message
        messages.error(request, "Memory verified but upload to AnythingLLM failed.")

    # Redirect to the memories page
    return redirect("memories")
