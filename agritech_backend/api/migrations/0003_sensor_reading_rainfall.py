from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0002_farmer_profile_memory_otp")]

    operations = [
        migrations.AddField(model_name="sensorreading", name="rainfall_mm", field=models.FloatField(default=0.0)),
    ]
