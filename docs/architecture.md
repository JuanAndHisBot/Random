# Encrypted Kanban — Architecture

## Design Decisions

| Concern | Decision |
|---|---|
| Frontend | Next.js (React) |
| Backend | Fastify + PostgreSQL |
| Crypto | OpenPGP.js |
| Real-time | WebSockets (encrypted payloads) |
| Auth | Challenge-response (sign with privkey) |
| Email storage | HMAC(email, SERVER_PEPPER) — never stored plaintext |
| Account recovery | Admin generates new invite link manually |
| Encryption model | Per-card DEK encrypted to each member's pubkey |
| Membership privacy | Server sees pubkey fingerprints only, not real identities |
| GitHub integration | Public repos, client-side fetch, no token required |
| GitHub caching | localStorage + ETags (304s cost zero rate-limit tokens) |
| Dates | Inside encrypted payload — server never sees schedule |
| Markdown | Stored in encrypted payload, rendered client-side |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser (Next.js)                                                  │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │  Crypto     │  │  Views       │  │  GitHub Integration      │   │
│  │  Layer      │  │              │  │                          │   │
│  │  OpenPGP.js │  │  ┌─────────┐ │  │  parse URL               │   │
│  │             │  │  │ Board   │ │  │  → derive API endpoint   │   │
│  │  keygen     │  │  │ Kanban  │ │  │  → check localStorage    │   │
│  │  encrypt    │  │  └─────────┘ │  │    ETag cache            │   │
│  │  decrypt    │  │  ┌─────────┐ │  │  → fetch api.github.com  │   │
│  │  sign       │  │  │Calendar │ │  │    (no token, public)    │   │
│  │  verify     │  │  └─────────┘ │  │  → store ETag + data     │   │
│  └──────┬──────┘  │  ┌─────────┐ │  └──────────┬───────────────┘   │
│         │         │  │Timeline │ │             │                    │
│         │         │  └─────────┘ │             │ direct fetch       │
│         │         │  ┌─────────┐ │             ▼                    │
│         │         │  │  List   │ │    api.github.com (public)       │
│         │         │  └─────────┘ │                                  │
│         │         └──────────────┘                                  │
│         │                                                           │
│  ┌──────▼──────────────────────────┐                               │
│  │  WebSocket Client               │                               │
│  │  receives encrypted events      │                               │
│  │  decrypts with card DEK         │                               │
│  └──────────────┬──────────────────┘                               │
└─────────────────│───────────────────────────────────────────────────┘
                  │ HTTPS (encrypted blobs only)
                  │ WSS  (encrypted events)
┌─────────────────▼───────────────────────────────────────────────────┐
│  Fastify API                                                        │
│                                                                     │
│  /auth      challenge-response, no password on wire                 │
│  /users     HMAC lookup, serves encrypted_privkey                   │
│  /workspaces  encrypted blobs                                       │
│  /cards       encrypted blobs + structural metadata                 │
│  /invites     one-time tokens                                       │
│  ws://      broadcasts encrypted events to workspace subscribers    │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────────┐
│  PostgreSQL                                                         │
│                                                                     │
│  users         initiatives    boards                                │
│  workspaces    epics          columns                               │
│  members       cards          comments                              │
│  invites                                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

