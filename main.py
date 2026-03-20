# CLI

import argparse
import sys
from snippet_manager import SnippetManager

sm = SnippetManager()


def cmd_add(args):

    snippet = sm.add_snippet(
        args.title, args.content, tag=args.tag, access_level=args.access
    )
    print(f"✓ Snippet added: {snippet.snippet_id}")


def cmd_archive(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if sm.is_archived(snippet):
        print(f"Snippet already archived")
        return

    confirmed = input(f"Archive '{snippet.title}'? (y/n): ")
    if confirmed == "y":
        sm.archive_snippet(snippet.snippet_id)
        print("✓ Snippet archived")


def cmd_unarchive(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if not sm.is_archived(snippet):
        print(f"Snippet already unarchived")
        return

    confirmed = input(f"Unarchive '{snippet.title}'? (y/n): ")
    if confirmed == "y":
        sm.unarchive_snippet(snippet.snippet_id)
        print("✓ Snippet unarchived")


def cmd_view(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if sm.is_locked(snippet):
        print(f"Snipped locked 🔒")
        return

    print("\n" + "━" * 70)
    print(f"\n  {snippet.title}\n")
    print(f"  ID:      {snippet.snippet_id}")
    print(f"  Tag:     {snippet.tag}")
    print(f"  Status:  {snippet.status}")
    print(f"  Access:  {snippet.access_level}")
    print(f"  Created: {snippet.created_at}")
    print("\n" + "━" * 70 + "\n")
    print(snippet.content)
    print("\n" + "━" * 70 + "\n")


def cmd_list(args):

    if args.tag:
        snippets = sm.list_by_tag(tag=args.tag.lower())

    elif args.archived:
        snippets = sm.list_all(status="ARCHIVED")

    else:
        snippets = sm.list_all(status="ACTIVE")

    if not snippets:
        if args.tag:
            print(f"No snippets with tag '{args.tag}' found")
        elif args.archived:
            print("No archived snippets")
        else:
            print("No snippets found")
        return

    if args.archived:
        print("ARCHIVED SNIPPETS")

    print(f"\n{'ID':<20} {'TITLE':<50} {'TAG':<10}")
    print("-" * 85)
    for i, s in enumerate(snippets, 1):
        lock = "🔒" if s.access_level == "LOCKED" else ""
        print(f"{s.snippet_id:<20} {s.title:<50} [{s.tag:<10}] {lock}")
    print(f"\nTotal: {len(snippets)} snippet(s)")


def main():

    parser = argparse.ArgumentParser(
        prog="main", description="Snippet Manager", add_help=True
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # add
    p_add = sub.add_parser("add", help="Add a new snippet")
    p_add.add_argument("title", help="Snippet title")
    p_add.add_argument("content", help="Content of the snippet")
    p_add.add_argument("--tag", help="Optional tag")
    p_add.add_argument(
        "--access",
        default="PUBLIC",
        choices=["PUBLIC", "LOCKED"],
        help="Access level (default: PUBLIC)",
    )
    p_add.set_defaults(func=cmd_add)

    # archive
    p_archive = sub.add_parser("archive", help="Archive a snippet using snippet ID")
    p_archive.add_argument("snippet_id", help="Snippet ID")
    p_archive.set_defaults(func=cmd_archive)

    # unarchive
    p_unarchive = sub.add_parser(
        "unarchive", help="Unrchive a snippet using snippet ID"
    )
    p_unarchive.add_argument("snippet_id", help="Snippet ID")
    p_unarchive.set_defaults(func=cmd_unarchive)

    # view
    p_view = sub.add_parser("view", help="View a snippet using ID")
    p_view.add_argument("snippet_id", help="Snippet ID")
    p_view.set_defaults(func=cmd_view)

    # list
    p_list = sub.add_parser("list", help="List all snippets")
    p_list.add_argument("--tag", help="Filter by tag")
    p_list.add_argument(
        "--archived", action="store_true", help="List all archived snippets"
    )
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()

    try:
        args.func(args)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
