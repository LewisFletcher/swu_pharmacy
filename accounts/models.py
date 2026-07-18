from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Override user model

class User(AbstractUser):
    class PracticeRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
        VIEWER = 'viewer', 'Viewer'

    # Order matters: index in this list is the role's rank (higher = more access).
    ROLE_HIERARCHY = [PracticeRole.VIEWER, PracticeRole.STAFF, PracticeRole.ADMIN]

    practice = models.ForeignKey(
        'pharmacy.Practice', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff'
    )
    practice_role = models.CharField(
        max_length=10, choices=PracticeRole.choices, default=PracticeRole.STAFF, blank=True,
    )

    @property
    def role_rank(self):
        try:
            return self.ROLE_HIERARCHY.index(self.practice_role)
        except ValueError:
            return -1

    @property
    def is_practice_admin(self):
        return self.practice_role == self.PracticeRole.ADMIN

    @property
    def is_practice_viewer(self):
        return self.practice_role == self.PracticeRole.VIEWER

    def can_manage(self, other):
        '''True if this user may change `other`'s role or remove them
        (viewers can manage no one; staff can manage staff & viewers, not
        admins; admins can manage anyone).'''
        if self.is_practice_viewer:
            return False
        return self.is_practice_admin or other.role_rank <= self.role_rank

    def can_grant_role(self, role):
        '''True if this user is allowed to set someone's role to `role`
        (viewers can grant nothing; staff can grant up to staff, not admin;
        admins can grant anything).'''
        if self.is_practice_viewer:
            return False
        return self.ROLE_HIERARCHY.index(role) <= self.role_rank
