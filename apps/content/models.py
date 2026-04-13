from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


def category_image_path(instance, filename):
    return f"categories/{instance.slug}/{filename}"


def content_thumbnail_path(instance, filename):
    return f"contents/{instance.slug}/thumbnail/{filename}"


def media_file_path(instance, filename):
    return f"contents/{instance.content.slug}/media/{instance.type}/{filename}"


def build_unique_slug(model, value, instance=None, slug_field="slug", max_length=255):
    base = slugify(value) or "item"
    base = base[:max_length]
    slug = base
    counter = 1

    queryset = model.objects.all()
    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(**{slug_field: slug}).exists():
        suffix = f"-{counter}"
        trimmed = base[: max_length - len(suffix)]
        slug = f"{trimmed}{suffix}"
        counter += 1

    return slug


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="CSS icon class or emoji",
    )
    image = models.ImageField(upload_to=category_image_path, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order (ascending)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        source = self.slug or self.name
        self.slug = build_unique_slug(
            Category,
            source,
            instance=self,
            max_length=self._meta.get_field("slug").max_length,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_categories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="sub_categories/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def save(self, *args, **kwargs):
        source = self.slug or self.name
        self.slug = build_unique_slug(
            SubCategory,
            source,
            instance=self,
            max_length=self._meta.get_field("slug").max_length,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} › {self.name}"


class SubSubCategory(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_sub_categories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="sub_sub_categories/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Sub-Sub Category"
        verbose_name_plural = "Sub-Sub Categories"

    def save(self, *args, **kwargs):
        source = self.slug or self.name
        self.slug = build_unique_slug(
            SubSubCategory,
            source,
            instance=self,
            max_length=self._meta.get_field("slug").max_length,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sub_category.category.name} › {self.sub_category.name} › {self.name}"


class Content(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    sub_sub_category = models.ForeignKey(SubSubCategory, on_delete=models.CASCADE, related_name="contents")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="contents")
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True, max_length=600)
    thumbnail = models.ImageField(
        upload_to=content_thumbnail_path,
        blank=True,
        null=True,
        help_text="Cover image shown in listing pages",
    )
    excerpt = models.TextField(blank=True, null=True, help_text="Short summary shown in cards/previews")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Content"
        verbose_name_plural = "Contents"

    def save(self, *args, **kwargs):
        source = self.slug or self.title
        self.slug = build_unique_slug(
            Content,
            source,
            instance=self,
            max_length=self._meta.get_field("slug").max_length,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def left_sections(self):
        return self.sections.filter(position=ContentSection.Position.LEFT, is_active=True).order_by("order")

    @property
    def right_sections(self):
        return self.sections.filter(position=ContentSection.Position.RIGHT, is_active=True).order_by("order")


class ContentSection(models.Model):
    class Position(models.TextChoices):
        LEFT = "left", "Left — Full Card"
        RIGHT = "right", "Right — Expandable Accordion"

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=300)
    body = models.TextField(help_text="TinyMCE rich-text HTML. May contain inline media shortcodes.")
    position = models.CharField(
        max_length=10,
        choices=Position.choices,
        default=Position.LEFT,
        help_text="LEFT = full card | RIGHT = collapsible accordion",
    )
    is_open_by_default = models.BooleanField(
        default=False,
        help_text="RIGHT only — if True, accordion starts expanded on page load.",
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order within its column")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "order"]
        verbose_name = "Content Section"
        verbose_name_plural = "Content Sections"

    def __str__(self):
        return f"[{self.get_position_display()}] {self.content.title} — {self.title}"


class ContentMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        YOUTUBE = "youtube", "YouTube"
        IFRAME = "iframe", "iFrame / Embed"

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="media")
    title = models.CharField(max_length=300, help_text="Display label for this media item")
    type = models.CharField(max_length=20, choices=MediaType.choices)
    file = models.FileField(upload_to=media_file_path, blank=True, null=True, help_text="Upload file directly (image, audio, video)")
    url = models.URLField(blank=True, null=True, help_text="YouTube URL, iframe src URL, or any external media link")
    thumbnail = models.ImageField(upload_to="media_thumbnails/", blank=True, null=True, help_text="Optional preview image shown before media opens")
    mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="Detected/stored MIME type, e.g. audio/mpeg, video/mp4, image/png")
    size_kb = models.PositiveIntegerField(blank=True, null=True, help_text="File size in KB (auto-populated on upload)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Content Media"
        verbose_name_plural = "Content Media"

    def clean(self):
        from django.core.exceptions import ValidationError

        needs_url = self.type in [self.MediaType.YOUTUBE, self.MediaType.IFRAME]
        needs_file = self.type in [self.MediaType.IMAGE, self.MediaType.AUDIO, self.MediaType.VIDEO]

        if needs_url and not self.url:
            raise ValidationError(f"A URL is required for media type '{self.get_type_display()}'.")
        if needs_file and not self.file and not self.url:
            raise ValidationError("Either a file upload or a URL is required for this media type.")

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"


class InlineMediaTag(models.Model):
    class TagType(models.TextChoices):
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        YOUTUBE = "youtube", "YouTube"
        IFRAME = "iframe", "iFrame / Embed"
        TEXT = "text", "Text / Definition"

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="inline_tags")
    media = models.ForeignKey(
        ContentMedia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inline_tags",
        help_text="Leave empty if tag type is Text/Definition",
    )
    tag_label = models.CharField(max_length=200, help_text="Visible text in the tag, e.g. 'সন্দেহ' or 'Audio'")
    tag_key = models.CharField(max_length=100, help_text="Unique shortcode identifier per content, e.g. 'audio_001', 'img_gold'")
    type = models.CharField(max_length=20, choices=TagType.choices)
    popup_body = models.TextField(
        blank=True,
        null=True,
        help_text="Used when type=Text. Shown as the popup content (plain text or HTML).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("content", "tag_key")]
        ordering = ["tag_key"]
        verbose_name = "Inline Media Tag"
        verbose_name_plural = "Inline Media Tags"

    def __str__(self):
        return f"[{self.get_type_display()}] {self.tag_label} ({self.tag_key})"
