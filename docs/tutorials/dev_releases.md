# Dev Releases

## About

To make use of a `.dev` suffix, as per
[PEP440](https://peps.python.org/pep-0440/#developmental-releases).

If multiple active branches attempt to create a tag relative to the main branch, there is a possibility that they will attempt to create the _same_ tag, resulting in a collision.

Developmental releases aim to avoid this by including a `.dev` segment which
includes a non-negative integer unique to that workflow:

```txt
X.Y.devN
```

!!! note
    As noted in
    [PEP440](https://peps.python.org/pep-0440/#developmental-releases),
    while developmental releases help avoid the situation described above, they can be _"difficult to parse for human readers"_ depending on the value passed as the developmental release.

## How to

### Example 1: CircleCI

For example, CircleCI [provides](https://circleci.com/docs/variables/)
`CIRCLE_BUILD_NUM`, a unique number for each job which will increment with each
run:

```sh
--devrelease ${CIRCLE_BUILD_NUM}
```

This will result in a unique developmental release of, for example:

```sh
1.3.2.dev2478
```

### Example 2: GitHub

GitHub also
[provides](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables)
`GITHUB_RUN_ID`, a _"unique number for each workflow run"_ which will also
provide a unique number for each workflow:

```sh
--devrelease ${GITHUB_RUN_ID}
```

This will result in a unique developmental release of, for example:

```sh
1.3.2.dev6048584598
```

### Example 3: Unix time

Equally, as the developmental release needs only a non-negative integer, it is
possible to use the Unix time (i.e. the number of seconds since 1st January
1970 UTC).

This approach could potentially create a collision if two builds occur at precisely the same second, but it may be sufficient for many use cases:

```sh
--devrelease $(date +%s)
```

This will result in a unique developmental release of, for example:

```sh
1.3.2.dev1696238452
```
