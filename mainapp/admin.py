from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.admin.options import get_ul_class
from django.contrib.admin.widgets import AutocompleteSelect
from django.utils.translation import gettext

from mainapp.models import (
    City, Category,
    Article, ArticleCategory,
    Place, PlaceImage, PlaceCategory, PlaceArticle,
    Travler)
from mainapp.forms.place import PlaceWidgetForm


class PlaceCategoryInline(admin.StackedInline):
    model = PlaceCategory
    extra = 0


class PlaceImageInline(admin.StackedInline):
    model = PlaceImage
    extra = 0


class PlaceAdminModel(admin.ModelAdmin):
    form = PlaceWidgetForm

    list_display = [
        'id', 'travler', 'title', 'city', 'latitude', 'longitude', 'created', 'modified', 'categories'
    ]

    inlines = [PlaceCategoryInline, PlaceImageInline, ]

    @staticmethod
    def categories(obj):
        cats = ', '.join([cat.category.name for cat in obj.placecategory_set.all()])
        return cats


class PlaceArticleInline(admin.StackedInline):
    model = PlaceArticle
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get('using')

        if db_field.name in self.get_autocomplete_fields(request):
            kwargs['widget'] = AutocompleteSelect(db_field.remote_field, self.admin_site, using=db)
        elif db_field.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.remote_field, self.admin_site, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = gettext('None') if db_field.blank else None

        if db_field.name == 'image':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.remote_field, self.admin_site, using=db)

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset
        return super(PlaceArticleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ArticleCategoryInline(admin.StackedInline):
    model = ArticleCategory
    extra = 0


class ArticleAdminModel(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'subtitle', 'modified'
    ]

    inlines = [PlaceArticleInline, ArticleCategoryInline]


admin.site.register(Travler)
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Article, ArticleAdminModel)
admin.site.register(ArticleCategory)
admin.site.register(Place, PlaceAdminModel)
admin.site.register(PlaceImage)
admin.site.register(PlaceCategory)
admin.site.register(PlaceArticle)
