from django import forms
from django_admin_json_editor import JSONEditorWidget

from mainapp.models import Place

# https://github.com/jdorn/json-editor#format
PLACE_SCHEMA = {
    'type': 'object',
    'properties': {
        'description': {
            'title': 'description',
            'type': 'string',
            'format': 'textarea',
        },
    },
}


class PlaceWidgetForm(forms.ModelForm):

    class Meta:
        model = Place
        fields = '__all__'
        widgets = {
            'info': JSONEditorWidget(PLACE_SCHEMA, collapsed=False),
        }
