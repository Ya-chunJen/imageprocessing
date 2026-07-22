import os
import pathlib
import configparser
from typing import Union, List

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import tinify

# ── 配置（通过环境变量设置）────────────────────────────────────────────
font_path = os.environ.get("FONT_PATH", "")
tinify_key = os.environ.get("TINIFY_KEY", "")
if tinify_key:
    tinify.key = tinify_key
else:
    config_path = os.environ.get("TINIFY_CONFIG_PATH", "")
    if config_path and os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        tinify.key = config["tinify"]["key"]

# ── 工具函数 ────────────────────────────────────────────────────────────


def _outpath(image_path: str, add_str: str, target_format: str = "") -> str:
    image_path_obj = pathlib.Path(image_path)
    image_dir = image_path_obj.parent
    image_name = image_path_obj.stem
    if target_format:
        return f"{image_dir}/{image_name}-{add_str}.{target_format}"
    return f"{image_dir}/{image_name}-{add_str}{image_path_obj.suffix}"


import sys
import subprocess


def _show_image(image_path: str, open_app: str = "default"):
    if sys.platform == "darwin":
        if open_app == "default":
            subprocess.run(["open", image_path])
        else:
            subprocess.run(["open", "-a", open_app, image_path])
    elif sys.platform == "win32":
        os.startfile(image_path)
    else:
        if open_app == "default":
            subprocess.run(["xdg-open", image_path])
        else:
            subprocess.run([open_app, image_path])


# ── 图片处理函数 ─────────────────────────────────────────────────────────


def get_images_from_dir(images_dir: str) -> list:
    """获取指定目录下的所有图片文件，并根据文件名排序。"""
    if not os.path.exists(images_dir):
        return []
    image_files = list(pathlib.Path(images_dir).glob("*.png"))
    image_files.extend(pathlib.Path(images_dir).glob("*.jpg"))
    image_files.extend(pathlib.Path(images_dir).glob("*.jpeg"))
    image_files.extend(pathlib.Path(images_dir).glob("*.PNG"))
    return [str(f) for f in sorted(image_files)]


def get_image_information(image_path: str) -> str:
    """获取图片的宽度、高度、格式、大小信息。"""
    with Image(filename=image_path) as img:
        return f"图片宽度: {img.width}, 图片高度: {img.height}, 图片格式: {img.format}, 图片大小: {img.size}。"


def resize_image(image_path: str, width: int) -> str:
    """调整图片宽度，高度等比例缩放。"""
    with Image(filename=image_path) as img:
        img.resize(width, int(width * img.height / img.width))
        outfilename = _outpath(image_path, "resize")
        img.save(filename=outfilename)
        _show_image(outfilename)
    return f"图片已调整到{width}像素宽度，处理后的图片保存到:{outfilename}"


def format_convert(image_path: str, target_format: str) -> str:
    """转换图片格式。"""
    with Image(filename=image_path) as img:
        img.format = target_format
        outfilename = _outpath(image_path, "convert", target_format)
        img.save(filename=outfilename)
        _show_image(outfilename)
    return f"图片已转换为{target_format}格式，处理后的图片保存到:{outfilename}"


def compress(image_path: str) -> str:
    """压缩图片或目录下所有图片（使用 TinyPNG）。"""
    outfilename = _outpath(image_path, "compress")
    source = tinify.from_file(image_path)
    source.to_file(outfilename)
    _show_image(outfilename)
    return f"图片已压缩，处理后的图片保存到:{outfilename}"


def concatenate_images(image_inputs: Union[str, list], direction: str = "horizontal",
                       bg_color: str = "white", spacing: int = 0) -> str:
    """将多张图片拼接为一张图片。"""
    if isinstance(image_inputs, str):
        image_paths = get_images_from_dir(image_inputs)
    elif isinstance(image_inputs, list):
        image_paths = image_inputs
    else:
        return "输入参数类型错误"

    if not image_paths:
        return "目录不存在或目录下无有效图片格式（jpeg/jpg/png）文件！"

    images = [Image(filename=path) for path in image_paths]

    if direction == "horizontal":
        total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
        total_height = max(img.height for img in images)
    else:
        total_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + spacing * (len(images) - 1)

    with Image(width=total_width, height=total_height, background=bg_color) as canvas:
        x_offset, y_offset = 0, 0
        for img in images:
            canvas.composite(img, left=x_offset, top=y_offset)
            if direction == "horizontal":
                x_offset += img.width + spacing
            else:
                y_offset += img.height + spacing
        outfilename = _outpath(image_paths[0], "concatenate")
        canvas.save(filename=outfilename)
        _show_image(outfilename)
    return f"图片已拼接，处理后的图片保存到:{outfilename}"


