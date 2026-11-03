from signalrcore.hub_connection_builder import HubConnectionBuilder
import time
from signalrcore.hub_connection_builder import HubConnectionBuilder


'''

def on_message(message):
    print(f"📨 Received: {message}")


def on_connected():
    print("✅ Connected to SignalR hub")


def on_error(error):
    print(f"❌ Error: {error}")


def on_close():
    print("🔌 Connection closed")


# Create connection
hub_url = "wss://api.qat.fraudsterkill.com/hubs/faip?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTg4NTM4MjAsInVzZXIiOnsiaWQiOjI2LCJuYW1lIjoiYWRtaW4ucWEzIn0sInBlcm1pc3Npb25zIjpbMywxMSwxMiwxNSwxNiwxNywxOSwyMCwyMSwyMiwyMywyNCwyNSwyOCwyOSwzMCwzMSwzMiwzMywzNCwzNSwzNiwzNywzOSw0MCw0MSw0Miw0Myw0NCw0NSw0Niw0Nyw0OCw0OSw1MCw1MSw1Miw1Myw2MCw2MSw2Miw2Myw2NCw2NSw2Niw2Nyw2OCw2OSw3Myw3NCw3NSw3Niw3Nyw3OCw3OSw4MCw4MSw4Miw4Myw4NCw4NSw4Niw4Nyw4OCw4OSw5Myw5NCw5NSw5Nyw5OCw5OSwxMDAsMTAxLDEwMiwxMDMsMTA0LDEwNSwxMDYsMTA3LDEwOCwxMDksMTEwLDExMSwxMTIsMTEzLDExNCwxMTUsMTE2LDExNywxMTgsMTIwLDEyMSwxMjIsMTIzLDEyNCwxMjUsMTI2LDEyNywxMjgsMTI5LDEzMCwxMzEsMTMyLDEzMywxMzQsMTM1LDEzNiwxMzcsMTM5LDE0MCwxNDEsMTQyLDE0MywxNDQsMTQ1LDE0NiwxNDcsMTQ4LDE0OSwxNTAsMTUxLDE1MiwxNTMsMTU0LDE1NSwxNTYsMTU4LDE1OSwxNjAsMTY3LDE2OCwxNjksMTcwLDE3MSwxNzIsMTczLDE3NCwxNzUsMTc2LDE3OCwxNzksMTgwLDE4MSwxODIsMTgzLDE4NCwxODUsMTg2LDE4NywxODgsMTg5LDE5MCwxOTEsMTkyLDE5MywxOTQsMTk1LDE5NiwxOTcsMTk4LDE5OSwyMDAsMjAxLDIwMiwyMDMsMjA0LDIwNSwyMDYsMjA3LDIwOCwyMDksMjEwLDIxMSwyMTIsMjEzLDIxNCwyMTUsMjE5LDIyMCwyMjEsMjIyLDIyMywyMjQsMjI1LDIyNiwyMjcsMjI4LDIyOSwyMzAsMjMxLDIzMiwyMzMsMjM0LDIzNSwyMzYsMjM3LDIzOCwyMzksMjQwLDI0MSwyNDIsMjQzLDI0NSwyNDYsMjQ3LDI0OCwyNDksMSwyLDksMjYsMjcsOTAsMTU3LDE3NywyNTFdfQ.vflvkgaoRWEgGG-elTVw9KjigyJmGmRgT_rOUP47_lU"  # Replace with your URL

connection = HubConnectionBuilder() \
    .with_url(hub_url) \
    .with_automatic_reconnect({
    "type": "interval",
    "reconnect_interval": 5,
    "max_attempts": 10
}) \
    .build()

# Set up event handlers
connection.on("ReceiveMessage", on_message)
connection.on_open(on_connected)
connection.on_error(on_error)
connection.on_close(on_close)

try:
    # Start connection
    print("🔗 Connecting...")
    connection.start()

    # Keep the connection alive
    time.sleep(2)  # Wait for connection to establish

    # Send a message (if your hub supports this method)
    connection.send("SendMessage", ["Hellotest!"])

    # Keep running to receive messages
    print("👂 Listening for messages...")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping...")
finally:
    connection.stop()
'''