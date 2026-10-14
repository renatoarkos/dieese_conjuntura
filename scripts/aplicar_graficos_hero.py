import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter

def make_time_series_chart(w, h, seed=101):
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    
    np.random.seed(seed)
    n = 60
    t = np.linspace(0, 12, n)
    # Realistic economic trend
    trend = 10 + 1.2 * t + 2.5 * np.sin(t * 0.8) + np.cumsum(np.random.randn(n) * 0.45)
    
    # Soft grid
    ax.grid(True, color='#ffffff', alpha=0.15, linestyle='--', linewidth=0.6)
    
    # Gradient area fill underneath
    ax.fill_between(t, trend, min(trend) - 1, color='#0284c7', alpha=0.3)
    ax.fill_between(t, trend, min(trend) - 1, color='#38bdf8', alpha=0.15)
    
    # Main line
    ax.plot(t, trend, color='#38bdf8', linewidth=2.0)
    
    # Secondary comparison benchmark line (dashed)
    comp = 8 + 0.9 * t + 1.8 * np.cos(t * 0.7) + np.cumsum(np.random.randn(n) * 0.3)
    ax.plot(t, comp, color='#ffffff', linewidth=1.2, alpha=0.75, linestyle=':')
    
    # Red accent dot at the latest point
    ax.scatter([t[-1]], [trend[-1]], color='#EC0000', s=35, zorder=6, edgecolors='#ffffff', linewidths=0.8)
    
    # Peak dots
    peaks = [15, 38]
    ax.scatter(t[peaks], trend[peaks], color='#38bdf8', s=16, zorder=5)
    
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(min(trend) - 1, max(trend) + 2)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.96)
    
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    im = Image.fromarray(arr).convert('RGB')
    return im.resize((w, h), Image.Resampling.LANCZOS)

def make_bar_chart(w, h, seed=202):
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    
    np.random.seed(seed)
    bars = 8
    x = np.arange(bars)
    vals = np.array([4.2, 5.8, 3.5, 7.1, 6.4, 8.9, 9.5, 11.2])
    
    colors = ['#0284c7'] * (bars - 1) + ['#EC0000'] # last bar highlighted in red
    
    ax.grid(True, axis='y', color='#ffffff', alpha=0.15, linestyle='--', linewidth=0.6)
    ax.bar(x, vals, color=colors, width=0.65, edgecolor='#38bdf8', linewidth=0.5)
    
    ax.set_ylim(0, max(vals) * 1.15)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.06, top=0.94)
    
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    im = Image.fromarray(arr).convert('RGB')
    return im.resize((w, h), Image.Resampling.LANCZOS)

def make_sparkline_card(w, h, kind='line', seed=303):
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    
    np.random.seed(seed)
    if kind == 'line':
        x = np.linspace(0, 5, 20)
        y = np.cumsum(np.random.randn(20) * 0.5) + np.linspace(2, 6, 20)
        ax.fill_between(x, y, min(y), color='#38bdf8', alpha=0.25)
        ax.plot(x, y, color='#38bdf8', linewidth=2.0)
        ax.scatter([x[-1]], [y[-1]], color='#EC0000', s=22, zorder=5)
    elif kind == 'bar':
        x = np.arange(5)
        y = np.array([2.5, 4.0, 3.2, 5.5, 6.8])
        ax.bar(x, y, color=['#0284c7', '#0284c7', '#38bdf8', '#38bdf8', '#EC0000'], width=0.6)
    elif kind == 'donut':
        # Gauge donut
        wedges, _ = ax.pie([74, 26], colors=['#38bdf8', (1, 1, 1, 0.2)], startangle=90)
        plt.setp(wedges, width=0.35, edgecolor='#04026e')
        ax.scatter([0], [0], color='#EC0000', s=12)
    else:
        x = np.linspace(0, 5, 20)
        y = 5 + np.sin(x*1.5) * 2 + np.cumsum(np.random.randn(20)*0.2)
        ax.plot(x, y, color='#4ade80', linewidth=1.8)
        ax.scatter([x[-1]], [y[-1]], color='#4ade80', s=20)
        
    ax.set_axis_off()
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.04, top=0.96)
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    im = Image.fromarray(arr).convert('RGB')
    return im.resize((w, h), Image.Resampling.LANCZOS)

def process_hero_home():
    path = 'frontend/assets/hero/hero-home.png'
    img = Image.open(path).convert('RGB')
    
    # 1. Main chart on Left Monitor: x=[692, 826], y=[462, 568] -> 135x107
    w1, h1 = (826 - 692 + 1), (568 - 462 + 1)
    chart1 = make_time_series_chart(w1, h1, seed=42)
    img.paste(chart1, (692, 462))
    
    # 2. Bottom right chart on Left Monitor: x=[930, 1010], y=[608, 674] -> 81x67
    w2, h2 = (1010 - 930 + 1), (674 - 608 + 1)
    chart2 = make_bar_chart(w2, h2, seed=88)
    img.paste(chart2, (930, 608))
    
    # 3. Four cards on Left Monitor:
    # Card 1: x=[694, 726], y=[592, 630]
    c1 = make_sparkline_card(726-694+1, 630-592+1, kind='line', seed=11)
    img.paste(c1, (694, 592))
    
    # Card 2: x=[736, 768], y=[592, 628]
    c2 = make_sparkline_card(768-736+1, 628-592+1, kind='bar', seed=22)
    img.paste(c2, (736, 592))
    
    # Card 3: x=[696, 728], y=[652, 686]
    c3 = make_sparkline_card(728-696+1, 686-652+1, kind='donut', seed=33)
    img.paste(c3, (696, 652))
    
    # Card 4: x=[736, 768], y=[648, 684]
    c4 = make_sparkline_card(768-736+1, 684-648+1, kind='alt', seed=44)
    img.paste(c4, (736, 648))
    
    # 4. Main chart on Right Monitor: x=[1184, 1284], y=[438, 530] -> 101x93
    w_r, h_r = (1284 - 1184 + 1), (530 - 438 + 1)
    chart_r = make_time_series_chart(w_r, h_r, seed=999)
    img.paste(chart_r, (1184, 438))
    
    # 5. Right Monitor cards:
    # x=[1182, 1204], y=[550, 580]
    cr1 = make_sparkline_card(1204-1182+1, 580-550+1, kind='line', seed=55)
    img.paste(cr1, (1182, 550))
    # x=[1212, 1236], y=[554, 582]
    cr2 = make_sparkline_card(1236-1212+1, 582-554+1, kind='bar', seed=66)
    img.paste(cr2, (1212, 554))
    # x=[1182, 1202], y=[600, 628]
    cr3 = make_sparkline_card(1202-1182+1, 628-600+1, kind='alt', seed=77)
    img.paste(cr3, (1182, 600))
    
    img.save(path, quality=95)
    print('hero-home.png updated successfully with real graphs!')

if __name__ == '__main__':
    process_hero_home()
