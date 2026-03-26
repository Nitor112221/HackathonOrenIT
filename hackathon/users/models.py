import django.contrib.auth.models
import django.db.models

class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
    )

    total_xp = django.db.models.IntegerField(default=0, verbose_name="всего опыта")
