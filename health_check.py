"""
health_check.py - Quick system test
Run this to verify your snippet manager is working correctly
"""

import sys
from pathlib import Path


# Add color output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_test(name, passed, message=""):
    """Print test result"""
    if passed:
        print(f"{Colors.GREEN}✓{Colors.RESET} {name}")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} {name}")
        if message:
            print(f"  Error: {message}")


def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}\n")


def main():
    """Run health checks"""

    print(f"\n{Colors.BOLD}Snippet Manager - Health Check{Colors.RESET}")

    failed = 0

    # ================================================================
    # 1. IMPORTS
    # ================================================================
    print_section("1. Testing Imports")

    try:
        from snippet_manager import SnippetManager

        print_test("Import SnippetManager", True)
    except Exception as e:
        print_test("Import SnippetManager", False, str(e))
        failed += 1
        return

    try:
        from snippet_entity import Snippet

        print_test("Import Snippet", True)
    except Exception as e:
        print_test("Import Snippet", False, str(e))
        failed += 1
        return

    try:
        from security import AuthService

        print_test("Import AuthService", True)
    except Exception as e:
        print_test("Import AuthService", False, str(e))
        failed += 1
        return

    try:
        from storage import SnippetDB, ConfigFile, AttemptsFile

        print_test("Import Storage Classes", True)
    except Exception as e:
        print_test("Import Storage Classes", False, str(e))
        failed += 1
        return

    try:
        from utils import generate_snippet_id, generate_hash

        print_test("Import Utilities", True)
    except Exception as e:
        print_test("Import Utilities", False, str(e))
        failed += 1
        return

    # ================================================================
    # 2. FILE CREATION
    # ================================================================
    print_section("2. Testing File Creation")

    try:
        sm = SnippetManager(
            SNIPPET_FILE="health_check_snippets.json",
            CONFIG_FILE="health_check_config.json",
            ATTEMPTS_FILE="health_check_attempts.json",
        )
        print_test("Create SnippetManager instance", True)
    except Exception as e:
        print_test("Create SnippetManager instance", False, str(e))
        failed += 1
        return

    data_dir = Path("data")
    if data_dir.exists():
        print_test("Data directory exists", True)
    else:
        print_test("Data directory exists", False, "data/ folder not found")
        failed += 1

    # ================================================================
    # 3. ID GENERATION
    # ================================================================
    print_section("3. Testing ID Generation")

    try:
        id1 = generate_snippet_id()
        id2 = generate_snippet_id()

        if "_" in id1 and len(id1.split("_")) == 2:
            print_test("ID format correct (DDMMYYYY_NNNNN)", True)
        else:
            print_test("ID format correct", False, f"Invalid format: {id1}")
            failed += 1

        if id1 != id2:
            print_test("IDs are unique", True)
        else:
            print_test("IDs are unique", False, "Generated same ID twice")
            failed += 1

    except Exception as e:
        print_test("Generate IDs", False, str(e))
        failed += 1

    # ================================================================
    # 4. PASSWORD HASHING
    # ================================================================
    print_section("4. Testing Password Hashing")

    try:
        hash1 = generate_hash("test123")
        hash2 = generate_hash("test123")
        hash3 = generate_hash("different")

        if hash1 == hash2:
            print_test("Hash is consistent", True)
        else:
            print_test("Hash is consistent", False, "Same input gave different hashes")
            failed += 1

        if hash1 != hash3:
            print_test("Different inputs produce different hashes", True)
        else:
            print_test("Different inputs produce different hashes", False)
            failed += 1

        if len(hash1) == 64:
            print_test("Hash length correct (SHA-256)", True)
        else:
            print_test("Hash length correct", False, f"Expected 64, got {len(hash1)}")
            failed += 1

    except Exception as e:
        print_test("Password hashing", False, str(e))
        failed += 1

    # ================================================================
    # 5. AUTHENTICATION
    # ================================================================
    print_section("5. Testing Authentication")

    try:
        if not sm.auth.config.is_initialized():
            sm.auth.setup("healthcheck123")
            print_test("Setup master password", True)
        else:
            print_test("Master password already set", True)
    except Exception as e:
        print_test("Setup master password", False, str(e))
        failed += 1

    try:
        result = sm.auth.verify("healthcheck123")
        if result:
            print_test("Verify correct password", True)
        else:
            print_test("Verify correct password", False, "Returned False")
            failed += 1
    except Exception as e:
        print_test("Verify correct password", False, str(e))
        failed += 1

    try:
        result = sm.auth.verify("wrongpassword")
        if not result:
            print_test("Reject wrong password", True)
        else:
            print_test("Reject wrong password", False, "Accepted wrong password!")
            failed += 1
    except Exception as e:
        # Wrong password should return False, not raise exception
        print_test("Reject wrong password", False, str(e))
        failed += 1

    # ================================================================
    # 6. ADD SNIPPETS
    # ================================================================
    print_section("6. Testing Add Snippets")

    try:
        snippet1 = sm.add_snippet("Health Check 1", "Test content", "test")
        print_test("Add public snippet", True)
    except Exception as e:
        print_test("Add public snippet", False, str(e))
        failed += 1
        snippet1 = None

    try:
        snippet2 = sm.add_snippet(
            "Health Check 2", "Secret", "test", access_level="LOCKED"
        )
        print_test("Add locked snippet", True)
    except Exception as e:
        print_test("Add locked snippet", False, str(e))
        failed += 1
        snippet2 = None

    # Validation tests
    try:
        sm.add_snippet("", "content")
        print_test("Reject empty title", False, "Empty title was accepted!")
        failed += 1
    except ValueError:
        print_test("Reject empty title", True)
    except Exception as e:
        print_test("Reject empty title", False, str(e))
        failed += 1

    try:
        sm.add_snippet("title", "")
        print_test("Reject empty content", False, "Empty content was accepted!")
        failed += 1
    except ValueError:
        print_test("Reject empty content", True)
    except Exception as e:
        print_test("Reject empty content", False, str(e))
        failed += 1

    # ================================================================
    # 7. LIST & FILTER
    # ================================================================
    print_section("7. Testing List & Filter")

    try:
        snippets = sm.list_all(status="ACTIVE")
        if len(snippets) >= 2:
            print_test("List all snippets", True)
        else:
            print_test(
                "List all snippets", False, f"Expected >= 2, got {len(snippets)}"
            )
            failed += 1
    except Exception as e:
        print_test("List all snippets", False, str(e))
        failed += 1

    try:
        snippets = sm.list_by_tag(tag="test")
        if len(snippets) >= 2:
            print_test("Filter by tag", True)
        else:
            print_test("Filter by tag", False, f"Expected >= 2, got {len(snippets)}")
            failed += 1
    except Exception as e:
        print_test("Filter by tag", False, str(e))
        failed += 1

    # ================================================================
    # 8. SEARCH
    # ================================================================
    print_section("8. Testing Search")

    try:
        results = sm.search_snippet("Health")
        if len(results) >= 2:
            print_test("Search by keyword", True)
        else:
            print_test("Search by keyword", False, f"Expected >= 2, got {len(results)}")
            failed += 1
    except Exception as e:
        print_test("Search by keyword", False, str(e))
        failed += 1

    try:
        results = sm.search_snippet("nonexistent_xyz")
        if len(results) == 0:
            print_test("Search returns empty for no match", True)
        else:
            print_test(
                "Search returns empty for no match",
                False,
                f"Found {len(results)} results",
            )
            failed += 1
    except Exception as e:
        print_test("Search returns empty for no match", False, str(e))
        failed += 1

    # ================================================================
    # 9. ARCHIVE/UNARCHIVE
    # ================================================================
    print_section("9. Testing Archive/Unarchive")

    if snippet1:
        try:
            sm.archive_snippet(snippet1.snippet_id)
            print_test("Archive snippet", True)
        except Exception as e:
            print_test("Archive snippet", False, str(e))
            failed += 1

        try:
            archived = sm.list_all(status="ARCHIVED")
            if len(archived) >= 1:
                print_test("List archived snippets", True)
            else:
                print_test(
                    "List archived snippets",
                    False,
                    f"Expected >= 1, got {len(archived)}",
                )
                failed += 1
        except Exception as e:
            print_test("List archived snippets", False, str(e))
            failed += 1

        try:
            sm.unarchive_snippet(snippet1.snippet_id)
            print_test("Unarchive snippet", True)
        except Exception as e:
            print_test("Unarchive snippet", False, str(e))
            failed += 1

    # ================================================================
    # 10. LOCK/UNLOCK
    # ================================================================
    print_section("10. Testing Lock/Unlock")

    if snippet1:
        try:
            sm.lock_snippet(snippet1.snippet_id)
            snippet = sm.get_snippet_by_id(snippet1.snippet_id)
            if snippet.access_level == "LOCKED":
                print_test("Lock snippet", True)
            else:
                print_test("Lock snippet", False, "Status not changed to LOCKED")
                failed += 1
        except Exception as e:
            print_test("Lock snippet", False, str(e))
            failed += 1

        try:
            sm.unlock_snippet(snippet1.snippet_id)
            snippet = sm.get_snippet_by_id(snippet1.snippet_id)
            if snippet.access_level == "PUBLIC":
                print_test("Unlock snippet", True)
            else:
                print_test("Unlock snippet", False, "Status not changed to PUBLIC")
                failed += 1
        except Exception as e:
            print_test("Unlock snippet", False, str(e))
            failed += 1

    # ================================================================
    # 11. GET BY ID
    # ================================================================
    print_section("11. Testing Get Snippet by ID")

    if snippet1:
        try:
            snippet = sm.get_snippet_by_id(snippet1.snippet_id)
            if snippet and snippet.snippet_id == snippet1.snippet_id:
                print_test("Get snippet by ID", True)
            else:
                print_test(
                    "Get snippet by ID", False, "Snippet not found or ID mismatch"
                )
                failed += 1
        except Exception as e:
            print_test("Get snippet by ID", False, str(e))
            failed += 1

    try:
        snippet = sm.get_snippet_by_id("99999999_99999")
        if snippet is None:
            print_test("Return None for invalid ID", True)
        else:
            print_test(
                "Return None for invalid ID", False, "Found snippet with fake ID!"
            )
            failed += 1
    except Exception as e:
        print_test("Return None for invalid ID", False, str(e))
        failed += 1

    # ================================================================
    # 12. CLEANUP
    # ================================================================
    print_section("12. Cleanup Test Files")

    try:
        # Clean up test files
        data_dir = Path("data")
        for filename in [
            "health_check_snippets.json",
            "health_check_config.json",
            "health_check_attempts.json",
        ]:
            filepath = data_dir / filename
            if filepath.exists():
                filepath.unlink()
        print_test("Cleanup test files", True)
    except Exception as e:
        print_test("Cleanup test files", False, str(e))
        failed += 1

    # ================================================================
    # SUMMARY
    # ================================================================
    print_section("Summary")

    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(
            f"{Colors.GREEN}Your snippet manager is working perfectly.{Colors.RESET}\n"
        )
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ {failed} CHECK(S) FAILED{Colors.RESET}")
        print(f"{Colors.RED}Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
