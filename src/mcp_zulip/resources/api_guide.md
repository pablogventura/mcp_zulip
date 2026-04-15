# Zulip REST API — MCP guide

Read this resource **before** calling `zulip_call_endpoint` so paths and methods match the official Python binding (`zulip.Client.call_endpoint`).

## Canonical documentation

- [REST API overview](https://zulip.com/api/rest)
- [Construct a narrow](https://zulip.com/api/construct-narrow) (for `get_messages`)
- [Send a message](https://zulip.com/api/send-message)
- [Get messages](https://zulip.com/api/get-messages)
- [Update message](https://zulip.com/api/update-message)
- [Delete message](https://zulip.com/api/delete-message)
- [Add reaction](https://zulip.com/api/add-reaction)
- [Subscriptions](https://zulip.com/api/subscribe)
- [Get stream ID](https://zulip.com/api/get-stream-id)

## Important: what `url` means here

The `url` argument to `zulip_call_endpoint` is the **relative API path** used by the official Python client (same string as in Zulip’s REST docs after `/api/v1/`), **not** the full browser URL of your organization.

Example: use `messages`, not `https://chat.zulip.org/api/v1/messages`.

## Curated `call_endpoint` cheat sheet

| HTTP method | `url` (path) | Typical use |
|-------------|--------------|-------------|
| GET | `messages` | Fetch with query params (`anchor`, `num_before`, `num_after`, `narrow`, …) |
| POST | `messages` | Send message (`type`, `to`, `content`, `subject` for streams) |
| PATCH | `messages/{message_id}` | Edit message (also exposed as `update_message` in Python) |
| DELETE | `messages/{message_id}` | Delete message |
| POST | `messages/flags` | Add/remove read/starred flags |
| POST | `mark_all_as_read` | Mark all messages as read |
| POST | `mark_stream_as_read` | Mark stream read |
| POST | `mark_topic_as_read` | Mark topic read |
| POST | `reactions` | Add reaction (or use Python `add_reaction`) |
| DELETE | `messages/{message_id}/reactions` | Remove reaction (see API docs for exact shape) |
| GET | `users` | List users |
| GET | `users/me` | Current user |
| GET | `users/{user_id}` | User by id |
| GET | `streams` | List streams (params per docs) |
| GET | `users/me/subscriptions` | List subscriptions |
| POST | `users/me/subscriptions` | Subscribe to streams |
| DELETE | `users/me/subscriptions` | Unsubscribe |
| GET | `get_stream_id` | Resolve stream name to id (GET with `stream` query) |
| POST | `user_uploads` | Upload attachment (multipart; prefer dedicated tooling for large files) |
| GET | `server_settings` | Server / realm settings |

When in doubt, open the linked endpoint page and match **method**, **path**, and **JSON/query** fields to the `request` dict.

## Real-time events

Long-lived event queues (`register` / `events`) are **not** supported as blocking MCP tools in this server. Use the REST API, webhooks, or a separate process if you need streaming events.
