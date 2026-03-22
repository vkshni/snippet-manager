# CLI - Personal Snippet Manager

import argparse
import sys
import getpass
from snippet_manager import SnippetManager

sm = SnippetManager()


# ============================================================================
# DECORATORS
# ============================================================================


def require_init(func):
    """
    Decorator that checks if system is initialized before running command.

    Ensures master password is set up before allowing snippet operations.
    """

    def wrapper(args):
        if not sm.auth.config.is_initialized():
            print("\n✗ System not initialized\n")
            print("First-time setup required:")
            print("  python main.py init\n")
            sys.exit(1)
        return func(args)

    return wrapper


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def confirm(message, default=False):
    """
    Ask user for yes/no confirmation with better input handling.

    Args:
        message (str): Question to ask user
        default (bool): Default answer if user just presses Enter

    Returns:
        bool: True if user confirms, False otherwise

    Accepts: y/yes/Y/YES or n/no/N/NO
    """
    if default:
        prompt = f"{message} (Y/n): "
    else:
        prompt = f"{message} (y/N): "

    while True:
        response = input(prompt).strip().lower()

        if response == "":
            return default
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            return False

        print("Please enter 'y' or 'n'")


def display_snippet(snippet):
    """
    Display full snippet details in formatted card layout.

    Args:
        snippet: Snippet object to display
    """
    lock_indicator = "🔒 LOCKED" if snippet.access_level == "LOCKED" else "PUBLIC"
    created = snippet.created_at.strftime("%d/%m/%Y %H:%M:%S")

    print("\n" + "━" * 70)
    print(f"\n  {snippet.title}\n")
    print(f"  ID:      {snippet.snippet_id}")
    print(f"  Tag:     {snippet.tag if snippet.tag else '-'}")
    print(f"  Status:  {snippet.status}")
    print(f"  Access:  {lock_indicator}")
    print(f"  Created: {created}")
    print("\n" + "━" * 70 + "\n")
    print(snippet.content)
    print("\n" + "━" * 70 + "\n")


def handle_password_verification(snippet, action="view"):
    """
    Handle password verification for locked snippets with retry logic.

    Args:
        snippet: Snippet object that requires password
        action (str): Action being performed (for display messages)

    Returns:
        bool: True if password verified, False if failed/locked out
    """
    print(f"\n🔒 This snippet is LOCKED")
    print(f"   Title: {snippet.title}")
    print(f"   Enter master password to {action}\n")

    MAX_ATTEMPTS = 3
    retry = 1

    while retry <= MAX_ATTEMPTS:
        try:
            user_password = getpass.getpass("Master password: ")
            if sm.auth.verify(user_password):
                return True

        except ValueError as e:
            # Lockout error from auth service
            print(f"\n✗ {e}\n")
            return False

        # Wrong password
        remaining = MAX_ATTEMPTS - retry
        if remaining > 0:
            print(
                f"✗ Wrong password ({remaining} attempt{'s' if remaining > 1 else ''} remaining)\n"
            )
        retry += 1

    # Exhausted all attempts
    print("\n✗ Too many failed attempts. Account locked for 5 minutes.\n")
    return False


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


def cmd_init(args):
    """
    Initialize the snippet manager with a master password.

    First-time setup command that creates the master password
    for protecting locked snippets.
    """
    if sm.auth.config.is_initialized():
        print("\n✗ System already initialized\n")
        print("To change your password, use:")
        print("  python main.py config (coming soon)\n")
        return

    print("\n=== First-Time Setup ===\n")
    password = getpass.getpass("Create master password (min 6 chars): ")
    confirm_password = getpass.getpass("Confirm password: ")

    # Validate password match
    if password != confirm_password:
        print("\n✗ Passwords don't match. Please try again.\n")
        return

    # Validate password length
    if len(password) < 6:
        print("\n✗ Password too short (minimum 6 characters)\n")
        return

    # Validate alphanumeric
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        print("\n✗ Password must contain both letters and numbers\n")
        return

    # Setup complete
    sm.auth.setup(password)
    print("\n✓ Master password created successfully!")
    print("\nYou can now:")
    print("  • Add snippets: python main.py add 'Title' 'Content'")
    print("  • List snippets: python main.py list")
    print("  • Get help: python main.py --help\n")


