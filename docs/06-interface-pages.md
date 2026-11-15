# Interface and Page Packets

## ServerMessage (210)

Server chat and system messages. Server chat is delivered through this packet,
not by echoing `ChatMessage`.

```packet
bound: client
summary: Formatted server chat/system message
partial: yes
Message | FormattedMessage | See below
```

`FormattedMessage`, known fields:

| Field Name     | Field Type | Notes    |
|----------------|------------|----------|
| Raw text       | ?          | Optional |
| Translation id | ?          | Optional |
| Parameters     | ?          | Optional |
| Color          | ?          | Optional |
| Link           | ?          | Optional |
| Children       | ?          | Optional |

## ChatMessage (211)

Player chat or slash-command text. This packet is client-to-server only.

```packet
bound: server
summary: Player chat or slash-command text
Flags | `u8`
Text  | `VarString` | Chat or slash-command text
```

## Notification (212)

Sent by the server. The fixed block is 2 bytes and the variable block starts at
byte 22.

```packet
bound: client
summary: Server-to-client notification
columns: Offset | Field Name | Field Type | Notes
0  | Null bits                  | `u8`  | bit0 message, bit1 secondary message, bit2 icon, bit3 item, bit4 tag
1  | `style`                    | `u8`  | See table below
2  | `message_offset`           | `i32` | Relative to byte 22; `-1` when absent
6  | `secondary_message_offset` | `i32` | Relative to byte 22; `-1` when absent
10 | `icon_offset`              | `i32` | Relative to byte 22; `-1` when absent
14 | `item_offset`              | `i32` | Relative to byte 22; `-1` when absent
18 | `tag_offset`               | `i32` | Relative to byte 22; `-1` when absent
22 | Variable block             | bytes | Variable fields
```

Variable fields: `message` and `secondary_message` are `FormattedMessage`
values, `icon` and `tag` are `VarString` values, and `item` is an
`ItemWithAllMetadata` structure.

| Value | Style   |
|------:|---------|
|     0 | Default |
|     1 | Danger  |
|     2 | Warning |
|     3 | Success |

## SetPage (216)

Fixed two-byte layout:

```packet
bound: client
summary: Fixed-payload page selection
`page`                          | `u8`   | `Page.None` is `0`
`can_close_through_interaction` | `bool`
```

## CustomPage (218)

A server-authored custom UI page.

```packet
bound: client
summary: Server-authored custom UI page
partial: yes
Page key | ? | Identifies the page class, for example a `RespawnPage` variant
Payload  | ? | Compressed
```

## CustomPageEvent (219)

```packet
bound: server
summary: Acknowledge/data/dismiss event
partial: yes
Event type | ? | See table below
Data       | ? | Optional
```

| Value | Event type  |
|------:|-------------|
|     0 | Acknowledge |
|     1 | Data        |
|     2 | Dismiss     |

## DismissServersidePage (527)

Closes the current server page. Layout not documented yet.

```packet
bound: client
summary: Close the current server page
```

## Page state

The client can have at most one server page active. A page can be replaced by
another `SetPage`/`CustomPage`, and some pages require a specific event before
the server considers them complete.
