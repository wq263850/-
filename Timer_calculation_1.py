import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, getcontext

# 设置高精度计算环境
getcontext().prec = 20  # 设置计算精度为20位小数

def calculate_missing_value():
    try:
        # 获取输入值
        clock_frequency = clock_frequency_entry.get()
        overflow_time = overflow_time_entry.get()
        psc = psc_entry.get()
        arr = arr_entry.get()

        # 统计已输入的值
        inputs = [clock_frequency, overflow_time, psc, arr]
        filled = sum(1 for x in inputs if x.strip() != "")

        if filled != 3:
            messagebox.showerror("错误", "请填写任意三个值")
            return

        # 将输入值转换为Decimal类型（仅overflow_time需要高精度）
        if clock_frequency:
            clock_frequency = float(clock_frequency) * 1e6  # MHz to Hz
        if overflow_time:
            overflow_time = Decimal(overflow_time) * Decimal(1e-6)  # us to s
        if psc:
            psc = int(psc)
        if arr:
            arr = int(arr)

        # 计算缺失的值
        if not clock_frequency:
            clock_frequency = (arr + 1) * (psc + 1) / float(overflow_time)
            clock_frequency_entry.delete(0, tk.END)
            clock_frequency_entry.insert(0, f"{clock_frequency / 1e6:.2f}")  # Hz to MHz

        elif not overflow_time:
            overflow_time = Decimal((arr + 1) * (psc + 1)) / Decimal(clock_frequency)
            overflow_time_entry.delete(0, tk.END)
            overflow_time_entry.insert(0, f"{float(overflow_time * Decimal(1e6)):.16f}")  # s to us

        elif not psc:
            psc = (clock_frequency * float(overflow_time)) / (arr + 1) - 1
            psc_entry.delete(0, tk.END)
            psc_entry.insert(0, f"{int(psc)}")

        elif not arr:
            arr = (clock_frequency * float(overflow_time)) / (psc + 1) - 1
            arr_entry.delete(0, tk.END)
            arr_entry.insert(0, f"{int(arr)}")

    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字")

# 清除输入框内容
def clear_entry(entry):
    entry.delete(0, tk.END)

# 创建主窗口
root = tk.Tk()
root.title("STM32定时器计算器")

# 创建输入框、标签和清除按钮
def create_entry_with_clear_button(label_text, row):
    label = tk.Label(root, text=label_text)
    label.grid(row=row, column=0, padx=10, pady=10)

    entry = tk.Entry(root)
    entry.grid(row=row, column=1, padx=10, pady=10)

    clear_button = tk.Button(root, text="清除", command=lambda: clear_entry(entry))
    clear_button.grid(row=row, column=2, padx=10, pady=10)

    return entry

# 创建输入框和清除按钮
clock_frequency_entry = create_entry_with_clear_button("时钟频率（MHz）:", 0)
overflow_time_entry = create_entry_with_clear_button("定时器溢出时间（us）:", 1)
psc_entry = create_entry_with_clear_button("PSC (Prescaler):", 2)
arr_entry = create_entry_with_clear_button("ARR (CounterPeriod):", 3)

# 创建计算按钮
calculate_button = tk.Button(root, text="计算", command=calculate_missing_value)
calculate_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# 运行主循环
root.mainloop()