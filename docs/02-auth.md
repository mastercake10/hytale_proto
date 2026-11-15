# Authentication Flow

## Packet sequence

Observed connection setup:

```text
C→S Connect (0)
C→S AuthToken (12)
S→C AuthGrant (11)
S→C ServerAuthToken (13)
C→S PasswordResponse (15)      only if challenged
S→C PasswordAccepted (16)      or PasswordRejected (17)
S→C ConnectAccept (14)
```

The exact order of `AuthGrant` and `ServerAuthToken` has not been verified
against a packet capture.

Auth packets use a fixed block of scalar fields followed by a variable block.
Offsets in the fixed block point into the variable block; `-1` marks an absent
optional field.

## Connect (0)

First packet of a connection. The fixed block is 30 bytes; the variable block
starts at byte 46.

```packet
bound: server
summary: Client build/version and identity token
columns: Offset | Field Name | Field Type | Notes
0  | Null bits                | `u8`            | bit0 identity token, bit1 referral data, bit2 referral source
1  | `protocol_crc`           | `i32`
5  | `protocol_build_number`  | `i32`
9  | `client_version`         | fixed ASCII[20] | Null-padded
29 | `client_type`            | `u8`            | `ClientType` enum
30 | `identity_token_offset`  | `i32`           | Relative to byte 46; `-1` when absent
34 | `language_offset`        | `i32`           | Relative to byte 46; always present
38 | `referral_data_offset`   | `i32`           | Relative to byte 46; `-1` when absent
42 | `referral_source_offset` | `i32`           | Relative to byte 46; `-1` when absent
46 | Variable block           | bytes           | Strings and byte arrays
```

The identity token and language are `VarString` values. Referral data is a
`VarInt` byte length followed by that many bytes. Referral source is a
`HostAddress` structure.

## AuthToken (12)

Sent by the client. The fixed block is 1 byte; the variable block starts at
byte 9.

```packet
bound: server
summary: Client access token and join grant
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                           | `u8`  | bit0 access token, bit1 server authorization grant
1 | `access_token_offset`               | `i32` | Relative to byte 9; `-1` when absent
5 | `server_authorization_grant_offset` | `i32` | Relative to byte 9; `-1` when absent
9 | Variable block                      | bytes | `VarString` values
```

## AuthGrant (11)

Sent by the server. The fixed block is 1 byte; the variable block starts at
byte 9.

```packet
bound: client
summary: Server authorization grant and identity token
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                      | `u8`  | bit0 authorization grant, bit1 server identity token
1 | `authorization_grant_offset`   | `i32` | Relative to byte 9; `-1` when absent
5 | `server_identity_token_offset` | `i32` | Relative to byte 9; `-1` when absent
9 | Variable block                 | bytes | `VarString` values
```

## ServerAuthToken (13)

Sent by the server. The fixed block is 1 byte; the variable block starts at
byte 9.

```packet
bound: client
summary: Server access token and password challenge
columns: Offset | Field Name | Field Type | Notes
0 | Null bits                    | `u8`  | bit0 server access token, bit1 password challenge
1 | `server_access_token_offset` | `i32` | Relative to byte 9; `-1` when absent
5 | `password_challenge_offset`  | `i32` | Relative to byte 9; `-1` when absent
9 | Variable block               | bytes | Access token is a `VarString`; challenge is a length-prefixed byte array
```

The password challenge is limited to 64 bytes.

## PasswordResponse (15)

Sent only if `ServerAuthToken` contained a password challenge. The client
proves with it that it can answer the challenge.

```packet
bound: server
summary: Password challenge response
columns: Offset | Field Name | Field Type | Notes
0 | Null bits | `u8`  | bit0 hash present
1 | `hash`    | bytes | `VarInt` length followed by up to 64 bytes
```

## PasswordAccepted (16)

Empty packet. The fixed block and variable block are both zero bytes.

```packet
bound: client
summary: Password accepted
fields: none
```

## PasswordRejected (17)

Sent by the server when the challenge answer was not accepted.

```packet
bound: client
summary: Password rejected
columns: Offset | Field Name | Field Type | Notes
0 | Null bits            | `u8`  | bit0 new challenge present
1 | `attempts_remaining` | `i32`
5 | `new_challenge`      | bytes | Optional; `VarInt` length plus up to 64 bytes
```

## Other packets

```packets
14 | ConnectAccept | client | Authentication accepted. A reliable marker that setup completed successfully
```

## Consistency rules

- The identity token, access token and grants must be consistent with each
  other. A mismatch is not recoverable by the server; the connection is
  rejected during setup.
- Authentication uses mutual TLS. The access token contains a `cnf.x5t#S256`
  claim: the base64url-encoded SHA-256 digest of the client certificate. The
  server compares this claim with the certificate presented during the
  connection and rejects the token when they differ.

No credentials or token contents belong in these notes.
