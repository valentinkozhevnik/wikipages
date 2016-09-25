# instalation

```
virtualenv env --python=python3.4
pip install -r requirements.txt
. env/bin/python
```

need Update local setting in folder wikipages

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'wikipages',
        'USER': 'vako',
        'PASSWORD': '',
        'HOST': 'localhost',

    }
}
```

```bash
python manage.py migrate
python manage.py runserver
```

# Test
```
python manage.py test
```


# Link list

```
^api/ ^pages/list/?$ [name='pages-list']
^api/ ^pages/(?P<pk>\d+)/?$ [name='pages-detail']
^api/ ^pages/create/?$ [name='pages-create']
^api/ ^pages/(?P<pk>\d+)/update/?$ [name='pages-update']
^api/ ^pages/(?P<pk>\d+)/version/current/?$ [name='pages-version-current']
^api/ ^pages/(?P<pk>\d+)/version/list/?$ [name='pages-version-list']
^api/ ^pages/(?P<pk>\d+)/version/(?P<version_id>\d+)/?$ [name='pages-version-retrieve']
^api/ ^pages/(?P<pk>\d+)/version/(?P<version_id>\d+)/set_current/?$ [name='pages-version-set-current']
```


# database

```
create table pages_active_storage (
 id bigserial PRIMARY KEY,
 version_id INT8
);

create table pages_version_storage (
 id bigserial PRIMARY KEY,
 page_id INT8 NOT NULL REFERENCES pages_active_storage(id),
  title varchar(256) NOT NULL,
  body text NOT NULL
);

alter table pages_active_storage add CONSTRAINT pages_active_storage_version_id_fkey FOREIGN KEY (version_id) REFERENCES pages_version_storage(id);
create UNIQUE index pages_active_storage_version_id_uniq on pages_active_storage(version_id) where version_id is not null;
```
