Output cli_interactive/shortcut_custom.gif

Source shared/base.tape
Source shared/git_init.tape

Type "git checkout -b awesome-docs"
Enter
Sleep 500ms

Type `cat > pyproject.toml << 'EOF'`
Enter
Type `[tool.commitizen]`
Enter
Type `name = "cz_customize"`
Enter
Type `use_shortcuts = true`
Enter
Type ``
Enter
Type `[tool.commitizen.customize]`
Enter
Type `message_template = "{{prefix}}: {{message}}"`
Enter
Type `schema = "<type>: <body>"`
Enter
Type `schema_pattern = "(feat|fix|docs|test):(\\s.*)"`
Enter
Type ``
Enter
Type `[[tool.commitizen.customize.questions]]`
Enter
Type `type = "list"`
Enter
Type `name = "prefix"`
Enter
Type `message = "Select the type of change you are committing"`
Enter
Type `choices = [`
Enter
Type `  { value = "feat", name = "feat: A new feature.", key = "f" },`
Enter
Type `  { value = "fix", name = "fix: A bug fix.", key = "x" },`
Enter
Type `  { value = "docs", name = "docs: Documentation only changes", key = "d" },`
Enter
Type `  { value = "test", name = "test: Adding or correcting tests", key = "t" },`
Enter
Type `]`
Enter
Type ``
Enter
Type `[[tool.commitizen.customize.questions]]`
Enter
Type `type = "input"`
Enter
Type `name = "message"`
Enter
Type `message = "Commit body: "`
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

# Question 2: Commit body
Type "demo with custom keys"
Sleep 500ms
Enter
Sleep 500ms

# Wait for commit success message
Sleep 1s

Source shared/cleanup.tape
