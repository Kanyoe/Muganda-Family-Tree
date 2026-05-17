#!/usr/bin/env python3
import argparse
import json
import os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "family.json")


def load():
    if os.path.exists(DB):
        with open(DB) as f:
            return json.load(f)
    return {"members": [], "next_id": 1}


def save(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=2)


def cmd_init(args):
    save({"members": [], "next_id": 1})
    print("Initialized.")


def cmd_add(args):
    data = load()

    member = {
        "id": data["next_id"],
        "name": args.name,
        "birth": args.birth or "",
        "gender": args.gender or "",
        "parents": args.parents or [],
        "notes": args.notes or "",
        "spouses": []
    }

    data["members"].append(member)
    data["next_id"] += 1

    save(data)

    print(f"Added: [{member['id']}] {member['name']}")


def cmd_list(args):
    data = load()

    if not data["members"]:
        print("No members.")
        return

    print(f"\n{'ID':<5} {'Name':<25} {'Gender':<8} {'Parents'}")
    print("-" * 70)

    for m in data["members"]:
        parents = ", ".join(map(str, m.get("parents", []))) or "-"

        print(
            f"{m['id']:<5} "
            f"{m['name']:<25} "
            f"{m['gender']:<8} "
            f"{parents}"
        )

    print()


def cmd_marry(args):
    data = load()

    by_id = {m["id"]: m for m in data["members"]}

    if args.id1 not in by_id or args.id2 not in by_id:
        print("Invalid member ID.")
        return

    p1 = by_id[args.id1]
    p2 = by_id[args.id2]

    p1.setdefault("spouses", [])
    p2.setdefault("spouses", [])

    if args.id2 not in p1["spouses"]:
        p1["spouses"].append(args.id2)

    if args.id1 not in p2["spouses"]:
        p2["spouses"].append(args.id1)

    save(data)

    print(f"{p1['name']} ❤ {p2['name']}")


def cmd_tree(args):
    data = load()

    members = data["members"]

    if not members:
        print("No members.")
        return

    by_id = {m["id"]: m for m in members}

    children = {}

    # Build parent → children map
    for m in members:
        for pid in m.get("parents", []):
            children.setdefault(pid, []).append(m["id"])

    roots = [m for m in members if not m.get("parents")]

    printed = set()

    # Dynasty style box
    def make_box(text, width=32):
        top = "┌" + "─" * width + "┐"
        middle = "│" + text.center(width) + "│"
        bottom = "└" + "─" * width + "┘"

        return [top, middle, bottom]

    def render_person(mid, level=0):
        if mid in printed:
            return

        printed.add(mid)

        member = by_id[mid]

        indent = "    " * level

        # PERSON BOX
        box = make_box(member["name"])

        for line in box:
            print(indent + line)

        # SPOUSES
        for sid in member.get("spouses", []):
            if sid in by_id:
                spouse = by_id[sid]

                print(indent + "        ❤")

                spouse_box = make_box(
                    f"Spouse: {spouse['name']}"
                )

                for line in spouse_box:
                    print(indent + line)

        # CHILDREN
        kids = children.get(mid, [])

        if kids:
            print(indent + "        │")
            print(indent + "   ┌────┴────┐")

        for kid in kids:
            render_person(kid, level + 1)

    print("\n")
    print("=" * 60)
    print("         DYNASTY FAMILY TREE")
    print("=" * 60)
    print()

    for root in roots:
        render_person(root["id"])

    print()

    def label(m):
        spouse_names = []

        for sid in m.get("spouses", []):
            if sid in by_id:
                spouse_names.append(by_id[sid]["name"])

        spouse_text = ""

        if spouse_names:
            spouse_text = " ❤ " + ", ".join(spouse_names)

        text = f"[{m['id']}] {m['name']}{spouse_text}"

        if m["birth"]:
            text += f" (b. {m['birth']})"

        return text

    def print_node(mid, prefix="", is_last=True):
        if mid in printed:
            return

        printed.add(mid)

        m = by_id[mid]

        connector = "└── " if is_last else "├── "

        print(prefix + connector + label(m))

        kids = children.get(mid, [])

        new_prefix = prefix + ("    " if is_last else "│   ")

        for i, kid in enumerate(kids):
            print_node(kid, new_prefix, i == len(kids) - 1)

    print("\n🌳 Family Tree\n")

    for i, root in enumerate(roots):
        if root["id"] in printed:
            continue

        printed.add(root["id"])

        print(label(root))

        kids = children.get(root["id"], [])

        for j, kid in enumerate(kids):
            print_node(kid, "", j == len(kids) - 1)

    print()


def cmd_remove(args):
    data = load()

    before = len(data["members"])

    data["members"] = [
        m for m in data["members"]
        if m["id"] != args.id
    ]

    if len(data["members"]) < before:
        save(data)
        print("Removed.")
    else:
        print("Not found.")


def main():
    parser = argparse.ArgumentParser(prog="ft")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")

    p = sub.add_parser("add")

    p.add_argument("name")
    p.add_argument("--birth")
    p.add_argument("--gender")

    p.add_argument(
        "--parents",
        type=int,
        nargs="*"
    )

    p.add_argument("--notes")

    sub.add_parser("list")
    sub.add_parser("tree")

    p2 = sub.add_parser("remove")
    p2.add_argument("id", type=int)

    p3 = sub.add_parser("marry")
    p3.add_argument("id1", type=int)
    p3.add_argument("id2", type=int)

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "list": cmd_list,
        "tree": cmd_tree,
        "remove": cmd_remove,
        "marry": cmd_marry,
    }

    commands.get(
        args.command,
        lambda a: parser.print_help()
    )(args)


if __name__ == "__main__":
    main()
