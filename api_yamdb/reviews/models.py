from django.db import models


class Review(models.Model):
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.ForeignKey('api.Title', on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
