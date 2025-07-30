# Generated migration for theme support

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0001_initial'),
    ]

    operations = [
        # Add theme fields to CustomUser
        migrations.AddField(
            model_name='customuser',
            name='purchased_themes',
            field=models.JSONField(default=lambda: ['default']),
        ),
        migrations.AddField(
            model_name='customuser',
            name='active_theme',
            field=models.CharField(default='default', max_length=50),
        ),
        
        # Remove Achievement and UserAchievement models
        migrations.DeleteModel(
            name='UserAchievement',
        ),
        migrations.DeleteModel(
            name='Achievement',
        ),
        
        # Add Theme and UserThemePurchase models
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme_id', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('preview_icon', models.CharField(default='🎨', max_length=10)),
                ('sp_cost', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserThemePurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchased_at', models.DateTimeField(auto_now_add=True)),
                ('theme', models.ForeignKey(on_delete=models.deletion.CASCADE, to='Core.theme')),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, to='Core.customuser')),
            ],
            options={
                'unique_together': {('user', 'theme')},
            },
        ),
    ]