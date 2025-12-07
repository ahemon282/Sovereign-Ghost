import time
import asyncio
import secrets
import os
import binascii
from typing import List
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# !!! PASTE YOUR KEY BELOW !!!
GEMINI_API_KEY = "AIzaSyCI945GvitflUOjgHsyqpufFdI1ig6gWho" 

# Setup Gemini (Updated to your available model)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

# --- 2. CRYPTO CLASS ---
class Shamir:
    _PRIME = 2**521 - 1
    @classmethod
    def _eval_at(cls, poly, x, prime):
        accum = 0
        for coeff in reversed(poly):
            accum = (accum * x + coeff) % prime
        return accum
    @classmethod
    def split(cls, secret_int, n, k):
        if secret_int >= cls._PRIME: raise ValueError("Secret too large")
        coef = [secret_int] + [secrets.randbelow(cls._PRIME) for _ in range(k - 1)]
        shares = []
        for i in range(1, n + 1):
            x = i
            y = cls._eval_at(coef, x, cls._PRIME)
            shares.append((x, y))
        return shares

# --- 3. SERVER STATE ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

class GameState:
    balance = 1000000.00
    is_active = False
    is_dead = False
    logs = [] 
    log_id_counter = 0

state = GameState()

def add_log(text, type):
    state.log_id_counter += 1
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{type.upper()}] {text}")
    state.logs.append({"id": state.log_id_counter, "time": timestamp, "msg": text, "type": type})
    if len(state.logs) > 50: state.logs.pop(0)

# --- 4. THE AI BRAIN (REAL + FALLBACK) ---

FALLBACK_REASONS = [
    "Detected 4.2% spread on QUBIC/USDT via Mayan Swap.",
    "RSI divergence detected on 1m chart (32.4). Executing.",
    "MEV protection enabled. Front-running blocked. Swapping.",
    "Liquidity crunch on sell-side. Slippage < 0.1%. Executing."
]

async def get_gemini_reason(action):
    """Calls Gemini 2.0 Flash for live market analysis."""
    try:
        if action == "buy":
            prompt = "You are a high-frequency crypto bot. Generate a 1-sentence ultra-technical reason why you just executed a profitable arbitrage trade. Use jargon like 'Slippage', 'Liquidity', 'Order Book', 'Delta'. Max 10 words. No intro."
        else:
            prompt = "You are a crypto bot scanning the network. Generate a 1-sentence technical status update. Use jargon like 'Latency', 'Gas', 'Mempool', 'ZK-Proof'. Max 8 words."

        # Run in a separate thread
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return secrets.choice(FALLBACK_REASONS)

# --- 5. TRADING ENGINE ---
async def trading_loop():
    print("--- GEMINI 2.0 FLASH TRADING LOOP STARTED ---")
    while state.is_active:
        # 1.5s tick (Gives AI time to reply)
        await asyncio.sleep(1.5) 
        
        if state.is_dead or not state.is_active: break

        # 40% chance to trade
        if secrets.randbelow(100) < 40:
            # CALL REAL AI
            reason = await get_gemini_reason("buy")
            
            profit = 4200
            state.balance += profit
            add_log(f"EXECUTED: {reason}", "success")
            
            if secrets.randbelow(100) < 30:
                compound = 12400
                state.balance += compound
                add_log(f"COMPOUNDING: Reinvested yield into Pool #4", "profit")
        
        else:
            if secrets.randbelow(100) < 40:
                # CALL REAL AI FOR SCAN
                reason = await get_gemini_reason("scan")
                add_log(reason, "info")
            elif secrets.randbelow(100) < 20:
                add_log("⚠️ Spread narrowing (0.05%). Holding position.", "danger")
            else:
                add_log("Scanning liquidity pools...", "info")

# --- 6. API ENDPOINTS ---

@app.get("/status")
def get_status():
    return {
        "balance": state.balance,
        "active": state.is_active,
        "dead": state.is_dead,
        "logs": state.logs[-20:]
    }

@app.post("/initialize")
async def start_protocol(background_tasks: BackgroundTasks):
    if state.is_active: return {"status": "already_running"}
    if state.is_dead: return {"status": "error", "msg": "System destroyed."}
    
    print("[*] Generating Keys...")
    seed_bytes = os.urandom(32)
    seed_int = int.from_bytes(seed_bytes, byteorder='big')
    shards = Shamir.split(seed_int, 5, 3)
    
    state.is_active = True
    add_log(f"PROTOCOL INITIALIZED. {len(shards)} SHARDS GENERATED.", "success")
    background_tasks.add_task(trading_loop)
    return {"status": "started"}

@app.post("/kill")
def kill_switch():
    state.is_active = False
    state.is_dead = True
    final_balance = state.balance
    
    timestamp = time.strftime("%H:%M:%S")
    state.log_id_counter += 1
    state.logs.append({
        "id": state.log_id_counter,
        "time": timestamp,
        "msg": "KILL SWITCH TRIGGERED. MEMORY WIPED.",
        "type": "danger"
    })
    print(f"\n[!!!] KILL SWITCH RECEIVED. FINAL BALANCE: {final_balance}\n")
    return {"status": "terminated", "final_balance": final_balance}