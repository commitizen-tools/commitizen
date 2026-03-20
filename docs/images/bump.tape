Output cli_interactive/bump.gif

Source shared/base.tape
Source shared/git_init.tape

# Initialize commitizen config with version 0.0.1 and changelog enabled
Type `cat > pyproject.toml << 'EOF'`
Enter
Type `[tool.commitizen]`
Enter
Type `version = "0.0.1"`
Enter
Type `update_changelog_on_bump = true`
Enter
Type "EOF"
Enter
Sleep 300ms

# Create initial commit (no tag, so cz bump will ask "Is this the first tag created?")
Type "git add pyproject.toml"
Enter
Sleep 300ms

Type "git commit -m 'chore: initial commit'"
Enter
Sleep 500ms

# Create a feat commit that will trigger a MINOR bump (0.0.1 -> 0.1.0)
Type "echo 'new feature' > feature.py"
Enter
Sleep 300ms

Type "git add feature.py"
Enter
Sleep 300ms

Type "git commit -m 'feat: add awesome new feature'"
Enter
Sleep 500ms

# Clear the screen to start fresh
Type "clear"
Enter
Sleep 500ms

# Show commands from here
Show

# Step 1: Show current version
Type "cz version --project"
Sleep 500ms
Enter
Sleep 1s

# Step 2: Run cz bump (no existing tag, will prompt for first tag)
Type "cz bump"
Sleep 500ms
Enter

# Wait for the "Is this the first tag created?" prompt
Sleep 2s

# Answer Yes to "Is this the first tag created?" (default is Yes, just press Enter)
Enter
Sleep 3s

# Step 3: Show new version after bump
Type "cz version --project"
Sleep 500ms
Enter
Sleep 1s

# Wait for final output
Sleep 1s

Source shared/cleanup.tape
