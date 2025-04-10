#!/usr/bin/env python

"""Configuring custom git hook path
Creating a separate folder .githooks in the root directory of the project
and add all the hooks there (i.e. pre-commit, prepare-commit-msg, commit-msg, etc.).

Next to update the configurations so that git knows where our hooks:

`git config --global core.hooksPath .githooks`
"""

# import os
# from typing import Callable, Any
#
#
# # def main():
# #     poetry_config = os.path.abspath('pyproject.toml')
# #     # poetry_config = os.path.abspath("../pyproject.toml")
# #
# #     with open(poetry_config) as handle:
# #         lines = handle.readlines()
# #
# #     i = 0
# #     for line in lines:
# #         ind = line.find("=")
# #         key = line[:ind].strip()
# #         value = line[ind + 1:].strip()
# #
# #         if ind > 0 and key == "version":
# #             version = list(map(int, value.strip('"').split(".")))
# #             version[2] += 1
# #             __version__ = ".".join(map(str, version))
# #             lines[i] = line.replace(value, f'"{__version__}"')
# #             break
# #
# #         i += 1
# #
# #     with open(poetry_config, "w", newline="\n") as handle:
# #         for line in lines:
# #             handle.writelines(line)
# #
# #
# # if __name__ == "__main__":
# #     main()
#
#
# def get_conf_value(path: str, key: str) -> tuple[str | None, list[str]]:
#     with open(path) as handle:
#         lines = handle.readlines()
#
#     for line in lines:
#         _ind = line.find("=")
#         _key = line[:_ind].strip()
#         _val = line[_ind + 1:].strip()
#
#         if _ind > 0 and _key == key:
#             return _val, lines
#
#     return None, []
#
#
# def set_conf_value(path: str, key: str, value: str | Callable[[str, Any], str], *options: Any) -> None:
#     # _val, lines = get_conf_value(path, key)
#     # if _val is not None:
#     #     __val = ""
#     #     if isinstance(value, str):
#     #         __val = value
#     #     elif isinstance(value, Callable):
#     #         __val = value(_val, **options)
#     #     else:
#     #         raise TypeError("error")
#     #
#     #     lines[i] = lines[i].replace(_val, __val)
#
#     with open(path) as handle:
#         lines = handle.readlines()
#
#     i = 0
#     for line in lines:
#         _ind = line.find("=")
#         _key = line[:_ind].strip()
#         _val = line[_ind + 1:].strip()
#
#         if _ind > 0 and _key == key:
#             if isinstance(value, str):
#                 lines[i] = line.replace(_val, value)
#             elif callable(value):
#                 lines[i] = line.replace(_val, value(_val, *options))
#             else:
#                 raise TypeError("error")
#             break
#         i += 1
#
#     with open(path, "w", newline="\n") as handle:
#         for line in lines:
#             handle.writelines(line)
#
#
# # MAJOR.MINOR.PATCH
# def increase_version(value: str, numeric: int = 2) -> str:
#     if numeric < 0 or numeric > 2:
#         raise IndexError("error")
#
#     tag = list(map(int, value.strip('"').split(".")))
#     tag[numeric] += 1
#
#     match numeric:
#         case 1:
#             tag[2] = 0
#         case 0:
#             tag[2] = tag[1] = 0
#
#     return f'"{".".join(map(str, tag))}"'

# set_conf_value(os.path.abspath("../pyproject.toml"), "version", increase_version)
# set_conf_value(os.path.abspath("../pyproject.toml"), "version", increase_version, w=0)
