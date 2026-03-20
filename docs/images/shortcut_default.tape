Output cli_interactive/shortcut_default.gif

Source shared/base.tape
Source shared/git_init.tape

Type "git checkout -b awesome-docs"
Enter
Sleep 500ms

# Initialize commitizen config with shortcuts enabled
Type `cat > pyproject.toml << 'EOF'`
Enter
Type `[tool.commitizen]`
Enter
Type `name = "cz_conventional_commits"`
Enter
Type `use_shortcuts = true`
Enter
Type "EOF"
Enter
Sleep 300ms

# Create a dummy file to commit
Type "echo 'test content' > README.md"
Enter
Sleep 300ms

Type "git add README.md"
Enter
Sleep 300ms

# Clear the screen to start fresh
Type "clear"
Enter
Sleep 500ms

# Show commands from here
Show

# Now run cz commit
Type "cz commit"
Sleep 500ms
Enter

# Wait for first prompt to appear
Sleep 2s

# Question 1: Select the type of change (press d to "docs")
Sleep 1s
Type "d"
Sleep 2s
Enter
Sleep 1s

# Question 2: Scope (optional, skip)
Enter
Sleep 1s

# Question 3: Subject
Type "demo with custom keys"
Sleep 500ms
Enter
Sleep 500ms

# Question 4: Is this a BREAKING CHANGE? (No)
Enter
Sleep 500ms

# Question 5: Body (optional, skip)
Enter
Sleep 500ms

# Question 6: Footer (optional, skip)
Enter
Sleep 500ms

# Wait for commit success message
Sleep 1s

Source shared/cleanup.tape
