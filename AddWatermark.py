"""
图片水印添加工具
功能：为图片添加水印，支持自定义水印位置、透明度、大小等参数
作者：Xujmzd
版本：V4.0
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageCms
import os
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_image_watermark(input_image_path, output_image_path, watermark_image_path, opacity, target_width,
                        watermark_ratio, position, output_format, custom_name, keep_original_name, file_index,
                        compression_level, jpeg_quality, jpeg_subsampling, dpi, jpeg_progressive, jpeg_qtables,
                        png_optimize, png_transparency, tiff_compression, webp_lossless):
    """
    为图片添加水印的主要函数
    
    Args:
        input_image_path (str): 输入图片路径
        output_image_path (str): 输出文件夹路径
        watermark_image_path (str): 水印图片路径
        opacity (float): 水印透明度 (0.1-1.0)
        target_width (int): 目标图片宽度
        watermark_ratio (float): 水印大小比例 (0.1-1.0)
        position (str): 水印位置 ("左上", "右上", "左下", "右下", "居中")
        output_format (str): 输出图片格式
        custom_name (str): 自定义输出文件名前缀
        keep_original_name (bool): 是否保留原文件名
        file_index (int): 文件序号（用于不保留原文件名时的命名）
        compression_level (int): PNG压缩级别 (0-9)
        jpeg_quality (int): JPEG质量 (1-100)
        jpeg_subsampling (int): JPEG子采样 (0-2)
        dpi (int): 图片DPI值
        jpeg_progressive (bool): 是否使用渐进式JPEG
        jpeg_qtables (str): JPEG量化表设置
        png_optimize (bool): 是否优化PNG的Huffman编码
        png_transparency (bool): 是否保留PNG透明通道
        tiff_compression (str): TIFF压缩算法
        webp_lossless (bool): 是否使用WebP无损压缩
    
    Returns:
        str: 输出图片的完整路径
    
    Raises:
        RuntimeError: 处理图片时出错
    """
    try:
        # 打开并处理基础图片
        base_image = Image.open(input_image_path)
        
        # 调整图片大小
        aspect_ratio = base_image.width / base_image.height
        if target_width:
            target_height = int(target_width / aspect_ratio)
            base_image = base_image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # 处理水印图片
        watermark = Image.open(watermark_image_path).convert("RGBA")
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda x: int(x * opacity))
        watermark.putalpha(alpha)

        # 调整水印大小
        watermark_width = int(watermark_ratio * (target_width if target_width else base_image.width))
        watermark_height = int(watermark_width * (watermark.height / watermark.width))
        watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)

        # 设置水印位置
        position_map = {
            "左上": (10, 10),
            "右上": (base_image.width - watermark_width - 10, 10),
            "右下": (base_image.width - watermark_width - 10, base_image.height - watermark_height - 10),
            "左下": (10, base_image.height - watermark_height - 10),
            "居中": ((base_image.width - watermark_width) // 2, (base_image.height - watermark_height) // 2)
        }
        watermark_position = position_map.get(position, position_map["左上"])

        # 合并图片
        final_image = base_image.copy()
        final_image.paste(watermark, watermark_position, watermark)

        # 处理输出文件名
        if custom_name == "watermarked_image":
            output_filename = f"watermarked_{os.path.splitext(os.path.basename(input_image_path))[0]}.{output_format.lower()}"
        else:
            if keep_original_name:
                output_filename = f"{custom_name}_{os.path.splitext(os.path.basename(input_image_path))[0]}.{output_format.lower()}"
            else:
                # 使用自增数字
                output_filename = f"{custom_name}_{file_index:03d}.{output_format.lower()}"

        output_path = os.path.join(output_image_path, output_filename)

        # 保存图片
        if output_format.upper() in ['JPG', 'JPEG']:
            final_image = final_image.convert('RGB')
            save_params = {
                'quality': jpeg_quality,
                'optimize': True,
                'subsampling': jpeg_subsampling,
                'progressive': jpeg_progressive,
                'dpi': (dpi, dpi)
            }
            if jpeg_qtables:
                save_params['qtables'] = jpeg_qtables
            final_image.save(output_path, 'JPEG', **save_params)
        elif output_format.upper() == 'PNG':
            if not png_transparency:
                final_image = final_image.convert('RGB')
            save_params = {
                'optimize': png_optimize,
                'compress_level': compression_level,
                'dpi': (dpi, dpi)
            }
            final_image.save(output_path, 'PNG', **save_params)
        elif output_format.upper() == 'TIFF':
            save_params = {
                'compression': tiff_compression,
                'dpi': (dpi, dpi)
            }
            final_image.save(output_path, 'TIFF', **save_params)
        elif output_format.upper() == 'WEBP':
            save_params = {
                'quality': jpeg_quality,
                'lossless': webp_lossless,
                'dpi': (dpi, dpi)
            }
            final_image.save(output_path, 'WEBP', **save_params)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        logger.info(f"Successfully saved watermarked image: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise RuntimeError(f"处理图片时出错：{e}")

def save_settings(settings):
    """保存设置到JSON文件"""
    try:
        settings_path = os.path.join('bin', 'settings.json')
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        logger.info("Settings saved successfully")
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        messagebox.showerror("错误", f"保存设置时出错：{str(e)}")

def load_settings():
    """从JSON文件加载设置"""
    try:
        settings_path = os.path.join('bin', 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return {}

def replace_watermark_image():
    """替换水印图片"""
    try:
        logo_dir = os.path.join('bin', 'logo')
        os.makedirs(logo_dir, exist_ok=True)

        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        
        if file_path:
            new_file_path = os.path.join(logo_dir, 'watermark.png')
            with open(file_path, 'rb') as src, open(new_file_path, 'wb') as dst:
                dst.write(src.read())
            logger.info(f"Watermark image replaced successfully: {new_file_path}")
            messagebox.showinfo("成功", f"水印图片已替换并保存为: {new_file_path}")
            return new_file_path
        else:
            logger.warning("No new watermark image selected")
            messagebox.showwarning("警告", "未选择新的水印图片。")
            return None
    except Exception as e:
        logger.error(f"Error replacing watermark image: {str(e)}")
        messagebox.showerror("错误", f"替换水印图片时出错：{str(e)}")
        return None

class WatermarkApp:
    """水印添加工具的主界面类"""
    
    def __init__(self, root):
        """
        初始化水印添加工具界面
        
        Args:
            root: tkinter主窗口对象
        """
        self.root = root
        self.root.title("图片水印工具 V4.0")
        self.settings = load_settings()
        self.watermark_preview = None  # 添加预览图片变量
        self.setup_ui()
        self.load_saved_settings()  # 加载保存的设置
        self.load_watermark_preview()  # 加载水印预览
        
        # 设置窗口大小和位置
        self.root.geometry("550x1100")  # 调整窗口大小为更窄更高
        self.root.resizable(True, True)  # 允许窗口自由缩放
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('bin/ico/icon.ico')
        except:
            pass

    def load_saved_settings(self):
        """加载保存的设置"""
        if self.settings:
            # 加载输入输出路径
            if 'input_folder' in self.settings:
                self.input_path.delete(0, tk.END)
                self.input_path.insert(0, self.settings['input_folder'])
            if 'output_folder' in self.settings:
                self.output_path.delete(0, tk.END)
                self.output_path.insert(0, self.settings['output_folder'])
            
            # 加载其他参数
            if 'opacity' in self.settings:
                self.opacity.delete(0, tk.END)
                self.opacity.insert(0, str(self.settings['opacity']))
            if 'target_width' in self.settings:
                self.target_width.delete(0, tk.END)
                self.target_width.insert(0, str(self.settings['target_width']))
            if 'watermark_ratio' in self.settings:
                self.watermark_ratio.delete(0, tk.END)
                self.watermark_ratio.insert(0, str(self.settings['watermark_ratio']))
            if 'position' in self.settings:
                self.position_var.set(self.settings['position'])
            if 'custom_name' in self.settings:
                self.custom_name.delete(0, tk.END)
                self.custom_name.insert(0, self.settings['custom_name'])
            if 'output_format' in self.settings:
                self.format_var.set(self.settings['output_format'])
                self.on_format_change()  # 更新压缩级别选项状态
            if 'keep_original_name' in self.settings:
                self.keep_original_name_var.set(self.settings['keep_original_name'])
            if 'compression_level' in self.settings:
                self.compression_var.set(str(self.settings['compression_level']))
            if 'jpeg_quality' in self.settings:
                self.jpeg_quality.delete(0, tk.END)
                self.jpeg_quality.insert(0, str(self.settings['jpeg_quality']))
            if 'jpeg_subsampling' in self.settings:
                self.jpeg_subsampling_var.set(str(self.settings['jpeg_subsampling']))
            if 'dpi' in self.settings:
                self.dpi_var.set(str(self.settings['dpi']))
            if 'jpeg_progressive' in self.settings:
                self.jpeg_progressive_var.set(str(self.settings['jpeg_progressive']))
            if 'jpeg_qtables' in self.settings:
                self.jpeg_qtables.delete(0, tk.END)
                self.jpeg_qtables.insert(0, self.settings['jpeg_qtables'])
            if 'png_optimize' in self.settings:
                self.png_optimize_var.set(str(self.settings['png_optimize']))
            if 'png_transparency' in self.settings:
                self.png_transparency_var.set(str(self.settings['png_transparency']))
            if 'tiff_compression' in self.settings:
                self.tiff_compression.delete(0, tk.END)
                self.tiff_compression.insert(0, self.settings['tiff_compression'])
            if 'webp_lossless' in self.settings:
                self.webp_lossless_var.set(str(self.settings['webp_lossless']))

    def load_watermark_preview(self):
        """加载水印预览图片"""
        try:
            watermark_path = os.path.join('bin', 'logo', 'watermark.png')
            if os.path.exists(watermark_path):
                # 打开水印图片
                image = Image.open(watermark_path)
                # 计算预览尺寸（保持宽高比）
                preview_width = 100
                preview_height = int(preview_width * (image.height / image.width))
                # 调整图片大小
                image = image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
                # 转换为PhotoImage
                self.watermark_preview = ImageTk.PhotoImage(image)
                # 更新预览标签
                self.preview_label.configure(image=self.watermark_preview)
            else:
                self.preview_label.configure(image='')
                self.preview_label.configure(text="未设置水印图片")
        except Exception as e:
            logger.error(f"Error loading watermark preview: {str(e)}")
            self.preview_label.configure(text="加载预览失败")

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # 输入文件夹选择
        ttk.Label(file_frame, text="输入文件夹：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_path = ttk.Entry(file_frame, width=40)
        self.input_path.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="选择", command=self.choose_input_folder).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(file_frame, text="选择需要添加水印的图片所在文件夹", foreground="gray").grid(row=1, column=0, columnspan=3, padx=5, pady=0, sticky=tk.W)

        # 输出文件夹选择
        ttk.Label(file_frame, text="输出文件夹：").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_path = ttk.Entry(file_frame, width=40)
        self.output_path.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="选择", command=self.choose_output_folder).grid(row=2, column=2, padx=5, pady=5)
        ttk.Label(file_frame, text="选择处理后的图片保存位置", foreground="gray").grid(row=3, column=0, columnspan=3, padx=5, pady=0, sticky=tk.W)

        # 水印设置区域
        watermark_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="5")
        watermark_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # 水印预览和替换
        preview_frame = ttk.Frame(watermark_frame)
        preview_frame.grid(row=0, column=0, columnspan=3, pady=5)
        
        ttk.Label(preview_frame, text="水印预览：").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.preview_label = ttk.Label(preview_frame, text="未设置水印图片", width=20)
        self.preview_label.grid(row=0, column=1, padx=5)
        ttk.Button(preview_frame, text="替换水印图片", command=self.replace_watermark).grid(row=0, column=2, padx=5)

        # 水印参数设置
        params_frame = ttk.Frame(watermark_frame)
        params_frame.grid(row=1, column=0, columnspan=5, pady=5)

        # 透明度设置
        ttk.Label(params_frame, text="透明度：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.opacity = ttk.Entry(params_frame, width=10)
        self.opacity.insert(0, "0.5")
        self.opacity.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(params_frame, text="(0.1-1.0)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # 水印比例设置
        ttk.Label(params_frame, text="水印比例：").grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        self.watermark_ratio = ttk.Entry(params_frame, width=10)
        self.watermark_ratio.insert(0, "0.1")
        self.watermark_ratio.grid(row=0, column=4, padx=5, pady=2, sticky=tk.W)
        ttk.Label(params_frame, text="(0.1-1.0)", foreground="gray").grid(row=0, column=5, padx=5, pady=2, sticky=tk.W)

        # 水印位置设置
        ttk.Label(params_frame, text="位置：").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.position_var = ttk.Combobox(params_frame, values=["左上", "左下", "右上", "右下", "居中"], width=10)
        self.position_var.set("左上")
        self.position_var.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

        # 图片设置区域
        image_frame = ttk.LabelFrame(main_frame, text="图片设置", padding="5")
        image_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # 目标宽度设置
        ttk.Label(image_frame, text="目标宽度：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.target_width = ttk.Entry(image_frame, width=10)
        self.target_width.insert(0, "1920")
        self.target_width.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(image_frame, text="(px，0表示保持原始大小)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # DPI设置
        ttk.Label(image_frame, text="DPI：").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.dpi_var = ttk.Combobox(image_frame, values=["72", "150", "300", "600"], width=10)
        self.dpi_var.set("300")
        self.dpi_var.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        # 命名设置
        ttk.Label(image_frame, text="命名前缀：").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.custom_name = ttk.Entry(image_frame, width=30)
        self.custom_name.insert(0, "watermarked_image")
        self.custom_name.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky=tk.W)

        # 保留原文件名选项
        self.keep_original_name_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(image_frame, text="保留原文件名", variable=self.keep_original_name_var).grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)

        # 输出设置区域
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="5")
        output_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # 输出格式设置
        ttk.Label(output_frame, text="格式：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.format_var = ttk.Combobox(output_frame, values=["JPG", "JPEG", "PNG", "TIFF", "WEBP"], width=10)
        self.format_var.set("JPG")
        self.format_var.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        self.format_var.bind('<<ComboboxSelected>>', self.on_format_change)

        # JPEG设置
        self.jpeg_frame = ttk.LabelFrame(output_frame, text="JPEG设置", padding="5")
        self.jpeg_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # JPEG质量设置
        ttk.Label(self.jpeg_frame, text="质量：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.jpeg_quality = ttk.Entry(self.jpeg_frame, width=10)
        self.jpeg_quality.insert(0, "95")
        self.jpeg_quality.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.jpeg_frame, text="(1-100，75为平衡值)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # JPEG渐进式设置
        ttk.Label(self.jpeg_frame, text="渐进式：").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.jpeg_progressive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.jpeg_frame, text="启用渐进式加载", variable=self.jpeg_progressive_var).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.jpeg_frame, text="(逐步加载图片)", foreground="gray").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)

        # JPEG子采样设置
        ttk.Label(self.jpeg_frame, text="色度采样：").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.jpeg_subsampling_var = ttk.Combobox(self.jpeg_frame, values=["0", "1", "2"], width=10)
        self.jpeg_subsampling_var.set("0")
        self.jpeg_subsampling_var.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.jpeg_frame, text="(0:最佳质量，2:最高压缩)", foreground="gray").grid(row=2, column=2, padx=5, pady=2, sticky=tk.W)

        # JPEG量化表设置
        ttk.Label(self.jpeg_frame, text="量化表：").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        self.jpeg_qtables = ttk.Entry(self.jpeg_frame, width=30)
        self.jpeg_qtables.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.jpeg_frame, text="(可选，自定义量化矩阵)", foreground="gray").grid(row=4, column=0, columnspan=3, padx=5, pady=0, sticky=tk.W)

        # PNG设置
        self.png_frame = ttk.LabelFrame(output_frame, text="PNG设置", padding="5")
        self.png_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # PNG压缩级别
        ttk.Label(self.png_frame, text="压缩级别：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.compression_var = ttk.Combobox(self.png_frame, values=[str(i) for i in range(10)], width=10)
        self.compression_var.set("6")
        self.compression_var.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.png_frame, text="(0:无压缩，9:最高压缩)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # PNG优化设置
        ttk.Label(self.png_frame, text="优化：").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.png_optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.png_frame, text="优化Huffman编码", variable=self.png_optimize_var).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.png_frame, text="(减小文件大小)", foreground="gray").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)

        # PNG透明度设置
        ttk.Label(self.png_frame, text="透明度：").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.png_transparency_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.png_frame, text="保留透明通道", variable=self.png_transparency_var).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.png_frame, text="(仅适用于带Alpha的图像)", foreground="gray").grid(row=2, column=2, padx=5, pady=2, sticky=tk.W)

        # TIFF设置
        self.tiff_frame = ttk.LabelFrame(output_frame, text="TIFF设置", padding="5")
        self.tiff_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # TIFF压缩算法
        ttk.Label(self.tiff_frame, text="压缩算法：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.tiff_compression = ttk.Combobox(self.tiff_frame, values=["raw", "tiff_lzw", "tiff_deflate"], width=15)
        self.tiff_compression.set("tiff_lzw")
        self.tiff_compression.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.tiff_frame, text="(tiff_lzw为无损压缩)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # WebP设置
        self.webp_frame = ttk.LabelFrame(output_frame, text="WebP设置", padding="5")
        self.webp_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # WebP无损压缩
        ttk.Label(self.webp_frame, text="压缩模式：").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.webp_lossless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.webp_frame, text="无损压缩", variable=self.webp_lossless_var).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.webp_frame, text="(默认使用有损压缩)", foreground="gray").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)

        # 进度条和开始按钮
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=4, sticky="ew", padx=5, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(progress_frame, text="开始添加水印", command=self.add_watermark).grid(row=0, column=1, padx=5)

        # 版本信息
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        ttk.Label(version_frame, text="图片水印工具 V4.0 @xujmzd", foreground="gray").pack(side=tk.RIGHT)

        # 配置所有框架的列权重
        for frame in [file_frame, watermark_frame, image_frame, output_frame, self.jpeg_frame, self.png_frame, self.tiff_frame, self.webp_frame]:
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=1)

    def choose_input_folder(self):
        """选择输入文件夹"""
        folder = filedialog.askdirectory(title="选择输入文件夹")
        if folder:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, folder)
            self.progress_var.set(0)

    def choose_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)
            self.progress_var.set(0)

    def replace_watermark(self):
        """替换水印图片"""
        new_path = replace_watermark_image()
        if new_path:
            self.progress_var.set(0)
            self.load_watermark_preview()  # 重新加载预览图片

    def validate_inputs(self):
        """验证输入参数"""
        try:
            # 验证输入输出路径
            if not self.input_path.get() or not os.path.exists(self.input_path.get()):
                raise ValueError("请选择有效的输入文件夹")
            if not self.output_path.get():
                raise ValueError("请选择输出文件夹")

            # 验证水印图片
            watermark_path = os.path.join('bin', 'logo', 'watermark.png')
            if not os.path.exists(watermark_path):
                raise ValueError("水印图片不存在，请先替换水印图片")

            # 验证数值参数
            opacity = float(self.opacity.get())
            if not 0.1 <= opacity <= 1.0:
                raise ValueError("水印透明度必须在0.1到1.0之间")

            target_width = int(self.target_width.get())
            if target_width < 0:
                raise ValueError("目标宽度不能小于0")

            watermark_ratio = float(self.watermark_ratio.get())
            if not 0.1 <= watermark_ratio <= 1.0:
                raise ValueError("水印大小比例必须在0.1到1.0之间")

            return True
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False

    def on_format_change(self, event=None):
        """当格式改变时更新压缩级别选项的可用性"""
        format_upper = self.format_var.get().upper()
        
        # 禁用所有高级设置
        for frame in [self.jpeg_frame, self.png_frame, self.tiff_frame, self.webp_frame]:
            for widget in frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                    widget.configure(state='disabled')
        
        # 根据选择的格式启用相应的设置
        if format_upper in ['JPG', 'JPEG']:
            for widget in self.jpeg_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                    widget.configure(state='normal')
        elif format_upper == 'PNG':
            for widget in self.png_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                    widget.configure(state='normal')
        elif format_upper == 'TIFF':
            for widget in self.tiff_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                    widget.configure(state='normal')
        elif format_upper == 'WEBP':
            for widget in self.webp_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                    widget.configure(state='normal')

    def add_watermark(self):
        """开始添加水印"""
        if not self.validate_inputs():
            return

        try:
            input_folder = self.input_path.get()
            output_folder = self.output_path.get()
            watermark_path = os.path.join('bin', 'logo', 'watermark.png')
            
            # 获取所有参数
            opacity = float(self.opacity.get())
            target_width = int(self.target_width.get())
            watermark_ratio = float(self.watermark_ratio.get())
            position = self.position_var.get()
            custom_name = self.custom_name.get()
            output_format = self.format_var.get()
            keep_original_name = self.keep_original_name_var.get()
            compression_level = int(self.compression_var.get()) if output_format.upper() == 'PNG' else 6
            jpeg_quality = int(self.jpeg_quality.get())
            jpeg_subsampling = int(self.jpeg_subsampling_var.get())
            dpi = int(self.dpi_var.get())
            jpeg_progressive = self.jpeg_progressive_var.get()  # 直接获取布尔值
            jpeg_qtables = self.jpeg_qtables.get()
            png_optimize = self.png_optimize_var.get()  # 直接获取布尔值
            png_transparency = self.png_transparency_var.get()  # 直接获取布尔值
            tiff_compression = self.tiff_compression.get()
            webp_lossless = self.webp_lossless_var.get()  # 直接获取布尔值

            # 获取所有需要处理的图片
            image_files = [f for f in os.listdir(input_folder) 
                         if f.lower().endswith(('jpg', 'jpeg', 'png'))]
            total_count = len(image_files)
            processed_count = 0

            # 处理所有图片
            for index, filename in enumerate(image_files, 1):  # 从1开始计数
                input_image_path = os.path.join(input_folder, filename)
                try:
                    add_image_watermark(
                        input_image_path, output_folder, watermark_path,
                        opacity, target_width, watermark_ratio,
                        position, output_format,
                        custom_name, keep_original_name,
                        index,
                        compression_level,
                        jpeg_quality,
                        jpeg_subsampling,
                        dpi,
                        jpeg_progressive,
                        jpeg_qtables,
                        png_optimize,
                        png_transparency,
                        tiff_compression,
                        webp_lossless
                    )
                    processed_count += 1
                    progress = (processed_count / total_count) * 100
                    self.progress_var.set(progress)
                    self.root.update()
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
                    messagebox.showwarning("警告", f"处理图片 {filename} 时出错：{str(e)}")

            messagebox.showinfo("完成", f"水印添加完成！\n成功处理 {processed_count}/{total_count} 张图片")
            
            # 保存设置
            settings = {
                'input_folder': input_folder,
                'output_folder': output_folder,
                'opacity': opacity,
                'target_width': target_width,
                'watermark_ratio': watermark_ratio,
                'position': position,
                'custom_name': custom_name,
                'output_format': output_format,
                'keep_original_name': keep_original_name,
                'compression_level': compression_level,
                'jpeg_quality': jpeg_quality,
                'jpeg_subsampling': jpeg_subsampling,
                'dpi': dpi,
                'jpeg_progressive': jpeg_progressive,
                'jpeg_qtables': jpeg_qtables,
                'png_optimize': png_optimize,
                'png_transparency': png_transparency,
                'tiff_compression': tiff_compression,
                'webp_lossless': webp_lossless
            }
            save_settings(settings)

        except Exception as e:
            logger.error(f"Error in add_watermark: {str(e)}")
            messagebox.showerror("错误", f"处理图片时出错：{str(e)}")
            self.progress_var.set(0)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WatermarkApp(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        messagebox.showerror("错误", f"程序运行出错：{str(e)}")
