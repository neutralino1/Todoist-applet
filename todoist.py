#!/usr/bin/env python

import json
import httplib
import sys
import pygtk
import gtk
import egg.trayicon
import pango

class Item:
    def __init__(self, i):        
        for n, v in i.iteritems():
            setattr(self, n, v)
    def __str__(self):
        return' %s- %s' % (' '*self.indent, self.content)

class Project:
    def __init__(self, p):        
        self.items = []
        for n, v in p.iteritems():
            setattr(self, n, v)
    def addItems(self, itms):
        for i in itms:
            self.addItem(i)
    def addItem(self, itm):
        if isinstance(itm, Item):
            self.items += [itm]
        else: 
            self.items += [Item(itm)]
    def __str__(self):
        out = '%s* %s (%i)' % (' '*self.indent, self.name, self.cache_count)
        return out
   
class Todoist:
    priority_colors = [gtk.gdk.color_parse('black'), gtk.gdk.color_parse('green'),
                       gtk.gdk.color_parse('blue'), gtk.gdk.color_parse('red')]
    def __init__(self):
        self.setupConnections()
        self.email = 'bluesmanu@hotmail.com'
        self.passw = 'epiphone'
        self.projects = []
        self.token = 0
        self.setupTodoList()
        self.setupSysTrayIcon()
        self.login()
        self.retrieveAll()
        self.fillTodoList()
        #self.printProjects()
        gtk.main()
        self.closeConnections()
    
    def setupConnections(self):
        self.http = httplib.HTTPConnection('todoist.com')
        self.https = httplib.HTTPSConnection('todoist.com')
    
    def closeConnections(self):
        self.http.close()
        self.https.close()

    def requestHTTP(self, req, https=False):
        if https: c = self.https
        else: c = self.http
        c.request('GET','/API/%s' % req)
        r = c.getresponse()
        if r.status == 200:
            data = r.read()
            djson = json.loads(data)
        else: djson = ''
        return r.status, djson

    def login(self):
        if not self.email or not self.login: return 0
        try:
            status, login = self.requestHTTP('login?email=%s&password=%s' % (self.email, self.passw), https=True)
        except: 
            login, status = 0, 0
        if login == 'LOGIN_ERROR':
            print 'Wrong credentials!'
            return 0
        if status != 200:
            print 'Unknown problem!'
            return 0
        self.full_name = login['full_name']
        print 'Hello %s!' % self.full_name
        self.token = login['api_token']
        return 1

    def retrieveAll(self):
        if not self.token: return
        status, proj = self.requestHTTP('getProjects?token=%s' % self.token)
        for p in proj:
            pr = Project(p)
            status, items = self.requestHTTP('getUncompletedItems?project_id=%s&token=%s' % (pr.id, self.token))
            pr.addItems(items)
            self.projects += [pr]

    def printProjects(self):
        print 'Your projects:'
        for p in self.projects:
            print p

    def setupTodoList(self):
        self.todoList = gtk.Menu()
        self.todoList.append(gtk.MenuItem('Login in...'))
        self.todoList.set_size_request(450, -1)
        self.todoList.show_all()
        self.popupMenu = gtk.Menu()
        exitIt = gtk.MenuItem('Exit')
        exitIt.connect('button-press-event', self.exitTodolist)
        self.popupMenu.append(exitIt)
        self.popupMenu.show_all()

    def fillTodoList(self):
        w5 = ' '*5
        w3 = ' '*3
        for c in self.todoList.get_children():
            self.todoList.remove(c)
        if len(self.projects) > 0:
            label = gtk.Label('Your projects')
            attr = pango.AttrList()
            attr.insert(pango.AttrSize(15000, 0, -1))
            attr.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, -1))
            label.set_attributes(attr)
            item = gtk.MenuItem()
            item.add(label)
            item.set_sensitive(False)
            self.todoList.append(item)
            cindent = -1
            for p in self.projects:
                if p.indent <= cindent:
                    self.todoList.append(gtk.SeparatorMenuItem())
                cindent = p.indent
                item = gtk.MenuItem()
                lalign = gtk.Alignment(0, 0, 0, 0)
                width = 2 if p.indent == 1 else 1
                start = p.indent-1
                label = gtk.Label('%s%s %s (%i)' % (start*w3, ' '*width, p.name, p.cache_count))
                attr = pango.AttrList()
                attr.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, -1))
                color = gtk.gdk.color_parse(p.color)
                attr.insert(pango.AttrBackground(color.red, color.green, color.blue, start*3, start*3 + width))
                attr.insert(pango.AttrSize(10000 - (p.indent - 1)*1000, 0, -1))
                label.set_attributes(attr)
                lalign.add(label)
                item.add(lalign)
                item.set_sensitive(False)
                self.todoList.append(item)
                for i in p.items:
                    #item = gtk.MenuItem()
                    #lalign = gtk.Alignment(0, 0, 0, 0)
                    #hb = gtk.HBox()
                    #hb.pack_start(gtk.Label('%s' % ' '*(end+5)))
                    #cb = gtk.CheckButton('%s' % i.content[:10])
                    #hb.pack_start(cb)
                    #lalign.add(hb)
                    #item.add(lalign)
                    #item.connect('select', self.selectItem)
                    #self.todoList.append(item)
                    ######
                    txt = i.content
                    if txt[0] == '*': 
                        txt = txt[2:]
                        cmi = gtk.MenuItem()
                    else:
                        cmi = gtk.CheckMenuItem()
                        cmi.connect('activate', self.activateCheckMenuItem)
                    lalign = gtk.Alignment(0, 0, 0, 0)
                    hb = gtk.HBox()
                    hb.pack_start(gtk.Label(w5*i.indent))
                    bullet = gtk.Label(u'\u2022 ')
                    valign = gtk.Alignment(1, 0, 0, 0)
                    valign.add(bullet)
                    attr = pango.AttrList()
                    attr.insert(pango.AttrSize(15000, 0, -1))
                    if i.priority > 1:
                        color = self.priority_colors[i.priority - 1]
                        attr.insert(pango.AttrForeground(color.red, color.green, color.blue, 0, -1))
                    bullet.set_attributes(attr)
                    bullet.set_size_request(-1, 12)
                    hb.pack_start(valign)
                    lab = self.prepareLabel(txt)
                    attr = pango.AttrList()
                    attr.insert(pango.AttrSize(7000, 0, -1))
                    if i.indent > 1 : 
                        lab.set_attributes(attr)
                    hb.pack_start(lab)
                    arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_IN)
                    #arrow.connect('button-press-event', self.arrowClick)
                    #hb.add(arrow)
                    btn = gtk.Button('he')
                    btn.connect('released', self.buttonClick)
                    #hb.add(btn)
                    lalign.add(hb)
                    cmi.add(lalign)
                    self.todoList.append(cmi)
        else:
            self.todoList.append(gtk.MenuItem('No projets.'))
        self.todoList.show_all()

    def prepareLabel(self, txt):
        out = ''
        for w in txt.split(' '):
            if len(w) > 50 : 
                w = '%s...' % w[:50]                
            out += '%s ' % w
        out = out[:-1]
        lab = gtk.Label(out)
        #lab.set_max_width_chars(50)
        lab.set_line_wrap(True)
        #lab.justify = gtk.JUSTIFY_LEFT
        return lab
    
    def buttonClick(self, obj):
        print 'ha'

    def activateCheckMenuItem(self, obj):
        bul = obj.get_child().get_child().get_children()[1].get_child()
        lab = obj.get_child().get_child().get_children()[2]
        txt = lab.get_text()
        attr = pango.AttrList()
        color = gtk.gdk.color_parse('dark gray')
        attr.insert(pango.AttrForeground(color.red, color.green, color.blue, 0, -1))
        attr.insert(pango.AttrStrikethrough(obj.active, 0, -1))
        lab.set_attributes(attr)
        attr = bul.get_attributes()
        attr.insert(pango.AttrForeground(color.red, color.green, color.blue, 0, -1))
        bul.set_attributes(attr)

    def selectItem(self, obj):
        cb = obj.get_child().get_child().get_children()[1]
        lab = cb.get_child()
        cb.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.Color(65535,0,0))
        cb.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(65535,0,0))
        #cb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535,0,0))
        #attr = pango.AttrList()
        #attr.insert(pango.AttrBackground(10000, 0, 0, 0, -1))
        #lab.set_attributes(attr)

    def setupSysTrayIcon(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_file('systray.png')
        self.statusIcon.set_tooltip('TodoIst.com')
        #self.clicked_menu.__dict__['mapped'] = False
        gtk.status_icon_position_menu(self.todoList, self.statusIcon)
        self.statusIcon.connect('button-press-event', self.sysTrayPress) 

    def sysTrayPress(self, obj, event):
        if event.button == 1:
            self.todoList.popup(None,None,gtk.status_icon_position_menu,1,event.time,self.statusIcon)
        if event.button == 3:
            self.popupMenu.popup(None,None,gtk.status_icon_position_menu,1,event.time,self.statusIcon)
        
    def exitTodolist(self, obj, event):
        if event.button == 1:
            gtk.main_quit()

def main():
    todo = Todoist()
                
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'Bye.'
