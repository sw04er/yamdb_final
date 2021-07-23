![example workflow](https://github.com/sw04er/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# yamdb_final - API для сервиса YAMDB
## Установка

#### 1. Запуск контейнера:
```bash
docker-compose up
```

## Использование
#### Создание superuser Django:
```
docker-compose run web python manage.py createsuperuser
```

#### Команда для заполнения базы данными:
```bash
docker-compose run web python manage.py loaddata fixtures.json
```

### Ссылка на сайт:
```
http://161.35.67.170
```