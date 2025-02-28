# Generated by Django 5.0.6 on 2024-07-17 08:54

import django.core.validators
from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_user_favorite_remove_user_shopping_cart'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('following',), 'verbose_name': 'Подписка'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',), 'verbose_name': 'Пользователь'},
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Не корректное имя пользователя', regex='^[w.@+-]+Z'), users.validators.validate_name], verbose_name='никнэйм'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('follower', 'following'), name='unique_follower_following'),
        ),
    ]
