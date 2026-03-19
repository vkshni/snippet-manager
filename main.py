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


def cmd_list(args):

    if args.tag:
        snippets = sm.list_by_tag(tag=args.tag.lower())

    else:
        snippets = sm.list_all()

    if not snippets:
        if args.tag:
            print("No snippets with tag '{args.tag}' found")
        else:
            print("No snippets found")
        return

    print(f"\n{'ID':<20} {'TITLE':<50} {'TAG':<10}")
    print("-" * 85)
    for i, s in enumerate(snippets, 1):
        lock = "🔒" if s.access_level == "LOCKED" else ""
        tag_display = s.tag if s.tag else "untagged"
        print(f"{s.snippet_id:<20} {s.title:<50} [{tag_display:<10}] {lock}")
    print(f"\nTotal: {len(snippets)} snippets")


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

    # list
    p_list = sub.add_parser("list", help="List all snippets")
    p_list.add_argument("--tag", help="Filter by tag")
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
