import json
import socket
import struct
from datetime import datetime

def query_quake3_server(host, port):
    """Query a Quake 3 server using UDP protocol"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    # Quake 3 getinfo request
    message = b'\xff\xff\xff\xffgetinfo xxx'
    
    try:
        sock.sendto(message, (host, port))
        data, addr = sock.recvfrom(8192)
        
        # Parse the response
        response = data.decode('latin-1')
        lines = response.split('\n')
        
        server_info = {}
        players = []
        
        for line in lines:
            if line.startswith('\\'):
                # Parse key-value pairs
                parts = line.split('\\')
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        key = parts[i]
                        value = parts[i+1]
                        server_info[key] = value
            elif line and not line.startswith('info') and not line.startswith('\\'):
                # This is a player name
                clean_name = line.strip()
                if clean_name and len(clean_name) > 1:
                    players.append(clean_name)
        
        # Filter out empty player names
        players = [p for p in players if p and p.strip()]
        
        return {
            'status': 'Online',
            'map': server_info.get('mapname', 'unknown'),
            'players': players,
            'playerCount': len(players),
            'maxPlayers': int(server_info.get('sv_maxclients', 64)),
            'gameType': server_info.get('g_gametype', 'FFA'),
            'lastUpdate': datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        print(f'Error querying server: {e}')
        return {
            'status': 'Offline',
            'map': 'unknown',
            'players': [],
            'playerCount': 0,
            'maxPlayers': 64,
            'gameType': 'FFA',
            'lastUpdate': datetime.utcnow().isoformat() + 'Z'
        }
    finally:
        sock.close()

# Query your server
result = query_quake3_server('videos-shut.gl.at.ply.gg', 5291)

# Save to JSON file
with open('server-data.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"✓ Updated: {result['playerCount']}/{result['maxPlayers']} players on {result['map']}")
print(f"Players: {', '.join(result['players'][:5])}..." if result['players'] else "No players")
