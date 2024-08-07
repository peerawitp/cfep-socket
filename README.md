# ColCode - Collaborative Code Editor Protocol (Simplified) 📝

This is a file editing collaboration application that allows multiple clients to connect to a server, authenticate, and collaboratively edit a shared file. The server handles file updates from clients and broadcasts changes to all connected clients in real-time. Which is a simple implementation of a collaborative code editor.

## Information
- **Author**: 6510405741 Peerawit Pharkdeepinyo

## Features

- **Authentication**: Clients must authenticate with a global authorization key to access the server.
- **Real-time Updates**: Changes to the file by any client are broadcast to all connected clients. Implemented from pub/sub pattern.
- **File Operations**: Clients can view the entire file or update specific lines.
- **Verbose Logging**: Detailed logging for debugging and monitoring is available.

## Characteristics

- **Reliability**: The server uses TCP, which ensures reliable data transfer by checking for errors and resending lost data. The protocol also has built-in error handling.
- **Delay**: Network delays and server processing time affect response times. The use of threading helps minimize delays and improve user experience.
- **Throughput**: The speed at which data is transferred depends on the size of messages, how often they are sent, and the network speed. In this case, messages are JSON objects which can contain a lot of data.
- **Security**: Basic authentication is used to verify clients. For better security, might consider using more advanced authentication methods like certificates or tokens.

## Usage

1. **Start the Server**

   Run the server script to start the server:

   ```bash
   cd server # Change to the server directory first
   python server.py
   ```

   The server will print the global authentication key and start listening for client connections.

2. **Connect a Client**

   Clients should connect to the server and provide the global authentication key which is printed by the server. Run the client script to connect to the server:

   ```bash
   cd client # Change to the client directory first
   python client.py
   ```

3. **Client Commands**

   Clients can use the following commands:

   - **VIEW**: Retrieve the current content of the file.

     ```json
     {"type": "VIEW"}
     ```

   - **UPDATE**: Update a specific line in the file.

     ```json
     {
         "type": "UPDATE",
         "payload": {
             "line": 1,
             "content": "New content for line 1"
         }
     }
     ```

## Error Handling

- **AUTH_FAILED**: Authentication failed. Ensure the correct authentication key is used.
- **ERROR**: General errors include invalid line numbers, incorrect command types, etc.
