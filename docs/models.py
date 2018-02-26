from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Post(models.Model):
    author = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    title = models.CharField(max_length=260)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def is_published(self):
        if self.publish_date == None:
            return False
        else:
            return True

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
## Comments - Not need for the Documenation Site
    def approve_comments(self):
        return self.comments.filter(approved_comment=True)

    def get_absolute_url(self):
        return reverse('docs:post_detail', kwargs={'pk':self.pk}) #Will be defined in the URLS
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('docs.Post',related_name='comments',on_delete=models.CASCADE)
    author = models.CharField(max_length=264)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)


    def approve(self):
        self.approved_comment = True
        self.save()
        
    def get_absolute_url(self):
        return reverse('post_list') #Will be defined in the URLS

    def __str__(self):
        return self.text
