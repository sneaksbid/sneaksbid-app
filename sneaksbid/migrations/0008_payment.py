# Generated by Django 4.2.10 on 2024-03-15 19:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djstripe.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djstripe', '0012_2_8'),
        ('sneaksbid', '0007_order_billingaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('djstripe_created', models.DateTimeField(auto_now_add=True)),
                ('djstripe_updated', models.DateTimeField(auto_now=True)),
                ('djstripe_id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('id', djstripe.fields.StripeIdField(max_length=255, unique=True)),
                ('livemode', models.BooleanField(blank=True, default=None, help_text='Null here indicates that the livemode status is unknown or was previously unrecorded. Otherwise, this field indicates whether this record comes from Stripe test mode or live mode operation.', null=True)),
                ('created', djstripe.fields.StripeDateTimeField(blank=True, null=True)),
                ('metadata', djstripe.fields.JSONField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=100)),
                ('paid', models.BooleanField(default=False)),
                ('djstripe_owner_account', djstripe.fields.StripeForeignKey(blank=True, help_text='The Stripe Account this object belongs to.', null=True, on_delete=django.db.models.deletion.CASCADE, to='djstripe.account', to_field=settings.DJSTRIPE_FOREIGN_KEY_TO_FIELD)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]