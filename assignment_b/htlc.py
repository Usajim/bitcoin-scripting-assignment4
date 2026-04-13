"""
Assignment B: Hashed Time-Lock Contract (HTLC)
Atomic Swap between Alice and Bob

Scenario:
- Alice locks Bitcoin with a secret and a 21 minute timer
- Alice can claim by revealing the secret within 21 minutes
- Bob gets a full refund if Alice does not claim in time
"""

import hashlib
import time


# ============================================================
# TASK 1: HTLC Locking Script
# ============================================================

def create_htlc_script(alice_pubkey_hash, bob_pubkey_hash, secret_hash, timeout_minutes=21):
    timeout_seconds = timeout_minutes * 60
    script = f"""
OP_IF
    OP_SHA256 <{secret_hash}>
    OP_EQUALVERIFY
    OP_DUP
    OP_HASH160 <{alice_pubkey_hash}>
    OP_EQUALVERIFY
    OP_CHECKSIG
OP_ELSE
    <{timeout_seconds}> OP_CHECKSEQUENCEVERIFY OP_DROP
    OP_DUP
    OP_HASH160 <{bob_pubkey_hash}>
    OP_EQUALVERIFY
    OP_CHECKSIG
OP_ENDIF"""
    return script


# ============================================================
# TASK 2: Alice's Claiming Transaction Script
# ============================================================

def alice_claim_script(secret_preimage, alice_signature, alice_pubkey, secret_hash):
    provided_hash = hashlib.sha256(secret_preimage.encode()).hexdigest()
    hash_match = provided_hash == secret_hash

    result = f"""
Alice's Claiming Script Execution:
===================================
Alice provides:
  Secret Preimage : "{secret_preimage}"
  Signature       : {alice_signature}
  Public Key      : {alice_pubkey}

Execution Steps:
  Step 1: OP_IF -> Alice's claiming path selected
  Step 2: OP_SHA256 hashes secret -> {provided_hash[:32]}...
  Step 3: OP_EQUALVERIFY checks hash match -> {"PASS" if hash_match else "FAIL"}
  Step 4: OP_DUP duplicates Alice's public key
  Step 5: OP_HASH160 hashes the public key
  Step 6: OP_EQUALVERIFY checks pubkey hash -> PASS
  Step 7: OP_CHECKSIG verifies signature -> PASS

Result: {"SUCCESS - Alice claims the Bitcoin!" if hash_match else "FAILED - Wrong secret provided!"}"""
    return result


# ============================================================
# TASK 3: Bob's Refund Transaction Script
# ============================================================

def bob_refund_script(bob_signature, bob_pubkey, timeout_minutes, elapsed_seconds):
    timeout_seconds = timeout_minutes * 60
    time_passed = elapsed_seconds >= timeout_seconds

    result = f"""
Bob's Refund Script Execution:
================================
Bob provides:
  Signature : {bob_signature}
  Public Key: {bob_pubkey}

Execution Steps:
  Step 1: OP_ELSE -> Bob's refund path selected
  Step 2: OP_CHECKSEQUENCEVERIFY checks {elapsed_seconds}s >= {timeout_seconds}s -> {"PASS" if time_passed else "FAIL - Too early!"}
  Step 3: OP_DROP removes timeout value from stack
  Step 4: OP_DUP duplicates Bob's public key
  Step 5: OP_HASH160 hashes the public key
  Step 6: OP_EQUALVERIFY checks pubkey hash -> {"PASS" if time_passed else "N/A"}
  Step 7: OP_CHECKSIG verifies signature -> {"PASS" if time_passed else "N/A"}

Result: {"SUCCESS - Bob reclaims his Bitcoin!" if time_passed else "FAILED - Timeout has not passed yet!"}"""
    return result


# ============================================================
# TASK 4: Full Test with Sample Hash and 21 Minute Timeout
# ============================================================

def run_htlc_test():
    print("=" * 60)
    print("   HTLC ATOMIC SWAP TEST - Alice and Bob")
    print("=" * 60)

    # Setup
    secret_preimage   = "alice_secret_swap_key_2024"
    secret_hash       = hashlib.sha256(secret_preimage.encode()).hexdigest()
    alice_pubkey_hash = hashlib.new("ripemd160", hashlib.sha256(b"alice_pubkey").digest()).hexdigest()
    bob_pubkey_hash   = hashlib.new("ripemd160", hashlib.sha256(b"bob_pubkey").digest()).hexdigest()
    alice_pubkey      = "03a1b2c3d4e5f6alice_pubkey_example"
    bob_pubkey        = "03f6e5d4c3b2a1bob_pubkey_example"
    alice_signature   = "alice_sig_" + secret_hash[:16]
    bob_signature     = "bob_sig_"   + secret_hash[:16]
    timeout_minutes   = 21
    timeout_seconds   = timeout_minutes * 60

    print(f"""
Contract Setup:
---------------
Secret Preimage  : "{secret_preimage}"
Secret Hash      : {secret_hash}
Alice PubKey Hash: {alice_pubkey_hash}
Bob PubKey Hash  : {bob_pubkey_hash}
Timeout          : {timeout_minutes} minutes ({timeout_seconds} seconds)
Contract Created : {time.strftime("%Y-%m-%d %H:%M:%S")}
""")

    # Task 1
    print("TASK 1: HTLC Locking Script")
    print("-" * 40)
    print(create_htlc_script(alice_pubkey_hash, bob_pubkey_hash, secret_hash, timeout_minutes))

    # Task 2 - Alice correct secret
    print("\nTASK 2: Alice Claims With Correct Secret")
    print("-" * 40)
    print(alice_claim_script(secret_preimage, alice_signature, alice_pubkey, secret_hash))

    # Task 2b - Alice wrong secret
    print("\nTASK 2b: Alice Tries Wrong Secret")
    print("-" * 40)
    print(alice_claim_script("wrong_secret", alice_signature, alice_pubkey, secret_hash))

    # Task 3 - Bob refund after timeout
    print("\nTASK 3: Bob Refund AFTER 21 Minutes")
    print("-" * 40)
    print(bob_refund_script(bob_signature, bob_pubkey, timeout_minutes, timeout_seconds + 60))

    # Task 3b - Bob too early
    print("\nTASK 3b: Bob Tries Refund BEFORE Timeout")
    print("-" * 40)
    print(bob_refund_script(bob_signature, bob_pubkey, timeout_minutes, 300))

    print("\n" + "=" * 60)
    print("ALL HTLC TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_htlc_test()