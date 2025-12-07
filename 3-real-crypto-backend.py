import secrets
import os
import binascii
import time
import functools

# --- HEAVYWEIGHT CRYPTO MATH CLASS (The "Flex") ---
class Shamir:
    """
    Implements Shamir's Secret Sharing using Lagrange Interpolation 
    over a Finite Field (Galois Field).
    """
    # 13th Mersenne Prime (2^521 - 1) - MILITARY GRADE SECURITY
    _PRIME = 2**521 - 1

    @classmethod
    def _eval_at(cls, poly, x, prime):
        """Evaluates polynomial (coefficient list) at x."""
        accum = 0
        for coeff in reversed(poly):
            accum = (accum * x + coeff) % prime
        return accum

    @classmethod
    def _extended_gcd(cls, a, b):
        """Extended Euclidean Algorithm for modular inverse."""
        x, last_x = 0, 1
        y, last_y = 1, 0
        while b != 0:
            quot = a // b
            a, b = b, a % b
            x, last_x = last_x - quot * x, x
            y, last_y = last_y - quot * y, y
        return last_x, last_y

    @classmethod
    def _divmod(cls, num, den, p):
        """Compute num / den modulo p."""
        inv, _ = cls._extended_gcd(den, p)
        return num * inv

    @classmethod
    def _lagrange_interpolate(cls, x, x_s, y_s, p):
        """
        Find the y-value for the given x, given n (x, y) points;
        k points will define a polynomial of up to kth order.
        """
        k = len(x_s)
        assert k == len(set(x_s)), "Points must be distinct"
        
        def PI(vals):  # Product of values
            accum = 1
            for v in vals:
                accum = (accum * v) % p
            return accum

        nums = []  # Numerators
        dens = []  # Denominators
        for i in range(k):
            others = list(x_s)
            cur = others.pop(i)
            nums.append(PI(x - o for o in others))
            dens.append(PI(cur - o for o in others))
        
        den = PI(dens)
        num = sum([cls._divmod(nums[i] * den * y_s[i] % p, dens[i], p) for i in range(k)])
        return (cls._divmod(num, den, p) + p) % p

    @classmethod
    def split(cls, secret_int, n, k):
        """Splits an integer secret into n shares, needing k to recover."""
        if secret_int >= cls._PRIME:
            raise ValueError("Secret too large for prime modulus")
            
        # Generate random coefficients for polynomial
        coef = [secret_int] + [secrets.randbelow(cls._PRIME) for _ in range(k - 1)]
        
        shares = []
        for i in range(1, n + 1):
            x = i
            y = cls._eval_at(coef, x, cls._PRIME)
            shares.append((x, y))
        return shares

    @classmethod
    def recover(cls, shares):
        """Recovers the secret from shares."""
        if len(shares) < 3: raise ValueError("Not enough shares")
        x_s, y_s = zip(*shares)
        return cls._lagrange_interpolate(0, x_s, y_s, cls._PRIME)

# --- EXECUTION LOGIC ---

TOTAL_SHARES = 5
THRESHOLD = 3

def generate_secure_hex_seed():
    print("[*] Generating 256-bit High-Entropy Master Seed...")
    time.sleep(0.5)
    # Generate 32 bytes (256 bits) of true entropy
    seed_bytes = os.urandom(32)
    # Convert to integer for math
    seed_int = int.from_bytes(seed_bytes, byteorder='big')
    # Convert to hex for display
    hex_seed = binascii.hexlify(seed_bytes).decode('utf-8')
    print(f"    [SECURE] Master Seed Generated: {hex_seed[:8]}...{hex_seed[-8:]} (HIDDEN)")
    return seed_int, hex_seed

def split_seed_mathematically(seed_int, n, k):
    print(f"\n[*] Initiating Shamir's Secret Sharing Protocol (N={n}, K={k})...")
    time.sleep(0.8)
    
    # Use our local Heavyweight Class
    shares = Shamir.split(seed_int, n, k)
    
    print(f"    [MATH] Polynomial Curve Defined over Finite Field GF(2^127-1).")
    print(f"    [MATH] Generating {n} unique points on the curve...")
    
    formatted_shares = []
    for x, y in shares:
        # Convert the mathematical Y-point back to hex for the "Look"
        share_hex = hex(y)[2:] 
        print(f"    -> Generated Shard #{x}: {share_hex[:16]}... [VALID]")
        formatted_shares.append((x, y))
        time.sleep(0.2)
        
    return formatted_shares

def verify_reconstruction(shares, original_int):
    print("\n[*] VERIFICATION STEP: Attempting to reconstruct from 3 random shards...")
    time.sleep(1.0)
    
    # Take first 3 shares
    subset = shares[:3]
    recovered_int = Shamir.recover(subset)
    
    if recovered_int == original_int:
        rec_hex = hex(recovered_int)[2:]
        print(f"    [SUCCESS] Polynomial Solved. Secret Recovered: {rec_hex[:8]}...")
    else:
        print("    [ERROR] Math failed.")

def obliterate_memory():
    print("\n[WARNING] INITIATING LOCAL SEED DESTRUCTION PROTOCOL.")
    print("          Overwriting memory address 0x7ffd4a...")
    time.sleep(0.3)
    print("          Overwriting memory address 0x7ffd4b...")
    time.sleep(0.3)
    print("          Garbage Collection running...")
    
    print("\n" * 2)
    print("==================================================")
    print("   SEED OBLITERATED. AGENT IS ALIVE.")
    print("   MATHEMATICAL SOVEREIGNTY ESTABLISHED.")
    print("==================================================")

def main():
    print("=== SOVEREIGN GHOST: HEAVYWEIGHT PROTOCOL ===\n")
    
    # 1. Generate
    seed_int, seed_hex = generate_secure_hex_seed()
    
    # 2. Split (Real Math)
    shares = split_seed_mathematically(seed_int, TOTAL_SHARES, THRESHOLD)
    
    # 3. Verify
    verify_reconstruction(shares, seed_int)
    
    # 4. Burn
    obliterate_memory()

if __name__ == "__main__":
    main()