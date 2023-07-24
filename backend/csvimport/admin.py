import csv

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from recipes.models import Ingredient

from .form import CsvImportForm
from .models import CsvImport


@admin.register(CsvImport)
class CsvImportAdmin(admin.ModelAdmin):
    list_display = ('id', 'csv_file', 'date_added')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

    # даем django(urlpatterns) знать
    # о существовании страницы с формой
    # иначе будет ошибка
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('upload-csv/', self.upload_csv))
        return urls

    def database_entry(self, obj, **kwargs):
        Ingredient.objects.bulk_create(
            [Ingredient(
                name=row[0], measurement_unit=row[1],
            ) for row in obj]
        )

    def upload_csv(self, request):
        if request.method == 'POST':
            # Т.к. это метод POST проводим валидацию данных
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                # сохраняем загруженный файл и делаем запись в базу
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['name', 'measurement_unit']:
                        # обновляем страницу пользователя
                        # с информацией о какой-то ошибке
                        messages.warning(request,
                                         'Неверные заголовки у файла')
                        return HttpResponseRedirect(request.path_info)
                    self.database_entry(rows)
                # возвращаем пользователя на главную с сообщением об успехе
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        # если это не метод POST, то возвращается форма с шаблоном
        form = CsvImportForm()
        return render(request, 'admin/csv_upload.html', {'form': form})
