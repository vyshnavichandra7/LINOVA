from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linen', '0002_linenassignment_destination_station_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_gender',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='passenger_phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='passengerpnr',
            name='ticket_image',
            field=models.ImageField(blank=True, null=True, upload_to='passenger_tickets/'),
        ),
    ]