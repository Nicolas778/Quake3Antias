import json
import socket
import struct
from datetime import datetime

def query_quake3_server(host, port):
    """Query a Quake 3 server using UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    # Quake 3 getinfo request
    message = b'\xff\xff\xff\xffgetinfo xxx'
    
    try:
        sock.sendto(message, (host, port))
        data, addr = sock.recvfrom(4096)
        
        # Parse the response
        response = data.decode('latin-1')
        lines = response.split('\n')
        
        # Extract info
        server_info = {}
        players = []
        in_players = False
        
        for line in lines:
            if line.startswith('\\'):
                parts = line.split('\\')
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        key = parts[i]
                        value = parts[i+1]
                        server_info[key] = value
            elif line and not line.startswith('info') and not line.startswith('\\'):
                # This might be a player
                if line.strip():
                    players.append(line.strip())
        
        # Filter out empty player names
        players = [p for p in players if p and len(p) > 1]
        
        return {
            'status': 'Online',
            'map': server_info.get('mapname', 'unknown'),
            'players': players,
            'playerCount': len(players),
            'maxPlayers': int(server_info.get('sv_maxclients', 64)),
            'lastUpdate': datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        print(f'Error querying server: {e}')
        return None
    finally:
        sock.close()

# Query the server
result = query_quake3_server('videos-shut.gl.at.ply.gg', 5291)

if result:
    with open('server-data.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✓ Server data updated: {result['playerCount']}/{result['maxPlayers']} players on {result['map']}")
else:
    print('✗ Failed to query server')
    exit(1)
