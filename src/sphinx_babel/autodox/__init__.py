# Copyright 2024 Ekumen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An Sphinx extension to generate and embed Doxygen documentation.

This extension introduces an `autodox` directive that relies on
:mod:`doxysphinx` to provide :mod:`sphinx.ext.autosummary` like
behavior.
"""

import os
import pathlib
import subprocess
import pkg_resources

from typing import Any, Dict

from doxysphinx.doxygen import ConfigDict, read_doxyconfig
from sphinx.application import Sphinx
import sphinx.util.logging


logger = sphinx.util.logging.getLogger(__name__)


class DoxygenConfig(ConfigDict):
    """In-memory Doxygen configuration."""

    @classmethod
    def read_from(
        cls,
        doxyfile_path: os.PathLike,
        doxygen_exe: str,
        cwd: os.PathLike
    ) -> 'DoxygenConfig':
        """
        Read configuration from file, fetching defaults from a dry Doxygen invocation.

        :param doxyfile_path: path to Doxyfile.
        :paran doxygen_exe: Doxygen executable name.
        :param cwd: working directory for Doxygen.
        :returns: configuration read.
        """
        cwd = pathlib.Path(cwd)
        doxyfile_path = pathlib.Path(doxyfile_path)
        return DoxygenConfig(read_doxyconfig(doxyfile_path, doxygen_exe, cwd))

    def write_to(self, doxyfile_path: os.PathLike) -> None:
        """Write configuration to file."""
        dquote = (lambda s: f'"{s}"')
        escape = (lambda s: s.replace('"', '\"'))
        with pathlib.Path(doxyfile_path).open('w') as f:
            for name, values in self.items():
                if isinstance(values, list):
                    values = ' '.join(map(dquote, map(escape, map(str, values))))
                else:
                    values = dquote(escape(str(values)))
                f.write(f'{name} = {values}\n')


def conforming_doxyconfig_defaults() -> DoxygenConfig:
    """Compute Doxygen configuration defaults that conform with `doxysphinx` requirements."""
    doxygen_awesome_css_path = pkg_resources.resource_filename(
        'sphinx_babel.autodox', 'themes/doxygen-awesome-css/doxygen-awesome.css'
    )
    return DoxygenConfig({
        'GENERATE_TREEVIEW': 'NO',
        'DISABLE_INDEX': 'NO',
        'SEARCHENGINE': 'NO',
        'GENERATE_HTML': 'YES',
        'CREATE_SUBDIRS': 'NO',
        'DOT_IMAGE_FORMAT': 'svg',
        'DOT_TRANSPARENT': 'YES',
        'INTERACTIVE_SVG': 'YES',
        'HTML_EXTRA_STYLESHEET': doxygen_awesome_css_path
    })


def generate_doxygen_documentation(app: Sphinx) -> None:
    """Generate embeddable Doxygen documentation for the given `app`."""
    if app.builder.format != 'html':
        msg = '[autodox] %s output not supported, ignoring'
        logger.info(msg, app.builder.format)
        return

    source_path = pathlib.Path(app.srcdir).resolve()
    output_path = pathlib.Path(app.outdir).resolve()

    for project, settings in app.config.autodox_projects.items():
        logger.info('[autodox] processing %s', project)

        if isinstance(settings, str):
            settings = {'srcdir': settings}

        doxygen_output_path = source_path / pathlib.Path(
            settings.get('outdir', pathlib.Path(app.config.autodox_outdir) / project))
        doxygen_output_path.mkdir(parents=True, exist_ok=True)

        doxygen_source_path = source_path / pathlib.Path(settings.get('srcdir', '.'))

        doxyconfig = DoxygenConfig.read_from(
            doxygen_source_path / settings.get('doxyfile', 'Doxyfile'),
            settings.get('doxygen_exe', 'doxygen'), doxygen_source_path
        )

        doxygen_html_output_path = doxygen_output_path / doxyconfig['HTML_OUTPUT']
        doxygen_tagfile_path = doxygen_html_output_path / 'tagfile.xml'

        if not settings.get('conforming', False):
            doxyconfig.update(conforming_doxyconfig_defaults())
        doxyconfig['OUTPUT_DIRECTORY'] = doxygen_output_path
        doxyconfig['GENERATE_TAGFILE'] = doxygen_tagfile_path
        if 'tagfiles' in settings:
            tagfiles = doxyconfig.get('TAGFILES', [])
            for tagfile, sitepath in settings['tagfiles']:
                tagfile = os.path.relpath(source_path / tagfile, doxygen_source_path)
                sitepath = os.path.relpath(source_path / sitepath, doxygen_html_output_path)
                tagfiles.append(f"{tagfile}={sitepath}")
            doxyconfig['TAGFILES'] = tagfiles

        doxyfile_path = doxygen_output_path / f'{project}.Doxyfile'

        doxyconfig.write_to(doxyfile_path)

        subprocess.check_call(['doxygen', doxyfile_path], cwd=doxygen_source_path)

        subprocess.check_call([
            'doxysphinx', 'build', source_path, output_path, doxygen_html_output_path
        ], cwd=doxygen_source_path)


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up ``autodox`` extension."""
    app.add_config_value('autodox_outdir', '_doxygen', 'env')
    app.add_config_value('autodox_doxygen_exe', 'doxygen', 'env')
    app.add_config_value('autodox_projects', {}, 'env')
    app.connect('builder-inited', generate_doxygen_documentation, priority=0)

    return {'version': '0.1.0', 'parallel_read_safe': True, 'parallel_write_safe': True}