@require_init
def cmd_add(args):
    """
    Add a new snippet to the manager.

    Creates a snippet with title, content, optional tag, and access level.
    """
    try:
        snippet = sm.add_snippet(
            args.title, args.content, tag=args.tag, access_level=args.access
        )
        lock_msg = " (🔒 LOCKED)" if args.access == "LOCKED" else ""
        print(f"\n✓ Snippet added: {snippet.snippet_id}{lock_msg}\n")

    except ValueError as e:
        print(f"\n✗ Validation error: {e}\n")
        print("Tips:")
        print("  • Title: 1-100 characters")
        print("  • Content: Cannot be empty")
        print("  • Tag: Lowercase, no spaces (use underscores)\n")
        sys.exit(1)


@require_init
def cmd_archive(args):
    """
    Archive a snippet by ID (moves from ACTIVE to ARCHIVED status).

    Archived snippets are hidden from default listings but can be
    viewed with --archived flag.
    """
    snippet = sm.get_snippet_by_id(args.snippet_id)

    if not snippet:
        print(f"\n✗ Snippet not found: {args.snippet_id}\n")
        print("Suggestions:")
        print("  • Check the snippet ID is correct")
        print("  • Use 'python main.py list' to see all snippets\n")
        return

    if sm.is_archived(snippet):
        print(f"\n✗ Snippet already archived\n")
        return

    if confirm(f"Archive '{snippet.title}'?"):
        sm.archive_snippet(snippet.snippet_id)
        print(f"\n✓ Snippet archived: {snippet.snippet_id}\n")
    else:
        print("\nArchive cancelled.\n")


@require_init
def cmd_unarchive(args):
    """
    Unarchive a snippet by ID (moves from ARCHIVED to ACTIVE status).

    Restores an archived snippet to active status.
    """
    snippet = sm.get_snippet_by_id(args.snippet_id)

    if not snippet:
        print(f"\n✗ Snippet not found: {args.snippet_id}\n")
        return

    if not sm.is_archived(snippet):
        print(f"\n✗ Snippet is not archived\n")
        return

    if confirm(f"Unarchive '{snippet.title}'?"):
        sm.unarchive_snippet(snippet.snippet_id)
        print(f"\n✓ Snippet restored: {snippet.snippet_id}\n")
    else:
        print("\nUnarchive cancelled.\n")


@require_init
def cmd_lock(args):
    """
    Lock a snippet to require password for viewing.

    Changes access level from PUBLIC to LOCKED.
    """
    snippet = sm.get_snippet_by_id(args.snippet_id)

    if not snippet:
        print(f"\n✗ Snippet not found: {args.snippet_id}\n")
        return

    if sm.is_locked(snippet):
        print(f"\n✗ Snippet already locked 🔒\n")
        return

    if confirm(f"Lock '{snippet.title}'?"):
        sm.lock_snippet(snippet.snippet_id)
        print(f"\n✓ Snippet locked 🔒: {snippet.snippet_id}\n")
        print("This snippet now requires your master password to view.\n")
    else:
        print("\nLock cancelled.\n")


@require_init
def cmd_unlock(args):
    """
    Unlock a snippet to make it publicly viewable.

    Requires master password verification.
    Changes access level from LOCKED to PUBLIC.
    """
    snippet = sm.get_snippet_by_id(args.snippet_id)

    if not snippet:
        print(f"\n✗ Snippet not found: {args.snippet_id}\n")
        return

    if not sm.is_locked(snippet):
        print(f"\n✗ Snippet is not locked\n")
        return

    # Verify password before unlocking
    if handle_password_verification(snippet, action="unlock"):
        if confirm(f"Unlock '{snippet.title}'?"):
            sm.unlock_snippet(snippet.snippet_id)
            print(f"\n✓ Snippet unlocked: {snippet.snippet_id}\n")
        else:
            print("\nUnlock cancelled.\n")


