# Image Processing

图片处理 Python 工具集，支持缩放、压缩、格式转换、水印、拼接、GIF/PDF 生成。

## 安装依赖

```bash
pip install wand tinify
brew install imagemagick
```

## 配置

通过环境变量设置：

| 环境变量 | 用途 | 必填 |
|----------|------|------|
| `FONT_PATH` | 水印字体路径 | 水印功能需要 |
| `TINIFY_KEY` | TinyPNG API 密钥 | 压缩功能需要 |

## 使用

### 命令行

```bash
# 查看图片信息
python3 scripts/image_server.py info image.png

# 缩放
python3 scripts/image_server.py resize image.png 800

# 格式转换
python3 scripts/image_server.py convert image.png jpg

# 压缩
python3 scripts/image_server.py compress image.png

# 添加水印
python3 scripts/image_server.py watermark image.png "水印" 0.5 0.9 --color white

# 拼接图片
python3 scripts/image_server.py concat dir/ --direction vertical --spacing 10

# 生成 GIF
python3 scripts/image_server.py gif dir/ --frame-delay 500

# 生成 PDF
python3 scripts/image_server.py pdf dir/
```

### Python API

```python
from scripts.image_server import resize_image, add_watermark, generate_pdf

# 缩放
resize_image("image.png", width=800)

# 添加水印
add_watermark("image.png", "Watermark", pos_x=0.5, pos_y=0.9, color="white", fontsize=24)

# 合并为 PDF
generate_pdf("images_dir/")
```

## 所有功能

| 函数 | 说明 |
|------|------|
| `get_images_from_dir` | 列出目录下所有图片 |
| `get_image_information` | 获取图片宽高、格式、大小 |
| `resize_image` | 按宽度缩放，高度等比 |
| `format_convert` | 转换图片格式 |
| `compress` | TinyPNG 压缩 |
| `concatenate_images` | 拼接多张图片 |
| `add_watermark` | 添加文字水印 |
| `generate_gif` | 生成 GIF 动图 |
| `generate_pdf` | 合并为 PDF |