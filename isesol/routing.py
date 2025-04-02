from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from host.webSocket import WebsocketSSH
application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path('webssh/', WebsocketSSH),
    ]
    )

})

