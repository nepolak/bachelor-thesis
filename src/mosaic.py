from typing import Any
from svgutils.compose import Unit, Figure, Panel, SVG, Text
import svgutils.transform as sg
from pathlib import Path
from dataclasses import dataclass
from PIL import Image
import numpy as np


class WrappedImage:
    def get_size(self) -> tuple[float, float]:
        raise NotImplementedError()
    
    def get_root(self) -> Any:
        raise NotImplementedError()

class WrappedPngImage(WrappedImage):
    width: float
    height: float
    image_element: sg.ImageElement

    def __init__(self, file_path: Path):
        with open(file_path, "rb") as f_img:
            img = Image.open(f_img)

            self.width = img.size[0]
            self.height = img.size[1]

            f_img.seek(0, 0)

            self.image_element = sg.ImageElement(f_img, self.width, self.height)

    
    def get_size(self):
        return self.width, self.height

    def get_root(self):
        return self.image_element


class WrappedSvgImage(WrappedImage):
    svg_image: sg.SVGFigure

    def __init__(self, file_path: Path):
        self.svg_image = sg.fromfile(str(file_path))

    def get_size(self):
        size = self.svg_image.get_size()

        return Unit(size[0]).value, Unit(size[1]).value

    def get_root(self):
        return self.svg_image.getroot()


def create_hanging_text(content: str, text_left_offset, text_top_offset, size=4, weight='bold'):
    text = Text(content, text_left_offset, text_top_offset, size=size, weight=weight)

    text.root.attrib["dominant-baseline"] = "hanging"

    return text



def arrange_two(file_one: WrappedImage, file_two: WrappedImage, spacing: float = 0):
    width = Unit("210mm")

    available_block_width = (width.value - spacing) / 2

    first_width, first_height = file_one.get_size()
    second_width, second_height = file_two.get_size()

    first_factor = available_block_width / first_width
    second_factor = available_block_width / second_width

    first_target_height = first_factor * first_height
    second_target_height = second_factor * second_height

    height = Unit(str(max(first_target_height, second_target_height)) + width.unit)

    text_left_offset = width.value * 0.008
    text_top_offset = height.value * 0.012

    file_one_root = file_one.get_root()
    file_one_root.moveto(0, 4, first_factor)

    file_two_root = file_two.get_root()
    file_two_root.moveto(0, 4, first_factor)

    Figure(str(width), str(height), 
            Panel(
                file_one_root,
                create_hanging_text("A", text_left_offset, text_top_offset, 4, "bold")),
            Panel(
                file_two_root,
                create_hanging_text("B", text_left_offset, text_top_offset, 4, "bold"),
                ).move(available_block_width + spacing, 0)
        ).save("panel.svg")
    
def arrange_two_to_height(out_name: str, file_one: WrappedImage, file_two: WrappedImage, spacing: float = 0):
    width = Unit("210mm")

    first_width, first_height = file_one.get_size()
    second_width, second_height = file_two.get_size()

    widths = np.array([first_width, second_width])

    target_height = min(first_height, second_height)

    height_factors = np.array([
        target_height / first_height,
        target_height / second_height
    ])

    width_factor = (width.value - spacing) / sum(widths * height_factors)

    eff_widths = (widths * height_factors) * width_factor

    height = Unit(str(target_height * width_factor + 4) + width.unit)

    text_left_offset = width.value * 0.008
    text_top_offset = height.value * 0.012

    file_one_root = file_one.get_root()
    file_one_root.moveto(0, 4, height_factors[0] * width_factor)

    file_two_root = file_two.get_root()
    file_two_root.moveto(0, 4, height_factors[1] * width_factor)

    Figure(str(width), str(height), 
            Panel(
                file_one_root,
                create_hanging_text("A", text_left_offset, text_top_offset, 4, "bold")
                ),
            Panel(
                file_two_root,
                create_hanging_text("B", text_left_offset, text_top_offset, 4, "bold"),
                ).move(eff_widths[0] + spacing, 0)
        ).save(out_name)

def arrange_four(out_name: str, files: tuple[WrappedImage, WrappedImage, WrappedImage, WrappedImage], spacing: float = 0):
    width = Unit("210mm")

    available_block_width = (width.value - spacing) / 2

    sizes = [a.get_size() for a in files]
    
    factors = [available_block_width / a[0] for a in sizes]
    target_heights = [factor * size[1] for factor, size in zip(factors, sizes)]

    available_block_height = max(target_heights)

    height = Unit(str(available_block_height * 2 + spacing + 2 * 4) + width.unit)

    text_left_offset = width.value * 0.008
    text_top_offset = height.value * 0.008

    files_roots = []

    for i, file in enumerate(files):
        root = file.get_root()
        root.moveto(0, 4, factors[i])

        files_roots.append(root)


    places = [
        (0, 0),
        (available_block_width + spacing, 0),
        (0, available_block_height + spacing + 4),
        (available_block_width + spacing, available_block_height + spacing + 4),
    ]


    labels = ["A", "B", "C", "D"]

    panels = [
        Panel(
            root, 
            create_hanging_text(labels[i], text_left_offset, text_top_offset, 4, "bold"))
            .move(*places[i]) for i, root in enumerate(files_roots)]

    Figure(str(width), str(height),*panels).save(out_name)