#!/usr/bin/env python3
"""Compute a Discord OAuth2 permission integer from a named allow-list.

Edit PERMS to tune the bot's invited permissions, then run:
    python3 scripts/compute_permissions.py

Do NOT include 'ADMINISTRATOR' for a least-privilege mod bot.
Bit values: https://discord.com/developers/docs/topics/permissions

CORRECT moderation integer (includes MANAGE_ROLES): 1494917180614
The earlier 1494648745158 was MISSING MANAGE_ROLES (bit 28) -> bot could
not apply the Muted role, its only enforcement lever in this Hermes build.
"""

from typing import Dict

# name -> bit position (log2 of the permission value)
PERMISSION_BITS: Dict[str, int] = {
    "VIEW_AUDIT_LOG": 7,
    "MANAGE_MESSAGES": 13,
    "KICK_MEMBERS": 1,
    "BAN_MEMBERS": 2,
    "MANAGE_ROLES": 28,          # REQUIRED so the bot can apply/remove the Muted role
    "MODERATE_MEMBERS": 40,
    "VIEW_CHANNEL": 10,
    "SEND_MESSAGES": 11,
    "EMBED_LINKS": 14,
    "ATTACH_FILES": 15,
    "READ_MESSAGE_HISTORY": 16,
    "ADD_REACTIONS": 6,
    "MANAGE_THREADS": 34,
    "SEND_MESSAGES_IN_THREADS": 38,
    "CREATE_PUBLIC_THREADS": 35,
    "CREATE_PRIVATE_THREADS": 36,
}

# What a moderation bot needs (scoped, no Administrator, no Manage Channels)
PERMS = [
    "VIEW_CHANNEL",
    "SEND_MESSAGES",
    "EMBED_LINKS",
    "ATTACH_FILES",
    "READ_MESSAGE_HISTORY",
    "ADD_REACTIONS",
    "MANAGE_MESSAGES",
    "MANAGE_THREADS",
    "MANAGE_ROLES",
    "KICK_MEMBERS",
    "BAN_MEMBERS",
    "MODERATE_MEMBERS",
    "VIEW_AUDIT_LOG",
    "SEND_MESSAGES_IN_THREADS",
    "CREATE_PUBLIC_THREADS",
    "CREATE_PRIVATE_THREADS",
]


def compute(perms: list[str]) -> int:
    unknown = [p for p in perms if p not in PERMISSION_BITS]
    if unknown:
        raise SystemExit(f"Unknown permission(s): {unknown}. Known: {sorted(PERMISSION_BITS)}")
    total = sum(1 << PERMISSION_BITS[p] for p in perms)
    return total


if __name__ == "__main__":
    total = compute(PERMS)
    print(f"Permission integer: {total}")
    print("Granted:")
    for p in PERMS:
        print(f"  {p}")
    assert total == 1494917180614, f"expected 1494917180614, got {total}"
