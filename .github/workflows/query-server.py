import json
import socket
from datetime import datetime

def query_quake3_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    message = b'\xff\xff\xff\xffgetinfo xxx'
    
    try:
        sock.sendto(message, (host, port))
        data, addr = sock.recvfrom(8192)
        
        response = data.decode('latin-1')
        lines = response.split('\n')
        
        server_info = {}
        players = []
        
        for line in lines:
            if line.startswith('\\'):
                parts = line.split('\\')
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        server_info[parts[i]] = parts[i+1]
            elif line and not line.startswith('info') and not line.startswith('\\'):
                if line.strip() and len(line.strip()) > 1:
                    players.append(line.strip())
        
        players = [p for p in players if p]
        
        return {
            'status': 'Online',
            'map': server_info.get('mapname', 'unknown'),
            'players': players,
            'playerCount': len(players),
            'maxPlayers': int(server_info.get('sv_maxclients', 64)),
            'lastUpdate': datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        print(f'Error: {e}')
        return None
    finally:
        sock.close()

result = query_quake3_server('videos-shut.gl.at.ply.gg', 5291)

if result:
    with open('server-data.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✓ Updated: {result['playerCount']}/{result['maxPlayers']} on {result['map']}")
else:
    print('✗ Failed')
    exit(1)
