from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import threading
import time
import random
import  queue

BUF_SIZE = 1
q1 = queue.Queue(BUF_SIZE)
q2 = queue.Queue(BUF_SIZE)

class mainWindow(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.master = master
        self.createWindow()
        self.images=[]


    def createWindow(self):
        self.master.title("GUI")
        self.pack(fill=BOTH,expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file=Menu(menu)
        file.add_command(label="File",command=self.client_exit)
        menu.add_cascade(label="File",menu=file)
        edit=Menu(menu)
        edit.add_command(label="Show IMG",command=self.show_img)
        edit.add_command(label="Settings",command=self.show_text)
        menu.add_cascade(label="edit",menu=edit)

    def client_exit(self):
        exit()

    def show_img(self):


        img1 = Image.open("./assets/background.png")
        self.images.append(ImageTk.PhotoImage(img1))
        w=self.images[0].width()
        h=self.images[0].height()
        self.master.geometry("{}x{}".format(w,h))

        canvas = Canvas(self,bg="black")
        canvas.create_image(0,0, image=self.images, anchor=NW)
        canvas.pack(expand=YES, fill=BOTH)



        thread1 = Bird(canvas,["./assets/0.png","./assets/1.png","./assets/3.png"])
        thread2 =Pipe(canvas,["./assets/top.png"],["./assets/bottom.png"],w,h)

        thread1.start()
        thread2.start()


    def show_text(self):
        text = Label(self,text="Settings")
        text.pack()


class Bird(threading.Thread):
    def __init__(self,frame,paths):
        threading.Thread.__init__(self)
        self.frame = frame
        self.position=[30,0]
        self.time = 0.04
        self.velocity=50
        self.acceleration=700
        pictures = [ImageTk.PhotoImage(Image.open(path)) for path in paths]
        tags = ["fly","fall","game over"]
        self.images=dict(zip(tags,pictures))
        self.canvas_image = []
        self.game_over=False

    def falling_bird(self):
        if self.velocity>=0:
            try:
                self.frame.delete(self.canvas_image)
            except:
                pass
            self.canvas_image=(self.frame.create_image(self.position[0],self.position[1],image=self.images["fall"],anchor=NW))

    def fly_bird(self,event):
        self.velocity = -300
        self.frame.delete(self.canvas_image)
        self.canvas_image=(self.frame.create_image(self.position[0],self.position[1],image=self.images["fly"],anchor=NW))

    def game_overr(self):
        try:
            self.frame.delete(self.canvas_image)
        except:
            pass
        self.canvas_image=(self.frame.create_image(self.position[0],self.position[1],image=self.images["game over"],anchor=NW))


    def run(self):

        self.falling_bird()
        while True:
            self.Bird_motion()
            if(self.game_over==False):
                self.frame.bind("<Up>", self.fly_bird)
                self.frame.pack()
                self.frame.focus_set()
                self.falling_bird()
            time.sleep(self.time)
            if not q1.full():
                bird_bbox = self.frame.bbox(self.canvas_image)
                print(bird_bbox)
                q1.put(bird_bbox)
            if not q2.empty():
                item = q2.get()
                if item ==True:
                    self.game_over=True
                    print("game over")
                    self.game_overr()


    def Bird_motion(self):

        self.velocity += self.acceleration * self.time
        self.position[1]+=self.velocity*self.time
        self.frame.move(self.canvas_image,0,self.velocity*self.time)





class Pipe(threading.Thread):
    def __init__(self,frame,bottom_pipes,up_pipes,width,height):
        threading.Thread.__init__(self)
        self.frame=frame
        self.canvas_image = []
        self.game_over = False
        self.bottom_pipes = [ ImageTk.PhotoImage(Image.open(pipe)) for pipe in
                            bottom_pipes]
        self.bottom_pipes = [[pipe,width-pipe.width(),0] for pipe in self.bottom_pipes]

        self.up_pipes = [ImageTk.PhotoImage(Image.open(pipe))for pipe in
                         up_pipes]
        self.up_pipes = [[pipe,width-pipe.width(),height-pipe.height()] for pipe in self.up_pipes]
        self.positions=[]
        self.width = width


    def create_pipes(self):

        pipes=random.choice([self.bottom_pipes,self.up_pipes])
        for pipe in pipes:
            x=random.randint(pipe[1], pipe[1]+500)
            y=pipe[2]
            self.canvas_image.append(self.frame.create_image(x,y, image=pipe[0], anchor=NW))
            self.positions.append([x,y])

    def pipe_update(self):
        for i,pipe in enumerate(self.canvas_image):
            x,y=self.frame.coords(pipe)
            if x < random.randint(0,100) and len(self.canvas_image)<2:
                self.create_pipes()
            if x <-self.width:
                self.frame.delete(pipe)
                self.canvas_image.remove(pipe)

            self.frame.move(pipe,-5,0)

    def run(self):
        self.create_pipes()
        while True:
            time.sleep(0.04)
            if self.game_over==False:
                self.pipe_update()

            # self.create_pipes()
            if not q1.empty():
                item = q1.get()
                try:
                    x1,x2,x3,x4 = item
                    if len(self.frame.find_overlapping(x1,x2,x3,x4))>2:

                        self.game_over=True
                        print("game over")
                except:
                    pass
            if not q2.full():
                q2.put(self.game_over)

def main():
    root = Tk()
    mainWindow(root)
    root.geometry("400x400")
    root.mainloop()

if __name__ == "__main__":
    main()


