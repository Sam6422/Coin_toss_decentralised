import streamlit as st
import streamlit.components.v1 as components

st.title("Decentralized Coin Toss Game 🎲")
st.markdown("This game uses **OrbitDB + IPFS** for P2P data storage. No central database!")

# Embed HTML + JS
game_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Coin Toss (Decentralized)</title>
  <script src="https://cdn.jsdelivr.net/npm/ipfs/dist/index.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/orbit-db/dist/orbitdb.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; }
    h3 { color: red; }
    button { margin: 5px; padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 5px; }
    button:hover { background: #0056b3; }
    #dbContent { max-height: 200px; overflow-y: auto; background: #f8f8f8; padding: 10px; margin-top: 10px; border: 1px solid #ccc; }
  </style>
</head>
<body>
  <h3>Join the Game</h3>
  <input id="username" placeholder="Enter username">
  <button onclick="joinGame()">Join</button>

  <div id="gameUI" style="display:none;">
    <hr>
    <button onclick="tossCoin()">Toss Coin</button>
    <p id="status"></p>
    <h4>Leaderboard</h4>
    <ul id="leaderboard"></ul>
    <hr>
    <button onclick="showData()">Show DB Data</button>
    <div id="dbContent"></div>
    <p><b>OrbitDB Address:</b> <span id="dbAddress">Loading...</span></p>
  </div>

<script>
let ipfs, orbitdb, db;
let username = "";
let gameId = "coin-toss-global";

async function joinGame() {
    username = document.getElementById("username").value;
    if (!username) return alert("Enter username");

    document.getElementById("gameUI").style.display = "block";

    // Start IPFS node with WebRTC signaling for browser P2P
    ipfs = await Ipfs.create({
        repo: 'ipfs-' + Math.random(),
        config: {
            Addresses: {
                Swarm: [
                    '/dns4/wrtc-star1.par.dwebops.pub/tcp/443/wss/p2p-webrtc-star/',
                    '/dns4/wrtc-star2.sjc.dwebops.pub/tcp/443/wss/p2p-webrtc-star/'
                ]
            }
        }
    });

    // Start OrbitDB
    orbitdb = await OrbitDB.createInstance(ipfs);

    // Create or open shared database
    db = await orbitdb.docstore(gameId, { indexBy: 'username' });
    await db.load();

    // Show OrbitDB address
    document.getElementById("dbAddress").innerText = db.address.toString();

    db.events.on("replicated", updateLeaderboard);
    updateLeaderboard();
}

async function tossCoin() {
    let result = Math.random() < 0.5 ? "win" : "lose";
    let record = db.get(username)[0] || { username, won: 0, lost: 0, played: 0 };

    record.played += 1;
    if (result === "win") record.won += 1; else record.lost += 1;

    await db.put(record);
    updateLeaderboard();
    document.getElementById("status").innerText = `You ${result}!`;
}

function updateLeaderboard() {
    let list = db.get('');
    list.sort((a, b) => b.won - a.won);
    let html = list.map(u => `<li>${u.username}: W:${u.won}, L:${u.lost}, P:${u.played}</li>`).join('');
    document.getElementById("leaderboard").innerHTML = html;
}

function showData() {
    let data = db.get('');
    document.getElementById("dbContent").innerHTML = "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
}
</script>
</body>
</html>
"""

# Render HTML
components.html(game_html, height=800)
