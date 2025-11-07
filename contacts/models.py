from django.db import models

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.IntegerField(unique = True)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
