# main.py

import argparse
from database import initialize_database, get_connection


def add_player(args):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO players (name, class_name, role, notes)
            VALUES (?, ?, ?, ?)
            """,
            (args.name, args.class_name, args.role, args.notes),
        )
        conn.commit()

    print(f"Added player: {args.name}")


def list_players(args):
    with get_connection() as conn:
        players = conn.execute(
            """
            SELECT id, name, class_name, role, active
            FROM players
            ORDER BY name
            """
        ).fetchall()

    if not players:
        print("No players found.")
        return

    for player in players:
        status = "Active" if player["active"] else "Inactive"
        print(
            f'{player["id"]}: {player["name"]} | '
            f'{player["class_name"] or "Unknown"} | '
            f'{player["role"] or "Unknown"} | {status}'
        )


def add_raid(args):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO raids (raid_date, instance_name, phase, notes)
            VALUES (?, ?, ?, ?)
            """,
            (args.raid_date, args.instance_name, args.phase, args.notes),
        )
        conn.commit()

    print(f"Added raid: {args.instance_name} on {args.raid_date}")


def add_dkp(args):
    with get_connection() as conn:
        player = conn.execute(
            "SELECT id FROM players WHERE name = ?",
            (args.name,),
        ).fetchone()

        if player is None:
            print(f"Player not found: {args.name}")
            return

        conn.execute(
            """
            INSERT INTO dkp_transactions
                (player_id, raid_id, amount, transaction_type, reason, officer)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                player["id"],
                args.raid_id,
                args.amount,
                args.transaction_type,
                args.reason,
                args.officer,
            ),
        )
        conn.commit()

    print(f'Added {args.amount} DKP for {args.name}: {args.reason}')


def standings(args):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT name, class_name, role, current_dkp
            FROM current_dkp
            ORDER BY current_dkp DESC, name
            """
        ).fetchall()

    if not rows:
        print("No DKP standings found.")
        return

    print("\nCurrent DKP Standings")
    print("-" * 55)
    print(f'{"Player":<18} {"Class":<12} {"Role":<12} {"DKP":>6}')
    print("-" * 55)

    for row in rows:
        print(
            f'{row["name"]:<18} '
            f'{(row["class_name"] or "-"):<12} '
            f'{(row["role"] or "-"):<12} '
            f'{row["current_dkp"]:>6}'
        )


def main():
    parser = argparse.ArgumentParser(
        description="RaidLedger - DKP and raid tracking tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize the database")

    add_player_parser = subparsers.add_parser("add-player", help="Add a player")
    add_player_parser.add_argument("name")
    add_player_parser.add_argument("--class-name", default=None)
    add_player_parser.add_argument("--role", default=None)
    add_player_parser.add_argument("--notes", default=None)

    subparsers.add_parser("list-players", help="List all players")

    add_raid_parser = subparsers.add_parser("add-raid", help="Add a raid")
    add_raid_parser.add_argument("raid_date", help="Example: 2026-07-01")
    add_raid_parser.add_argument("instance_name", help="Example: Black Temple")
    add_raid_parser.add_argument("--phase", default=None)
    add_raid_parser.add_argument("--notes", default=None)

    dkp_parser = subparsers.add_parser("add-dkp", help="Add or subtract DKP")
    dkp_parser.add_argument("name")
    dkp_parser.add_argument("amount", type=int)
    dkp_parser.add_argument("reason")
    dkp_parser.add_argument("--transaction-type", default="manual")
    dkp_parser.add_argument("--officer", default="system")
    dkp_parser.add_argument("--raid-id", type=int, default=None)

    subparsers.add_parser("standings", help="Show DKP standings")

    args = parser.parse_args()

    if args.command == "init":
        initialize_database()
        print("RaidLedger database initialized.")
    elif args.command == "add-player":
        add_player(args)
    elif args.command == "list-players":
        list_players(args)
    elif args.command == "add-raid":
        add_raid(args)
    elif args.command == "add-dkp":
        add_dkp(args)
    elif args.command == "standings":
        standings(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()