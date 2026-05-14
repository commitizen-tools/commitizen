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
Sleep 1s

Source shared/cleanup.tape