def add_watermark(image_path: str, watermark_text: str, pos_x: float, pos_y: float,
                  color: str = "red", fontsize: int = 20) -> str:
    """给图片添加文字水印。pos_x/pos_y 为相对位置（0-1）。"""
    with Image(filename=image_path) as img:
        draw = Drawing()
        if font_path:
            draw.font = font_path
        draw.font_size = fontsize
        draw.fill_color = Color(color)
        draw.text(int(img.width * pos_x), int(img.height * pos_y), watermark_text)
        draw.draw(img)
        outfilename = _outpath(image_path, "watermark")
        img.save(filename=outfilename)
        _show_image(outfilename)
    return f"图片已添加水印，处理后的图片保存到:{outfilename}"


def generate_gif(image_inputs: Union[str, List[str]], frame_delay: int = 1000) -> str:
    """将多张图片生成为 GIF 动图。frame_delay 单位为毫秒。"""
    if isinstance(image_inputs, str):
        image_paths = get_images_from_dir(image_inputs)
        images_dir = image_inputs
    elif isinstance(image_inputs, list):
        image_paths = image_inputs
        images_dir = os.path.dirname(image_paths[0])
    else:
        return "输入参数类型错误"

    if not image_paths:
        return "目录不存在或目录下无有效图片格式（jpeg/jpg/png）文件！"

    with Image() as gif:
        for image_file in image_paths:
            with Image(filename=image_file) as img:
                gif.sequence.append(img)
        gif.format = "gif"
        gif.delay = frame_delay
        outfilename = os.path.join(images_dir, "output.gif")
        gif.save(filename=outfilename)
        _show_image(outfilename, "Google Chrome")
    return f"GIF图已生成，保存到: {outfilename}"


def generate_pdf(image_inputs: Union[str, list]) -> str:
    """将多张图片合并为一个 PDF 文件。"""
    if isinstance(image_inputs, str):
        image_paths = get_images_from_dir(image_inputs)
        images_dir = image_inputs
    elif isinstance(image_inputs, list):
        image_paths = image_inputs
        images_dir = os.path.dirname(image_paths[0])
    else:
        return "输入参数类型错误"

    if not image_paths:
        return "目录不存在或目录下无有效图片格式（jpeg/jpg/png）文件！"

    with Image() as pdf:
        for image_file in image_paths:
            with Image(filename=image_file) as img:
                pdf.sequence.append(img)
        pdf.format = "pdf"
        outfilename = os.path.join(images_dir, "output.pdf")
        pdf.save(filename=outfilename)
        _show_image(outfilename, "Google Chrome")
    return f"PDF文档已生成，保存到: {outfilename}"




# ── 命令行入口 ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="图片处理工具")
    subparsers = parser.add_subparsers(dest="command")

    # info
    p = subparsers.add_parser("info")
    p.add_argument("image_path")

    # resize
    p = subparsers.add_parser("resize")
    p.add_argument("image_path")
    p.add_argument("width", type=int)

    # convert
    p = subparsers.add_parser("convert")
    p.add_argument("image_path")
    p.add_argument("target_format")

    # compress
    p = subparsers.add_parser("compress")
    p.add_argument("image_path")

    # watermark
    p = subparsers.add_parser("watermark")
    p.add_argument("image_path")
    p.add_argument("text")
    p.add_argument("pos_x", type=float)
    p.add_argument("pos_y", type=float)
    p.add_argument("--color", default="red")
    p.add_argument("--fontsize", type=int, default=20)

    # concat
    p = subparsers.add_parser("concat")
    p.add_argument("image_inputs", nargs="+")
    p.add_argument("--direction", default="horizontal")
    p.add_argument("--bg-color", default="white")
    p.add_argument("--spacing", type=int, default=0)

    # gif
    p = subparsers.add_parser("gif")
    p.add_argument("image_dir")
    p.add_argument("--frame-delay", type=int, default=1000)

    # pdf
    p = subparsers.add_parser("pdf")
    p.add_argument("image_dir")

    args = parser.parse_args()

    commands = {
        "info": lambda: print(get_image_information(args.image_path)),
        "resize": lambda: print(resize_image(args.image_path, args.width)),
        "convert": lambda: print(format_convert(args.image_path, args.target_format)),
        "compress": lambda: print(compress(args.image_path)),
        "watermark": lambda: print(add_watermark(args.image_path, args.text, args.pos_x, args.pos_y, args.color, args.fontsize)),
        "concat": lambda: print(concatenate_images(args.image_inputs, args.direction, args.bg_color, args.spacing)),
        "gif": lambda: print(generate_gif(args.image_dir, args.frame_delay)),
        "pdf": lambda: print(generate_pdf(args.image_dir)),
    }

    if args.command in commands:
        commands[args.command]()
    else:
        parser.print_help()