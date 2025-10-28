from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """Inline admin interface for Choice model."""

    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""

    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
