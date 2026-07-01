# Version 0.1.0 Release Record

The 0.1.0 release establishes the toolkit as a small public research package. A new user can inspect the source, install the wheel from the GitHub release, run examples, and read the stated limitations.

## Release Contents

- Source install works on Python 3.9, 3.10, and 3.11.
- Tests and quality gate pass in CI.
- README, docs, changelog, citation metadata, and contribution guidance are present.
- Examples run without private data, credentials, or model downloads.
- Responsible AI notes explain the limits of routing and emotion labels.

## Not in Scope

- Bundled private datasets.
- Model weights committed to the repository.
- API-backed demos that require secrets.
- Claims that the router identifies a speaker, ethnicity, nationality, or community membership.

## Completed Checks

- `make check` passed locally.
- GitHub Actions passed on `main`.
- Isolated source and wheel builds passed.
- `twine check` passed.
- Fresh wheel install and CLI smoke tests passed.
- `v0.1.0` was tagged and published as a GitHub release.
- The release includes the source distribution and wheel.

## Package Index Publishing

The package-index publishing path uses trusted publishing rather than long-lived API tokens. The repository workflow is `.github/workflows/publish.yml`.

Trusted publisher settings:

- Project name: `low-resource-nlp-toolkit`
- Owner: `oyinkanchekwas`
- Repository: `low-resource-nlp-toolkit`
- Workflow: `publish.yml`
- TestPyPI environment: `testpypi`
- PyPI environment: `pypi`

After the pending publishers are configured on TestPyPI and PyPI, run the `publish` workflow manually with `target=testpypi`, test installation from TestPyPI, and then run it with `target=pypi`.

## Evidence to Preserve

- CI run link.
- GitHub release link.
- Package index release link once PyPI publication is complete.
- Documentation link.
- External issue, pull request, citation, workshop/demo acceptance, or adoption note.
