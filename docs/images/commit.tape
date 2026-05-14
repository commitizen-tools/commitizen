Output cli_interactive/commit.gif

Source shared/base.tape
Source shared/git_init.tape

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
Sleep 1s

Source shared/cleanup.tape
