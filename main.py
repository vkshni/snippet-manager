# CLI

import argparse
import sys
import getpass
from snippet_manager import SnippetManager

sm = SnippetManager()


# Decorator to check initialization
def require_init(func):
    """Decorator that checks if system is initialized before running command"""

    def wrapper(args):
        if not sm.auth.config.is_initialized():
            print("✗ System not initialized. Run 'python main.py init' first.")
            sys.exit(1)
        return func(args)

    return wrapper


def cmd_init(args):

    if sm.auth.config.is_initialized():
        print("✗ System already initialized")
        return

    password = getpass.getpass("Create master password (min 6 chars): ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("✗ Passwords don't match")
        return

    if len(password) < 6:
        print("✗ Password too short (min 6 characters)")
        return

    sm.auth.setup(password)
    print("✓ Master password created successfully!")


@require_init
def cmd_add(args):

    snippet = sm.add_snippet(
        args.title, args.content, tag=args.tag, access_level=args.access
    )
    print(f"✓ Snippet added: {snippet.snippet_id}")


@require_init
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


@require_init
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


@require_init
def cmd_lock(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if sm.is_locked(snippet):
        print(f"Snippet already locked")
        return

    confirmed = input(f"Lock '{snippet.title}'? (y/n): ")
    if confirmed == "y":
        sm.lock_snippet(snippet.snippet_id)
        print(f"✓ Snippet locked")


@require_init
def cmd_unlock(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if not sm.is_locked(snippet):
        print(f"Snippet already unlocked")
        return

    print(f"Enter master password to unlock")
    retry = 1
    MAX_ATTEMPTS = 3
    while retry <= MAX_ATTEMPTS:
        try:
            user_password = getpass.getpass("Master password: ")
            if sm.auth.verify(user_password):
                confirmed = input(f"Unlock '{snippet.title}'? (y/n): ")
                if confirmed == "y":
                    sm.unlock_snippet(snippet.snippet_id)
                    print(f"✓ Snippet locked")
                return
        except ValueError as e:
            print(f"✗ {e}")

        print(f"✗ Wrong password. {MAX_ATTEMPTS-retry} attempt(s) remaining")
        retry += 1

    print("✗ Account locked. Try again after 30 seconds")
    return


@require_init
def cmd_search(args):

    snippets = sm.search_snippet(args.keyword)

    if not snippets:
        print(f"No snippet found with keyword '{args.keyword}'")
        return

    print(f"Search result(s) for keyword '{args.keyword}'")
    print(f"\n{'ID':<20} {'TITLE':<50} {'TAG':<10}")
    print("-" * 85)
    for s in snippets:
        lock = "🔒" if s.access_level == "LOCKED" else ""
        print(f"{s.snippet_id:<20} {s.title:<50} [{s.tag:<10}] {lock}")
    print(f"\nTotal: {len(snippets)} snippet(s)")


@require_init
def cmd_view(args):

    snippet = sm.get_snippet_by_id(args.snippet_id)
    if not snippet:
        print(f"X no snippets found with ID '{args.snippet_id}'")
        return

    if sm.is_locked(snippet):
        print(f"Snipped locked 🔒 Enter master password to view")
        retry = 1
        MAX_ATTEMPTS = 3
        while retry <= MAX_ATTEMPTS:
            try:
                user_password = getpass.getpass("Master password: ")
                if sm.auth.verify(user_password):
                    display_format(snippet)
                    return
            except ValueError as e:
                print(f"✗ {e}")

            print(f"✗ Wrong password. {MAX_ATTEMPTS-retry} attempt(s) remaining")
            retry += 1

        print("✗ Account locked. Try again after 30 seconds")
        return

    display_format(snippet)


def display_format(snippet):

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


@require_init
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
    for s in snippets:
        lock = "🔒" if s.access_level == "LOCKED" else ""
        print(f"{s.snippet_id:<20} {s.title:<50} [{s.tag:<10}] {lock}")
    print(f"\nTotal: {len(snippets)} snippet(s)")


def main():

    parser = argparse.ArgumentParser(
        prog="main", description="Snippet Manager", add_help=True
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # init
    p_init = sub.add_parser("init", help="Initialize system with master password")
    p_init.set_defaults(func=cmd_init)

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

    # lock
    p_lock = sub.add_parser("lock", help="Lock a snippet using snippet ID")
    p_lock.add_argument("snippet_id", help="Snippet ID")
    p_lock.set_defaults(func=cmd_lock)

    # unlock
    p_unlock = sub.add_parser("unlock", help="Unlock a snippet using snippet ID")
    p_unlock.add_argument("snippet_id", help="Snippet ID")
    p_unlock.set_defaults(func=cmd_unlock)

    # search
    p_search = sub.add_parser("search", help="Search snippets by keyword")
    p_search.add_argument("keyword", help="Search item")
    p_search.set_defaults(func=cmd_search)

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
