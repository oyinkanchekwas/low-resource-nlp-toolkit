# Version 0.1.0 Release Plan

The 0.1.0 release should establish the toolkit as a trustworthy public artefact, not a large package. The release is ready only when a new user can install it, run examples, understand the limitations, and decide whether it is suitable for their own research.

## Release Goals

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

## Release Checklist

- [ ] Confirm `make check` passes locally.
- [ ] Confirm GitHub Actions passes on `main`.
- [ ] Build source distribution and wheel with `python3 -m build`.
- [ ] Review package metadata and long description.
- [ ] Tag the release as `v0.1.0`.
- [ ] Publish to PyPI after checking the package on TestPyPI.
- [ ] Add a short release note explaining why the first release stays dependency-light.

## Evidence to Preserve

- CI run link.
- PyPI release link.
- Documentation link.
- Demo video or notebook link.
- External issue, pull request, citation, workshop/demo acceptance, or adoption note.
