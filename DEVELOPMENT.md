# development

## prepare to cut a release

order matters:

0. set a tag version

```bash
export TAG=v1.0
```

1. tag and push base:

```bash
pushd .
cd images/machina-base &&\
  git tag -a $TAG -m "$TAG" &&|
  git push origin $TAG
popd
```

Make release in GH UI

Once image(s) are created, continue

2. tag and push ghidra base

```bash
pushd .
cd images/machina-base-ghidra &&\
  git tag -a $TAG -m "$TAG" &&|
  git push origin $TAG
popd
```

Make release in GH UI

Once image is created, continue

3. tag and push worker modules

```bash
git submodule foreach git tag -f -a $TAG -m "$TAG"  &&\
git submodule foreach git push -f origin $TAG
```

Make releases in GH UI



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