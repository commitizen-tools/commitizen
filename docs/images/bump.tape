Output cli_interactive/bump.gif

Require cz

# Use bash for cross-platform compatibility (macOS, Linux, Windows)
Set Shell bash

Set FontSize 16
Set Width 878
Set Height 568
Set Padding 20
Set TypingSpeed 50ms

Set Theme {
  "name": "Commitizen",
  "black": "#232628",
  "red": "#fc4384",
  "green": "#b3e33b",
  "yellow": "#ffa727",
  "blue": "#75dff2",
  "magenta": "#ae89fe",
  "cyan": "#708387",
  "white": "#d5d5d0",
  "brightBlack": "#626566",
  "brightRed": "#ff7fac",
  "brightGreen": "#c8ed71",
  "brightYellow": "#ebdf86",
  "brightBlue": "#75dff2",
  "brightMagenta": "#ae89fe",
  "brightCyan": "#b1c6ca",
  "brightWhite": "#f9f9f4",
  "background": "#1e1e2e",
  "foreground": "#afafaf",
  "cursor": "#c7c7c7"
}

# Hide initial shell prompt
Hide

# Wait for terminal to be ready
Sleep 1s

# Set a clean, simple prompt (while hidden)
Type "PS1='$ '"
Enter
Sleep 300ms

# Create a clean temporary directory for recording
Type "rm -rf /tmp/commitizen-example && mkdir -p /tmp/commitizen-example && cd /tmp/commitizen-example"
Enter
Sleep 500ms

# Initialize git repository
Type "git init"
Enter
Type "git config user.email 'you@example.com'"
Enter
Type "git config user.name 'Your Name'"
Enter
Sleep 500ms

# Initialize commitizen config with version 0.0.1 and changelog enabled
Type `cat > pyproject.toml << 'EOF'`
Enter
Sleep 100ms
Type `[tool.commitizen]`
Enter
Sleep 100ms
Type `version = "0.0.1"`
Enter
Sleep 100ms
Type `update_changelog_on_bump = true`
Enter
Sleep 100ms
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
Sleep 3s
