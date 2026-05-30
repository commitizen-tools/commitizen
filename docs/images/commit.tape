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

# Q1: prefix -- select the type of change (move down to "feat")
Wait+Screen /Select the type of change/
Sleep 500ms
Down
Sleep 500ms
Enter

# Q2: scope (optional, skip)
Wait+Screen /What is the scope/
Sleep 500ms
Enter

# Q3: subject
Wait+Screen /imperative summary/
Sleep 500ms
Type "awesome new feature"
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
