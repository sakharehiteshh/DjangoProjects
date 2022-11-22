from django.db import models
from django.conf import settings


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	date_of_birth = models.DateField(blank=True, null=True)
	photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
	
	def __str__(self):
		return f'Profile for user {self.user.username}'


def save_profile(backend, user, response, *args, **kwargs):
	if backend.name == 'google-oauth2':
		try:
			profile = user.profile
		except Profile.DoesNotExist:
			profile = Profile(user = user)
			profile.save()