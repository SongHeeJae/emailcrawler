from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
from urllib import parse
from time import time
from time import localtime
import csv

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)    

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

def getCurrentTime() :
    now = localtime()
    return "%04d-%02d%02d-%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)



def search(url, text, menu_list) :
    menu_list.clear()
    text.delete('1.0', END) # 초기화

    if(len(url.get()) == 0) :
        messagebox.showinfo("알림", "url을 입력해주세요")
        return

    path = 'https://cafe.naver.com/' + url.get()
    req = requests.get(path)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    cafe_menu_list = soup.find_all('ul', class_='cafe-menu-list')
    
    for cml in cafe_menu_list :
        li = cml.find_all('li')
        for l in li :
            a = l.find('a')
            url_ = parse.urlparse(path + a['href'])
            query = parse.parse_qs(url_.query)
            if 'search.menuid' not in query :
                continue
            menu_list.append([a.text.strip(),  query['search.clubid'][0], query['search.menuid'][0]])
    
    if(len(menu_list) == 0) :
        text.insert(INSERT, '카페명 URL이 잘못되었습니다.')
        return

    for i in range(len(menu_list)) :
        text.insert(END, str(i+1) + ' - ' + menu_list[i][0] + '\n')

def getClubId(url) :
    path = 'https://cafe.naver.com/' + url
    req = requests.get(path)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script').text
    script = script[script.find("g_sClubId"):]
    clubid = script[script.find('"'):script.find(';')].strip('"')
    return clubid
    
def getMenuId(url) :
    path = 'https://cafe.naver.com/' + url
    req = requests.get(path)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    cafe_menu_list = soup.find_all('ul', class_='cafe-menu-list')
    
    menu_id_list = []
    for cml in cafe_menu_list :
        li = cml.find_all('li')
        for l in li :
            a = l.find('a')
            url_ = parse.urlparse(path + a['href'])
            query = parse.parse_qs(url_.query)
            if 'search.menuid' not in query :
                continue
            menu_id_list.append(query['search.menuid'][0])
    
    return menu_id_list

def downloadText(emails, num) :
    with open(getCurrentTime() + '_' + str(num) +'.txt', 'w') as f :
        i=0
        for k in emails.keys() :
            if i==0 :
                f.write(k + "@naver.com")
                i+=1
            else :
                f.write(',' + k + "@naver.com")
    

def downloadExcel(emails, num) :
    with open(getCurrentTime() + '_' + str(num) + '.csv', 'w', newline='') as f :
        wr = csv.writer(f)
        for k in emails.keys() :
            wr.writerow([k + "@naver.com"])

def download(radVar, emails, num) :
    if radVar.get() == 1:
        downloadText(emails, num)
    else :
        downloadExcel(emails, num)

def do_crawling(radVar, radVar2, items) :
    
  
    if(radVar.get() == 0) :
        messagebox.showinfo("알림", "다운로드 파일을 선택해주세요.")
        return

    if(radVar2.get() == 0) :
        messagebox.showinfo("알림", "다운로드 방식을 선택해주세요.")
        return
    num = 1
    emails = {}
    for item in items :
        if(item[0].get() == 0) : continue
        url = item[2].get()
        board_num = item[3].get().strip().split(',')
        page_num = item[4].get().strip().split(',')

        if(url == '' or board_num == '' or page_num == '') : continue

        club_id = getClubId(url)
        menu_id_list = getMenuId(url)
        
        for i in range(len(board_num)) :
            menu_id = menu_id_list[int(board_num[i].strip()) - 1]
            for j in range(1, int(page_num[i].strip())+ 1):
                path = 'https://cafe.naver.com/' + url + '/ArticleList.nhn?search.clubid='+club_id+'&search.menuid='+menu_id+'&search.boardtype=L&search.page=' + str(j)
                req = requests.get(path)
                html = req.text
                soup = BeautifulSoup(html, 'html.parser')
                a_board = soup.find_all('div', class_='article-board')[1]
                trlist = a_board.find_all('tr')
                if(trlist[0].text.strip()[0] == '등') :
                    break
                for tr in trlist :
                    a = tr.find('a')['onclick']
                    if a[0] != 'u' : continue
                    s = a.find("'")
                    e = a.find("'", s+1)
                    email = a[s+1:e]
                    if(email not in emails) : 
                        emails[email] = 0
            if radVar2.get() == 3 :
                download(radVar, emails, num)
                num += 1
                emails.clear()
        if radVar2.get() == 2 :
            download(radVar, emails, num)
            num += 1
            emails.clear()
            
    if(radVar2.get() == 1) :
        download(radVar, emails, num)


    messagebox.showinfo("알림", "완료되었습니다.")
    return