```
users
  id              HMAC(email, SERVER_PEPPER)
  pubkey          X25519 public key
  fingerprint     hash(pubkey)
  encrypted_privkey  privkey wrapped with Argon2(password)

invites
  token           random 256-bit secret
  workspace_id
  invited_by      fingerprint
  expires_at
  claimed         boolean

workspaces
  id
  ciphertext      encrypted { name }
  signed_by       fingerprint
  signature
  keys            { fingerprint → encrypted_DEK }

initiatives
  id
  workspace_id
  ciphertext      encrypted { name, description, start_date, end_date }
  signed_by
  signature
  keys            { fingerprint → encrypted_DEK }

epics
  id
  initiative_id
  workspace_id
  ciphertext      encrypted { name, description, start_date, end_date }
  signed_by
  signature
  keys            { fingerprint → encrypted_DEK }

boards
  id
  workspace_id
  ciphertext      encrypted { name }
  signed_by
  signature
  keys            { fingerprint → encrypted_DEK }

columns
  id
  board_id
  position        integer (plaintext — needed for ordering)
  ciphertext      encrypted { name }
  signed_by
  signature
  keys            { fingerprint → encrypted_DEK }

cards
  id
  workspace_id    (plaintext — needed to fetch all workspace cards)
  column_id       (plaintext — needed for board grouping)
  epic_id         (plaintext FK — reveals hierarchy structure only)
  position        integer (plaintext — needed for column ordering)
  ciphertext      encrypted {
                    title
                    description  (Markdown)
                    start_date
                    due_date
                    priority
                    assignees    [ fingerprint, ... ]
                    labels       [ string, ... ]
                    checklist    [ { text, done }, ... ]
                    github_refs  [ url, ... ]
                  }
  signed_by       fingerprint
  signature
  keys            { fingerprint → encrypted_DEK }

comments
  id
  card_id         (plaintext FK)
  ciphertext      encrypted { body (Markdown), created_at }
  signed_by       fingerprint
  signature
  keys            { fingerprint → encrypted_DEK }
```

---

## Auth Flow

```
REGISTRATION
────────────
Browser                                Server
  generate keypair ──────────────────────────────────────────────────┐
  alice_pub, alice_priv                                              │
                                                                     │
  derive wrap_key = Argon2(password)                                 │
  encrypted_priv = encrypt(alice_priv, wrap_key)                     │
                                                                     │
  POST /users ──────────────────────────────────────────────────────►│
  { email, pubkey, fingerprint, encrypted_privkey }                  │
                                                                     │  compute user_id = HMAC(email, PEPPER)
                                                                     │  store { user_id, pubkey, fingerprint, encrypted_privkey }
                                                                     │  email: discarded
  ◄── { ok } ────────────────────────────────────────────────────────┘

LOGIN
─────
Browser                                Server
  POST /auth/init ─────────────────────────────────────────────────►│
  { email }                                                          │  HMAC(email, PEPPER) → lookup
                                                                     │  return encrypted_privkey + challenge
  ◄── { encrypted_privkey, challenge } ──────────────────────────────┘
                                                                     
  decrypt privkey = decrypt(encrypted_privkey, Argon2(password))    
  signature = sign(challenge, privkey)                              
                                                                     
  POST /auth/verify ───────────────────────────────────────────────►│
  { fingerprint, signature }                                         │  verify(signature, challenge, pubkey)
                                                                     │  issue JWT
  ◄── { jwt } ───────────────────────────────────────────────────────┘

RECOVERY (admin resets a friend)
─────────────────────────────────
  Admin creates invite link → friend re-registers → new keypair
  Admin re-encrypts all workspace DEKs for new fingerprint
  Old cards: readable (encrypted under DEK, not personal key)
  Old signatures: show "key changed" warning
```

---

## Encryption Flow — Writing a Card

```
Browser (Alice)
─────────────────────────────────────────────────────────────────────
card_payload = {
  title: "Add Stripe SDK",
  description: "## Overview\n...",
  due_date: "2025-03-15",
  github_refs: ["https://github.com/org/repo/pull/142"]
}

1. generate DEK  →  random 256-bit key

2. ciphertext = AES-256-GCM(card_payload, DEK)

3. for each member fingerprint in workspace:
     enc_DEK[fp] = OpenPGP.encrypt(DEK, member_pubkey)

4. signature = OpenPGP.sign(ciphertext, alice_priv)

5. POST /cards
   {
     workspace_id: "ws_abc",    ← plaintext
     column_id: "col_todo",     ← plaintext
     epic_id: "epic_xyz",       ← plaintext
     position: 3,               ← plaintext
     ciphertext,                ← opaque
     signed_by: "alice_fp",     ← pseudonymous
     signature,                 ← opaque
     keys: {
       alice_fp: enc_DEK[alice_fp],
       bob_fp:   enc_DEK[bob_fp]
     }
   }
─────────────────────────────────────────────────────────────────────
Server stores the blob. Knows: workspace, column, position, who signed (pseudonym).
Knows nothing: title, description, dates, github links.
```

---

## Encryption Flow — Reading the Board

