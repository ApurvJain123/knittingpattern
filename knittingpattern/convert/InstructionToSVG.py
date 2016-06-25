"""This module maps instructions to SVG.

Use :func:`default_instructions_to_SVG` to load the svg files provided by
this package.
"""
import os
import xmltodict
from knittingpattern.Loader import PathLoader


REPLACE_IN_DEFAULT_SVG = "{instruction.type}"


class InstructionToSVG(object):
    """This class maps instructions to SVGs."""

    @property
    def _loader_class(self):
        """:return: the loader to load svgs from different locations
        :rtype: knittingpattern.Loader.PathLoader"""
        return PathLoader

    def __init__(self):
        """create a InstructionToSVG object without arguments"""
        self._instruction_type_to_file_content = {}

    @property
    def load(self):
        """:return: a loader object that allows loading SVG files from
          various sources such as files and folders.
        :rtype: knittingpattern.Loader.PathLoader

        Examples:

        - ``instruction_to_svg.load.path(path)`` loads an SVG from a file named
          path
        - ``instruction_to_svg.load.folder(path)`` loads all SVG files for
          instructions in the folder recursively.
          If multiple files have the same name, the last occurrence is used.

        """
        return self._loader_class(self._process_loaded_object)

    def _process_loaded_object(self, path):
        """process the :paramref:`path`

        :param str path: the path to load an svg from
        """
        file_name = os.path.basename(path)
        name = os.path.splitext(file_name)[0]
        with open(path) as file:
            string = file.read()
            self._instruction_type_to_file_content[name] = string

    def instruction_to_svg_dict(self, instruction):
        """
        :return: an xml-dictionary with the same content as
          :meth:`instruction_to_svg`
        """
        instruction_type = instruction.type
        if instruction_type in self._instruction_type_to_file_content:
            svg = self._instruction_type_to_file_content[instruction_type]
            return self._set_fills_in_color_layer(svg, instruction.color)
        return self.default_instruction_to_svg_dict(instruction)

    def instruction_to_svg(self, instruction):
        """:return: an SVG representing the instruction

        The SVG file is determined by the type attribute of the instruction.
        An instruction of type ``"knit"`` is looked for in a file named
        ``"knit.svg"``.

        Every element inside a group labeled ``"color"`` of mode ``"layer"``
        that has a ``"fill"`` style gets this fill replaced by the color of
        the instruction.
        Example of a recangle that gets filled like the instruction:

        .. code:: xml

            <g inkscape:label="color" inkscape:groupmode="layer">
                <rect style="fill:#ff0000;fill-opacity:1;fill-rule:nonzero"
                      id="rectangle1" width="10" height="10" x="0" y="0" />
            </g>

        If nothing was loaded to display this instruction, a default image is
        be generated by :meth:`default_instruction_to_svg`.
        """
        return xmltodict.unparse(self.instruction_to_svg_dict(instruction))

    def _set_fills_in_color_layer(self, svg_string, color):
        """replaces fill colors in ``<g inkscape:label="color"
        inkscape:groupmode="layer">`` with :paramref:`color`

        :param color: a color fill the objects in the layer with
        """
        structure = xmltodict.parse(svg_string)
        if color is None:
            return structure
        layers = structure["svg"]["g"]
        if not isinstance(layers, list):
            layers = [layers]
        for layer in layers:
            if not isinstance(layer, dict):
                continue
            if layer.get("@inkscape:label") == "color" and \
                    layer.get("@inkscape:groupmode") == "layer":
                for key, elements in layer.items():
                    if key.startswith("@") or key.startswith("#"):
                        continue
                    if not isinstance(elements, list):
                        elements = [elements]
                    for element in elements:
                        style = element.get("@style", None)
                        if style:
                            style = style.split(";")
                            processed_style = []
                            for e in style:
                                if e.startswith("fill:"):
                                    e = "fill:" + color
                                processed_style.append(e)
                            style = ";".join(processed_style)
                            element["@style"] = style
        return structure

    def has_svg_for_instruction(self, instruction):
        """:return: whether there is an image for the instruction
        :rtype: bool

        This can be used before :meth:`instruction_to_svg` as it determines
        whether

        - the default value is used (:obj:`False`)
        - or there is a dedicated svg representation (:obj:`True`).

        """
        instruction_type = instruction.type
        return instruction_type in self._instruction_type_to_file_content

    def default_instruction_to_svg(self, instruction):
        """As :meth:`instruction_to_svg` but it only takes the ``default.svg``
        file into account.

        In case no file is found for an instruction in
        :meth:`instruction_to_svg`,
        this method is used to determine the default svg for it.

        The content is created by replacing the text ``{instruction.type}`` in
        the whole svg file named ``default.svg``.

        If no file ``default.svg`` was loaded, an empty string is returned.
        """
        svg_dict = self.default_instruction_to_svg_dict(instruction)
        return xmltodict.unparse(svg_dict)

    def default_instruction_to_svg_dict(self, instruction):
        """Returns an xml-dictionary with the same content as
        :meth:`default_instruction_to_svg`

        If no file ``default.svg`` was loaded, an empty svg-dict is returned.
        """
        instruction_type = instruction.type
        default_type = "default"
        rep_str = "{instruction.type}"
        if default_type not in self._instruction_type_to_file_content:
            return {"svg": ""}
        default_svg = self._instruction_type_to_file_content[default_type]
        default_svg = default_svg.replace(rep_str, instruction_type)
        colored_svg = self._set_fills_in_color_layer(default_svg,
                                                     instruction.color)
        return colored_svg


def default_instructions_to_SVG():
    """load the default set of svg files for instructions

    :return: the default svg files for the instructions in this package
    :rtype: knittingpattern.InstructionToSVG.InstructionToSVG

    """
    instruction_to_SVG = InstructionToSVG()
    instruction_to_SVG.load.relative_folder(__name__, "SVG-Instructions")
    return instruction_to_SVG

__all__ = ["InstructionToSVG", "default_instructions_to_SVG"]
