from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import (
    Category,
    Content,
    ContentMedia,
    ContentSection,
    InlineMediaTag,
    SubCategory,
    SubSubCategory,
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 0
    fields = ("name", "slug", "is_active", "order")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]


class SubSubCategoryInline(admin.TabularInline):
    model = SubSubCategory
    extra = 0
    fields = ("name", "slug", "is_active", "order")
    show_change_link = True


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    inlines = [SubSubCategoryInline]


@admin.register(SubSubCategory)
class SubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sub_category", "is_active", "order")
    list_filter = ("sub_category", "is_active")
    search_fields = ("name", "slug", "sub_category__name", "sub_category__category__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("sub_category",)


class ContentSectionInline(admin.StackedInline):
    model = ContentSection
    extra = 0
    fields = ("title", "body", "position", "is_open_by_default", "order", "is_active")
    show_change_link = True
    formfield_overrides = {forms.Textarea: {"widget": TinyMCE()}}


class ContentMediaInline(admin.TabularInline):
    model = ContentMedia
    extra = 0
    fields = ("title", "type", "file", "url", "thumbnail", "mime_type", "size_kb")
    show_change_link = True


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = "__all__"
        widgets = {"excerpt": TinyMCE()}


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    form = ContentAdminForm
    list_display = ("title", "sub_sub_category", "status", "published_at", "created_at")
    list_filter = ("status", "sub_sub_category")
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "sub_sub_category__name",
        "sub_sub_category__sub_category__name",
        "sub_sub_category__sub_category__category__name",
    )
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("sub_sub_category",)
    raw_id_fields = ("created_by",)
    readonly_fields = ("created_at", "updated_at", "published_at")
    inlines = [ContentSectionInline, ContentMediaInline]


class ContentSectionAdminForm(forms.ModelForm):
    class Meta:
        model = ContentSection
        fields = "__all__"
        widgets = {"body": TinyMCE()}


@admin.register(ContentSection)
class ContentSectionAdmin(admin.ModelAdmin):
    form = ContentSectionAdminForm
    list_display = ("title", "content", "position", "order", "is_active")
    list_filter = ("position", "is_active")
    search_fields = ("title", "content__title")
    autocomplete_fields = ("content",)


@admin.register(ContentMedia)
class ContentMediaAdmin(admin.ModelAdmin):
    list_display = ("title", "content", "type", "mime_type", "size_kb", "created_at")
    list_filter = ("type",)
    search_fields = ("title", "content__title")
    autocomplete_fields = ("content",)


@admin.register(InlineMediaTag)
class InlineMediaTagAdmin(admin.ModelAdmin):
    list_display = ("tag_label", "tag_key", "type", "content", "media", "created_at")
    list_filter = ("type",)
    search_fields = ("tag_label", "tag_key", "content__title")
    autocomplete_fields = ("content", "media")
