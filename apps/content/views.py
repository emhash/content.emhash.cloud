import json
import os
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import ContentForm, ContentMediaForm, ContentSectionFormSet
from .models import Category, Content, ContentMedia, InlineMediaTag, SubCategory, SubSubCategory


def home_view(request):
    contents = Content.objects.filter(status=Content.Status.PUBLISHED).select_related(
        "sub_sub_category__sub_category__category", "created_by"
    ).order_by("-published_at", "-created_at")

    category_slug = request.GET.get("category", "").strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        contents = contents.filter(sub_sub_category__sub_category__category=selected_category)

    q = request.GET.get("q", "").strip()
    if q:
        contents = contents.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

    paginator = Paginator(contents, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    return render(
        request,
        "home/index.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "selected_category": selected_category,
            "query": q,
        },
    )


def content_detail_view(request, slug):
    qs = Content.objects.select_related("sub_sub_category__sub_category__category", "created_by")

    if request.user.is_staff:
        content = get_object_or_404(qs, slug=slug)
    else:
        content = get_object_or_404(qs, slug=slug, status=Content.Status.PUBLISHED)

    related = Content.objects.filter(
        sub_sub_category=content.sub_sub_category,
        status=Content.Status.PUBLISHED,
    ).exclude(pk=content.pk).order_by("-published_at")[:5]

    return render(
        request,
        "content/content_details.html",
        {
            "content": content,
            "related": related,
            "left_sections": content.left_sections,
            "right_sections": content.right_sections,
        },
    )


@login_required(login_url="accounts:login")
def dashboard_view(request):
    base_qs = Content.objects.filter(created_by=request.user).select_related(
        "sub_sub_category__sub_category__category"
    )

    stats = {
        "total": base_qs.count(),
        "published": base_qs.filter(status=Content.Status.PUBLISHED).count(),
        "draft": base_qs.filter(status=Content.Status.DRAFT).count(),
        "archived": base_qs.filter(status=Content.Status.ARCHIVED).count(),
    }

    status_filter = request.GET.get("status", "").strip()
    qs = base_qs.order_by("-created_at")
    if status_filter in ("draft", "published", "archived"):
        qs = qs.filter(status=status_filter)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "content/dashboard.html",
        {
            "page_obj": page_obj,
            "stats": stats,
            "status_filter": status_filter,
            "query": q,
        },
    )


@login_required(login_url="accounts:login")
def content_create_view(request):
    if request.method == "POST":
        form = ContentForm(request.POST, request.FILES)
        temp_content = Content()

        if form.is_valid():
            temp_content = form.save(commit=False)

        formset = ContentSectionFormSet(request.POST, instance=temp_content)

        if form.is_valid() and formset.is_valid():
            content = temp_content
            content.created_by = request.user
            if content.status == Content.Status.PUBLISHED and not content.published_at:
                content.published_at = timezone.now()
            content.save()

            formset.instance = content
            formset.save()

            messages.success(request, f'"{content.title}" created successfully.')
            return redirect("content:content-detail", slug=content.slug)
    else:
        form = ContentForm()
        formset = ContentSectionFormSet(instance=Content())

    return render(
        request,
        "content/content_form.html",
        {
            "form": form,
            "formset": formset,
            "categories": Category.objects.filter(is_active=True).order_by("order", "name"),
            "action": "Create",
        },
    )


@login_required(login_url="accounts:login")
def content_edit_view(request, slug):
    if request.user.is_staff:
        content = get_object_or_404(Content, slug=slug)
    else:
        content = get_object_or_404(Content, slug=slug, created_by=request.user)

    if request.method == "POST":
        form = ContentForm(request.POST, request.FILES, instance=content)
        formset = ContentSectionFormSet(request.POST, instance=content)

        if form.is_valid() and formset.is_valid():
            updated = form.save(commit=False)
            if updated.status == Content.Status.PUBLISHED and not updated.published_at:
                updated.published_at = timezone.now()
            updated.save()
            formset.save()
            messages.success(request, "Content updated successfully.")
            return redirect("content:content-detail", slug=updated.slug)
    else:
        form = ContentForm(instance=content)
        formset = ContentSectionFormSet(instance=content)

    return render(
        request,
        "content/content_form.html",
        {
            "form": form,
            "formset": formset,
            "categories": Category.objects.filter(is_active=True).order_by("order", "name"),
            "content": content,
            "action": "Edit",
        },
    )


@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def content_delete_view(request, slug):
    if request.user.is_staff:
        content = get_object_or_404(Content, slug=slug)
    else:
        content = get_object_or_404(Content, slug=slug, created_by=request.user)

    title = content.title
    content.delete()
    messages.success(request, f'"{title}" deleted.')
    return redirect("content:dashboard")


