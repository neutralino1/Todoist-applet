#! /usr/bin/env python

#import gobject
import gtk

class qwerty12():
    tah_timeout = 1000

    def __init__(self):
        #self.screen = None
        #self.root_win = None
        #self.rec = None
        #self.mapped = False
        #self.is_icon_on_top = True
        #self.press_event = None
        #self.last_tah_press_num = -1
        #self.press_num = 0
        #self.pressing = False
        gtk.gdk.event_handler_set(self.on_any_event)
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_stock(gtk.STOCK_CONNECT)
        self.clicked_menu = gtk.Menu()
        self.clicked_menu.__dict__['mapped'] = False
        self.clicked_menu.append(gtk.MenuItem('Clicked 1'))
        self.clicked_menu.show_all()
        gtk.status_icon_position_menu(self.clicked_menu, self.statusIcon)
    def on_any_event(self, event):
        if event.type == gtk.gdk.MOTION_NOTIFY: return
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            self.clicked_menu.popup(None,None,gtk.status_icon_position_menu,1,event.time,self.statusIcon)
        gtk.main_do_event(event)

if __name__ == "__main__":
    q12 = qwerty12()
    gtk.main()
