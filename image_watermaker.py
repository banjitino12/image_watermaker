import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
from datetime import datetime

# 支持的图片格式
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png']

# 水印位置映射
POSITION_MAP = {
    'top-left': 'top-left',
    'center': 'center',
    'bottom-right': 'bottom-right',
}

def get_exif_datetime(img_path):
    try:
        image = Image.open(img_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                # 格式如 '2023:09:24 12:34:56'
                try:
                    dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    return dt.strftime('%Y-%m-%d')
                except Exception:
                    return None
        return None
    except Exception:
        return None

def add_watermark(img_path, output_path, text, font_size, color, position):
    image = Image.open(img_path).convert('RGBA')
    width, height = image.size
    # 字体路径可根据实际环境调整
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except Exception:
        font = ImageFont.load_default()
    txt_layer = Image.new('RGBA', image.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)
    text_width, text_height = draw.textsize(text, font=font)
    # 计算位置
    if position == 'top-left':
        x, y = 10, 10
    elif position == 'center':
        x = (width - text_width) // 2
        y = (height - text_height) // 2
    elif position == 'bottom-right':
        x = width - text_width - 10
        y = height - text_height - 10
    else:
        x, y = 10, 10
    draw.text((x, y), text, font=font, fill=color+(128,))  # 半透明
    watermarked = Image.alpha_composite(image, txt_layer)
    # 保存
    watermarked = watermarked.convert('RGB')
    watermarked.save(output_path)

def process_images(input_path, font_size, color, position):
    if os.path.isfile(input_path):
        files = [input_path]
        base_dir = os.path.dirname(input_path)
    else:
        files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                 if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]
        base_dir = input_path
    output_dir = base_dir + '_watermark'
    os.makedirs(output_dir, exist_ok=True)
    for file in files:
        dt = get_exif_datetime(file)
        if not dt:
            print(f'跳过无拍摄时间的图片: {file}')
            continue
        filename = os.path.basename(file)
        output_path = os.path.join(output_dir, filename)
        add_watermark(file, output_path, dt, font_size, color, position)
        print(f'已处理: {output_path}')

def parse_color(color_str):
    # 支持 #RRGGBB 或常见英文
    if color_str.startswith('#') and len(color_str) == 7:
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        return (r, g, b)
    # 可扩展更多颜色名
    color_dict = {
        'red': (255,0,0), 'green': (0,255,0), 'blue': (0,0,255),
        'white': (255,255,255), 'black': (0,0,0)
    }
    return color_dict.get(color_str.lower(), (255,255,255))

def main():
    parser = argparse.ArgumentParser(description='批量图片水印工具')
    parser.add_argument('--path', required=True, help='图片文件或目录路径')
    parser.add_argument('--font-size', type=int, default=32, help='字体大小，默认32')
    parser.add_argument('--color', type=str, default='#FFFFFF', help='字体颜色，支持#RRGGBB或red/blue等')
    parser.add_argument('--position', type=str, default='bottom-right', choices=POSITION_MAP.keys(), help='水印位置')
    args = parser.parse_args()
    color = parse_color(args.color)
    process_images(args.path, args.font_size, color, args.position)

if __name__ == '__main__':
    main()
