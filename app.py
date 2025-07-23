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
</head>
<body>
  <h3 style="color: red;">Join the Game</h3>
  <input id="username" placeholder="Enter username">
  <button onclick="joinGame()">Join</button>
  <div id="gameUI" style="display:none;">
    <hr>
    <button onclick="tossCoin()">Toss Coin</button>
    <p id="status"></p>
    <h4>Leaderboard</h4>
    <ul id="leaderboard"></ul>
  </div>

<script>
let ipfs, orbitdb, db;
let username = "";
let gameId = "coin-toss-global";

async function joinGame() {
    username = document.getElementById("username").value;
    if (!username) return alert("Enter username");

    document.getElementById("gameUI").style.display = "block";

    // Start IPFS node
    ipfs = await Ipfs.create({ repo: 'ipfs-' + Math.random() });

    // Start OrbitDB
    orbitdb = await OrbitDB.createInstance(ipfs);

    // Create or open a shared database
    db = await orbitdb.docstore(gameId, { indexBy: 'username' });
    await db.load();

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
</script>
</body>
</html>
"""

# Render HTML
components.html(game_html, height=600)
