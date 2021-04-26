from dearpygui.simple import *
from dearpygui.core import *
from dearpygui.demo import *

from src.utils import subscribe_button_cb, subwindow_button_callback

add_additional_font('fonts/msyh.ttc', 18, glyph_ranges='chinese_full')

with window('Subscribe', width=250, height=280, x_pos=50, y_pos=50, no_close=True, label='订阅管理'):
    add_button("new_sub", label='新增订阅', height=40, width=230)
    set_item_callback("new_sub", callback=subscribe_button_cb)
    add_text('已订阅列表：')
    add_child('subs', autosize_x=True, autosize_y=True)
    end()


with window('subscribe_input', width=250, height=200, show=False, x_pos=100, y_pos=130, label='新增订阅'):
    add_input_text('author', label='作者', hint='留空表示不限', no_spaces=True)
    add_input_text('keywords', label='关键词', hint='若有多个请用空格分隔')
    add_checkbox('hit', label='Hit优化', default_value=True)
    add_text('err_msg', default_value=' ', color=(255, 0, 0, 255))
    add_button("Done", label='确定',  callback=subwindow_button_callback)
    add_same_line(spacing=10)
    add_button("Cancel", label='取消',  callback=subwindow_button_callback)

set_main_window_size(720, 540)
set_main_window_title('Poems subscribing')
# set_primary_window('Subscribe', True)

start_dearpygui()