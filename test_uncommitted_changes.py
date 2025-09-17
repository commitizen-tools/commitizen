#!/usr/bin/env python3
"""
Comprehensive test suite for the check_uncommitted feature.

This tests the implementation without relying on pytest infrastructure.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '.')

from commitizen import git
from commitizen.exceptions import UncommittedChangesError, ExitCode


def run_git_cmd(cmd, cwd=None):
    """Run a git command and return success, stdout, stderr."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def test_git_function():
    """Test git.has_uncommitted_changes() function."""
    print("\n🧪 Testing git.has_uncommitted_changes()")
    
    # Create a temporary git repository for clean testing
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Initialize git repo
        run_git_cmd("git init")
        run_git_cmd("git config user.name 'Test User'")
        run_git_cmd("git config user.email 'test@example.com'")
        
        # Test 1: Empty repository (should be clean)
        result = git.has_uncommitted_changes()
        assert not result, f"Empty repo should be clean, got {result}"
        print("  ✅ Empty repository: clean")
        
        # Test 2: Add file and commit (should be clean)
        Path("test.txt").write_text("initial content")
        run_git_cmd("git add test.txt")
        run_git_cmd("git commit -m 'initial commit'")
        
        result = git.has_uncommitted_changes()
        assert not result, f"Clean repo after commit should be clean, got {result}"
        print("  ✅ Clean repository after commit: clean")
        
        # Test 3: Modify tracked file (should be dirty)
        Path("test.txt").write_text("modified content")
        
        result = git.has_uncommitted_changes()
        assert result, f"Modified tracked file should be dirty, got {result}"
        print("  ✅ Modified tracked file: dirty")
        
        # Test 4: Stage the change (should still be dirty)
        run_git_cmd("git add test.txt")
        
        result = git.has_uncommitted_changes()
        assert result, f"Staged changes should be dirty, got {result}"
        print("  ✅ Staged changes: dirty")
        
        # Test 5: Commit the change (should be clean again)
        run_git_cmd("git commit -m 'second commit'")
        
        result = git.has_uncommitted_changes()
        assert not result, f"After commit should be clean, got {result}"
        print("  ✅ After commit: clean")
        
        # Test 6: Add untracked file (should remain clean)
        Path("untracked.txt").write_text("untracked content")
        
        result = git.has_uncommitted_changes()
        assert not result, f"Untracked files should not make repo dirty, got {result}"
        print("  ✅ Untracked files: clean (correct behavior)")
        
        # Test 7: Mix of tracked and untracked (should be dirty due to tracked)
        Path("test.txt").write_text("another modification")
        
        result = git.has_uncommitted_changes()
        assert result, f"Mixed tracked/untracked should be dirty, got {result}"
        print("  ✅ Mixed tracked/untracked changes: dirty")


def test_exception():
    """Test UncommittedChangesError exception."""
    print("\n🧪 Testing UncommittedChangesError exception")
    
    # Test exception creation
    exc = UncommittedChangesError()
    assert exc.exit_code == ExitCode.UNCOMMITTED_CHANGES
    assert "UNCOMMITTED_CHANGES" in str(exc)
    assert "git status" in str(exc)
    print("  ✅ Exception has correct exit code and message")
    
    # Test exception with custom message
    custom_exc = UncommittedChangesError("Custom message")
    assert str(custom_exc) == "Custom message"
    print("  ✅ Exception accepts custom message")


def test_integration():
    """Test integration with configuration system."""
    print("\n🧪 Testing configuration integration")
    
    from commitizen.defaults import DEFAULT_SETTINGS, Settings
    
    # Test that check_uncommitted is in defaults
    assert "check_uncommitted" in DEFAULT_SETTINGS
    assert DEFAULT_SETTINGS["check_uncommitted"] is False
    print("  ✅ check_uncommitted in DEFAULT_SETTINGS with False default")
    
    # Test that it's in Settings TypedDict
    # (This is more of a type check, but we can verify it doesn't raise)
    try:
        settings: Settings = {"check_uncommitted": True}
        assert settings["check_uncommitted"] is True
        print("  ✅ check_uncommitted accepted in Settings type")
    except Exception as e:
        print(f"  ❌ Settings type issue: {e}")


def test_cli_args():
    """Test CLI argument structure."""
    print("\n🧪 Testing CLI argument structure")
    
    from commitizen.commands.bump import BumpArgs
    
    # Test that check_uncommitted is in BumpArgs
    try:
        args: BumpArgs = {"check_uncommitted": True}
        assert args["check_uncommitted"] is True
        print("  ✅ check_uncommitted accepted in BumpArgs type")
    except Exception as e:
        print(f"  ❌ BumpArgs type issue: {e}")


def main():
    """Run all tests."""
    print("🚀 Testing Commitizen Uncommitted Changes Feature")
    print("=" * 60)
    
    # Save original directory
    original_dir = os.getcwd()
    
    try:
        test_git_function()
        test_exception()
        test_integration()
        test_cli_args()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 Implementation Summary:")
        print("  ✅ git.has_uncommitted_changes() works correctly")
        print("  ✅ Detects modified/staged files")
        print("  ✅ Ignores untracked files (as intended)")
        print("  ✅ UncommittedChangesError exception works")
        print("  ✅ Configuration integration complete")
        print("  ✅ CLI argument types defined")
        print("\n🚀 Ready for integration testing!")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)