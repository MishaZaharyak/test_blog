1. Заранити ```docker-compose up```

2. Увійти в django контейнер ```docker exec -it server bash``` та заранити ```python manage.py migrate```

3. Створити сеперюзера ```python manage.py createsuperuser```

## Адмін панель

доступна лише для юзерів з ```is_staff=True or is_superuser=True```

можливість премодерації постів

## Django адмінка
управління користувачами та постами

у дерикторії ```test_blog/test_blog/.env``` видаліть ```_DELETE_THIS_LINE_``` з коду для його використання