Output cli_interactive/init.gif

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

# Set a clean, simple prompt
Type "PS1='$ '"
Enter
Sleep 300ms


# Create a clean temporary directory for recording
Type "rm -rf /tmp/commitizen-example && mkdir -p /tmp/commitizen-example && cd /tmp/commitizen-example"
Enter
Sleep 500ms

# Clear the screen to start fresh
Type "clear"
Enter
Sleep 500ms

# Show commands from here
Show

# Now run cz init in the clean environment
Type "cz init"
Sleep 500ms
Enter

# Wait for welcome message and first prompt
Sleep 500ms
Sleep 1s
# Question 1: Please choose a supported config file
# Default is .cz.toml, just press Enter
Enter
Sleep 1s

# Question 2: Please choose a cz (commit rule)
# Default is cz_conventional_commits, just press Enter
Enter
Sleep 1s

# Question 3: Choose the source of the version
# Default is "commitizen: Fetch and set version in commitizen config, just press Enter"
Enter
Sleep 1s

# Question 4: Choose version scheme
# Default is semver, just press Enter
Enter
Sleep 1s

# Question 5: Please enter the correct version format
# Default is "$version", just press Enter
Enter
Sleep 1s

# Question 6: Create changelog automatically on bump
# Default is Yes, just press Enter
Enter
Sleep 1s

# Question 7: Keep major version zero (0.x) during breaking changes
# Default is Yes, just press Enter
Enter
Sleep 1s

# Question 8: What types of pre-commit hook you want to install?
# Default is [commit-msg], just press Enter to accept
Enter
Sleep 1s

# Wait for completion message
Sleep 3s
