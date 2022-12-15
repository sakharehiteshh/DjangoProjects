from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


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


class Contact(models.Model):
	user_from = models.ForeignKey('auth.User',
				related_name='rel_from_set',
				on_delete=models.CASCADE)
	user_to = models.ForeignKey('auth.User',
				related_name='rel_to_set',
				on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True,
			db_index=True)

	class Meta:
		ordering = ('-created',)

	def __str__(self):
		return f"{self.user_from} follows {self.user_to}"

user_model = get_user_model()
user_model.add_to_class('following',
						models.ManyToManyField('self',
												through=Contact,
												related_name='followers',
												symmetrical=False))