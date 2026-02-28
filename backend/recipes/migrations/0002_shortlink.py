import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShortLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_link', to='recipes.recipe')),
            ],
        ),
    ]
