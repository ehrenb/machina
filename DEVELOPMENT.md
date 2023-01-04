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