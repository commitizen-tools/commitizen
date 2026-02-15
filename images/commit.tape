Output cli_interactive/commit.gif

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
Type "rm -rf /tmp/commitizen-demo && mkdir -p /tmp/commitizen-demo && cd /tmp/commitizen-demo"
Enter
Sleep 500ms

# Initialize git repository
Type "git init"
Enter
Sleep 500ms

Type "git checkout -b awesome-feature"
Enter
Sleep 500ms

# Create a dummy file to commit
Type "echo 'test content' > example.py"
Enter
Sleep 300ms

Type "git add example.py"
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
Sleep 1s

# Question 1: Select the type of change (move down to "feat")
Down
Sleep 500ms
Enter
Sleep 1s

# Question 2: Scope (optional, skip)
Enter
Sleep 1s

# Question 3: Subject
Type "awesome new feature"
Sleep 500ms
Enter
Sleep 1s

# Question 4: Is this a BREAKING CHANGE? (No)
Enter
Sleep 1s

# Question 5: Body (optional, skip)
Enter
Sleep 1s

# Question 6: Footer (optional, skip)
Enter
Sleep 1s

# Wait for commit success message
Sleep 2s
