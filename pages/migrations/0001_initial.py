# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            """
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
            """,
            """""",
            state_operations=[
                migrations.CreateModel(
                    name='PagesStorage',
                    fields=[
                        ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                    ],
                    options={
                        'db_table': 'pages_active_storage',
                    },
                ),
                migrations.CreateModel(
                    name='PagesVersionStorage',
                    fields=[
                        ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                        ('title', models.CharField(max_length=256)),
                        ('body', models.TextField()),
                        ('page', models.ForeignKey(to='pages.PagesStorage', related_name='versions')),
                    ],
                    options={
                        'db_table': 'pages_version_storage',
                    },
                ),
                migrations.AddField(
                    model_name='pagesstorage',
                    name='version',
                    field=models.OneToOneField(to='pages.PagesVersionStorage'),
                ),
            ]

        )

    ]
