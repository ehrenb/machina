# development

## creating a new repository

1. Create GH project
2. Add submodule to `machina/images`
  * use https clone link option when adding to allow for anonymous cloning

```bash
git submodule add https://github.com/ehrenb/<REPO>.git
git commit -m <MSG>
git push
```

2. Add GH Repository Secrets, `DOCKER_USERNAME` and `DOCKER_PASSWORD` for Actions
  * Settings -> Secrets and Variables -> Actions
3. Create Publish GH workflow
  * Actions -> "Skip this and set up a workflow yourself" -> name `docker-image.yml`
  * Populate using any of the other `docker-image.yml` files (except for machina-docs, which publishes on tag AND main commit)
4. Create Docker Hub project, named after `<REPO>`

## prepare to cut a release

```bash
gh auth login
```

0. set a tag version

```bash
export TAG=v1.X
```

1. create release (release and tag) for base:

```bash
pushd .
cd images/machina-base &&\
  gh release create $TAG -t $TAG --generate-notes --latest
popd
```

Once image(s) are created, continue...

2. create release (release and tag) for ghidra base:

```bash
pushd .
cd images/machina-base-ghidra &&\
  gh release create $TAG -t $TAG --generate-notes --latest
popd
```

Once image is created, continue...

3. tag and push worker modules

Ignore non-zero exit codes, because releases have already been made for some submodules.

```bash
git submodule foreach 'gh release create $TAG -t $TAG --generate-notes --latest || :'
```

## automation

* Could poll 'gh workflow view' to detect when an image has built and been pushed, then trigger subsequent releases.
  - https://www.softwaretester.blog/detecting-github-workflow-job-run-status-changes
  
## delete a release

0. set a tag version

```bash
export TAG=v1.X
```

3. delete release for all modules

```bash
git submodule foreach gh release delete $TAG -y --cleanup-tag
```
## misc

Disable a workflow across all repositories

Use '|| :' to ignore non-zero exit codes across 'git submodule foreach'

```bash
git submodule foreach 'gh workflow disable "Publish Release" || :'
```

## Old release process

This old workflow depended on using a 'release' Github Action that triggered a new release when a tag was created. Ultimately, I moved away from this because deleting the tags was still a manual process.  To streamline both the creation of tags+releases and the deletion, 'gh release' cli can do all of this without additional Actions.

order matters:

1. tag and push base:

```bash
pushd .
cd images/machina-base &&\
  git tag -a $TAG -m "$TAG" &&|
  git push origin $TAG
popd
```


Once image(s) are created, continue

2. tag and push ghidra base

```bash
pushd .
cd images/machina-base-ghidra &&\
  git tag -a $TAG -m "$TAG" &&|
  git push origin $TAG
popd
```

Once image is created, continue

3. tag and push worker modules

```bash
git submodule foreach git tag -f -a $TAG -m "$TAG"  &&\
git submodule foreach git push -f origin $TAG
```



## ssh push

By default, to allow for anonymous cloning, repositories are pulled using HTTPS.  This defaults the 'push' remote to use HTTPS as well.  In order to push to this repository (and all submodules) with SSH instead of HTTPS, set the remote for each repo to its respective SSH url:

```bash
cd machina
git remote set-url --push origin git@github.com:ehrenb/machina.git &&\
  git submodule foreach 'git remote set-url --push origin git@github.com:ehrenb/${name##*/}.git'
```

## docstrings

docstrings format: [Sphinx](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)

## viz

Compose 'depends_on' dependency graph:

```bash
cd machina/
docker run --rm -it --name dcv -v $(pwd):/input pmsipilot/docker-compose-viz render -m image --force docker-compose.yml --output-file=topology.png --no-volumes --no-ports --no-networks
```