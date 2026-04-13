# Assignment B: HTLC Implementation Report

## What is an HTLC?

A Hashed Time-Lock Contract (HTLC) is a special Bitcoin script that enables
trustless atomic swaps between two parties — Alice and Bob.

Think of it like a safe with two keys and a timer:
- Alice holds the secret key that opens it immediately
- Bob holds a backup key that only works after the timer runs out
- Either Alice claims using her secret, or Bob gets a refund — no cheating possible

---

## How Our Implementation Works

### Task 1: The Locking Script (create_htlc_script)
This is placed on the Bitcoin output when the contract is created.
It defines two spending paths using OP_IF and OP_ELSE:

Alice's Path (OP_IF):
- Alice provides the secret preimage
- Script hashes it and checks it matches the stored secret hash
- Then verifies Alice's signature
- If both pass, Alice gets the Bitcoin

Bob's Path (OP_ELSE):
- Bob must wait for 21 minutes (1260 seconds)
- OP_CHECKSEQUENCEVERIFY enforces the time lock
- Then verifies Bob's signature
- If both pass, Bob gets his refund

### Task 2: Alice's Claiming Script (alice_claim_script)
Alice unlocks the contract by revealing:
1. The original secret preimage
2. Her digital signature
3. Her public key

The network hashes her secret and compares it to the stored hash.
If it matches and her signature is valid, she claims successfully.

### Task 3: Bob's Refund Script (bob_refund_script)
Bob unlocks the contract by providing:
1. His digital signature
2. His public key
3. Proof that 21 minutes have passed (enforced by OP_CHECKSEQUENCEVERIFY)

### Task 4: Test Scenarios

| Scenario | Expected Result |
|----------|----------------|
| Alice provides correct secret | SUCCESS |
| Alice provides wrong secret | FAILED |
| Bob refunds after 21 minutes | SUCCESS |
| Bob tries refund before 21 minutes | FAILED |

---

## Key Bitcoin Opcodes Used

| Opcode | Purpose |
|--------|---------|
| OP_IF / OP_ELSE / OP_ENDIF | Creates two spending paths |
| OP_SHA256 | Hashes the secret Alice provides |
| OP_EQUALVERIFY | Checks the hash matches |
| OP_CHECKSEQUENCEVERIFY | Enforces the time lock for Bob |
| OP_DUP + OP_HASH160 | Standard public key verification |
| OP_CHECKSIG | Verifies digital signatures |

---

## Why HTLCs Matter

HTLCs are the foundation of the Bitcoin Lightning Network.
They allow payments to be routed through multiple hops trustlessly
because each hop uses an HTLC — either everyone gets paid or nobody does.
This is the atomic property — all or nothing, no partial outcomes.