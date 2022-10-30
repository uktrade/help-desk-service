from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField

ZENDESK = "zendesk"
HALO = "halo"
HELP_DESK_CHOICES = [
    (ZENDESK, "Zendesk"),
    (HALO, "Halo"),
]


class DITTeam(AbstractUser):
    """
    Username and password are Halo username and password
    DRF token should be set to Zendesk token
    """

    is_cleaned = False

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["zendesk_account"], name="zendesk_user"),
        ]

    zendesk_subdomain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    zendesk_user = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Needs at least one choice, enforced by not having null=True on the field
    help_desk = MultiSelectField(
        max_length=7,
        max_choices=2,
        choices=HELP_DESK_CHOICES,
        default=ZENDESK,
    )

    last_modified = models.DateTimeField(auto_now=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)

        if ZENDESK not in self.help_desk.choices:
            raise ValidationError(
                {
                    "help_desk": "You must have Zendesk chosen until go system go live",
                }
            )
        self.is_cleaned = True

    # Enforce the fact that Zendesk MUST be selected until we go live
    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean_fields()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"
