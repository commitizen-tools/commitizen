<!--
Thanks for sending a pull request!
Please fill in the following content to let us know better about this change.
-->

## Description
<!-- Describe what the change is -->


## Checklist

- [ ] I have read the [contributing guidelines](https://commitizen-tools.github.io/commitizen/contributing/)

### Code Changes

- [ ] Add test cases to all the changes you introduce
- [ ] Run `poetry all` locally to ensure this change passes linter check and tests
- [ ] Manually test the changes:
  - [ ] Verify the feature/bug fix works as expected in real-world scenarios
  - [ ] Test edge cases and error conditions
  - [ ] Ensure backward compatibility is maintained
  - [ ] Document any manual testing steps performed
- [ ] Update the documentation for the changes

### Documentation Changes

- [ ] Run `poetry doc` locally to ensure the documentation pages renders correctly
  - [ ] Check if there are any broken links in the documentation

> When running `poetry doc`, any broken internal documentation links will be reported in the console output like this:
>
> ```text
> INFO    -  Doc file 'config.md' contains a link 'commands/bump.md#-post_bump_hooks', but the doc 'commands/bump.md' does not contain an anchor '#-post_bump_hooks'.
> ```

## Expected Behavior
<!-- A clear and concise description of what you expected to happen -->


## Steps to Test This Pull Request
<!-- Steps to reproduce the behavior:
1. ...
2. ...
3. ... -->


## Additional Context
<!-- Add any other RELATED ISSUE, context or screenshots about the pull request here. -->
