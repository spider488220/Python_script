भाई, यह टाइमआउट इसलिए आया क्योंकि हमारे कोड के `execute` फ़ंक्शन में **12 सेकंड की सख्त समय सीमा (`timeout=12`)** लगी हुई है।

जब आप `adb pull` चलाकर पूरा का पूरा Screenshots फ़ोल्डर पीसी में कॉपी करने की कोशिश करते हैं, तो अगर फ़ोल्डर का साइज़ बड़ा हो या Wireless ADB की स्पीड थोड़ी कम हो, तो ट्रांसफर होने में 12 सेकंड से ज़्यादा का समय लग जाता है। जैसे ही 12 सेकंड पूरे होते हैं, स्क्रिप्ट प्रोसेस को बीच में ही मार देती है।

### 🛠️ इसका परफ़ेक्ट फ़िक्स:

मैंने बैकएंड में दो बड़े बदलाव किए हैं:

1. **Dynamic Timeout Engine:** अब साधारण शेल कमांड्स के लिए 12 सेकंड का टाइमआउट रहेगा, लेकिन जैसे ही आप कोई भारी काम करेंगे (जैसे फ़ाइल ट्रांसफर `pull`/`push` या पूरा स्टोरेज डंप `ls -R`), तो टाइमआउट अपने आप बढ़कर **5 मिनट (300 सेकंड)** हो जाएगा।
2. **Explicit Target Path:** जब आप `adb pull` करते हैं, तो फाइलें कहाँ सेव होंगी यह बताना ज़रूरी होता है। बैकएंड अब इसे अपने आप आपके पीसी के करंट डायरेक्टरी में डाउनलोड कर देगा।

यहाँ आपका अपग्रेटेड कोड है, इसे रिप्लेस कर लें:

