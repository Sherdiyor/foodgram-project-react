[![Foodgram](https://github.com/Sherdiyor/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Sherdiyor/foodgram-project-react/actions/workflows/main.yml)

# Foodgram

Этот проект поможет вам находить рецепты и идеи блюд. Надеюсь, он будет вам полезен! Для начала использования вам нужно просто зарегистрироваться или войти. И теперь у вас есть возможность делать все, что вам нравится. Удачи!

## Технологии:
- Python 3.12
- Django 5.0
- Django REST framework 3.15
- Nginx
- Docker
- Postgres

# Где можно проверить

Развернуть проект 

# Как запустить проект локально

1. Скачайте репозиторий любым удобным для вас способом.

2. Откройте терминал bash (Ctrl + Alt + T на Linux).

3. Перейдите в папку foodgram-project-react/infra с помощью команды cd.

4. Установите docker и docker-compose sudo apt install docker.io docker-compose.

5. После успешной установки пакетов просто выполните команду sudo docker-compose up --build -d. Дождитесь завершения процесса.

6. Выполните команду sudo docker exec -it backend bash, это откроет bash внутри контейнера Django приложения.

7. Теперь вам нужно выполнить несколько команд:
- python3 manage.py makemigrations & python3 manage.py migrate & python3 manage.py collectstatic & python manage.py loads_ingredients & python manage.py loaddata data.json
(Просто скопируйте и вставьте, возможно, вам придется ввести "Yes" и нажать Enter)
- Вы создали миграции и применили их (настроили базу данных), создали статические файлы (для того, чтобы панель администратора и конечные точки API выглядели красиво) и загрузили данные об ингредиентах. Также создан предварительный администратор. (Учетные данные внизу README)

Теперь вы можете получить доступ к своему проекту по адресу http://localhost

## Ваш проект готов, но если вы хотите узнать, как сделать что-то еще

- Создайте нового администратора. В терминале bash Django App (шаг 6) выполните python3 manage.py createsuperuser. Заполните все учетные данные.

- Выйдите из терминала bash, просто введите exit.

- Чтобы получить доступ к панели администратора, перейдите на http://localhost/admin/, введите имя пользователя и пароль администратора. Теперь вы можете выполнять административные задачи

- Чтобы остановить проект, выполните шаг 3 и запустите sudo docker-compose stop.

- Полная документация доступна на [127.0.0.1/api/swagger](http://127.0.0.1/api/swagger/) 

## Автор

![Sherdiyor](https://github.com/Sherdiyor)

# Сайт сейчас доступен на хостинге

[Ссылка на сайт](158.160.76.3) \
[Ссылка на документацию](158.160.76.3/api/docs/)