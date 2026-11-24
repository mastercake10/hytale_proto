# Authentication Flow

All auth packets use the [nullable field layout](01-framing.md#nullable-fields):
null bits, fixed block, `i32` offsets (`-1` = absent), variable block.

## Packet sequence

Authenticated mode (identity token present):

```text
C→S Connect (0)
S→C AuthGrant (11)
C→S AuthToken (12)
S→C ServerAuthToken (13)       password challenge included if required
C→S PasswordResponse (15)      only if challenged
S→C PasswordAccepted (16)      or PasswordRejected (17)
```

Insecure mode (development/offline servers, no identity token):

```text
C→S Connect (0)
S→C RequestInsecurePlayerOptions (364)
C→S InsecurePlayerOptions (363)  uuid, username, skin
S→C ConnectAccept (14)           password challenge included if required
    then password exchange as above
```

Observed client behaviour (release client 0.7.7, which sends an identity
token): on `RequestInsecurePlayerOptions` it still answers with
`InsecurePlayerOptions`, then aborts the connection with "Server requires
development mode which is not supported in this build". Release clients can
only join servers that use the authenticated flow.

After the password step (or immediately, without a challenge) the server
moves to world setup. A packet that does not fit the current step is a
disconnect.

## Connect (0)

First packet. Fixed block 30 bytes; variable block starts at byte 46.

```packet
bound: server
summary: Client build/version and identity token
columns: Offset | Field Name | Field Type | Notes
0  | Null bits                | `u8`            | bit0 identity token, bit1 referral data, bit2 referral source
1  | `protocol_crc`           | `i32`
5  | `protocol_build_number`  | `i32`
9  | `client_version`         | fixed ASCII[20] | Null-padded
29 | `client_type`            | `u8`            | `ClientType`: 0 Game, 1 Editor
30 | `identity_token_offset`  | `i32`           | `VarString`
34 | `language_offset`        | `i32`           | `VarString`; always present
38 | `referral_data_offset`   | `i32`           | `VarInt` length + bytes, max 4096
42 | `referral_source_offset` | `i32`           | `HostAddress`: `i16` port, then `VarString` host
46 | Variable block           | bytes
```

Server checks, in order:

1. `protocol_crc` must equal the server's protocol CRC. Otherwise the
   connection is closed with application error `ClientOutdated` (5) if
   `protocol_build_number` is lower than the server's build, else
   `ServerOutdated` (6).
2. Server must be booted and not shutting down.
3. Referral data: at most 4096 bytes; requires a referral source with a
   non-empty host.
4. Authenticated mode requires a non-empty identity token.
5. `client_type` Editor is rejected unless the server supports editors.

QUIC application error codes: 0 NoError, 1 RateLimited, 2 AuthFailed,
3 InvalidVersion, 4 Timeout, 5 ClientOutdated, 6 ServerOutdated, 7 Crash.

## AuthToken (12)

Fixed block 1 byte; variable block starts at byte 9.

```packet
bound: server
summary: Client access token and join grant
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                           | `u8`  | bit0 access token, bit1 server authorization grant
1 | `access_token_offset`               | `i32` | `VarString`
5 | `server_authorization_grant_offset` | `i32` | `VarString`
9 | Variable block                      | bytes
```

Accepted only once, and only after [[AuthGrant]] was sent.

## AuthGrant (11)

Fixed block 1 byte; variable block starts at byte 9.

```packet
bound: client
summary: Server authorization grant and identity token
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                      | `u8`  | bit0 authorization grant, bit1 server identity token
1 | `authorization_grant_offset`   | `i32` | `VarString`
5 | `server_identity_token_offset` | `i32` | `VarString`
9 | Variable block                 | bytes
```

## ServerAuthToken (13)

Fixed block 1 byte; variable block starts at byte 9.

```packet
bound: client
summary: Server access token and password challenge
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                    | `u8`  | bit0 server access token, bit1 password challenge
1 | `server_access_token_offset` | `i32` | `VarString`
5 | `password_challenge_offset`  | `i32` | `VarInt` length + bytes, max 64
9 | Variable block               | bytes
```

## ConnectAccept (14)

Insecure mode only. Single variable field, so no offset table.

```packet
bound: client
summary: Insecure-mode accept, optional password challenge
columns: Offset | Field Name | Field Type | Notes
0 | Null bits            | `u8`  | bit0 password challenge
1 | `password_challenge` | bytes | `VarInt` length + bytes, max 64
```

## PasswordResponse (15)

```packet
bound: server
summary: Password challenge response
columns: Offset | Field Name | Field Type | Notes
0 | Null bits | `u8`  | bit0 hash present
1 | `hash`    | bytes | `VarInt` length + bytes, max 64
```

`hash = SHA-256(challenge || UTF-8(password))`. A missing or empty hash is a
disconnect.

## PasswordAccepted (16)

Empty body.

```packet
bound: client
summary: Password accepted
fields: none
```

## PasswordRejected (17)

```packet
bound: client
summary: Password rejected
columns: Offset | Field Name | Field Type | Notes
0 | Null bits            | `u8`  | bit0 new challenge present
1 | `attempts_remaining` | `i32`
5 | `new_challenge`      | bytes | `VarInt` length + bytes, max 64
```

The response must be computed against `new_challenge`.

## Password rules

- A challenge is 32 random bytes.
- No challenge when the server has no password, or for the world owner on a
  singleplayer server.
- 3 attempts. Each wrong hash decrements `attempts_remaining` and issues a new
  challenge; at 0 the client is disconnected.

## Token validation

- Identity token (from [[Connect]]): valid JWT with non-empty subject and
  username, and scope `hytale:client` (or `hytale:editor` for Editor clients).
- Access token (from [[AuthToken]]): valid JWT bound to the client TLS
  certificate. Its `cnf.x5t#S256` claim (base64url SHA-256 of the client
  certificate) must match the certificate presented on the connection.
- Access token subject and username must equal those of the identity token.
- `server_authorization_grant` is required (mutual auth); without it the
  client is disconnected.

## Timeouts

Per-stage limits; the client is disconnected when a stage does not complete in
time. Defaults (multiplayer / singleplayer), configurable:

| Stage | Multiplayer | Singleplayer |
|-------|-------------|--------------|
| Initial (until `Connect` / insecure options) | 20 s | 30 s |
| Auth (identity token check)   | 30 s | 60 s |
| Auth grant (until `AuthGrant` sent) | 30 s | 60 s |
| Auth token (until `AuthToken` received) | 30 s | 60 s |
| Server token exchange         | 15 s | 30 s |
| Password                      | 45 s | 60 s |
