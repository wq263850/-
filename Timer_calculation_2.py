import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation, getcontext

# 配置高精度计算环境
getcontext().prec = 30  # 设置更高的计算精度
TIMER_FORMULA_TEXT = """定时器溢出时间计算公式：
T = (ARR + 1) * (PSC + 1) / F_clock
其中：
T = 溢出时间（秒）
ARR = 自动重装载值（整数）
PSC = 预分频系数（整数）
F_clock = 定时器时钟频率（Hz）"""

FREQ_CONV_TEXT = """时间与频率换算公式：
Frequency = 1 / Time
Time = 1 / Frequency"""

class TimerCalculator:
    def __init__(self, master):
        self.master = master
        master.title("STM32定时器精密计算器 v2.1")
        self.create_widgets()
        self.setup_validations()
        
    def create_widgets(self):
        # 定时器计算器框架
        timer_frame = ttk.LabelFrame(self.master, text="定时器计算器")
        timer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 定时器输入字段配置
        self.timer_fields = {
            "clock": {"label": "时钟频率 (MHz)", "unit": "MHz", "var": tk.StringVar(), "row": 0},
            "time": {"label": "溢出时间 (μs)", "unit": "μs", "var": tk.StringVar(), "row": 1},
            "psc": {"label": "预分频系数 (PSC)", "unit": "", "var": tk.StringVar(), "row": 2},
            "arr": {"label": "自动重载值 (ARR)", "unit": "", "var": tk.StringVar(), "row": 3}
        }

        # 动态创建定时器输入组件
        self.timer_entries = {}
        for key, config in self.timer_fields.items():
            row = config["row"]
            ttk.Label(timer_frame, text=config["label"]).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            
            entry = ttk.Entry(timer_frame, textvariable=config["var"], width=18)
            entry.grid(row=row, column=1, padx=5, pady=5)
            
            ttk.Label(timer_frame, text=config["unit"]).grid(row=row, column=2, padx=5, pady=5, sticky="w")
            self.timer_entries[key] = entry

        # 定时器操作按钮
        timer_button_frame = ttk.Frame(timer_frame)
        timer_button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(timer_button_frame, text="计算", command=self.calculate_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_button_frame, text="清除", command=self.clear_timer).pack(side=tk.LEFT, padx=5)

        # 定时器结果显示
        timer_result_frame = ttk.LabelFrame(timer_frame, text="计算结果")
        timer_result_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.timer_result_text = tk.Text(timer_result_frame, height=5, width=45, state=tk.DISABLED)
        self.timer_result_text.pack(padx=5, pady=5)

        # 定时器公式说明
        ttk.Label(timer_frame, text=TIMER_FORMULA_TEXT, justify=tk.LEFT).grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        # 频率换算框架
        freq_frame = ttk.LabelFrame(self.master, text="时间与频率换算")
        freq_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 频率换算输入字段配置
        self.freq_fields = {
            "time": {"label": "时间 (μs)", "unit": "μs", "var": tk.StringVar(), "row": 0},
            "frequency": {"label": "频率 (Hz)", "unit": "Hz", "var": tk.StringVar(), "row": 1}
        }

        # 动态创建频率换算输入组件
        self.freq_entries = {}
        for key, config in self.freq_fields.items():
            row = config["row"]
            ttk.Label(freq_frame, text=config["label"]).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            
            entry = ttk.Entry(freq_frame, textvariable=config["var"], width=18)
            entry.grid(row=row, column=1, padx=5, pady=5)
            
            ttk.Label(freq_frame, text=config["unit"]).grid(row=row, column=2, padx=5, pady=5, sticky="w")
            self.freq_entries[key] = entry

        # 频率换算操作按钮
        freq_button_frame = ttk.Frame(freq_frame)
        freq_button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(freq_button_frame, text="计算", command=self.calculate_freq).pack(side=tk.LEFT, padx=5)
        ttk.Button(freq_button_frame, text="清除", command=self.clear_freq).pack(side=tk.LEFT, padx=5)

        # 频率换算结果显示
        freq_result_frame = ttk.LabelFrame(freq_frame, text="计算结果")
        freq_result_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.freq_result_text = tk.Text(freq_result_frame, height=5, width=45, state=tk.DISABLED)
        self.freq_result_text.pack(padx=5, pady=5)

        # 频率换算公式说明
        ttk.Label(freq_frame, text=FREQ_CONV_TEXT, justify=tk.LEFT).grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="w")

    def setup_validations(self):
        # 设置定时器输入验证
        for key in ['psc', 'arr']:
            self.timer_entries[key].configure(
                validate='key',
                validatecommand=(self.master.register(self.validate_int), '%P')
            )
        for key in ['time']:
            self.timer_entries[key].configure(
                validate='key',
                validatecommand=(self.master.register(self.validate_float), '%P')
            )

        # 设置频率换算输入验证
        for key in ['time', 'frequency']:
            self.freq_entries[key].configure(
                validate='key',
                validatecommand=(self.master.register(self.validate_float), '%P')
            )

    def validate_int(self, value):
        """验证整数输入"""
        if value.strip() in ('', '-'):
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def validate_float(self, value):
        """验证浮点数输入"""
        if value.strip() in ('', '.', '-', '+'):
            return True
        try:
            Decimal(value)
            return True
        except InvalidOperation:
            return False

    def clear_timer(self):
        """清除定时器所有输入"""
        for var in [config["var"] for config in self.timer_fields.values()]:
            var.set("")
        self.timer_result_text.config(state=tk.NORMAL)
        self.timer_result_text.delete(1.0, tk.END)
        self.timer_result_text.config(state=tk.DISABLED)

    def clear_freq(self):
        """清除频率换算所有输入"""
        for var in [config["var"] for config in self.freq_fields.values()]:
            var.set("")
        self.freq_result_text.config(state=tk.NORMAL)
        self.freq_result_text.delete(1.0, tk.END)
        self.freq_result_text.config(state=tk.DISABLED)

    def parse_timer_input(self, key):
        """解析定时器输入值为Decimal类型"""
        value = self.timer_fields[key]["var"].get().strip()
        if not value:
            return None
        try:
            if key == 'clock':  # MHz转Hz
                return Decimal(value) * Decimal('1e6')
            elif key == 'time':  # μs转s
                return Decimal(value) * Decimal('1e-6')
            elif key in ['psc', 'arr']:
                return Decimal(int(value))
            return Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError(f"无效的输入格式: {self.timer_fields[key]['label']}")

    def parse_freq_input(self, key):
        """解析频率换算输入值为Decimal类型"""
        value = self.freq_fields[key]["var"].get().strip()
        if not value:
            return None
        try:
            if key == 'time':  # μs转s
                return Decimal(value) * Decimal('1e-6')
            elif key == 'frequency':
                return Decimal(value)
            return Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError(f"无效的输入格式: {self.freq_fields[key]['label']}")

    def calculate_timer(self):
        """执行定时器主计算逻辑"""
        try:
            # 解析所有定时器输入值
            inputs = {
                'clock': self.parse_timer_input('clock'),
                'time': self.parse_timer_input('time'),
                'psc': self.parse_timer_input('psc'),
                'arr': self.parse_timer_input('arr')
            }

            # 检查有效输入数量
            filled = sum(1 for v in inputs.values() if v is not None)
            if filled != 3:
                raise ValueError("请准确填写三个参数")

            # 执行定时器计算
            result = {}
            if inputs['clock'] is None:
                # 计算时钟频率: F_clock = (ARR+1)(PSC+1)/T
                numerator = (inputs['arr'] + 1) * (inputs['psc'] + 1)
                result['clock'] = numerator / inputs['time']
            elif inputs['time'] is None:
                # 计算溢出时间: T = (ARR+1)(PSC+1)/F_clock
                numerator = (inputs['arr'] + 1) * (inputs['psc'] + 1)
                result['time'] = numerator / inputs['clock']
            elif inputs['psc'] is None:
                # 计算PSC: PSC = (F_clock*T)/(ARR+1) - 1
                psc = (inputs['clock'] * inputs['time']) / (inputs['arr'] + 1) - 1
                result['psc'] = psc
            elif inputs['arr'] is None:
                # 计算ARR: ARR = (F_clock*T)/(PSC+1) - 1
                arr = (inputs['clock'] * inputs['time']) / (inputs['psc'] + 1) - 1
                result['arr'] = arr

            # 更新定时器输入框
            if 'clock' in result:
                freq_mhz = result['clock'] / Decimal('1e6')
                self.timer_fields['clock']["var"].set(f"{freq_mhz:.6f}")
            if 'time' in result:
                time_us = result['time'] * Decimal('1e6')
                self.timer_fields['time']["var"].set(f"{float(time_us):.12f}")
            if 'psc' in result:
                recommended = max(0, int(result['psc'].quantize(Decimal('1'), rounding='ROUND_HALF_UP')))
                self.timer_fields['psc']["var"].set(f"{recommended}")
            if 'arr' in result:
                recommended = max(0, int(result['arr'].quantize(Decimal('1'), rounding='ROUND_HALF_UP')))
                self.timer_fields['arr']["var"].set(f"{recommended}")

            self.display_timer_result(result)

        except Exception as e:
            messagebox.showerror("计算错误", str(e))

    def calculate_freq(self):
        """执行频率换算逻辑"""
        try:
            # 解析所有频率换算输入值
            inputs = {
                'time': self.parse_freq_input('time'),
                'frequency': self.parse_freq_input('frequency')
            }

            # 检查有效输入数量
            filled = sum(1 for v in inputs.values() if v is not None)
            if filled != 1:
                raise ValueError("请填写时间或频率中的一个")

            # 执行频率换算计算
            result = {}
            if inputs['time'] is not None and inputs['frequency'] is None:
                # 计算频率: Frequency = 1 / T
                result['frequency'] = Decimal(1) / inputs['time']
            elif inputs['frequency'] is not None and inputs['time'] is None:
                # 计算时间: Time = 1 / Frequency
                result['time'] = Decimal(1) / inputs['frequency']

            # 更新频率换算输入框
            if 'time' in result:
                time_us = result['time'] * Decimal('1e6')
                self.freq_fields['time']["var"].set(f"{float(time_us):.12f}")
            if 'frequency' in result:
                self.freq_fields['frequency']["var"].set(f"{result['frequency']:.6f}")

            self.display_freq_result(result)

        except Exception as e:
            messagebox.showerror("计算错误", str(e))

    def display_timer_result(self, result):
        """格式化显示定时器计算结果"""
        self.timer_result_text.config(state=tk.NORMAL)
        self.timer_result_text.delete(1.0, tk.END)
        
        try:
            results = []
            if 'clock' in result:
                freq_hz = result['clock']
                freq_mhz = freq_hz / Decimal('1e6')
                results.append(f"时钟频率：{freq_mhz:.6f} MHz ({freq_hz:.0f} Hz)")
            if 'time' in result:
                time_us = result['time'] * Decimal('1e6')
                results.append(f"溢出时间：{float(time_us):.12f} μs")
            if 'psc' in result:
                psc = result['psc']
                recommended = max(0, int(psc.quantize(Decimal('1'), rounding='ROUND_HALF_UP')))
                results.append(f"预分频系数：推荐值 PSC = {recommended}")
            if 'arr' in result:
                arr = result['arr']
                recommended = max(0, int(arr.quantize(Decimal('1'), rounding='ROUND_HALF_UP')))
                results.append(f"自动重载值：推荐值 ARR = {recommended}")
            
            self.timer_result_text.insert(tk.END, "\n".join(results))
        except Exception as e:
            self.timer_result_text.insert(tk.END, f"结果显示错误: {str(e)}")
        finally:
            self.timer_result_text.config(state=tk.DISABLED)

    def display_freq_result(self, result):
        """格式化显示频率换算结果"""
        self.freq_result_text.config(state=tk.NORMAL)
        self.freq_result_text.delete(1.0, tk.END)
        
        try:
            results = []
            if 'time' in result:
                time_us = result['time'] * Decimal('1e6')
                results.append(f"时间：{float(time_us):.12f} μs")
            if 'frequency' in result:
                results.append(f"频率：{result['frequency']:.6f} Hz")
            
            self.freq_result_text.insert(tk.END, "\n".join(results))
        except Exception as e:
            self.freq_result_text.insert(tk.END, f"结果显示错误: {str(e)}")
        finally:
            self.freq_result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerCalculator(root)
    root.mainloop()