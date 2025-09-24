# 自动化测试脚本：批量处理 test_imgs 下图片并移动结果到 result_imgs
import os
import shutil
import subprocess

def run_watermark():
    # 执行水印命令
    cmd = [
        'python', 'image_watermaker.py',
        '--path', 'test_images',
        '--font-size', '32',
        '--color', '#FF0000',
        '--position', 'bottom-right'
    ]
    print('运行命令:', ' '.join(cmd))
    subprocess.run(cmd, check=True)

def move_results():
    src_dir = 'test_images_watermark'
    dst_dir = 'result_images'
    os.makedirs(dst_dir, exist_ok=True)
    for fname in os.listdir(src_dir):
        src_file = os.path.join(src_dir, fname)
        dst_file = os.path.join(dst_dir, fname)
        shutil.move(src_file, dst_file)
        print(f'已移动: {dst_file}')

def main():
    run_watermark()
    move_results()
    print('全部处理完成！')

if __name__ == '__main__':
    main()
