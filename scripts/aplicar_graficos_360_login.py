import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

def make_chart(w, h, kind='line', seed=123):
    fig, ax = plt.subplots(figsize=(max(w, 20)/100, max(h, 20)/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    np.random.seed(seed)
    
    if kind == 'line':
        t = np.linspace(0, 10, 40)
        y = 5 + 1.1*t + np.cumsum(np.random.randn(40)*0.4)
        ax.grid(True, color='#ffffff', alpha=0.15, linestyle=':')
        ax.fill_between(t, y, min(y)-1, color='#0284c7', alpha=0.3)
        ax.plot(t, y, color='#38bdf8', linewidth=2.0)
        ax.scatter([t[-1]], [y[-1]], color='#EC0000', s=25, zorder=5)
    elif kind == 'bar':
        bars = 6
        x = np.arange(bars)
        vals = np.array([3.2, 4.8, 6.1, 5.0, 7.8, 9.2])
        colors = ['#0284c7'] * (bars - 1) + ['#EC0000']
        ax.grid(True, axis='y', color='#ffffff', alpha=0.15, linestyle=':')
        ax.bar(x, vals, color=colors, width=0.6, edgecolor='#38bdf8', linewidth=0.5)
    elif kind == 'spark':
        t = np.linspace(0, 5, 20)
        y = np.cumsum(np.random.randn(20)*0.5)
        ax.plot(t, y, color='#38bdf8', linewidth=2.0)
        ax.scatter([t[-1]], [y[-1]], color='#EC0000', s=18)
    else:
        wedges, _ = ax.pie([68, 32], colors=['#38bdf8', (1, 1, 1, 0.2)], startangle=90)
        plt.setp(wedges, width=0.4, edgecolor='#04026e')
        ax.scatter([0], [0], color='#EC0000', s=10)
        
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    im = Image.fromarray(arr).convert('RGB')
    return im.resize((w, h), Image.Resampling.LANCZOS)

def process_360():
    path = 'frontend/assets/secoes/o-que-e-dieese-360.png'
    if not os.path.exists(path): return
    img = Image.open(path).convert('RGB')
    
    # Apply to the prominent monitor cards
    boxes = [
        (408, 460, 478-408+1, 514-460+1, 'line', 101),
        (414, 378, 474-414+1, 454-378+1, 'bar', 102),
        (476, 348, 528-476+1, 454-348+1, 'line', 103),
        (704, 310, 768-704+1, 366-310+1, 'bar', 104),
        (520, 186, 572-520+1, 230-186+1, 'spark', 105),
        (610, 226, 652-610+1, 268-226+1, 'donut', 106),
        (986, 256, 1016-986+1, 328-256+1, 'bar', 107),
        (1018, 264, 1048-1018+1, 328-264+1, 'spark', 108),
    ]
    for x, y, w, h, kind, s in boxes:
        ch = make_chart(w, h, kind=kind, seed=s)
        img.paste(ch, (x, y))
        
    img.save(path, quality=95)
    print('o-que-e-dieese-360.png updated with real graphs!')

def process_login():
    path = 'frontend/assets/login/login-lateral.png'
    if not os.path.exists(path): return
    img = Image.open(path).convert('RGB')
    arr = np.array(img)
    # Find monitor area in login image:
    # Blue pixels roughly around x=300..750, y=400..900
    # Let's paste a prominent dashboard graphic on the central monitor screen
    # Check bounds
    mask = (arr[:, :, 0] < 45) & (arr[:, :, 1] < 45) & (arr[:, :, 2] > 65)
    ys, xs = np.where(mask)
    if len(xs) > 0:
        # Find the center cluster of the monitor
        ch1 = make_time_series_chart_login(220, 140, seed=555)
        # Paste inside the main screen area
        ch2 = make_bar_chart_login(140, 90, seed=666)
        # Let's inspect where the main monitor display is:
        # We can paste on the detected center
        cx, cy = int(np.median(xs)), int(np.median(ys))
        if cx - 110 >= 0 and cy - 70 >= 0 and cx + 110 < img.size[0] and cy + 70 < img.size[1]:
            img.paste(ch1, (cx - 110, cy - 70))
            if cx - 110 >= 0 and cy + 80 + 90 < img.size[1]:
                img.paste(ch2, (cx - 110, cy + 80))
    img.save(path, quality=95)
    print('login-lateral.png updated with real graphs!')

def make_time_series_chart_login(w, h, seed=555):
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    np.random.seed(seed)
    t = np.linspace(0, 12, 50)
    y = 8 + 1.2*t + 2*np.sin(t*0.9) + np.cumsum(np.random.randn(50)*0.4)
    ax.grid(True, color='#ffffff', alpha=0.18, linestyle=':')
    ax.fill_between(t, y, min(y)-1, color='#0284c7', alpha=0.35)
    ax.plot(t, y, color='#38bdf8', linewidth=2.5)
    ax.scatter([t[-1]], [y[-1]], color='#EC0000', s=40, zorder=5)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    return Image.fromarray(arr).convert('RGB').resize((w, h), Image.Resampling.LANCZOS)

def make_bar_chart_login(w, h, seed=666):
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=300)
    fig.patch.set_facecolor('#04026e')
    ax.set_facecolor('#04026e')
    x = np.arange(7)
    vals = np.array([4, 6, 5, 8, 7, 10, 12])
    colors = ['#0284c7'] * 6 + ['#EC0000']
    ax.bar(x, vals, color=colors, width=0.6, edgecolor='#38bdf8', linewidth=0.6)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    return Image.fromarray(arr).convert('RGB').resize((w, h), Image.Resampling.LANCZOS)

if __name__ == '__main__':
    process_360()
    process_login()
