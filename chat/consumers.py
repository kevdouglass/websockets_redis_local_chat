import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
# Get data from DB 
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from .models import Message, Room


class ChatMessageConsumer( AsyncWebsocketConsumer ):
    '''
       > Synchronous Chat Consumer.
        self.connect : Obtains the 'room_name' param fro the UrlRoute in chat/routing.py that opened the WS connection to this Consumer.
            Every consumer has a 'Scope' that contains information about its connection, including kwargs fro the URL route and currently authenticated user, through request.<method> (if any)
                    - room_group_name: constructs a Channels Group name directly fro the user-specified room name, without any weird characters (quoting or escaping)
                    - async_to_sync( channel_layer.<GROUP_ADD> ): Joins a Group. the 'async_to_sync( ... )' wrapper is REQUIRED* because ChatConsumer is a synchronous WsConsumer but is calling an Async channels layer method (All channel layer methods are Async. calls). 
                    - self.accept():  Accepts Ws connection. If you don't call accept, the connection will be rejected and closed (you may want this behavior when a requesting user is not authorized to perform this requested action (Not yet signed Up)). 
        self.disconnect :            
                    - async_to_sync( channel_layer.<GROUP_DISCARD> ): When user leaves the Group (logout)
        self.receive :
                    - async_to_sync( channel_layer.<GROUP_SEND> ):  Sends an Event to a Group. An Event has a special 'type' key corresponding to the name of the METHOD that should be invoked on Consumers that receive the event.

        > Read more (Channels Docs): https://channels.readthedocs.io/en/stable/tutorial/part_2.html
    '''
    def fetch_messages(self, data):
        pass 

    def new_message(self, data):
        pass

    user_queue = []
    async def enqueue_user(self, user):
        userHash = {}
        # if user is an authenticated User
        # if await User.objects.filter(id=user.id).exists():
            # Check if this user is in waiting list for game-room yet
            # authenticated_users = User.objects.get(id=user.id)
        print("User.is_authenticated == TRUE")
        if user.username not in self.user_queue:
            print(f"****\n\t\tAdding {str(user)} to UserQueue!!\n")
            # userHash[user.username] = user.id
            self.user_queue.append(user.username)
            # else:

            # userHash['user'] = {'id':user.id, 'username':user.username}
            # self.user_queue.append(userHash)

    async def display_user_queue(self):
        print("\n\n***\tDisplay_user_queue!\n")
        for item in self.user_queue:
            print(item)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    async def connect(self):
        '''Make handshake & connect Consumer to WS'''
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print("(1) Django.Connecting")
        print(f"(Room-Name, Room-Group-Name) : ({self.room_name}, {self.room_group_name}) ")
        
        # Join Room Group through WS
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )

        await self.enqueue_user(self.scope['user'])
        # if len(self.user_queue) > 1:
        #     await self.display_user_queue()

        # a_user = self.scope['user']
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user_broadcast",
                "user_queue_nodes": self.user_queue,
            }
        )
        # self.send(text_data=json.dumps({ 
        #     'wating_queue': self.scope['user'].username,
        # }))
        # print(f"Creating New Room: {self.room_name}")
        # database_sync_to_async()(self.room_name)
        # self.set_room(self.room_name, self.user)
        await self.accept()

    async def user_broadcast(self, event):
        print("---"*75)
        isUser = True
        print("= new WebSocket.Connection: Channel.user_broadcast(): ")
        print("Broadcast.EVENT: ")
        print(f"User_Queue_Nodes: {event['user_queue_nodes']}")
        print("---"*75)

    #     await self.send(text_data=json.dumps({ 
    #         'user_node': {'id': None, 'username':None}
    #     }))

    async def disconnect(self, disconnect_code):
        ''' Leave a Room (Group)'''
        # print(f"disconnect_code: {disconnect_code}")
        for i in range(0, len(self.user_queue)):
            if self.user_queue[i] == self.scope['user'].username:
                print(f"Disconnecting {self.user_queue[i]}")
                del self.user_queue[i]

        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name 
        )


    async def receive(self, text_data):
        '''Receive message FROM WS:'''
        '''calls group_send message after determining which command waas called'''
        print("(2) Django.Receive")
        
        text_data_json = json.loads(text_data)
        print(f"\t******Text_Data_JSON: {text_data_json} \n\n")
        message = text_data_json['message']
        frontend_user = text_data_json #['waitingQ_broadcast']
        print(f"Front-End User: {frontend_user}")
        self.user = self.scope['user']  # Other User is: ['url_route']['kwargs']['']
        self.user_id = self.user.id
        # self.all_other_users = await self.get_all_other_users(self.user.username)
    # def send_chat_message(self, message):
        # await print(self.all_other_users)
        # print("All other Users: \t{}".format(self.all_other_users))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id' : self.user_id,
                'user_username' : self.user.username,
                'user_queue_nodes':self.user_queue,
                # 'all_other_users' : self.all_other_users,
            }
        )

    async def chat_message(self, event):
        '''Receives messages from our Group'''
        print("\n(3) chat_message get-EVENT,")
        print("send-EVENT: \n{}".format(event))
        # print("All other Users: \t{}".format(all_other_users))
        # Send message to WS 
        await self.send(text_data=json.dumps({ 
            'message' : event['message'],
            'user_id' : event['user_id'],
            'user_username': event['user_username'],
            # 'all_other_users' : event['all_other_users']
        }))
    
    def get_username(self):
        return User.objects.all()[0].name
    
    @database_sync_to_async
    def get_all_other_users(self, this_user_username):
        print("\n\nGet ALl Other Users:")
        # Query Message Model to see which user is currently logged in to this channel?
        # this_message_room = Message.objects.filter(room=self.room_name)
        # print(f"******This->MessageRoom: {this_message_room}\n\n")
        user_set = User.objects.exclude(username=this_user_username)
        user_dict = {'id': None, 'username':None}
        user_list = []
        for user in user_set:
            # for item in row:
            # print(user.id, user.username)
            # user_dict['id'] = user.id
            # user_dict['username'] = user.username
            user_list.append({"user":{"id":user.id, "username":user.username}})
        # print(f"DB->Users_user_list: {user_list}")
        # self.display_users(user_list)
        return user_list

    async def display_users(self,user_list):
        await print("Display All Current USers: ")
        for row in user_list:
            for user in row:
                print(user)

    # def set_message(self, message_data):
    #     msg = Message(user=self.user, content=message_data)
    #     msg.save()
    # def isNewRoom(self, _room_name):
    #     # Room.objects.filter(name=_room_name).
    #     if Room.objects.filter(name=_room_name).exists():
    #         return redirect
    
    # def set_room(self, _room_name, _user_name):
    #     this_room_name = _room_name
    #     this_user_name = _user_name
    #     print(f"User: {this_user_name} is CREATING New Room: {this_room_name}")
        
    #     room = Room(name=this_room_name, user=this_user_name)
    #     room.save()





