from dearpygui.simple import *
from dearpygui.core import *
from dearpygui.demo import *

from .PubRead import Publisher, Reader
import config as c

ENTRY_PER_PAGE = c.enrty_per_page

__subscribe_counter = 0
__publisher = Publisher('publisher')

def subentry_button_callback(sender, data):
    if 'del' in sender:
        delete_item('button_' + data.name)
        delete_item(data.name)
        data.unsubscribeToPublisher()
        delete_item(sender)
    else:
        show_item(data.name)

def turn_page_callback(sender, data):
    ws = sender.split('_')
    current_page = get_item_callback_data(ws[0] + '_last_button')
    total_page = get_item_callback_data(ws[0] + '_next_button')
    if ws[1] == 'last':
        if current_page == 1:
            return
        new_page = current_page - 1
    elif ws[1] == 'next':
        if current_page == total_page:
            return
        new_page = current_page + 1
    else:
        new_page = int(get_value(sender))
    if new_page == current_page:
        return
    
    set_item_callback_data(ws[0] + '_last_button', new_page)
    configure_item(ws[0] + '_last_button', enabled= new_page > 1)
    configure_item(ws[0] + '_next_button', enabled= new_page < total_page)
    set_value(ws[0] + '_selectpage', str(new_page))
    hide_item(f'{ws[0]}_p{current_page}')

    if does_item_exist(f'{ws[0]}_p{new_page}'):
        show_item(f'{ws[0]}_p{new_page}')
    else:
        build_page(get_item_callback_data(ws[0] + '_selectpage'), new_page, parent=ws[0] + '_pannel')
    

def build_line(index, poem, ch_name, word_set):
    if index < 0:
        content = poem.title
        tokens = poem.title_token
    else:
        content = poem.content[index]
        tokens = poem.tokens[index]
    i = 0
    for token in filter(lambda x: x in word_set, tokens.split(' ')):
        tmp = content.find(token, i)
        if tmp >= 0:
            if tmp > i:
                add_text(f'{ch_name}_line{index}_{i}', default_value=content[i:tmp])
                add_same_line(spacing=0)
            i = tmp + len(token)
            add_text(f'{ch_name}_line{index}_{tmp}', default_value=content[tmp:i], color=(255, 50, 50, 255))
            if i >= len(content):
                break
            add_same_line(spacing=0)
    else:
        add_text(f'{ch_name}_line{index}_{i}', default_value=content[i:])

    # add_text(f'{ch_name}_line{index}', default_value=content)

def build_page(reader, page, parent=''):
    win_name = reader.name

    with group(f'{win_name}_p{page}', parent=parent):
        for i, poem in enumerate(reader.poems[(page - 1)*ENTRY_PER_PAGE : page*ENTRY_PER_PAGE]):
            poem = poem[0]
            showing = i < 3

            ch_name = f'{win_name}_p{page}_{i}'
            with collapsing_header(ch_name, label=poem.title + ' - ' + poem.author, default_open=showing, show=True):
                add_text(ch_name + '_titie', default_value='标题：')
                add_same_line()
                build_line(-1, poem, ch_name, reader.sym_set)
                add_text(ch_name + '_author', default_value='作者：'+poem.author)
                add_spacing(count=5)
                for j in range(len(poem.content)):
                    build_line(j, poem, ch_name, reader.sym_set)
                    # add_text(f'{ch_name}_line{j}', default_value=content)


def build_windows(author, keywords, hit):
    global __subscribe_counter

    if author == '':
        author = None

    __subscribe_counter += 1
    win_name = f's{__subscribe_counter}'
    reader = Reader(win_name)
    reader.subscribeToPublisher(__publisher, keywords, author, hit)

    with window(win_name, width=320, height=400, show=False, x_pos=230, y_pos=50, label=str(reader)):
        add_text(win_name+'_author', default_value='订阅作者：' + (author if author else '[不限]'))
        add_text(win_name+'_keywords', default_value='关键词：' + (', '.join(keywords)))
        
        total_page = (len(reader.poems) + ENTRY_PER_PAGE - 1) // ENTRY_PER_PAGE
        if total_page > 0:
            add_button(win_name+'_last_button', label='上一页', enabled=False, callback=turn_page_callback, callback_data=1)
            add_same_line(spacing=10)

            page_list = list(map(str, range(1, 1 + total_page)))
            add_combo(win_name+'_selectpage', items=page_list, label=f'/{total_page}页', width=100, default_value='1', callback=turn_page_callback, callback_data=reader)

            add_same_line(spacing=10)
            add_button(win_name+'_next_button', label='下一页', enabled=(total_page>1), callback=turn_page_callback, callback_data=total_page)
            
        with child(win_name + '_pannel', autosize_x=True, autosize_y=True, horizontal_scrollbar=True):
            if total_page == 0:
                add_text(win_name+'_noresult', default_value='没有符合条件的结果')
                add_text(win_name+'_noresult1', default_value='只有data/wordlist_v2.xlsx中的词才能返回结果', color=(255, 0, 0, 255))
                # if c.debug_mode:
                #     add_text(win_name+'_noresult2', default_value='调试模式下请前往命令行查看结果!', color=(255, 0, 0, 255))
                #     add_text(win_name+'_noresult3', default_value='命令行的输出结果为实际检索结果', color=(255, 0, 0, 255))
            else:
                build_page(reader, 1)
    add_button('button_' + win_name, label=str(reader), width=180, height=25,
                callback=subentry_button_callback, callback_data=reader, parent='subs')
    add_same_line(parent='subs', spacing=2)
    add_button('del_' + win_name, label='删除', width=36, height=25,
                callback=subentry_button_callback, callback_data=reader, parent='subs')
    

def subwindow_button_callback(sender, data):
    author = get_value('author')
    keywords = get_value('keywords')
    hit = get_value('hit')
    # print(type(hit))
    # print(author, keywords, hit)
    if sender == 'Done':
        if keywords == '':
            set_value('err_msg', '关键词不能为空.')
            return
        keywords = keywords.split(' ')
        set_value('author', '')
        set_value('keywords', '')
        set_value('err_msg', '')
        build_windows(author, keywords, hit)
    else:
        set_value('err_msg', '')
    hide_item('subscribe_input')

def subscribe_button_cb(sender, data):
    # print(sender, data)
    show_item('subscribe_input')