import csv

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, path

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
    list_filter = ('name', 'measurement_unit')

    # даем django(urlpatterns) знать
    # о существовании страницы с формой
    # иначе будет ошибка
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('upload-csv/', self.upload_csv))
        return urls

        # если пользователь открыл url 'csv-upload/',
        # то он выполнит этот метод,
        # который работает с формой

    def upload_csv(self, request):
        if request.method == 'POST':
            # Т.к. это метод POST проводим валидацию данных
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                # сохраняем загруженный файл и делаем запись в базу
                form_object = form.save()
                # обработка csv файла
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['name', 'measurement_unit']:
                        # обновляем страницу пользователя
                        # с информацией о какой-то ошибке
                        messages.warning(request,
                                         'Неверные заголовки у файла')
                        return HttpResponseRedirect(request.path_info)
                    for row in rows:
                        print(row[1])
                        # добавляем данные в базу
                        Ingredient.objects.update_or_create(
                            name=row[0],
                            measurement_unit=row[1],
                        )

                # возвращаем пользователя на главную с сообщением об успехе
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        # если это не метод POST, то возвращается форма с шаблоном
        form = CsvImportForm()
        return render(request, 'admin/csv_upload.html', {'form': form})
