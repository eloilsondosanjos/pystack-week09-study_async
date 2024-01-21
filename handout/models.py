from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Handout(models.Model):
  user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
  title = models.CharField(max_length=100)
  file = models.FileField(upload_to='handout')

  def __str__(self):
    return self.title

class ViewHandout(models.Model):
  ip = models.GenericIPAddressField()
  handout = models.ForeignKey(Handout, on_delete=models.DO_NOTHING)

  def __str__(self) -> str:
    return self.ip