def ajax_load_subcategories(request):
    category_id = request.GET.get("category_id", "").strip()
    if not category_id:
        return JsonResponse([], safe=False)

    subs = SubCategory.objects.filter(category_id=category_id, is_active=True).order_by("order", "name").values("id", "name")
    return JsonResponse(list(subs), safe=False)


def ajax_load_subsubcategories(request):
    sub_id = request.GET.get("sub_category_id", "").strip()
    if not sub_id:
        return JsonResponse([], safe=False)

    subsubs = SubSubCategory.objects.filter(sub_category_id=sub_id, is_active=True).order_by("order", "name").values("id", "name")
    return JsonResponse(list(subsubs), safe=False)


@login_required(login_url="accounts:login")
@csrf_exempt
@require_http_methods(["POST"])
def tinymce_upload_view(request):
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"error": "No file provided."}, status=400)

    allowed_mime = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/ogg",
        "video/mp4",
        "video/webm",
        "video/ogg",
    }
    if upload.content_type not in allowed_mime:
        return JsonResponse({"error": "Unsupported media type."}, status=400)

    if upload.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "File exceeds 5 MB limit."}, status=400)

    ext = os.path.splitext(upload.name)[1].lower() or ".jpg"
    filename = f"tinymce/{uuid.uuid4().hex}{ext}"
    saved = default_storage.save(filename, ContentFile(upload.read()))
    file_url = default_storage.url(saved)

    return JsonResponse({"location": file_url})


@login_required(login_url="accounts:login")
def content_media_list_view(request, content_id):
    content = get_object_or_404(Content, pk=content_id, created_by=request.user)
    media_qs = content.media.all().order_by("-created_at")

    data = [
        {
            "id": m.pk,
            "title": m.title,
            "type": m.type,
            "url": m.file.url if m.file else (m.url or ""),
            "thumbnail": m.thumbnail.url if m.thumbnail else "",
            "mime_type": m.mime_type or "",
            "size_kb": m.size_kb,
        }
        for m in media_qs
    ]
    return JsonResponse({"media": data})


@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def content_media_upload_view(request, content_id):
    content = get_object_or_404(Content, pk=content_id, created_by=request.user)
    form = ContentMediaForm(request.POST, request.FILES)

    if form.is_valid():
        media = form.save(commit=False)
        media.content = content

        upload = request.FILES.get("file")
        if upload:
            media.mime_type = upload.content_type
            media.size_kb = upload.size // 1024

        media.save()

        return JsonResponse(
            {
                "success": True,
                "media": {
                    "id": media.pk,
                    "title": media.title,
                    "type": media.type,
                    "url": media.file.url if media.file else (media.url or ""),
                    "thumbnail": media.thumbnail.url if media.thumbnail else "",
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required(login_url="accounts:login")
@require_http_methods(["DELETE"])
def content_media_delete_view(request, content_id, media_id):
    media = get_object_or_404(
        ContentMedia,
        pk=media_id,
        content_id=content_id,
        content__created_by=request.user,
    )

    if media.file:
        try:
            if default_storage.exists(media.file.name):
                default_storage.delete(media.file.name)
        except Exception:
            pass

    media.delete()
    return JsonResponse({"success": True})


def inline_tag_resolve_view(request):
    key = request.GET.get("key", "").strip()
    content_id = request.GET.get("content", "").strip()

    if not key or not content_id:
        return JsonResponse({"error": "key and content are required."}, status=400)

    tag = get_object_or_404(InlineMediaTag, tag_key=key, content_id=content_id)

    payload = {
        "id": tag.pk,
        "key": tag.tag_key,
        "label": tag.tag_label,
        "type": tag.type,
        "popup_body": tag.popup_body or "",
    }

    if tag.media:
        media = tag.media
        payload["media"] = {
            "id": media.pk,
            "title": media.title,
            "type": media.type,
            "url": media.file.url if media.file else (media.url or ""),
            "thumbnail": media.thumbnail.url if media.thumbnail else "",
            "mime_type": media.mime_type or "",
        }

    return JsonResponse(payload)


@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def inline_tag_save_view(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    content = get_object_or_404(Content, pk=data.get("content_id"), created_by=request.user)

    media = None
    if data.get("media_id"):
        media = get_object_or_404(ContentMedia, pk=data["media_id"], content=content)

    tag_key = str(data.get("tag_key", "")).strip()
    if not tag_key:
        return JsonResponse({"error": "tag_key is required."}, status=400)

    tag, created = InlineMediaTag.objects.update_or_create(
        content=content,
        tag_key=tag_key,
        defaults={
            "media": media,
            "tag_label": data.get("tag_label", ""),
            "type": data.get("type", "text"),
            "popup_body": data.get("popup_body", ""),
        },
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "tag": {
                "id": tag.pk,
                "key": tag.tag_key,
                "label": tag.tag_label,
                "type": tag.type,
            },
        }
    )