@require_init
def cmd_search(args):
    """
    Search snippets by keyword in title or tag.

    Case-insensitive search across snippet titles and tags.
    """
    snippets = sm.search_snippet(args.keyword)

    if not snippets:
        print(f"\n✗ No snippets found for '{args.keyword}'\n")
        print("Suggestions:")
        print("  • Try a different keyword")
        print("  • Use 'python main.py list' to see all snippets")
        print("  • Search is case-insensitive\n")
        return

    print(f"\n🔍 Search results for '{args.keyword}':\n")
    print(f"{'ID':<20} {'TITLE':<50} {'TAG':<15} {'ACCESS'}")
    print("─" * 90)

    for s in snippets:
        lock_indicator = "🔒" if s.access_level == "LOCKED" else ""
        tag_display = s.tag if s.tag else "-"
        print(f"{s.snippet_id:<20} {s.title:<50} {tag_display:<15} {lock_indicator}")

    print(f"\nFound: {len(snippets)} snippet{'s' if len(snippets) != 1 else ''}\n")


@require_init
def cmd_view(args):
    """
    View full snippet details including content.

    For locked snippets, requires master password verification.
    """
    snippet = sm.get_snippet_by_id(args.snippet_id)

    if not snippet:
        print(f"\n✗ Snippet not found: {args.snippet_id}\n")
        print("Suggestions:")
        print("  • Check the snippet ID is correct")
        print("  • Use 'python main.py list' to see all snippets")
        print("  • Use 'python main.py search <keyword>' to find snippets\n")
        return

    # Handle locked snippets
    if sm.is_locked(snippet):
        if not handle_password_verification(snippet, action="view"):
            return

    # Display snippet
    display_snippet(snippet)


@require_init
def cmd_list(args):
    """
    List snippets with optional filtering.

    Can filter by tag or show archived snippets.
    Default shows all active snippets.
    """
    # Determine which snippets to show
    if args.tag:
        snippets = sm.list_by_tag(tag=args.tag.lower())
    elif args.archived:
        snippets = sm.list_all(status="ARCHIVED")
    else:
        snippets = sm.list_all(status="ACTIVE")

    # Handle empty results
    if not snippets:
        if args.tag:
            print(f"\n✗ No snippets found with tag: {args.tag}\n")
            print("Tips:")
            print("  • Check tag spelling")
            print("  • Tags are case-insensitive")
            print("  • Use 'python main.py list' to see all tags\n")
        elif args.archived:
            print("\nℹ No archived snippets\n")
        else:
            print("\nℹ No snippets yet!\n")
            print("Get started:")
            print("  python main.py add 'My First Snippet' 'Hello World' --tag test\n")
        return

    # Display header
    if args.archived:
        print("\n📦 ARCHIVED SNIPPETS\n")
    else:
        print()

    # Table header
    print(f"{'ID':<20} {'TITLE':<50} {'TAG':<15} {'ACCESS'}")
    print("─" * 95)

    # Table rows
    for s in snippets:
        lock_indicator = "🔒" if s.access_level == "LOCKED" else ""
        tag_display = s.tag if s.tag else "-"

        # Truncate title if too long
        title_display = s.title[:47] + "..." if len(s.title) > 50 else s.title

        print(
            f"{s.snippet_id:<20} {title_display:<50} {tag_display:<15} {lock_indicator}"
        )

    # Summary
    status_text = "archived" if args.archived else "active"
    print(
        f"\nTotal: {len(snippets)} {status_text} snippet{'s' if len(snippets) != 1 else ''}\n"
    )


# ============================================================================
# MAIN CLI SETUP
# ============================================================================


