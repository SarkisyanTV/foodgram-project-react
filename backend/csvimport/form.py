from django.forms import ModelForm

from .models import CsvImport


class CsvImportForm(ModelForm):
    class Meta:
        model = CsvImport
        fields = ('csv_file',)
