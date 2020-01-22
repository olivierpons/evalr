from django.db import migrations, connection


def link_person_with_entity(apps, schema_editor):
    cursor = connection.cursor()
    cls_person = apps.get_model('app', 'Person')
    cls_entity = apps.get_model('app', 'Entity')
    for person in cls_person.objects.all():
        entity = cls_entity.objects.create(is_physical=True)
        sql = f"UPDATE app_person " \
              f"SET entity_ptr_id={entity.id} " \
              f"WHERE user_id={person.user.id};"
        cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_person_entity_ptr'),
    ]

    operations = [
        migrations.RunPython(link_person_with_entity,
                             reverse_code=migrations.RunPython.noop),
    ]
