---
name: imageprocessing
description: >
  Image processing utilities for resize, compress, format convert, watermark,
  concatenate, GIF and PDF generation. Triggers on requests like: "resize this image",
  "compress these images", "convert PNG to JPG", "add a watermark", "make a GIF",
  "generate a PDF from images", "拼接图片", "压缩图片", "调整图片大小",
  "图片格式转换", "添加水印", "生成gif", "生成pdf", "获取图片信息", "图片处理".
---

# Image Processing

## Overview

图片处理工具，代码位于 `scripts/image_server.py`，可作为 Python 模块导入或命令行使用。

## Setup

### Dependencies

```bash
pip install wand tinify
```

需要 ImageMagick：

- **macOS**: `brew install imagemagick`
- **Windows**: [下载安装包](https://imagemagick.org/script/download.php#windows)
- **Linux**: `sudo apt install imagemagick`

### Configuration

通过环境变量配置：

| 环境变量 | 用途 | 默认值 |
|----------|------|--------|
| `FONT_PATH` | 水印中文字体文件路径 | 无 |
| `TINIFY_KEY` | TinyPNG API 密钥（推荐） | 无 |
| `TINIFY_CONFIG_PATH` | TinyPNG 配置文件路径（备选） | 无 |

`TINIFY_KEY` 优先级高于 `TINIFY_CONFIG_PATH`。配置文件格式：

```ini
[tinify]
key = YOUR_TINYPNG_API_KEY
```

### CLI Usage

```bash
python3 scripts/image_server.py info path/to/image.png
python3 scripts/image_server.py resize path/to/image.png 800
python3 scripts/image_server.py convert path/to/image.png jpg
python3 scripts/image_server.py compress path/to/image.png
python3 scripts/image_server.py watermark path/to/image.png "水印文字" 0.5 0.9 --color white
python3 scripts/image_server.py concat path/to/dir --direction vertical --spacing 10
python3 scripts/image_server.py gif path/to/dir --frame-delay 500
python3 scripts/image_server.py pdf path/to/dir
```

## Python API

| 函数 | 用途 |
|------|------|
| `get_images_from_dir(dir)` | 列出目录下所有图片 |
| `get_image_information(path)` | 获取图片宽高、格式、大小 |
| `resize_image(path, width)` | 按宽度缩放，高度等比 |
| `format_convert(path, format)` | 转换图片格式 |
| `compress(path)` | TinyPNG 压缩 |
| `concatenate_images(inputs, direction, bg_color, spacing)` | 拼接多张图片 |
| `add_watermark(path, text, pos_x, pos_y, color, fontsize)` | 添加文字水印 |
| `generate_gif(inputs, frame_delay)` | 生成 GIF 动图 |
| `generate_pdf(inputs)` | 合并为 PDF |

## Quick Reference

### Get image info
```python
get_image_information("path/to/image.png")
```

### Resize
```python
resize_image("path/to/image.png", width=800)
```

### Convert format
```python
format_convert("path/to/image.png", "jpg")
```

### Compress
```python
compress("path/to/image.png")
# or a directory:
compress("path/to/images_dir")
```

### Add watermark
```python
add_watermark(
    "path/to/image.png",
    "My Watermark",
    pos_x=0.5,    # 0=left, 1=right
    pos_y=0.9,    # 0=top, 1=bottom
    color="white",
    fontsize=24,
)
```

### Concatenate images
```python
concatenate_images(
    "path/to/images_dir",   # or a list of paths
    direction="horizontal", # or "vertical"
    bg_color="white",
    spacing=10,
)
```

### Generate GIF
```python
generate_gif("path/to/images_dir", frame_delay=500)
```

### Generate PDF
```python
generate_pdf("path/to/images_dir")
```

## Common Workflows

### Prepare images for sharing (resize + watermark)
1. `resize_image` to desired width
2. `add_watermark` on the resized output

### Batch convert and compress
1. `get_images_from_dir` to list images
2. For each: `format_convert` then `compress`

### Create a presentation deck from images
1. Optionally `resize_image` each to uniform width
2. `generate_pdf` to combine into a single PDF

### Create an animated GIF
1. `get_images_from_dir` to verify images and order
2. `generate_gif` with appropriate `frame_delay`

## Important Notes

- 所有函数返回处理后文件的路径，可用于后续操作链式调用。
- `compress` 使用 TinyPNG API，需配置密钥。
- `resize_image` 只需宽度，高度自动等比计算。
- `add_watermark` 位置参数为相对值 (0.0–1.0)，非绝对像素。
- `generate_gif` 和 `generate_pdf` 接受目录路径或文件路径列表。
- `concatenate_images` 传入目录时按文件名排序处理。