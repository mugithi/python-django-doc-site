from django.db import models
from django.utils import timezone
from django.urls import reverse

class Post(models.Model):
    author = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    title = models.CharField(max_length=260)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
    
## Comments - Not need for the Documenation Site
    def approve_comment(self):
        return self.comments.filter(approved_comments=True)

    def get_absolute_url(self):
        return reverse('docs:post_detail', kwargs={'pk':self.pk}) #Will be defined in the URLS
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('docs.Post',related_name='comments',on_delete=models.CASCADE)
    author = models.CharField(max_length=264)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    approved_comments = models.BooleanField(default=False)


    def approve(self):
        self.approve_comment = True
        self.save()
        
    def get_absolute_url(self):
        return reverse('post_list') #Will be defined in the URLS

    def __str__(self):
        return self.text
