# development

## prepare to cut a release

Create a versioned tag

```bash
git submodule foreach git tag -a v0.2 -m "v0.2"
```

Push the tags

```bash
git submodule foreach git push origin v0.2
```