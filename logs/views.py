from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Log
from .utils import create_log_entry, upload_log_to_workspace, get_machine_list
from django.conf import settings

def create_log(request):
    """
    Create a new log with an associated machine.
    """
    machines = get_machine_list()

    if request.method == "POST":
        log_text = request.POST.get("log_text")
        machine_slug = request.POST.get("machine_slug")

        if not log_text or not machine_slug:
            messages.error(request, "Both log text and machine selection are required.")
            return redirect("create_log")

        # Save the log
        create_log_entry(log_text, machine_slug)
        messages.success(request, "Log created successfully.")
        return redirect("view_logs")

    return render(request, "logs/create_log.html", {"machines": machines})


def view_logs(request):
    """
    View all logs and their associated machines.
    """
    logs = Log.objects.all().order_by("-created_at")
    return render(request, "logs/view_logs.html", {"logs": logs})


def commit_log(request, log_id):
    """
    Commit a log to the machine's database via the correct API endpoints.
    """
    log = get_object_or_404(Log, id=log_id)
    filename = f"Log_{log.created_at.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    content = log.log_text

    # Use utility to upload and commit the log
    success, error_message = upload_log_to_workspace(content, filename, log.machine, settings.API_KEY, settings.BASE_URL)

    if success:
        log.committed = True
        log.save()
        messages.success(request, "Log successfully committed to the machine database.")
    else:
        messages.error(request, f"An error occurred: {error_message}")

    return redirect("view_logs")