```
Browser (Bob)
─────────────────────────────────────────────────────────────────────
GET /workspaces/ws_abc/cards
← [ { id, column_id, position, ciphertext, signed_by, keys }, ... ]

for each card:
  1. enc_DEK = card.keys[bob_fp]
  2. DEK = OpenPGP.decrypt(enc_DEK, bob_priv)
  3. payload = AES-256-GCM-decrypt(card.ciphertext, DEK)
  4. valid = OpenPGP.verify(card.signature, card.ciphertext, pubkeys[card.signed_by])
  5. render card on board
─────────────────────────────────────────────────────────────────────
```

---

## Invite Flow

```
Alice (existing member)                Server                Bob
────────────────────────────────────────────────────────────────────
POST /invites ─────────────────────►
{ workspace_id }                       generate token
                                       store { token, ws_id,
                                               alice_fp, expires }
◄── { token } ─────────────────────
                                       
Alice shares link out-of-band: https://app/invite#<token>

                                                     Bob clicks link
                                                     POST /auth/register
                                                     { pubkey, fp, enc_priv }
                                       store user
                                       ◄── { ok }

                                                     POST /invites/claim
                                                     { token, bob_fp }
                                       validate token
                                       notify Alice ──────────────────►
Alice receives notification
fetches all workspace cards
for each card:
  DEK = decrypt(keys[alice_fp], alice_priv)
  enc_DEK_bob = encrypt(DEK, bob_pub)
  PATCH /cards/{id}/keys
  { bob_fp: enc_DEK_bob }
────────────────────────────────────────────────────────────────────
Bob can now decrypt all cards.
Server never learned Bob's email. Knows bob_fp has workspace access.
```

---

## GitHub Integration Flow

```
Card detail opened by Alice
───────────────────────────────────────────────────────────────────
1. decrypt card → payload.github_refs = ["https://github.com/org/repo/pull/142"]

2. for each ref:
   a. check localStorage["gh:org/repo/pull/142"]
      → found: { etag: "abc123", data: {...}, cachedAt: ... }

   b. fetch api.github.com/repos/org/repo/pulls/142
      header: If-None-Match: "abc123"
      → 304 Not Modified  (costs 0 rate-limit tokens)
         use cached data

      → 200 OK (if changed)
         update localStorage with new etag + data

3. render inline in card detail:
   ⬡ merged  #142  Add Stripe SDK integration
             feat/stripe → main · @alice · 2d ago
───────────────────────────────────────────────────────────────────
Board view: no GitHub calls. Only card detail triggers fetch.
Server: never involved. Never sees the PR link. Never sees the token.
```

---

## What the Server Knows vs. Does Not Know

```
KNOWS                               DOES NOT KNOW
──────────────────────────────────  ────────────────────────────────────────
workspace ws_abc exists             workspace name
fingerprint alice_fp has access     who alice_fp is (no email stored)
card_1 exists in ws_abc             card title, description, dates
card_1 is in column col_todo        any card content
card_1 was signed by alice_fp       alice_fp's real identity
bob_fp joined ws_abc                bob_fp's real identity
an invite was created               who received it
a card has an epic_id               epic name or content
card position in column             task schedule or deadlines
                                    any GitHub links
                                    any Markdown content
                                    assignees or labels
```

---

## Monorepo Structure

```
/
├── apps/
│   ├── web/                    Next.js frontend
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   └── (app)/
│   │   │       ├── workspace/[id]/
│   │   │       │   ├── board/
│   │   │       │   ├── calendar/
│   │   │       │   ├── timeline/
│   │   │       │   └── list/
│   │   │       └── invite/[token]/
│   │   └── components/
│   │       ├── card/
│   │       ├── views/
│   │       └── github/
│   │
│   └── api/                    Fastify backend
│       ├── routes/
│       │   ├── auth.ts
│       │   ├── users.ts
│       │   ├── workspaces.ts
│       │   ├── cards.ts
│       │   ├── invites.ts
│       │   └── ws.ts
│       └── db/
│           └── migrations/
│
└── packages/
    └── crypto/                 Shared crypto primitives
        ├── keys.ts             keypair gen, wrap/unwrap
        ├── cards.ts            encrypt/decrypt/sign card payloads
        ├── dek.ts              DEK generation and member key management
        └── github.ts           URL parsing, ETag cache, normalizer
```
