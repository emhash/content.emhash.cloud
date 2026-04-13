from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("content/create/", views.content_create_view, name="content-create"),
    path("content/<slug:slug>/", views.content_detail_view, name="content-detail"),
    path("content/<slug:slug>/edit/", views.content_edit_view, name="content-edit"),
    path("content/<slug:slug>/delete/", views.content_delete_view, name="content-delete"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("ajax/subcategories/", views.ajax_load_subcategories, name="ajax-subcategories"),
    path("ajax/subsubcategories/", views.ajax_load_subsubcategories, name="ajax-subsubcategories"),
    path("api/tinymce-upload/", views.tinymce_upload_view, name="tinymce-upload"),
    path("api/content/<int:content_id>/media/", views.content_media_list_view, name="api-media-list"),
    path("api/content/<int:content_id>/media/upload/", views.content_media_upload_view, name="api-media-upload"),
    path(
        "api/content/<int:content_id>/media/<int:media_id>/delete/",
        views.content_media_delete_view,
        name="api-media-delete",
    ),
    path("api/inline-tags/", views.inline_tag_resolve_view, name="api-inline-tag-resolve"),
    path("api/inline-tags/save/", views.inline_tag_save_view, name="api-inline-tag-save"),
]
