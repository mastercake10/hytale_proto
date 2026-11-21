# Interface and Page Packets

## ServerMessage (210)

Server chat and system messages. Player chat reaches other clients through this
packet, not as [[ChatMessage]].

```packet
bound: client
summary: Formatted server chat/system message
columns: Offset | Field Name | Field Type | Notes
0 | Null bits      | `u8` | bit0 `message`
1 | `type`         | `u8` | `ChatType`: `0` = Chat
2 | Variable block | bytes | One [FormattedMessage](#formattedmessage)
```

## FormattedMessage

Fixed block 40 bytes; offsets are `i32` relative to byte 40, `-1` when absent.
Null bit `a.b` = null-bits byte `a`, bit `b`.

| Offset | Field | Type | Null bit | Notes |
|-------:|-------|------|----------|-------|
| 0  | Null bits 1      | `u8`   |        | bit0-4 bold/italic/monospace/underlined/strikethrough, bit5 `raw_text`, bit6 `message_id`, bit7 `children` |
| 1  | Null bits 2      | `u8`   |        | bit0 `params`, bit1 `message_params`, bit2 `color`, bit3 `link`, bit4 `image` |
| 2  | `bold`           | `bool` | 1.0 | |
| 3  | `italic`         | `bool` | 1.1 | |
| 4  | `monospace`      | `bool` | 1.2 | |
| 5  | `underlined`     | `bool` | 1.3 | |
| 6  | `strikethrough`  | `bool` | 1.4 | |
| 7  | `markup_enabled` | `bool` |     | Always present; enables markup parsing in the text |
| 8  | `raw_text`       | offset | 1.5 | VarString |
| 12 | `message_id`     | offset | 1.6 | VarString, translation id |
| 16 | `children`       | offset | 1.7 | `VarInt` count + `FormattedMessage[]` |
| 20 | `params`         | offset | 2.0 | `VarInt` count + (VarString key, `ParamValue` with type id) |
| 24 | `message_params` | offset | 2.1 | `VarInt` count + (VarString key, `FormattedMessage`) |
| 28 | `color`          | offset | 2.2 | VarString, hex like `#ff5555` |
| 32 | `link`           | offset | 2.3 | VarString |
| 36 | `image`          | offset | 2.4 | `FormattedMessageImage` |

## ChatMessage (211)

Player chat or slash command.

```packet
bound: server
summary: Player chat or slash-command text
columns: Offset | Field Name | Field Type | Notes
0 | Null bits | `u8`        | bit0 `message`
1 | `message` | `VarString` | Max 255 characters; present only when bit0 is set
```

## Notification (212)

Fixed block 2 bytes, offset table 20 bytes, variable block at byte 22.

```packet
bound: client
summary: Server-to-client notification
columns: Offset | Field Name | Field Type | Notes
0  | Null bits                  | `u8`  | bit0 `message`, bit1 `secondary_message`, bit2 `icon`, bit3 `item`, bit4 `tag`
1  | `style`                    | `u8`  | `0` Default, `1` Danger, `2` Warning, `3` Success
2  | `message`                  | `i32` offset | [FormattedMessage](#formattedmessage)
6  | `secondary_message`        | `i32` offset | [FormattedMessage](#formattedmessage)
10 | `icon`                     | `i32` offset | VarString
14 | `item`                     | `i32` offset | [ItemWithAllMetadata](07-inventory-slots.md#itemwithallmetadata)
18 | `tag`                      | `i32` offset | VarString
22 | Variable block             | bytes | Offsets relative to byte 22, `-1` absent
```

## SetPage (216)

Fixed 2 bytes.

```packet
bound: client
summary: Fixed-payload page selection
`page`                          | `u8`   | `Page`, see below
`can_close_through_interaction` | `bool`
```

`Page`: 0 None, 1 Bench, 2 Inventory, 3 ToolsSettings, 4 Map, 5 MachinimaEditor,
6 ContentCreation, 7 Custom, 8 Serverside, 9 Chapters, 10 ChapterRewards,
11 PortalSummon, 12 PortalActive, 13 PortalError.

## CustomPage (218)

Server-authored UI page. zstd-compressed. Variable block at byte 15.

```packet
bound: client
summary: Server-authored custom UI page
columns: Offset | Field Name | Field Type | Notes
0  | Null bits       | `u8` | bit0 `key`, bit1 `commands`, bit2 `event_bindings`
1  | Flags           | `u8` | bit0 `is_initial`, bit1 `clear`
2  | `lifetime`      | `u8` | `0` CantClose, `1` CanDismiss, `2` CanDismissOrCloseThroughInteraction
3  | `key`           | `i32` offset | VarString, page identifier (e.g. a `RespawnPage` variant)
7  | `commands`      | `i32` offset | `VarInt` count + `CustomUICommand[]`
11 | `event_bindings`| `i32` offset | `VarInt` count + `CustomUIEventBinding[]`
15 | Variable block  | bytes | Offsets relative to byte 15, `-1` absent
```

## CustomPageEvent (219)

Client reply to a [[CustomPage]].

```packet
bound: server
summary: Acknowledge/data/dismiss event
columns: Offset | Field Name | Field Type | Notes
0 | Null bits | `u8`        | bit0 `data`
1 | `type`    | `u8`        | `0` Acknowledge, `1` Data, `2` Dismiss
2 | `data`    | `VarString` | JSON; present only when bit0 is set
```

## DismissServersidePage (527)

Client request to close the active server-side page.

```packet
bound: server
summary: Close the current server page
columns: Offset | Field Name | Field Type | Notes
0 | `id` | `VarString` | Page id, max 128 characters
```

The server ignores it when no server-side page is open, the id does not match,
or the page lifetime is `CantClose`.

## Page state

At most one server page is active. A new [[SetPage]] / [[CustomPage]] replaces
it.
