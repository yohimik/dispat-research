#!/usr/bin/env python3
"""The only permitted path to the delivery bot. Hard allow-list: every
send and every processed update is checked against OWNER; anything else
is refused before any network call, and foreign updates are dropped and
reported. Token comes from TG_BOT_TOKEN env — never stored in a file.

  tg.py send <path> [caption]      # document to the owner, only
  tg.py msg  <text>                # text to the owner, only
  tg.py watch                      # print owner updates, drop foreign
"""
import json
import os
import sys
import urllib.parse
import urllib.request
import uuid

OWNER_ID = 360613745          # @yohimik, verified via getChat
OWNER_USERNAME = "yohimik"


def api(method, data=None, files=None):
    tok = os.environ.get("TG_BOT_TOKEN")
    if not tok:
        sys.exit("TG_BOT_TOKEN not set")
    url = f"https://api.telegram.org/bot{tok}/{method}"
    if files:
        boundary = uuid.uuid4().hex
        body = b""
        for k, v in (data or {}).items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{k}\"\r\n\r\n{v}\r\n").encode()
        for k, (fname, blob) in files.items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{k}\"; filename=\"{fname}\"\r\n"
                     f"Content-Type: application/octet-stream\r\n\r\n"
                     ).encode() + blob + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, body, {
            "Content-Type": f"multipart/form-data; boundary={boundary}"})
    else:
        req = urllib.request.Request(
            url, urllib.parse.urlencode(data or {}).encode())
    return json.load(urllib.request.urlopen(req))


def assert_owner(chat_id):
    """Refuse any target but OWNER, and verify the id still resolves to
    the owner's username before the first payload of a run."""
    if int(chat_id) != OWNER_ID:
        sys.exit(f"REFUSED: chat_id {chat_id} is not the owner "
                 f"({OWNER_ID}/@{OWNER_USERNAME}); no request sent")
    got = api("getChat", {"chat_id": OWNER_ID})["result"]
    if got.get("username") != OWNER_USERNAME or got.get("type") != "private":
        sys.exit(f"REFUSED: id {OWNER_ID} no longer resolves to "
                 f"@{OWNER_USERNAME} private chat (got {got}); no payload sent")


def owner_updates(updates):
    """Split updates into (owner's, foreign). Foreign ones are never
    acted on, only counted for the report."""
    ours, foreign = [], []
    for u in updates:
        m = u.get("message") or u.get("edited_message") or {}
        frm, chat = m.get("from", {}), m.get("chat", {})
        if frm.get("id") == OWNER_ID and chat.get("id") == OWNER_ID:
            ours.append(u)
        else:
            foreign.append(u)
    return ours, foreign


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    target = os.environ.get("TG_CHAT_ID", str(OWNER_ID))  # guard catches overrides
    if cmd == "send":
        assert_owner(target)
        path = sys.argv[2]
        caption = sys.argv[3] if len(sys.argv) > 3 else ""
        blob = open(path, "rb").read()
        r = api("sendDocument", {"chat_id": OWNER_ID, "caption": caption},
                {"document": (os.path.basename(path), blob)})
        print("sent:", r["ok"])
    elif cmd == "msg":
        assert_owner(target)
        r = api("sendMessage", {"chat_id": OWNER_ID, "text": sys.argv[2]})
        print("sent:", r["ok"])
    elif cmd == "watch":
        ours, foreign = owner_updates(
            api("getUpdates").get("result", []))
        for u in ours:
            print("owner:", u["message"].get("text", "")[:100])
        if foreign:
            print(f"DROPPED {len(foreign)} foreign update(s) from ids:",
                  sorted({(u.get('message') or {}).get('from', {}).get('id')
                          for u in foreign}))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