def main():
    """
    Main entry point for the snippet manager CLI.

    Sets up argument parser and routes commands to handlers.
    """
    parser = argparse.ArgumentParser(
        prog="snippet",
        description="Personal Snippet Manager - Store and manage code snippets, commands, and notes securely",
        epilog="""
Examples:
  # First-time setup
  python main.py init

  # Add snippets
  python main.py add "Git Reset" "git reset --hard HEAD" --tag git
  python main.py add "API Key" "sk-123..." --tag secrets --access LOCKED

  # List and search
  python main.py list
  python main.py list --tag python
  python main.py list --archived
  python main.py search docker

  # View and manage
  python main.py view 19032026_00001
  python main.py archive 19032026_00001
  python main.py lock 19032026_00002

For more help on a specific command:
  python main.py <command> --help
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")
    sub.required = True

    # ========== INIT ==========
    p_init = sub.add_parser(
        "init",
        help="Initialize system (first-time setup)",
        description="Set up master password for protecting locked snippets",
    )
    p_init.set_defaults(func=cmd_init)

    # ========== ADD ==========
    p_add = sub.add_parser(
        "add",
        help="Add a new snippet",
        description="Create a new snippet with title, content, and optional tag",
    )
    p_add.add_argument("title", help="Snippet title (1-100 characters)")
    p_add.add_argument("content", help="Snippet content (code, command, or note)")
    p_add.add_argument("--tag", help="Category tag (e.g., python, git, docker)")
    p_add.add_argument(
        "--access",
        default="PUBLIC",
        choices=["PUBLIC", "LOCKED"],
        help="Access level: PUBLIC (default) or LOCKED (requires password)",
    )
    p_add.set_defaults(func=cmd_add)

    # ========== LIST ==========
    p_list = sub.add_parser(
        "list", help="List snippets", description="Display all active snippets"
    )
    p_list.add_argument("--tag", help="Filter by specific tag")
    p_list.add_argument(
        "--archived", action="store_true", help="Show archived snippets"
    )
    p_list.set_defaults(func=cmd_list)

    # ========== SEARCH ==========
    p_search = sub.add_parser(
        "search",
        help="Search snippets",
        description="Search snippets by keyword (searches title and tag)",
    )
    p_search.add_argument("keyword", help="Search term (case-insensitive)")
    p_search.set_defaults(func=cmd_search)

    # ========== VIEW ==========
    p_view = sub.add_parser(
        "view",
        help="View snippet details",
        description="Display full snippet content (password required for locked snippets)",
    )
    p_view.add_argument("snippet_id", help="Snippet ID (e.g., 19032026_00001)")
    p_view.set_defaults(func=cmd_view)

    # ========== ARCHIVE ==========
    p_archive = sub.add_parser(
        "archive",
        help="Archive a snippet",
        description="Move snippet to archived status (hidden from default list)",
    )
    p_archive.add_argument("snippet_id", help="Snippet ID to archive")
    p_archive.set_defaults(func=cmd_archive)

    # ========== UNARCHIVE ==========
    p_unarchive = sub.add_parser(
        "unarchive",
        help="Restore archived snippet",
        description="Move snippet back to active status",
    )
    p_unarchive.add_argument("snippet_id", help="Snippet ID to restore")
    p_unarchive.set_defaults(func=cmd_unarchive)

    # ========== LOCK ==========
    p_lock = sub.add_parser(
        "lock",
        help="Lock a snippet",
        description="Require master password to view this snippet",
    )
    p_lock.add_argument("snippet_id", help="Snippet ID to lock")
    p_lock.set_defaults(func=cmd_lock)

    # ========== UNLOCK ==========
    p_unlock = sub.add_parser(
        "unlock",
        help="Unlock a snippet",
        description="Remove password requirement (requires password verification)",
    )
    p_unlock.add_argument("snippet_id", help="Snippet ID to unlock")
    p_unlock.set_defaults(func=cmd_unlock)

    # Parse and execute
    args = parser.parse_args()

    try:
        args.func(args)

    except ValueError as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)

    except PermissionError as e:
        print(f"\n✗ Permission error: {e}\n")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        print("If this persists, please check your data files or reinitialize.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
