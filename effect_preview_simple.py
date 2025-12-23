#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序列帧特效预览器 - 简化版本（不依赖tkinterdnd2）
用于预览指定文件夹下的所有特效动画
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import platform
import re
from PIL import Image, ImageTk
import threading
import time

class EffectPreview:
    def __init__(self, root):
        self.root = root
        self.root.title("序列帧特效预览器")
        self.root.geometry("1200x700")
        
        # 当前播放状态
        self.current_effect = None
        self.current_effect_path = None
        self.current_base_dir = ""  # 当前扫描的基础目录
        self.max_scan_depth = 5  # 最大扫描深度
        self.is_playing = False
        self.current_frame = 0
        self.frames = []
        self.play_thread = None
        self.effect_tree = {}  # 存储分类的特效树
        self.current_effect_list = []  # 当前特效列表（用于自动播放下一个）
        self.current_effect_index = -1  # 当前特效在列表中的索引
        self.is_loading = False  # 是否正在加载
        self.is_auto_playing_next = False  # 是否正在自动播放下一个
        
        # 创建界面
        self.create_widgets()
        
        # 初始化界面状态
        self.init_ui_state()
    
    def init_ui_state(self):
        """初始化UI状态"""
        # 显示初始提示
        self.effect_tree_widget.insert("", "end", text="请选择或拖拽文件夹开始扫描")
        self.stats_label.config(text="总计: 0 个特效")
        self.effect_name_label.config(text="未选择特效")
        self.effect_path_label.config(text="")
        self.effect_stats_label.config(text="")
    
    def natural_sort_key(self, text):
        """
        自然排序键函数，用于正确排序包含数字的文件名
        例如：1.png, 2.png, 10.png, 11.png 而不是 1.png, 10.png, 11.png, 2.png
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', text)]
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧特效列表区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 目录选择区域
        dir_frame = ttk.Frame(left_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="当前目录:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.current_dir_label = ttk.Label(dir_frame, text="未选择目录", foreground="gray")
        self.current_dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 目录操作按钮
        dir_buttons_frame = ttk.Frame(dir_frame)
        dir_buttons_frame.pack(fill=tk.X)
        
        self.select_dir_button = ttk.Button(dir_buttons_frame, text="选择目录", command=self.select_directory)
        self.select_dir_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_dir_button = ttk.Button(dir_buttons_frame, text="重置", command=self.reset_directory)
        self.reset_dir_button.pack(side=tk.LEFT)
        
        # 特效列表标题和筛选
        effect_header_frame = ttk.Frame(left_frame)
        effect_header_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(effect_header_frame, text="特效列表", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # 筛选输入框
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_frame, text="筛选:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.on_filter_change)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 特效树形控件
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.effect_tree_widget = ttk.Treeview(tree_frame, height=15)
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.effect_tree_widget.yview)
        self.effect_tree_widget.config(yscrollcommand=tree_scrollbar.set)
        
        self.effect_tree_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.effect_tree_widget.bind('<<TreeviewSelect>>', self.on_effect_select)
        
        # 扫描深度控制
        depth_frame = ttk.Frame(left_frame)
        depth_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(depth_frame, text="扫描深度:").pack(side=tk.LEFT)
        self.depth_var = tk.IntVar(value=5)
        depth_spinbox = ttk.Spinbox(depth_frame, from_=1, to=5, width=5, 
                                   textvariable=self.depth_var, command=self.on_depth_change)
        depth_spinbox.pack(side=tk.LEFT, padx=5)
        
        # 项目统计显示
        self.stats_label = ttk.Label(depth_frame, text="", foreground="gray")
        self.stats_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 中间序列帧文件列表区域
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 5))
        
        # 当前特效详细信息
        info_frame = ttk.LabelFrame(middle_frame, text="特效信息", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 特效名称
        self.effect_name_label = ttk.Label(info_frame, text="未选择特效", font=("Arial", 10, "bold"))
        self.effect_name_label.pack(anchor=tk.W)
        
        # 特效路径
        self.effect_path_label = ttk.Label(info_frame, text="", font=("Arial", 8), foreground="gray")
        self.effect_path_label.pack(anchor=tk.W)
        
        # 特效统计
        self.effect_stats_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.effect_stats_label.pack(anchor=tk.W, pady=(2, 0))
        
        # 序列帧文件列表标题
        ttk.Label(middle_frame, text="序列帧文件", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        # 文件列表框架
        file_frame = ttk.Frame(middle_frame)
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(file_frame, width=25, height=20)
        file_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定文件列表点击事件
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # 打开目录按钮
        self.open_dir_button = ttk.Button(middle_frame, text="打开文件目录", command=self.open_directory)
        self.open_dir_button.pack(pady=(5, 0))
        self.open_dir_button.config(state=tk.DISABLED)
        
        # 右侧预览区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 预览标题
        self.preview_title = ttk.Label(right_frame, text="选择一个特效进行预览", font=("Arial", 14, "bold"))
        self.preview_title.pack(pady=(0, 10))
        
        # 加载状态标签
        self.loading_label = ttk.Label(right_frame, text="", foreground="orange")
        self.loading_label.pack()
        
        # 预览画布
        self.canvas = tk.Canvas(right_frame, bg="black", width=600, height=400)
        self.canvas.pack(pady=10)
        
        # 控制按钮
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(pady=10)
        
        self.play_button = ttk.Button(control_frame, text="播放", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="停止", command=self.stop_play)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 自动播放选项
        self.auto_play_var = tk.BooleanVar(value=True)
        self.auto_play_check = ttk.Checkbutton(control_frame, text="选择后自动播放", 
                                             variable=self.auto_play_var)
        self.auto_play_check.pack(side=tk.LEFT, padx=10)
        
        # 自动播放下一个选项
        self.auto_next_var = tk.BooleanVar(value=False)
        self.auto_next_check = ttk.Checkbutton(control_frame, text="自动播放下一个", 
                                             variable=self.auto_next_var)
        self.auto_next_check.pack(side=tk.LEFT, padx=5)
        
        # 反序播放选项
        self.reverse_var = tk.BooleanVar(value=False)
        self.reverse_check = ttk.Checkbutton(control_frame, text="反序播放", 
                                           variable=self.reverse_var, command=self.on_reverse_change)
        self.reverse_check.pack(side=tk.LEFT, padx=5)
        
        # 播放速度控制
        speed_frame = ttk.Frame(right_frame)
        speed_frame.pack(pady=5)
        
        ttk.Label(speed_frame, text="播放速度:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.1)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.05, to=0.5, 
                                   variable=self.speed_var, orient=tk.HORIZONTAL, length=200,
                                   command=self.on_speed_change)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        # 速度数值显示
        self.speed_label = ttk.Label(speed_frame, text="0.1s")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # 帧信息
        self.frame_info = ttk.Label(right_frame, text="")
        self.frame_info.pack(pady=5)
    
    def on_speed_change(self, value):
        """当播放速度改变时"""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.2f}s")
    
    def on_reverse_change(self):
        """当反序选项改变时"""
        if self.frames and not self.is_playing:
            # 如果当前没有播放，调整当前帧位置
            if self.reverse_var.get():
                # 切换到反序：当前帧位置从正序转换为反序
                self.current_frame = len(self.frames) - 1 - self.current_frame
            else:
                # 切换到正序：当前帧位置从反序转换为正序
                self.current_frame = len(self.frames) - 1 - self.current_frame
            self.show_frame(self.current_frame)
    
    def on_filter_change(self, *args):
        """当筛选条件改变时"""
        self._build_tree()
    
    def on_file_select(self, event):
        """当选择文件列表中的文件时，预览单张图片"""
        selection = self.file_listbox.curselection()
        if selection and self.current_effect_path and self.frames:
            file_index = selection[0]
            if 0 <= file_index < len(self.frames):
                # 停止当前播放
                if self.is_playing:
                    self.pause_play()
                
                self.current_frame = file_index
                self.show_frame(file_index)
                self.update_frame_info()
    
    def get_next_effect(self):
        """获取下一个特效"""
        if not self.current_effect_list or self.current_effect_index < 0:
            return None
        
        next_index = (self.current_effect_index + 1) % len(self.current_effect_list)
        return self.current_effect_list[next_index]
    
    def play_next_effect(self):
        """播放下一个特效"""
        next_effect = self.get_next_effect()
        if next_effect:
            # 设置自动播放标志
            self.is_auto_playing_next = True
            
            # 更新当前特效索引
            self.current_effect_index = (self.current_effect_index + 1) % len(self.current_effect_list)
            
            # 在树形控件中选中下一个特效
            self.select_effect_in_tree(next_effect['path'])
            
            # 加载并播放下一个特效
            self.load_effect_by_path(next_effect['path'], next_effect['name'])
            if self.auto_play_var.get():
                self.root.after(100, self.start_play)
    
    def select_effect_in_tree(self, effect_path):
        """在树形控件中选中指定的特效"""
        # 遍历树形控件中的所有项目
        def find_and_select(item=""):
            children = self.effect_tree_widget.get_children(item)
            for child in children:
                values = self.effect_tree_widget.item(child, "values")
                if values and len(values) >= 3 and values[0] == "effect" and values[2] == effect_path:
                    # 找到了对应的特效，选中它
                    self.effect_tree_widget.selection_set(child)
                    self.effect_tree_widget.see(child)  # 确保可见
                    return True
                # 递归搜索子项
                if find_and_select(child):
                    return True
            return False
        
        find_and_select()
    
    def select_directory(self):
        """选择目录对话框"""
        directory = filedialog.askdirectory(title="选择包含特效文件夹的目录")
        if directory:
            self.load_directory(directory)
    
    def load_directory(self, directory):
        """加载指定目录"""
        if not os.path.exists(directory):
            messagebox.showerror("错误", f"目录不存在: {directory}")
            return
        
        self.current_base_dir = directory
        self.current_dir_label.config(text=os.path.basename(directory))
        self.current_dir_label.config(foreground="blue")
        self.scan_effects()
        
        # 清空当前预览
        self.stop_play()
        self.current_effect = None
        self.current_effect_path = None
        self.frames = []
        self.file_listbox.delete(0, tk.END)
        self.open_dir_button.config(state=tk.DISABLED)
        self.canvas.delete("all")
        self.preview_title.config(text="选择一个特效进行预览")
        self.frame_info.config(text="")
    
    def reset_directory(self):
        """重置到初始状态"""
        self.current_base_dir = ""
        self.current_dir_label.config(text="未选择目录")
        self.current_dir_label.config(foreground="gray")
        
        # 清空当前预览
        self.stop_play()
        self.current_effect = None
        self.current_effect_path = None
        self.frames = []
        self.file_listbox.delete(0, tk.END)
        self.open_dir_button.config(state=tk.DISABLED)
        self.canvas.delete("all")
        self.preview_title.config(text="选择一个特效进行预览")
        self.frame_info.config(text="")
        
        # 清空特效树和相关数据
        self.effect_tree = {}
        self.current_effect_list = []
        self.current_effect_index = -1
        
        # 清空树形控件
        for item in self.effect_tree_widget.get_children():
            self.effect_tree_widget.delete(item)
        
        # 重置UI状态
        self.init_ui_state()
    
    def on_depth_change(self):
        """当扫描深度改变时"""
        self.max_scan_depth = self.depth_var.get()
        self.scan_effects()
    
    def scan_effects(self):
        """扫描当前目录下的所有特效，支持多层分类"""
        # 清空树形控件
        for item in self.effect_tree_widget.get_children():
            self.effect_tree_widget.delete(item)
        
        if not self.current_base_dir or not os.path.exists(self.current_base_dir):
            self.effect_tree_widget.insert("", "end", text="请选择或拖拽文件夹开始扫描")
            self.stats_label.config(text="总计: 0 个特效")
            return
        
        # 显示扫描状态
        self.loading_label.config(text="正在扫描文件夹...")
        self.effect_tree_widget.insert("", "end", text="正在扫描，请稍候...")
        
        # 重置扫描数据
        self.effect_tree = {}
        self.scan_progress = {'scanned': 0, 'max_dirs': 500}  # 简化版初始限制500个目录
        
        # 使用简单的同步扫描，定期更新界面
        self.root.after(10, self._start_simple_scan)
    
    def _start_simple_scan(self):
        """开始简单的同步扫描"""
        try:
            self.loading_label.config(text="正在扫描文件夹...")
            self.root.update()  # 更新界面
            
            # 记录扫描开始时间，设置超时机制
            import time
            scan_start_time = time.time()
            max_scan_time = 30  # 最大扫描时间30秒
            
            # 直接扫描，不使用复杂的异步逻辑
            self._scan_directory_simple(self.current_base_dir, "", 0)
            
            # 检查是否超时
            scan_duration = time.time() - scan_start_time
            if scan_duration > max_scan_time:
                self.loading_label.config(text="扫描超时，显示已找到的特效")
            else:
                self.loading_label.config(text="")
            
            # 清空临时显示
            for item in self.effect_tree_widget.get_children():
                self.effect_tree_widget.delete(item)
            
            # 构建树形结构
            self._build_tree()
            
        except Exception as e:
            print(f"扫描失败: {e}")
            self.loading_label.config(text="扫描失败")
            self._build_tree()  # 显示已找到的特效
    
    def _scan_directory_simple(self, directory, parent_path, depth):
        """简单的同步目录扫描"""
        if depth >= self.max_scan_depth:
            return
        
        # 检查是否超过最大扫描目录数
        if self.scan_progress['scanned'] >= self.scan_progress['max_dirs']:
            # 显示提示对话框询问是否继续
            result = messagebox.askyesno(
                "扫描限制", 
                f"已扫描 {self.scan_progress['max_dirs']} 个目录，继续扫描可能会很慢。\n\n是否继续扫描？",
                icon="question"
            )
            if not result:
                self.loading_label.config(text="扫描已停止，显示已找到的特效")
                return
            else:
                # 用户选择继续，增加限制数量
                self.scan_progress['max_dirs'] += 1000
                self.loading_label.config(text=f"继续扫描... 已处理 {self.scan_progress['scanned']} 个文件夹")
        
        # 检查路径是否为有效目录
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return
        
        try:
            items = os.listdir(directory)
            # 对目录项进行自然排序
            items.sort(key=self.natural_sort_key)
            
            for item in items:
                item_path = os.path.join(directory, item)
                
                # 跳过非目录文件（如ZIP、RAR等压缩文件）
                if not os.path.exists(item_path) or not os.path.isdir(item_path):
                    continue
                
                # 跳过隐藏文件夹和系统文件夹
                if item.startswith('.') or item.startswith('$'):
                    continue
                
                self.scan_progress['scanned'] += 1
                
                # 每处理5个文件夹更新一次界面，更频繁地更新防止卡死
                if self.scan_progress['scanned'] % 5 == 0:
                    progress_text = f"正在扫描... 已处理 {self.scan_progress['scanned']} 个文件夹"
                    if self.scan_progress['scanned'] > self.scan_progress['max_dirs'] * 0.8:
                        progress_text += f" (接近限制 {self.scan_progress['max_dirs']})"
                    self.loading_label.config(text=progress_text)
                    self.root.update_idletasks()  # 使用update_idletasks而不是update，更轻量
                
                # 检查是否包含图片文件
                image_files = self._get_image_files(item_path)
                
                if image_files:
                    # 这是一个特效文件夹
                    relative_path = os.path.relpath(item_path, self.current_base_dir)
                    category = os.path.dirname(relative_path) if os.path.dirname(relative_path) else "根目录"
                    
                    if category not in self.effect_tree:
                        self.effect_tree[category] = []
                    
                    self.effect_tree[category].append({
                        'name': item,
                        'path': item_path,
                        'relative_path': relative_path,
                        'image_count': len(image_files)
                    })
                else:
                    # 继续递归扫描子目录
                    self._scan_directory_simple(item_path, 
                                              os.path.join(parent_path, item) if parent_path else item, 
                                              depth + 1)
        
        except (PermissionError, OSError, NotADirectoryError) as e:
            print(f"扫描目录失败 {directory}: {e}")
        except Exception as e:
            print(f"扫描过程中出现未知错误 {directory}: {e}")
            # 继续扫描其他目录，不要因为一个错误就停止
    
    def _get_image_files(self, directory):
        """获取目录中的图片文件"""
        try:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                return []
            
            files = os.listdir(directory)
            image_files = [f for f in files 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            return sorted(image_files, key=self.natural_sort_key)
        except (OSError, PermissionError, NotADirectoryError):
            return []
    
    def _build_tree(self):
        """构建树形结构"""
        # 清空树形控件
        for item in self.effect_tree_widget.get_children():
            self.effect_tree_widget.delete(item)
        
        if not self.effect_tree:
            self.effect_tree_widget.insert("", "end", text="未找到包含图片的文件夹")
            return
        
        # 获取筛选条件
        filter_text = self.filter_var.get().lower().strip()
        
        # 重建当前特效列表（用于自动播放下一个）
        self.current_effect_list = []
        
        # 对分类进行排序
        categories = sorted(self.effect_tree.keys(), key=self.natural_sort_key)
        
        for category in categories:
            # 对该分类下的特效进行排序和筛选
            effects = sorted(self.effect_tree[category], key=lambda x: self.natural_sort_key(x['name']))
            
            # 应用筛选
            if filter_text:
                effects = [e for e in effects if filter_text in e['name'].lower()]
            
            if not effects:
                continue  # 如果该分类下没有符合条件的特效，跳过
            
            # 添加到当前特效列表
            self.current_effect_list.extend(effects)
            
            # 创建分类节点
            if category == "根目录":
                category_node = ""  # 根目录的特效直接放在根级别
            else:
                category_node = self.effect_tree_widget.insert("", "end", text=f"📁 {category}", 
                                                              values=("category",), open=True)
            
            for effect in effects:
                display_name = f"🎬 {effect['name']} ({effect['image_count']}帧)"
                parent = category_node if category_node else ""
                self.effect_tree_widget.insert(parent, "end", text=display_name, 
                                              values=("effect", effect['relative_path'], effect['path']))
        
        # 更新统计信息
        total_effects = len(self.current_effect_list)
        self.stats_label.config(text=f"总计: {total_effects} 个特效")
        
        # 更新当前选择信息
        self._update_selection_stats()
    
    def _update_selection_stats(self):
        """更新当前选择的统计信息"""
        if self.current_effect_index >= 0 and self.current_effect_list:
            current_num = self.current_effect_index + 1
            total_num = len(self.current_effect_list)
            self.stats_label.config(text=f"总计: {total_num} 个特效 | 当前: 第 {current_num} 个")
        else:
            total_num = len(self.current_effect_list) if self.current_effect_list else 0
            self.stats_label.config(text=f"总计: {total_num} 个特效")
    
    def _update_effect_info(self, effect_name, effect_path, image_count):
        """更新特效详细信息显示"""
        self.effect_name_label.config(text=effect_name)
        
        # 显示相对路径，如果太长则截断
        relative_path = os.path.relpath(effect_path, self.current_base_dir)
        if len(relative_path) > 50:
            display_path = "..." + relative_path[-47:]
        else:
            display_path = relative_path
        self.effect_path_label.config(text=display_path)
        
        # 显示统计信息
        file_size = self._get_directory_size(effect_path)
        size_text = self._format_file_size(file_size)
        self.effect_stats_label.config(text=f"帧数: {image_count} | 大小: {size_text}")
    
    def _get_directory_size(self, directory):
        """获取目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def on_effect_select(self, event):
        """当选择特效时"""
        selection = self.effect_tree_widget.selection()
        if selection:
            item = selection[0]
            values = self.effect_tree_widget.item(item, "values")
            
            # 只有特效项才能播放，分类项不能播放
            if values and len(values) >= 3 and values[0] == "effect":
                effect_path = values[2]  # 完整路径
                effect_name = os.path.basename(effect_path)
                
                # 只有在非自动播放时才更新索引
                if not self.is_auto_playing_next:
                    # 找到当前特效在列表中的索引
                    self.current_effect_index = -1
                    for i, effect in enumerate(self.current_effect_list):
                        if effect['path'] == effect_path:
                            self.current_effect_index = i
                            break
                
                # 重置自动播放标志
                self.is_auto_playing_next = False
                
                # 更新选择统计
                self._update_selection_stats()
                
                self.load_effect_by_path(effect_path, effect_name)
                
                # 如果启用自动播放，则自动开始播放
                if self.auto_play_var.get():
                    self.root.after(100, self.start_play)  # 延迟100ms开始播放
    
    def load_effect_by_path(self, effect_path, effect_name):
        """通过完整路径加载特效序列帧"""
        if self.is_loading:
            return  # 如果正在加载，忽略新的加载请求
        
        self.stop_play()
        
        if not os.path.exists(effect_path):
            return
        
        # 获取所有图片文件并使用自然排序
        image_files = self._get_image_files(effect_path)
        
        if not image_files:
            return
        
        # 更新特效信息显示
        self._update_effect_info(effect_name, effect_path, len(image_files))
        
        # 设置加载状态
        self.is_loading = True
        self.loading_label.config(text=f"正在加载 {effect_name}... (0/{len(image_files)})")
        
        self.current_effect = effect_name
        self.current_effect_path = effect_path
        self.frames = []
        
        # 更新文件列表
        self.file_listbox.delete(0, tk.END)
        for img_file in image_files:
            self.file_listbox.insert(tk.END, img_file)
        
        # 启用打开目录按钮
        self.open_dir_button.config(state=tk.NORMAL)
        
        # 异步加载帧
        self.preview_title.config(text=f"特效: {effect_name} ({len(image_files)} 帧)")
        self._load_frames_async(image_files, 0)
    
    def _load_frames_async(self, image_files, index):
        """异步加载帧，避免界面假死"""
        if index >= len(image_files):
            # 加载完成
            self.is_loading = False
            self.loading_label.config(text="")
            
            if self.frames:
                # 根据反序选项设置起始帧
                if self.reverse_var.get():
                    self.current_frame = len(self.frames) - 1  # 反序从最后一帧开始
                else:
                    self.current_frame = 0  # 正序从第一帧开始
                self.show_frame(self.current_frame)
                self.update_frame_info()
            return
        
        # 加载当前帧
        img_file = image_files[index]
        img_path = os.path.join(self.current_effect_path, img_file)
        
        try:
            img = Image.open(img_path)
            # 调整图片大小以适应画布
            img = self.resize_image(img, 600, 400)
            photo = ImageTk.PhotoImage(img)
            self.frames.append(photo)
        except Exception as e:
            print(f"加载图片失败 {img_path}: {e}")
        
        # 更新加载进度
        self.loading_label.config(text=f"正在加载 {self.current_effect}... ({index + 1}/{len(image_files)})")
        
        # 每加载5帧更新一次界面，避免界面卡顿
        if (index + 1) % 5 == 0:
            self.root.update_idletasks()
        
        # 继续加载下一帧
        self.root.after(1, lambda: self._load_frames_async(image_files, index + 1))
    
    def resize_image(self, img, max_width, max_height):
        """调整图片大小保持比例"""
        width, height = img.size
        ratio = min(max_width/width, max_height/height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def show_frame(self, frame_index):
        """显示指定帧"""
        if 0 <= frame_index < len(self.frames):
            self.canvas.delete("all")
            photo = self.frames[frame_index]
            self.canvas.create_image(300, 200, image=photo)
            self.current_frame = frame_index
            self.update_frame_info()
    
    def update_frame_info(self):
        """更新帧信息显示"""
        if self.frames:
            info = f"帧: {self.current_frame + 1}/{len(self.frames)}"
            self.frame_info.config(text=info)
    
    def toggle_play(self):
        """切换播放状态"""
        if self.is_playing:
            self.pause_play()
        else:
            self.start_play()
    
    def start_play(self):
        """开始播放"""
        if not self.frames:
            return
        
        self.is_playing = True
        self.play_button.config(text="暂停")
        
        if self.play_thread is None or not self.play_thread.is_alive():
            self.play_thread = threading.Thread(target=self.play_animation)
            self.play_thread.daemon = True
            self.play_thread.start()
    
    def pause_play(self):
        """暂停播放"""
        self.is_playing = False
        self.play_button.config(text="播放")
    
    def stop_play(self):
        """停止播放"""
        self.is_playing = False
        self.play_button.config(text="播放")
        if self.frames:
            # 根据反序选项设置起始帧
            if self.reverse_var.get():
                self.current_frame = len(self.frames) - 1  # 反序从最后一帧开始
            else:
                self.current_frame = 0  # 正序从第一帧开始
            self.show_frame(self.current_frame)
    
    def play_animation(self):
        """播放动画循环"""
        start_frame = self.current_frame
        frames_played = 0
        
        while self.is_playing and self.frames:
            self.root.after(0, lambda: self.show_frame(self.current_frame))
            
            # 根据反序选项决定帧的递增方向
            if self.reverse_var.get():
                # 反序播放：从最后一帧到第一帧
                self.current_frame = (self.current_frame - 1) % len(self.frames)
            else:
                # 正序播放：从第一帧到最后一帧
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            
            frames_played += 1
            
            # 检查是否完成一轮播放（播放了所有帧）
            if frames_played >= len(self.frames) and self.auto_next_var.get():
                self.is_playing = False
                self.play_button.config(text="播放")
                self.root.after(500, self.play_next_effect)  # 延迟500ms播放下一个
                break
            
            # 使用速度控制
            time.sleep(self.speed_var.get())
    
    def open_directory(self):
        """打开当前特效文件所在目录"""
        if not self.current_effect_path or not os.path.exists(self.current_effect_path):
            return
        
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.current_effect_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.current_effect_path])
            else:  # Linux
                subprocess.run(["xdg-open", self.current_effect_path])
        except Exception as e:
            print(f"打开目录失败: {e}")

def main():
    root = tk.Tk()
    app = EffectPreview(root)
    root.mainloop()

if __name__ == "__main__":
    main()