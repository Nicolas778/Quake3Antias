const Gamedig = require('gamedig');
const fs = require('fs');

async function queryServer() {
    try {
        const state = await Gamedig.query({
            type: 'quake3',
            host: 'videos-shut.gl.at.ply.gg',
            port: 5291
        });
        
        const data = {
            status: 'Online',
            players: state.players.map(p => p.name),
            playerCount: state.players.length,
            maxPlayers: state.maxplayers,
            map: state.map,
            lastUpdate: new Date().toISOString()
        };
        
        fs.writeFileSync('server-data.json', JSON.stringify(data, null, 2));
        console.log('✓ Server data updated successfully');
        console.log(`Map: ${state.map}, Players: ${state.players.length}/${state.maxplayers}`);
    } catch (error) {
        console.error('✗ Query failed:', error.message);
        process.exit(1);
    }
}

queryServer();
