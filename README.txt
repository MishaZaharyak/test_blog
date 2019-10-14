1. Заранити ```docker-compose up```

2. Увійти в django контейнер ```docker exec -it server bash``` та заранити ```python manage.py migrate```

3. Створити сеперюзера ```python manage.py createsuperuser```

## Адмін панель

доступна лише для юзерів з ```is_staff=True or is_superuser=True```

можливість премодерації постів

## Django адмінка
управління користувачами та постами