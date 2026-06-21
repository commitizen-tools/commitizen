Output cli_interactive/init.gif

Source shared/base.tape

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

# Q1: Please choose a supported config file
# Default is .cz.toml, just press Enter
Wait+Screen /Please choose a supported config/
Sleep 500ms
Enter

# Q2: Please choose a cz (commit rule)
# Default is cz_conventional_commits, just press Enter
Wait+Screen /Please choose a cz/
Sleep 500ms
Enter

# Q3: Choose the source of the version
# Default is "commitizen", just press Enter
Wait+Screen /Choose the source of the version/
Sleep 500ms
Enter

# Q4: Choose version scheme
# Default is semver, just press Enter
Wait+Screen /Choose version scheme/
Sleep 500ms
Enter

# Q5: Please enter the correct version format
# Default is "$version", just press Enter
Wait+Screen /Please enter the correct version format/
Sleep 500ms
Enter

# Q6: Create changelog automatically on bump
# Default is Yes, just press Enter
Wait+Screen /Create changelog automatically on bump/
Sleep 500ms
Enter

# Q7: Keep major version zero (0.x) during breaking changes
# Default is Yes, just press Enter
Wait+Screen /Keep major version zero/
Sleep 500ms
Enter

# Q8: What types of pre-commit hook you want to install?
# Default is [], just press Enter to accept
Wait+Screen /types of pre-commit hook/
Sleep 500ms
Enter

# Wait for completion message
Sleep 2s

Source shared/cleanup.tape
