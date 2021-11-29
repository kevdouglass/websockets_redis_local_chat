const roomName = JSON.parse(document.getElementById('room-name').textContent);
const chatLog = document.getElementById("chat-log");
//this_user-name
console.warn("New Room Name: {"+ roomName +"}");

/** TODO */
// create function to return True/False and handle processing in ChatSocket.onMessage
if (!(chatLog.hasChildNodes()) || chatLog.childNodes.length >= 1 ){
    const emptyTextNode = document.createElement('h3');
    emptyTextNode.id = 'emptyTextNode';
    emptyTextNode.innerText = 'No Messages';
    emptyTextNode.className = 'emptyTextNode';
    chatLog.appendChild(emptyTextNode);
}

function isMessageSender(ws_user_id, logged_in_user_id){
    return (ws_user_id === logged_in_user_id)
}
/* Handle Client Side WebSocket Connection */
const BASE_URL = "ws://"+window.location.host;
const ENDPOINT = "/ws/chat/rooms/";
// const chatSocket = new WebSocket( BASE_URL+ENDPOINT+roomName+"/" );
// console.log("New ChatSocket(", BASE_URL+ENDPOINT+roomName+"/" ,")")

// var chatForm = document.getElementById('chatForm')

const chatSocket = new WebSocket(
    BASE_URL +
    ENDPOINT +
    roomName + '/'
);
chatSocket.onopen = function(ws_event){
    // if self.postMessage
    // const data = JSON.parse(ws_event)
    console.log("\n\nws.onOpen() EVENT:", ws_event  )
    // const data  = {'user_username':'Testicles', 'user_id':-99} //JSON.parse(ws_event.data);
    // const user_username = data['user_username']
    // const user_user_id = data['user_id']
    // logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
    const logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
        // if (chatSocket.protocol == chatSocket.OPEN){
        // }
        // console.warn("\n\n*Logged in User: "+ (user_user_id===logged_in_user_id ? ("Username: "+user_username) : "Unknown User" ))
        const waitingUserQueueDiv = document.getElementById('waiting_queue');
        // const waitingUserNode = document.getElementById('waiting_user');
        console.log("Waiting Users: ");
        // for (let idx in all_other_users){ 
        //     var waiting_user = all_other_users[idx]['user']
        //     var waiting_user_id = waiting_user['id'];
        //     var waiting_user_username = waiting_user['username'];
        //     console.log(waiting_user['id'], waiting_user['username']);

        var waitingUserNode = document.createElement('a');
        waitingUserNode.innerText = JSON.stringify(logged_in_user_id) + "\n";
        waitingUserNode.classList.add('list-group-item', 'list-group-item-action');
        waitingUserQueueDiv.appendChild(waitingUserNode);
        // }
        console.warn("Logged_in_User_id: ", JSON.stringify(logged_in_user_id))
        // chatSocket.send(JSON.stringify({
        //         'waitingQ_broadcast': logged_in_user_id,
        //     }))

}

// once client side wS recieves a message,
chatSocket.onmessage = function(event) {
    /** When user sends message through input field, create new div element and send to other Ws functions */
    
    console.log("onMessage: ", event)
    const data = JSON.parse(event.data);
    // if (data['chat_msg']){
    // }

        const messageNode = document.createElement('div');
        const user_username = data['user_username']
        const user_user_id = data['user_id']
        const logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
        const all_other_users = data['all_other_users'];
        // const waitingUserQueueDiv = document.getElementById('waiting_queue');
        // // const waitingUserNode = document.getElementById('waiting_user');
        // console.log("Waiting Users: ");
        // // for (var i = 0; i < all_other_users.length ; i++){
        //     for (let idx in all_other_users){ 
        //         var waiting_user = all_other_users[idx]['user']
        //         var waiting_user_id = waiting_user['id'];
        //         var waiting_user_username = waiting_user['username'];
        //         console.log(waiting_user['id'], waiting_user['username']);
                
        //         var waitingUserNode = document.createElement('a');
        //         waitingUserNode.innerText = JSON.stringify(waiting_user) + "\n";
        //         waitingUserNode.classList.add('list-group-item', 'list-group-item-action');
        //         waitingUserQueueDiv.appendChild(waitingUserNode);
        //     }
            
            // }
            // var waiting_user = all_other_users[i];
            // waitingUserNode.innerText = (all_other_users)
            // console.log("User: "+JSON.stringify({"this_user_id": user_id, "this_username": user}) +"")
            const user_name_span = document.createElement('small')
            user_name_span.innerText = user_username + " , " + user_user_id;
            user_name_span.classList.add('badge','badge-dark');
            // <span class="badge badge-light">4</span>
            // messageNode.innerHTML =  //.classList.add('')
            messageNode.innerText = data['message'];
            messageNode.appendChild(user_name_span);
    // messageNode.className = 'message'; // insead create class list item of '.message sender' or '.message receiver'
    if (isMessageSender(user_user_id, logged_in_user_id)){
        messageNode.classList.add('message', 'sender');
    }else{
        messageNode.classList.add('message', 'receiver');
    }
    chatLog.appendChild( messageNode );
    
    console.log("WS.onMessage() : {BEGIN}\n\n")
    console.log("User_id: ", JSON.stringify(user_user_id))
    console.log("Username: " , JSON.stringify(user_username));
    
    console.log("WS.onMessage() : {END}")
    if (document.getElementById('emptyTextNode')){
        document.getElementById('emptyTextNode').remove();
    }
}
// chatSocket.onmessage = function(e) {
//     const data = JSON.parse(e.data);
//     console.log("Client Message-event, ", data);
//     document.querySelector('#chat-log').value += (data.message + '\n');
// };

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    const request_user_id = JSON.parse(document.getElementById('request_user_id').textContent)
    // print("Sending MESSAGE + USER to BACKEND.")
    // 'user_username' : user_username,
    chatSocket.send(JSON.stringify({
        'message': message, 
        'waiting_queue_users': request_user_id, 
    }));
    messageInputDom.value = '';
};