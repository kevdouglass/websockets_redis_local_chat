from django.core.checks import messages
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
# Create your models here.
class Room(models.Model):
    '''a room can have many users,
        a room has a name,
        a room can have many messages,
    '''
    name = models.CharField(max_length=75, blank=True, null=True)


class Message(models.Model):
    """
        A Room can have MANY messages,
        A User can have MANY messages
        
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.content

    def pre_load(self):
        '''load the most recent 10 messages'''
        return Message.objects.order_by('-timestamp').all()[:10]

    
    
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # messages = models.ForeignKey(Message, on_delete=models.SET_NULL, blank=True, null=True)

    # def connect_user(self, user):
    #     """
    #     return True if user is added to users list, keeps a counter of current users
    #     """
    #     # if user not inside of current user list, add them
    #     # otherwise, if user is in there, return true
    #     if user in self.user.all():
    #         return True 
    #     else:
    #         return False 

    # def disconnect_user(self, user):

    #     if 



