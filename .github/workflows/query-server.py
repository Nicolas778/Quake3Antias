import json
import socket
from datetime import datetime

def query_quake3_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    # Quake 3 getinfo request
    message = b'\xff\xff\xff\xffgetinfo xxx'
    
    try:
        sock.sendto(message, (host, port))
        data, addr = sock.recvfrom(8192)
        
        response = data.decode('latin-1')
        lines = response.split('\n')
        
        server_info = {}
        players = []
        in_players_section = False
        
        for line in lines:
            if line.startswith('\\'):
                parts = line.split('\\')
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        key = parts[i]
                        value = parts[i+1]
                        server_info[key] = value
            elif line and not line.startswith('info') and not line.startswith('\\'):
                # Player names are in the response
                clean_name = line.strip()
                if clean_name and len(clean_name) > 1:
                    players.append(clean_name)
        
        # Filter out empty entries
        players = [p for p in players if p and p.strip()]
        
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

# Query your server
result = query_quake3_server('videos-shut.gl.at.ply.gg', 5291)

if result:
    with open('server-data.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✓ Success: {result['playerCount']}/{result['maxPlayers']} players on {result['map']}")
    print(f"Players: {', '.join(result['players'][:5])}...")  # Show first 5
else:
    print('✗ Failed to query server')
    exit(1)
