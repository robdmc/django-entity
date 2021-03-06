# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-12-12 18:20
from __future__ import unicode_literals

from django.db import migrations, connection
from django.db.models import Count, Max


def disable_triggers(apps, schema_editor):
    """
    Temporarily disable user triggers on the relationship table. We do not want things
    like entity history to attach onto these migrations as this is a core bug where duplicates
    should not exist

    :param apps:
    :param schema_editor:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE entity_entityrelationship DISABLE TRIGGER USER;
            """
        )


def enable_triggers(apps, schema_editor):
    """
    Re-enable the triggers (if any)
    :param apps:
    :param schema_editor:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE entity_entityrelationship ENABLE TRIGGER USER;
            """
        )


def remove_duplicates(apps, schema_editor):
    """
    Remove any duplicates from the entity relationship table
    :param apps:
    :param schema_editor:
    :return:
    """

    # Get the model
    EntityRelationship = apps.get_model('entity', 'EntityRelationship')

    # Find the duplicates
    duplicates = EntityRelationship.objects.all().order_by(
        'sub_entity_id',
        'super_entity_id'
    ).values(
        'sub_entity_id',
        'super_entity_id'
    ).annotate(
        Count('sub_entity_id'),
        Count('super_entity_id'),
        max_id=Max('id')
    ).filter(
        super_entity_id__count__gt=1
    )

    # Loop over the duplicates and delete
    for duplicate in duplicates:
        EntityRelationship.objects.filter(
            sub_entity_id=duplicate['sub_entity_id'],
            super_entity_id=duplicate['super_entity_id']
        ).exclude(
            id=duplicate['max_id']
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0005_remove_entitygroup_entities'),
    ]

    operations = [
        migrations.RunPython(disable_triggers),
        migrations.RunPython(remove_duplicates),
        migrations.RunPython(enable_triggers),
        migrations.AlterUniqueTogether(
            name='entityrelationship',
            unique_together=set([('sub_entity', 'super_entity')]),
        ),
    ]