# #########################################
# Synchronous WS Consumer
##############################################33



# class ChatMessageConsumer( WebsocketConsumer ):
#     '''
#        > Synchronous Chat Consumer.
#         self.connect : Obtains the 'room_name' param fro the UrlRoute in chat/routing.py that opened the WS connection to this Consumer.
#             Every consumer has a 'Scope' that contains information about its connection, including kwargs fro the URL route and currently authenticated user, through request.<method> (if any)
#                     - room_group_name: constructs a Channels Group name directly fro the user-specified room name, without any weird characters (quoting or escaping)
#                     - async_to_sync( channel_layer.<GROUP_ADD> ): Joins a Group. the 'async_to_sync( ... )' wrapper is REQUIRED* because ChatConsumer is a synchronous WsConsumer but is calling an Async channels layer method (All channel layer methods are Async. calls). 
#                     - self.accept():  Accepts Ws connection. If you don't call accept, the connection will be rejected and closed (you may want this behavior when a requesting user is not authorized to perform this requested action (Not yet signed Up)). 
#         self.disconnect :            
#                     - async_to_sync( channel_layer.<GROUP_DISCARD> ): When user leaves the Group (logout)
#         self.receive :
#                     - async_to_sync( channel_layer.<GROUP_SEND> ):  Sends an Event to a Group. An Event has a special 'type' key corresponding to the name of the METHOD that should be invoked on Consumers that receive the event.

#         > Read more (Channels Docs): https://channels.readthedocs.io/en/stable/tutorial/part_2.html
#     '''
#     def fetch_messages(self, data):
#         pass 

#     def new_message(self, data):
#         pass

#     commands = {
#         'fetch_messages': fetch_messages,
#         'new_message': new_message,
#     }

#     def connect(self):
#         '''Make handshake & connect Consumer to WS'''
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.user = self.scope['user']
#         self.room_group_name = 'chat_%s' % self.room_name
#         print("(1) Django.Connecting")
#         print(f"(Room-Name, Room-Group-Name) : ({self.room_name}, {self.room_group_name}) ")
        
#         # Join Room Group through WS
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, 
#             self.channel_name
#         )
#         # print(f"Creating New Room: {self.room_name}")
#         # database_sync_to_async()(self.room_name)
#         # self.set_room(self.room_name, self.user)
#         self.accept()

#     def disconnect(self, disconnect_code):
#         ''' Leave a Room (Group)'''
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name 
#         )


#     def receive(self, text_data):
#         '''Receive message FROM WS:'''
#         '''calls group_send message after determining which command waas called'''
#         text_data_json = json.loads(text_data)
#         print("(2) Django.Receive")
#         self.user = self.scope['user']  # Other User is: ['url_route']['kwargs']['']
#         print(f"User? {self.user}")

#     # def send_chat_message(self, message):
#         message = text_data_json['message']
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#             }
#         )

#     def chat_message(self, event):
#         '''Receives messages from our Group'''
#         message = event['message']
#         print("\n(3) chat_message get-EVENT,")
#         print("send-EVENT: \n{}".format(event))
#         # Send message to WS 
#         self.send(text_data=json.dumps({ 
#             'message' : message,
#         }))
    
#     def get_username(self):
#         return User.objects.all()[0].name

    # def set_message(self, message_data):
    #     msg = Message(user=self.user, content=message_data)
    #     msg.save()
    # def isNewRoom(self, _room_name):
    #     # Room.objects.filter(name=_room_name).
    #     if Room.objects.filter(name=_room_name).exists():
    #         return redirect
    
    # def set_room(self, _room_name, _user_name):
    #     this_room_name = _room_name
    #     this_user_name = _user_name
    #     print(f"User: {this_user_name} is CREATING New Room: {this_room_name}")
        
    #     room = Room(name=this_room_name, user=this_user_name)
    #     room.save()