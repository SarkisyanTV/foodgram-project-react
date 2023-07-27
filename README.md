    IP  158.160.12.247
    https://foodgram-stigos.ddns.net
    superuser "stigos"  password: stigos1976
    email: stigos@example.com password: stigos1976 

## Foodgram
  Проект позволяет:
   - публиковать рецепты
   - подписываться на рецепты авторов
   - добавлять понравившиеся рецепты в избранное
   - сохранять рецепты в список покупок

  Добавлять, редактировать и удалять рецепты могут только зарегистрированные пользователи.  
  Зарегистрированным пользователям доступны все возможности проекта.  
Для работы с проектом понадобятся следующие технологии  
- Django 3.2 - https://docs.djangoproject.com/en/3.2/
- Python 3.9 - https://www.python.org/
- Node.js - https://nodejs.org/en
- Docker(с установленным пакетом docker_compose) - https://docs.docker.com/
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:SarkisyanTV/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Создать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
Перейти в папку backend/:
```
cd backend
```
Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

В проекте использована технология Docker, о том как установить Doker на свою машину  
вы можете прочитать здесь https://docs.docker.com/engine/install/ubuntu/  

### Запустить проект c Docker:  

    $ cd infra/
    $ sudo docker compose up

Проект будет доступен в браузере по адресу http://localhost/ 

### Использование API проекта 

В проекте использована библиотека Djoser https://djoser.readthedocs.io/en/latest/settings.html  
для работы с пользователями. Авторизация пользователей реализована по токенам.  

#### Api доступен по адресу http://localhost/api/
#### Документация к api http://localhost/api/docs/

Пример:

Перейдя по адресу  
`GET` http://localhost/api/users/ 
вы получите список всех зарегистрированных пользователей.  

`POST` http://localhost/api/users/  c данными в формате `Json`  
вы зарегистрируете нового пользователя. :
 ```
 {

    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"

}
 ```  
 
`GET` http://localhost/api/recipes/ список всех постов:  
```
{

    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": 

[

{

    "id": 0,
    "tags": 

[

    {
        "id": 0,
        "name": "Завтрак",
        "color": "#E26C2D",
        "slug": "breakfast"
    }

],
"author": 
{

    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false

},
"ingredients": 
[

                {
                    "id": 0,
                    "name": "Картофель отварной",
                    "measurement_unit": "г",
                    "amount": 1
                }
            ],
            "is_favorited": true,
            "is_in_shopping_cart": true,
            "name": "string",
            "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
            "text": "string",
            "cooking_time": 1
        }
    ]

}

```
### Автор 
Тигран Саркисян, студент [Яндекс.Пактикум](https://practicum.yandex.ru/) *python-backend* 
E-mail: s.tigo@yandex.ru