```python
import io
from flask import Flask, jsonify, request, send_file
import subprocess

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>⚡ NEXUS-X: ADVANCED OPERATOR CONTROL CORE v6.8 ⚡</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&display=swap');

        body {
            background-color: #0a0a0c;
            color: #00ff66;
            font-family: 'Fira Code', monospace;
            padding: 25px;
            margin: 0;
            overflow-x: hidden;
        }

        .container {
            max-width: 1600px;
            margin: auto;
        }

        header {
            text-align: center;
            border-bottom: 2px solid #00ff66;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        header h1 {
            margin: 5px 0;
            letter-spacing: 4px;
            font-size: 28px;
            color: #ffffff;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        @media (max-width: 1200px) {
            .grid { grid-template-columns: 1fr 1fr; }
        }

        @media (max-width: 850px) {
            .grid { grid-template-columns: 1fr; }
        }

        .box {
            background: #111115;
            border: 2px solid #33333f;
            padding: 22px;
            border-radius: 6px;
            position: relative;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }

        .box:hover {
            border-color: #00ff66;
        }

        .box::before {
            position: absolute;
            top: -12px;
            left: 15px;
            background: #0a0a0c;
            padding: 0 10px;
            font-size: 12px;
            color: #00ffaa;
            font-weight: 600;
        }

        .box.recon::before { content: "[ MODULE 01 // DEVICE INTELLIGENCE ]"; }
        .box.apps::before { content: "[ MODULE 02 // APP CONTROL MATRIX ]"; }
        .box.db-search::before { content: "[ MODULE 03 // SMART SHELL TERMINAL ]"; }
        .box.live-feed::before { content: "[ MODULE 04 // REALTIME SCREEN ENGINE ]"; }
        .box.storage::before { content: "[ MODULE 05 // STORAGE INTERCEPT & DUMP ]"; }

        .status-bar {
            grid-column: 1 / -1;
            background: #121218;
            border: 2px solid #00ff66;
            padding: 20px;
            border-radius: 6px;
        }

        .matrix-title {
            font-size: 16px;
            color: #ffffff;
            margin-bottom: 15px;
            border-bottom: 1px solid #33333f;
            padding-bottom: 8px;
            font-weight: 600;
        }

        .control-row {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }

        .panel-section {
            display: flex;
            align-items: center;
            gap: 10px;
            background: #1a1a24;
            padding: 8px 15px;
            border: 1px solid #33333f;
            border-radius: 4px;
        }

        .section-label {
            font-weight: 600;
            color: #00ffaa;
            font-size: 13px;
        }

        input[type="text"] {
            background: #000000;
            border: 1px solid #33333f;
            color: #ffffff;
            padding: 8px 12px;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
            border-radius: 4px;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #00ff66;
        }

        .input-ip { width: 140px; }
        .input-port { width: 75px; }
        .input-code { width: 95px; }

        button {
            padding: 9px 16px;
            background: #111115;
            color: #00ff66;
            border: 1px solid #00ff66;
            font-family: 'Fira Code', monospace;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            text-transform: uppercase;
            font-size: 13px;
            border-radius: 4px;
        }

        button:hover {
            background: #00ff66;
            color: #000000;
            box-shadow: 0 0 10px rgba(0, 255, 102, 0.4);
        }

        .status-display {
            font-size: 16px;
            font-weight: 600;
            margin-left: auto;
            background: #000;
            padding: 8px 15px;
            border-radius: 4px;
            border: 1px solid #33333f;
        }

        .output-box {
            grid-column: 1 / -1;
        }
        .output-box::before { content: "[ LIVE TERMINAL STACK LOG ]"; }

        pre {
            background: #000000;
            border: 1px solid #33333f;
            padding: 18px;
            height: 350px;
            overflow: auto;
            color: #ffffff;
            font-size: 14px;
            line-height: 1.6;
            border-radius: 4px;
        }

        .screen-container {
            text-align: center;
            margin-top: 15px;
            background: #000000;
            border: 1px dashed #33333f;
            padding: 10px;
            min-height: 450px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 4px;
        }

        #live-screen {
            max-width: 100%;
            max-height: 600px;
            border: 1px solid #33333f;
            display: none;
        }

        .placeholder-text {
            color: #555566;
            letter-spacing: 1px;
        }

        .btn-grid {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 10px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 5px;
        }

        .input-group input {
            flex-grow: 1;
        }
    </style>

    <script>
        let isStreaming = false;

        function logTerminal(text) {
            let out = document.getElementById("out");
            let timestamp = new Date().toISOString().slice(11, 19);
            out.innerHTML += `\\n[${timestamp}] ${text}`;
            out.scrollTop = out.scrollHeight;
        }

        async function run(name, inputId = null) {
            let url = "/run/" + name;
            if (inputId) {
                let val = document.getElementById(inputId).value;
                if(!val) {
                    logTerminal(`[-] Error: Data required for target field.`);
                    return;
                }
                url += "?arg=" + encodeURIComponent(val);
            }
            try {
                let r = await fetch(url);
                let data = await r.text();
                document.getElementById("out").innerText = data;
                logTerminal(`[+] Module [${name}] operation flushed.`);
            } catch(e) {
                logTerminal(`[-] Connection pipeline dispatch error.`);
            }
        }

        async function runRawAdb() {
            let fullCommand = document.getElementById("adb-master-search").value.trim();
            if(!fullCommand) return;
            logTerminal(`🚀 Executing Direct Vector: [${fullCommand}]...`);
            try {
                let r = await fetch("/run_raw?cmd=" + encodeURIComponent(fullCommand));
                let data = await r.text();
                document.getElementById("out").innerText = data;
                logTerminal(`[+] Execution complete.`);
            } catch(e) {
                logTerminal(`[-] Shell execution fault.`);
            }
        }

        async function connect() {
            logTerminal("📡 Initializing hardware scan...");
            let r = await fetch("/connect");
            let data = await r.json();
            document.getElementById("status").innerText = data.message;
            document.getElementById("status").style.color = data.ok ? "#00ff66" : "#ff3333";
            logTerminal(data.ok ? "[+] Connection validated successfully." : "[-] System hardware node offline.");
        }

        async function pairWireless() {
            let ip = document.getElementById("pair-ip").value.trim();
            let port = document.getElementById("pair-port").value.trim();
            let code = document.getElementById("pair-code").value.trim();

            if(!ip || !port || !code) {
                alert("Please complete the pairing fields.");
                return;
            }

            logTerminal(`🔑 Registering device pairing protocol -> ${ip}:${port}...`);
            try {
                let r = await fetch(`/pair_wireless?ip=${encodeURIComponent(ip)}&port=${encodeURIComponent(port)}&code=${encodeURIComponent(code)}`);
                let data = await r.json();
                document.getElementById("out").innerText = data.details;
                if(data.ok) {
                    logTerminal(`[+] Handshake verified. Target paired.`);
                    document.getElementById("connect-ip").value = ip;
                } else {
                    logTerminal(`[-] Pair refused by target node.`);
                }
            } catch(e) {
                logTerminal("[-] Security layer error.");
            }
        }

        async function connectWireless() {
            let ip = document.getElementById("connect-ip").value.trim();
            let port = document.getElementById("connect-port").value.trim();

            if(!ip || !port) return;
            logTerminal(`📡 Bridging socket connection to ${ip}:${port}...`);
            try {
                let r = await fetch(`/connect_wireless?ip=${encodeURIComponent(ip)}&port=${encodeURIComponent(port)}`);
                let data = await r.json();
                document.getElementById("status").innerText = data.message;
                document.getElementById("status").style.color = data.ok ? "#00ff66" : "#ff3333";
                if(data.ok) {
                    logTerminal(`[+] Transport connection link established.`);
                } else {
                    logTerminal(`[-] Handshake dropped. Target refused link.`);
                }
            } catch(e) {
                logTerminal("[-] Socket channel fault.");
            }
        }

        function loadNextFrame() {
            if (!isStreaming) return;

            let img = document.getElementById("live-screen");
            let placeholder = document.getElementById("placeholder");
            
            let bufferImg = new Image();
            bufferImg.src = "/screen.png?t=" + new Date().getTime();

            bufferImg.onload = function() {
                if (!isStreaming) return;
                img.src = bufferImg.src;
                placeholder.style.display = "none";
                img.style.display = "inline-block";
                setTimeout(loadNextFrame, 150);
            };

            bufferImg.onerror = function() {
                if (!isStreaming) return;
                setTimeout(loadNextFrame, 500);
            };
        }

        function toggleStream() {
            let img = document.getElementById("live-screen");
            let placeholder = document.getElementById("placeholder");
            let btn = document.getElementById("stream-btn");

            if (isStreaming) {
                isStreaming = false;
                btn.innerText = "▶ START LIVE MONITOR FEED";
                img.style.display = "none";
                placeholder.style.display = "block";
                logTerminal("🛑 Screen stream engine halted.");
            } else {
                isStreaming = true;
                btn.innerText = "🛑 BLOCK LIVE MONITOR FEED";
                logTerminal("⚡ Synchronizing persistent async frame buffer...");
                loadNextFrame();
            }
        }
    </script>
</head>
<body>

<div class="container">
    <header>
        <h1>⚡ NEXUS-X // MAIN DEPLOYMENT CENTER v6.8 ⚡</h1>
        <div style="color: #888899; font-size: 14px; margin-top: 5px;">DYNAMIC TIMEOUT OVERRIDE ONLINE • DESKTOP OPERATOR VIEW</div>
    </header>

    <div class="grid">
        <div class="status-bar">
            <div class="matrix-title">🌐 SUBSYSTEM RUNTIME INTERACTION CONTROL</div>
            <div class="control-row">
                <div class="panel-section">
                    <button onclick="connect()">🔌 AUTO-SCAN USB</button>
                </div>

                <div class="panel-section">
                    <span class="section-label">1. PAIR:</span>
                    <input type="text" id="pair-ip" class="input-ip" placeholder="Target IP">
                    <input type="text" id="pair-port" class="input-port" placeholder="Pair Port">
                    <input type="text" id="pair-code" class="input-code" placeholder="6-Digit PIN">
                    <button onclick="pairWireless()" style="border-color: #00ffaa; color: #00ffaa;">⚡ PAIR</button>
                </div>

                <div class="panel-section">
                    <span class="section-label">2. CONNECT:</span>
                    <input type="text" id="connect-ip" class="input-ip" placeholder="Target IP">
                    <input type="text" id="connect-port" class="input-port" placeholder="Conn Port" value="5555">
                    <button onclick="connectWireless()">📡 CONNECT</button>
                </div>

                <div class="status-display">NODE STATUS: <span id="status" style="color: #ff3333;">OFFLINE</span></div>
            </div>
        </div>

        <div class="box db-search full-width">
            <h3>SMART SHELL TERMINAL ENGINE (Pre-routed shell)</h3>
            <div style="color: #888899; font-size: 13px; margin-bottom: 10px;">
                * Direct execution active. Files pulled via <span style="color: #00ffaa;">pull</span> will stream directly to your local execution core folder.
            </div>
            <div class="input-group">
                <input type="text" id="adb-master-search" placeholder="Type direct command or pull path (e.g., pull /sdcard/Pictures/Screenshots)...">
                <button onclick="runRawAdb()">⚡ EXECUTE COMMAND</button>
            </div>
        </div>

        <div class="box recon">
            <h3>Device Intelligence</h3>
            <div class="btn-grid">
                <button onclick="run('info')">Fetch Subsystem Architecture</button>
                <button onclick="run('battery')">Query Power Management</button>
                <button onclick="run('wm_size')">Display Aspect Parameters</button>
                <button onclick="run('reboot')" style="border-color: #ff3333; color: #ff3333;">⚠️ Soft Reboot System</button>
            </div>
        </div>

        <div class="box apps">
            <h3>App Control Matrix</h3>
            <div class="btn-grid">
                <button onclick="run('list_packages')">Enumerate Package Database</button>
                <div style="border-top: 1px solid #22222b; margin: 5px 0;"></div>
                <input type="text" id="pkg-name" placeholder="com.target.package">
                <button onclick="run('clear_data', 'pkg-name')">Purge Application Space</button>
                <button onclick="run('force_stop', 'pkg-name')">Terminate App Process</button>
            </div>
        </div>

        <div class="box storage">
            <h3>Storage Intercept & Dump</h3>
            <div class="btn-grid">
                <button onclick="run('list_storage')">📁 List Root Storage (/sdcard)</button>
                <button onclick="run('dump_storage_tree')">🌳 Recursive Hierarchy Dump</button>
                <button onclick="run('storage_metrics')">📊 Inspect Drive Mount Allocation</button>
            </div>
        </div>

        <div class="box live-feed full-width">
            <h3>REALTIME DISPLAY BUFFER MIRROR</h3>
            <button id="stream-btn" onclick="toggleStream()">▶ START LIVE MONITOR FEED</button>
            <div class="screen-container">
                <span id="placeholder" class="placeholder-text">[ DEVICE DISPLAY NODE INACTIVE ]</span>
                <img id="live-screen" src="" alt="Live Device Frame">
            </div>
        </div>

        <div class="box output-box">
            <pre id="out">⚡ SYSTEM CORE INITIALIZED. ENVIRONMENT PIPELINE CLEAN. AWAITING OPERATION...</pre>
        </div>
    </div>
</div>

</body>
</html>
"""

# --- CRITICAL FIX: EXPLICIT TIMEOUT MANAGEMENT ---
def execute(cmd, timeout_seconds=12):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
        return r.stdout if r.stdout else r.stderr
    except subprocess.TimeoutExpired:
        return f"[-] OPERATION TIMEOUT: The execution exceeded {timeout_seconds}s limit. The folder payload size might be massive or connection is throttling."
    except Exception as e:
        return str(e)

@app.route("/")
def home():
    return HTML

@app.route("/connect")
def connect():
    out = execute(["adb", "devices"])
    if "\tdevice" in out:
        return jsonify({"ok": True, "message": "ONLINE"})
    return jsonify({"ok": False, "message": "OFFLINE"})

@app.route("/pair_wireless")
def pair_wireless():
    ip = request.args.get('ip', '').strip()
    port = request.args.get('port', '').strip()
    code = request.args.get('code', '').strip()
    
    if not ip or not port or not code:
        return jsonify({"ok": False, "details": "Parameters missing."})
    
    out = execute(["adb", "pair", f"{ip}:{port}", code])
    if "successfully paired" in out.lower():
        return jsonify({"ok": True, "details": out.strip()})
    return jsonify({"ok": False, "details": out.strip()})

@app.route("/connect_wireless")
def connect_wireless():
    ip = request.args.get('ip', '').strip()
    port = request.args.get('port', '').strip()
    if not ip or not port:
        return jsonify({"ok": False, "message": "MISSING INFO"})
    
    out = execute(["adb", "connect", f"{ip}:{port}"])
    if "connected to" in out.lower():
        return jsonify({"ok": True, "message": "ONLINE"})
    return jsonify({"ok": False, "message": "REFUSED"})

@app.route("/screen.png")
def serve_live_screen():
    try:
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True, timeout=3)
        if result.stdout and len(result.stdout) > 0:
            return send_file(io.BytesIO(result.stdout), mimetype='image/png')
    except Exception:
        pass
    return "Stream failure", 500

@app.route("/run_raw")
def run_raw():
    cmd_str = request.args.get('cmd', '').strip()
    if not cmd_str: return "Buffer empty."
    
    # Check if user explicitly wrote adb command
    if cmd_str.startswith("adb "):
        parts = cmd_str.split()
    else:
        parts = ["adb", "shell"] + cmd_str.split()
    
    # --- DYNAMIC TIMEOUT ROUTING ---
    # If downloading/uploading files or requesting a deep recursive tree, inject a 5-minute threshold
    current_timeout = 12
    if "pull" in parts or "push" in parts or "-R" in parts:
        current_timeout = 300  # 5 Minutes allocation
        
        # Security validation for generic 'pull' without destination target path
        if "pull" in parts and len(parts) == 3:
            # Inject a '.' to make sure it pulls to the current working directory of the script
            parts.append(".")

    return execute(parts, timeout_seconds=current_timeout)

@app.route("/run/<action>")
def run(action):
    arg = request.args.get('arg', '')
    
    # Core command registry
    commands = {
        "info": ["adb", "shell", "getprop"],
        "battery": ["adb", "shell", "dumpsys", "battery"],
        "wm_size": ["adb", "shell", "wm", "size"],
        "reboot": ["adb", "reboot"],
        "list_packages": ["adb", "shell", "pm", "list", "packages"],
        "clear_data": ["adb", "shell", "pm", "clear", arg],
        "force_stop": ["adb", "shell", "am", "force-stop", arg],
        "list_storage": ["adb", "shell", "ls", "-la", "/sdcard/"],
        "dump_storage_tree": ["adb", "shell", "ls", "-R", "/sdcard/"],
        "storage_metrics": ["adb", "shell", "df", "-h"]
    }
    
    if action not in commands: return "Invalid Execution Target Vector"
    
    # Assign higher timeout for recursive storage tree dump module
    timeout_threshold = 300 if action == "dump_storage_tree" else 12
    return execute(commands[action], timeout_seconds=timeout_threshold)

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=True, threaded=True)


