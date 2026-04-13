from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

from .models import Category, Content, ContentMedia, ContentSection, SubCategory, SubSubCategory


class ContentForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by("order", "name"),
        required=False,
        label="Category",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_category"}),
    )
    sub_category = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        required=False,
        label="Sub Category",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_sub_category"}),
    )

    class Meta:
        model = Content
        fields = ["sub_sub_category", "title", "thumbnail", "excerpt", "status", "published_at"]
        widgets = {
            "sub_sub_category": forms.Select(attrs={"class": "form-select", "id": "id_sub_sub_category"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Content title…"}),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Short summary shown in listing cards…",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "published_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sub_sub_category"].widget.attrs["class"] = "form-select"
        self.fields["sub_sub_category"].queryset = SubSubCategory.objects.none()
        self.fields["sub_category"].queryset = SubCategory.objects.none()

        if self.is_bound:
            category_id = self.data.get("category")
            sub_category_id = self.data.get("sub_category")

            if category_id:
                self.fields["sub_category"].queryset = SubCategory.objects.filter(
                    category_id=category_id,
                    is_active=True,
                )

            if sub_category_id:
                self.fields["sub_sub_category"].queryset = SubSubCategory.objects.filter(
                    sub_category_id=sub_category_id,
                    is_active=True,
                )

        if self.instance.pk:
            ssc = self.instance.sub_sub_category
            if ssc:
                sub_category = ssc.sub_category
                category = sub_category.category
                self.fields["category"].initial = category
                self.fields["sub_category"].initial = sub_category
                self.fields["sub_category"].queryset = SubCategory.objects.filter(
                    category=category, is_active=True
                )
                self.fields["sub_sub_category"].queryset = SubSubCategory.objects.filter(
                    sub_category=sub_category, is_active=True
                )


class ContentSectionForm(forms.ModelForm):
    class Meta:
        model = ContentSection
        fields = ["title", "body", "position", "is_open_by_default", "order", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Section title…"}),
            "body": TinyMCE(attrs={"cols": 80, "rows": 20}),
            "position": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_open_by_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


ContentSectionFormSet = inlineformset_factory(
    parent_model=Content,
    model=ContentSection,
    form=ContentSectionForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class ContentMediaForm(forms.ModelForm):
    class Meta:
        model = ContentMedia
        fields = ["title", "type", "file", "url", "thumbnail"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Media label…"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://…"}),
        }
