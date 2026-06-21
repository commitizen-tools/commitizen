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

# Q1: prefix -- press "d" shortcut for "docs"
Wait+Screen /Select the type of change/
Sleep 1s
Type "d"
Sleep 2s
Enter

# Q2: scope (optional, skip)
Wait+Screen /What is the scope/
Sleep 500ms
Enter

# Q3: subject
Wait+Screen /imperative summary/
Sleep 500ms
Type "demo with custom keys"
Sleep 500ms
Enter

# Q4: body (optional, skip)
Wait+Screen /additional contextual information/
Sleep 500ms
Enter

# Q5: is_breaking_change (No)
Wait+Screen /BREAKING CHANGE\?/
Sleep 500ms
Enter

# Q6: footer (optional, skip)
Wait+Screen /Footer\. Information/
Sleep 500ms
Enter

# Wait for commit success message
Sleep 2s

Source shared/cleanup.tape
