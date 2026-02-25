# Django Chat Application

A comprehensive real-time chat application built with Django Channels and Redis.

## Features

- **Real-time messaging** using WebSockets
- **Private and group chats**
- **Message history** stored in PostgreSQL
- **JWT authentication** for WebSocket connections
- **Delivery and read receipts**
- **Typing indicators**
- **Message editing and deletion**
- **User search functionality**
- **Participant management** for group chats
- **RESTful API** for all chat operations

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Redis server**:
   ```bash
   redis-server
   ```

3. **Run Django migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the server**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
All endpoints require JWT authentication via:
- **REST API**: `Authorization: Bearer <token>` header
- **WebSocket**: `token` query parameter

### Chat Rooms

- `GET /chat/rooms/` - List all chat rooms
- `GET /chat/rooms/{room_id}/` - Get room details
- `POST /chat/rooms/create/private/` - Create private room
- `POST /chat/rooms/create/group/` - Create group room

### Messages

- `GET /chat/rooms/{room_id}/messages/` - List messages (paginated)
- `POST /chat/rooms/{room_id}/messages/` - Send message
- `GET /chat/rooms/{room_id}/messages/{message_id}/` - Get message details
- `PATCH /chat/rooms/{room_id}/messages/{message_id}/` - Edit message
- `DELETE /chat/rooms/{room_id}/messages/{message_id}/` - Delete message
- `POST /chat/rooms/{room_id}/messages/mark-read/` - Mark messages as read

### Participants

- `GET /chat/rooms/{room_id}/participants/` - List participants
- `POST /chat/rooms/{room_id}/participants/add/` - Add participant (group only)
- `DELETE /chat/rooms/{room_id}/participants/{user_id}/remove/` - Remove participant

### Users

- `GET /chat/users/search/?q=query` - Search users

## WebSocket API

### Connection
Connect to: `ws://localhost:8000/ws/chat/{room_id}/?token={jwt_token}`

### Message Types

#### Send Message
```json
{
  "type": "chat_message",
  "message": "Hello, world!",
  "message_type": "text",
  "file_url": null
}
```

#### Typing Indicators
```json
{
  "type": "typing_start"
}
```

```json
{
  "type": "typing_stop"
}
```

#### Mark as Read
```json
{
  "type": "mark_as_read",
  "message_id": "uuid"
}
```

#### Edit Message
```json
{
  "type": "edit_message",
  "message_id": "uuid",
  "new_content": "Updated message"
}
```

### Received Message Types

#### New Message
```json
{
  "type": "chat_message",
  "message": {
    "id": "uuid",
    "content": "Hello, world!",
    "message_type": "text",
    "sender": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "is_edited": false,
    "edited_at": null
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing_indicator",
  "user_id": "uuid",
  "user_email": "user@example.com",
  "is_typing": true
}
```

#### Read Receipt
```json
{
  "type": "read_receipt",
  "message_id": "uuid",
  "user_id": "uuid",
  "user_email": "user@example.com"
}
```

#### Message Edited
```json
{
  "type": "message_edited",
  "message": {
    "id": "uuid",
    "content": "Updated message",
    "is_edited": true,
    "edited_at": "2023-01-01T00:00:00Z"
  }
}
```

#### User Status
```json
{
  "type": "user_status",
  "user_id": "uuid",
  "status": "online"
}
```

## Usage Examples

### Creating a Private Chat Room

```python
import requests

# Create private room
response = requests.post('http://localhost:8000/chat/rooms/create/private/', {
    'participant_id': 'user-uuid'
}, headers={'Authorization': 'Bearer your-jwt-token'})

room_data = response.json()
room_id = room_data['id']
```

### Creating a Group Chat Room

```python
# Create group room
response = requests.post('http://localhost:8000/chat/rooms/create/group/', {
    'name': 'Project Team',
    'participant_ids': ['user1-uuid', 'user2-uuid', 'user3-uuid']
}, headers={'Authorization': 'Bearer your-jwt-token'})

room_data = response.json()
```

### Sending a Message

```python
# Send message via REST API
response = requests.post(f'http://localhost:8000/chat/rooms/{room_id}/messages/', {
    'content': 'Hello everyone!',
    'message_type': 'text'
}, headers={'Authorization': 'Bearer your-jwt-token'})
```

### WebSocket Connection (JavaScript)

```javascript
const token = 'your-jwt-token';
const roomId = 'room-uuid';
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/?token=${token}`);

socket.onopen = function(event) {
    console.log('Connected to chat room');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    switch(data.type) {
        case 'chat_message':
            displayMessage(data.message);
            break;
        case 'typing_indicator':
            showTypingIndicator(data);
            break;
        case 'read_receipt':
            markMessageAsRead(data.message_id);
            break;
        // ... handle other message types
    }
};

// Send message
function sendMessage(content) {
    socket.send(JSON.stringify({
        type: 'chat_message',
        message: content,
        message_type: 'text'
    }));
}

// Send typing indicator
function startTyping() {
    socket.send(JSON.stringify({
        type: 'typing_start'
    }));
}

function stopTyping() {
    socket.send(JSON.stringify({
        type: 'typing_stop'
    }));
}
```

### Marking Messages as Read

```python
# Mark multiple messages as read
response = requests.post(f'http://localhost:8000/chat/rooms/{room_id}/messages/mark-read/', {
    'message_ids': ['msg1-uuid', 'msg2-uuid', 'msg3-uuid']
}, headers={'Authorization': 'Bearer your-jwt-token'})
```

### Searching Users

```python
# Search for users to invite
response = requests.get('http://localhost:8000/chat/users/search/', {
    'q': 'john'
}, headers={'Authorization': 'Bearer your-jwt-token'})

users = response.json()
```

## Models

### ChatRoom
- Supports both private and group chats
- Tracks participants and last activity
- Provides methods for room management

### Message
- Stores message content and metadata
- Supports different message types (text, image, file)
- Tracks editing history

### MessageStatus
- Tracks delivery and read status per user
- Enables read receipts functionality

### TypingIndicator
- Manages typing indicators per room
- Automatically cleaned up on disconnect

### ChatRoomMembership
- Tracks user roles in chat rooms
- Manages permissions and unread counts

## Security Features

- JWT authentication for all connections
- Permission-based access control
- User can only access rooms they're part of
- Message editing/deletion restricted to sender
- Group management restricted to admins/owners

## Performance Optimizations

- Database query optimization with prefetch_related
- Pagination for message history
- Efficient WebSocket message broadcasting
- Redis-based channel layer for scaling

## Testing

Run the test suite:
```bash
python manage.py test chat
```

## Production Deployment

1. **Configure Redis** for production use
2. **Set up SSL/TLS** for WebSocket connections
3. **Configure Django settings** for production
4. **Use a reverse proxy** like Nginx for WebSocket handling
5. **Set up monitoring** for WebSocket connections and Redis

## Environment Variables

- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `POSTGRES_*`: PostgreSQL database settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request
