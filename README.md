<!--
to installl a package from a local path
pip install -e PATH
https://pythonhosted.org/an_example_pypi_project/sphinx.html
-->

# Dependency Manager
[![current](https://img.shields.io/badge/version-1.0.0rc0-brightgreen.svg)](https://pypi.org/project/simplestRPC/) :green_heart:
[![license](https://img.shields.io/badge/license-zlib-brightgreen.svg)](https://www.zlib.net/zlib_license.html)
[![python](https://img.shields.io/badge/python-3.6+-brightgreen.svg)](https://python.org)

Dependency Manager comes to resolve the lack of a **good development/production dependency management** in python pip daily use.

With this tool you're gonna be able to add development and production dependencies to your project in separeted. Once the package can exports all requirements to a file in particular **without losing any compatibility** with who only use pip. Also it differentiates packages which your project is directly dependent on, from its dependency tree.

### Getting Started
```shell
# you can install it globaly
sudo pip install dependencymanager
## this way you're gonna have dependencymanager globaly to use in all your projects

# or

# localy, but remembet to add it as development dependency ;)
pip install virtualenv
virtualenv --python=python3 .virenv
source .virenv/bin/activate

pip install dependencymanager
python -m dependecymanager init
python -m dependecymanager move --name=dependencymanager
python -m dependecymanager export
## this way dependency manager will be contained in a specify project,
## and will be installed only in development environment.
## if you want it not to stay in production, just do execute the 'move' command.
```

### Comands:
##### List
|   Command     |                     Description                   |
| ------------  | ------------------------------------------------  |
|     init      | create DM environment tree from existente installed |
| i - install   | Install the project or an specific dependecy  |
| u - uninstall | Uninstall required package and its dependency. Maintaining possible cross dependencies with other packages, moving them if necessary, and updating the tree.  |
|   f - info    | Get info about the requested pack.  |
|   m - move    | Move package between environments, production for developer and vice versa. |
| mh - makehead | Make the given package head. That is, the project is now directly dependent on this package.  |
| ex - export   | Export requirements files. |

##### Flags
| Command  |      Flag     |        Description        |
| -------- | ------------- | ------------------------- |
| install  | with no flag | install the dev or prod tree: *according to --dev flag*. |
| install  |   -n --name   | name of the package to install. |
| install  | -v --version  | version to install. leave empty for latest. |
| install  |    -d --dev   | Install as dev dependency? **Default is False**. |
| uninstall|   -n --name   | name of the package to uninstall. |
|   info   |   -n --name   | name of the package to get info. |
|   info   |   -e --extra  | Brings all information available about the package, including disponible versions. |
|   move   |   -n --name   | name of the package to move. |
| makehead |   -n --name   | name of the package to make head. |
| makehead |  -rm --remove | "Undead" the given pack, removing the 'head' status from it. **Default is False**. |

### WARNING:
As the package is still not fully released there are two things you might want to consider:

- Dependency Manager **still does not supports locally installed packages**. It's a rare but possible case of use for pip. So if you, for any reason, need to deal with this kind of approach in your project, Dependency Manager is still not the tool for you. Although adding such support is fairly easy from the point we are, and **this will be present in a future full release version**.
- The package **craetes 3 files** in you'r current directory: **dmtree.json, requirements.txt and dev_requirements.txt**. **There's still not how to custom these names**, Although adding such feature is fairly easy too, and **will be present in a future full release**.


##### See also
- [Varenv](https://github.com/davincif/varenv) project: A simple way to mock your environment variables during development.
- [SimplestRPC](https://github.com/davincif/simplestRPC) project: A simple RPC for python - *study project*.