def addItem(items, frame) :
    cVar = IntVar()
    chk = Checkbutton(frame.interior, variable = cVar)
    chk.select()
    chk.grid(row=1+len(items), column=0)

    url = Entry(frame.interior, width=20)
    url.grid(row=1+len(items), column=1)

    board_num = Entry(frame.interior, width=20)
    board_num.grid(row=1+len(items), column=2)

    page_num = Entry(frame.interior, width=20)
    page_num.grid(row=1+len(items), column=3)

    items.append([cVar, chk, url, board_num, page_num])

    

def checkAll(items, cVar1) :
    for item in items :
        if(cVar1.get()==1) :
            item[1].select()
        else :
            item[1].deselect()
        
def save(radVar, radVar2, items) :
    filename = filedialog.asksaveasfilename(filetypes=[('text', '.txt')], title="save")
  
    if filename[-4:] != '.txt' :
        filename += '.txt'

    with open(filename, 'w') as f :
        f.write('navercafe\n')
        f.write(str(radVar.get()) + '\n')
        f.write(str(radVar2.get()) + '\n')
        for item in items :
            f.write(item[2].get() + '-' + item[3].get() + '-' + item[4].get() + '\n')

def widgetClear(items) :
    for item in items:
        item[1].destroy()
        item[2].destroy()
        item[3].destroy()
        item[4].destroy()

def load(radVar, radVar2, items, frame2) :
    
    filename = filedialog.askopenfilename(filetypes=[('text', '.txt')], title="save")
    if(filename == '') : return
    
    with open(filename, 'r', encoding='utf-8') as f :
        lines = f.readlines()
        if lines[0].strip('\n') == 'navercafe' :
            widgetClear(items)
            items.clear()
            radVar.set(lines[1].strip())
            radVar2.set(lines[2].strip())
            lines = lines[3:]
            for line in lines :
                l = line.strip('\n').split('-')
                addItem(items, frame2)
                item = items[len(items)-1]
                item[2].insert(0, l[0].strip())
                item[3].insert(0, l[1].strip())
                item[4].insert(0, l[2].strip())

if __name__ == '__main__' :
    
    menu_list = []
    items = []

    window = Tk()
    window.title('cafe_id_crawling')
    window.geometry('800x500')
    
    frame1 = Frame(window)
    Label(frame1, text="카페명 URL 입력").pack()
    url = Entry(frame1,width=20)
    url.pack()

    frame1_1 = Frame(frame1)
    scrollbar = Scrollbar(frame1_1)
    text = Text(frame1_1, width=30)
    text.pack(side=LEFT, fill=Y)
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    text.pack()
    frame1_1.pack()
    
    Button(frame1, text='게시판 제목 검색', command=lambda url=url, text=text, menu_list=menu_list:search(url, text, menu_list)).pack()
    frame1.pack(side=LEFT)
    

    frame2 = Frame()
    
    radVar = IntVar()
    r1 = Radiobutton(frame2, text="메모장", variable=radVar, value=1)
    r1.grid(row=0, column=0)
    r2 = Radiobutton(frame2, text="엑셀", variable=radVar, value=2)
    r2.grid(row=1, column=0)

    radVar2 = IntVar()
    r3 = Radiobutton(frame2, text="통합", variable=radVar2, value=1)
    r3.grid(row=0, column=1)
    r4 = Radiobutton(frame2, text="카페별", variable=radVar2, value=2)
    r4.grid(row=1, column=1)
    r5 = Radiobutton(frame2, text="게시판별", variable=radVar2, value=3)
    r5.grid(row=2, column=1)
    
    

    frame3 = VerticalScrolledFrame(frame2)
    Label(frame3.interior, text='', width=60).grid(row=0,column=0,columnspan=4)

    Button(frame2, text="추가", command=lambda items=items, frame=frame3: addItem(items, frame)).grid(row=3, column=0)
    
    Label(frame2, text="카페URL", width=20).grid(row=4, column=1)
    Label(frame2, text="게시판번호", width=20).grid(row=4, column=2)
    Label(frame2, text="페이지수",width=20).grid(row=4, column=3)
    Button(frame2, text="시작", command=lambda radVar=radVar, radVar2=radVar2, items=items: do_crawling(radVar, radVar2, items)).grid(row=4, column=4)
    frame3.grid(row=5, column=0, columnspan=6)

    cVar1 = IntVar()
    all_chk = Checkbutton(frame2, text="전체", command=lambda items=items, cVar1=cVar1: checkAll(items, cVar1), variable=cVar1)
    all_chk.select()
    all_chk.grid(row=4, column=0)

    Button(frame2, text="저장", command=lambda radVar=radVar, radVar2=radVar2, items=items: save(radVar, radVar2, items)).grid(row=0, column=3)
    Button(frame2, text="불러오기", command=lambda radVar=radVar, radVar2=radVar2, items=items, frame3=frame3: load(radVar, radVar2, items,frame3) ).grid(row=0, column=4)

    frame2.pack() 
    
   
    window.mainloop()