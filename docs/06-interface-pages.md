# Interface and Page Packets

## ServerMessage (210)

Server chat and system messages. Server chat is delivered through this packet,
not by echoing `ChatMessage`.

```packet
bound: client
summary: Formatted server chat/system message
columns: Offset | Field Name | Field Type | Null bit | Notes
0 | Null bits | `u8` | | bit0 `message`
1 | `type` | `u8` | | `ChatType`; `0` = Chat
2 | Variable block | bytes | | One `FormattedMessage`
```

## FormattedMessage

Fixed block: 40 bytes. Variable block starts at byte 40; every string/array
offset is an `i32` relative to that variable block, `-1` when absent.

```text
Offset | Field Name | Field Type | Null bit | Notes
0  | Null bits         | `u8`  |        | bit0 bold, bit1 italic, bit2 monospace, bit3 underlined, bit4 strikethrough, bit5 `raw_text`, bit6 `message_id`, bit7 `children`
1  | Null bits 2       | `u8`  |        | bit0 `params`, bit1 `message_params`, bit2 `color`, bit3 `link`, bit4 `image`
2  | `bold`            | `bool`| byte0 bit0 |
3  | `italic`          | `bool`| byte0 bit1 |
4  | `monospace`       | `bool`| byte0 bit2 |
5  | `underlined`      | `bool`| byte0 bit3 |
6  | `strikethrough`   | `bool`| byte0 bit4 |
7  | `markup_enabled`  | `bool`| | Always present
8  | `raw_text` offset | `i32` | byte0 bit5 | VarString
12 | `message_id` offset | `i32` | byte0 bit6 | VarString (translation id)
16 | `children` offset | `i32` | byte0 bit7 | VarInt count + `FormattedMessage[]`
20 | `params` offset   | `i32` | byte1 bit0 | VarInt count + key/value pairs (`ParamValue` carries a type id)
24 | `message_params` offset | `i32` | byte1 bit1 | VarInt count + key + `FormattedMessage`
28 | `color` offset    | `i32` | byte1 bit2 | VarString, hex color like `#ff5555`
32 | `link` offset     | `i32` | byte1 bit3 | VarString
36 | `image` offset    | `i32` | byte1 bit4 | `FormattedMessageImage`
40 | Variable block    | bytes | |
```

`color` is a hex string (for example `#ff5555`); `markup_enabled` controls
markup parsing in the text and is independent of the color field.

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
columns: Offset | Field Name | Field Type | Notes
0 | Null bits  | `u8`        | bit0 `data` present
1 | Event type | `u8`        | See table below
2 | Data       | `VarString` | Only when bit0 is set; JSON text
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
