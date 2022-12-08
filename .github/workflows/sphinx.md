# This is a basic workflow to help you get started with Actions

name: deploy Sphinx to github pages

# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the "master" branch
  push:
    branches: [ "master" ]
  pull_request:
    branches: [ "master" ]

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v1
    - uses: ammaraskar/sphinx-action@master
      with:
        docs-folder: "docs/"
