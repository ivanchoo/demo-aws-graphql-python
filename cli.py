#!/usr/bin/env python
import glob
import os
import re
import shutil
import subprocess
import sys

import click

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
BUILD_INCLUDES = ['main.py', 'demo']
BUILD_DEPENDENCIES_EXCLUDES = [
    re.compile(expr) for expr in
    ['easy_install.*', 'pip.*', 'setuptools.*', 'wheel.*', 'pkg_resources.*']
]


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.pass_context
def server(ctx):
    """Run a local dev server."""
    try:
        from flask import Flask  # noqa
    except ImportError:
        sys.exit(
            'Failed to import dev dependencies. '
            'Did you run `pipenv install --dev --three`?'
        )

    click.echo('Running local dev server...')
    app = Flask(__name__)
    app.debug = True

    from demo.schema import schema
    from flask_graphql import GraphQLView
    graphql_view = GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    app.add_url_rule('/', view_func=graphql_view)

    app.run()


@cli.command()
@click.pass_context
def clean(ctx):
    """Cleans build."""
    shutil.rmtree(BUILD_DIR, ignore_errors=True)


@cli.command()
@click.pass_context
def build(ctx):
    """Build the lambda package"""
    try:
        venv = subprocess.getoutput('pipenv --venv')
        site_package = glob.glob(
            '{}/lib/python*/site-packages'.format(venv))[0]
    except Exception as e:
        click.echo(
            'Fail to locate python site-packages, '
            'did you run `pipenv install --three`?'
        )
        raise e
    click.echo('Using site-packages in: `{}`'.format(site_package))
    target = os.path.join(BUILD_DIR, 'graphql')
    click.echo('Building into `{}`'.format(target))
    shutil.rmtree(target, ignore_errors=True)
    os.makedirs(target)
    content = []
    for each in BUILD_INCLUDES:
        src = os.path.join(ROOT_DIR, each)
        dst = os.path.join(target, each)
        content.append((src, dst))
    for each in os.listdir(site_package):
        src = os.path.join(site_package, each)
        dst = os.path.join(target, each)
        content.append((src, dst))
    for src, dst in content:
        if _is_exclude_from_build(src):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
        click.echo('  Copied {}'.format(src))


def _is_exclude_from_build(filename):
    filename = os.path.basename(filename)
    for regex in BUILD_DEPENDENCIES_EXCLUDES:
        if regex.match(filename):
            return True
    return False


if __name__ == '__main__':
    cli(obj={})
