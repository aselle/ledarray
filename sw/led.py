# MIT License

# Copyright (c) 2025 Andrew Selle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import machine
import struct
import random
import time
ADDR=0x50
ENABLE_ADDR=0xfe
ENABLE_WORD=b'\xc5'
BANKSEL_ADDR=0xfd
RESET_ADDR=0x11
CTRL_ADDR=0x00
ROWS = 20
COLS = 14


class LED:
    def __init__(self):
        self.pin16=machine.Pin(16,machine.Pin.OUT)
        self.pin16.value(1)
        self.i2c=machine.I2C(freq=100000,id=0,scl=1,sda=0)
        self.addrs = [ADDR, ADDR+1]
        self.mems = [[],[]]
        self.clear()
        for addr in self.addrs:
            self.select_bank(addr, 3)
            self.i2c.readfrom_mem(addr, RESET_ADDR, 1)  #RESET
            self.i2c.writeto_mem(addr,CTRL_ADDR, b'\x01') # set enable
            self.i2c.writeto_mem(addr, 0x01, b'\xff') # set 0xff as PCM global.
            self.select_bank(addr, 1)
            for i in range(0xbf):
                self.i2c.writeto_mem(addr, i, b'\xff')
            self.select_bank(addr, 0)
        #for i in range(0x17):
        #    self.i2c.writeto_mem(ADDR, i, b'\xff')
        self.refresh()
    def clear(self, refresh=True):
        for mem in self.mems:
            mem.clear()
            for i in range(0x17):
                mem.append(0)
        if refresh:
            self.refresh()
    def refresh(self):
        for addr,mem in zip(self.addrs, self.mems):
            self.select_bank(addr, 0)
            bytes = b"".join(struct.pack('B',x) for x in mem)
            self.i2c.writeto_mem(addr, 0, bytes)
    def select_bank(self, addr, bank):
        self.i2c.writeto_mem(addr, ENABLE_ADDR, ENABLE_WORD)
        self.i2c.writeto_mem(addr, BANKSEL_ADDR, struct.pack('B',bank))
    def remap(self, col, row):
        if row>=10:
            row-=10
            mem=1
        else:
            mem=0
        #mem=1
        if col < 7:
            r = row*2
            c = col
        elif col < 8:
            c = col
            r = 10+2*(row) if row < 5 else (row-5)*2
        else:
            c = col - 8
            r = 11+row*2 if row < 5 else 1+(row-5)*2
        return mem,c,r
    def plot(self, col,row):
        mem,c,r = self.remap(col, row)
        self.mems[mem][r] |= 1<<c
    def unplot(self, col,row):
        mem,c,r = self.remap(col, row)
        self.mems[mem][r] &= ~(1<<c)
    def draw(self,col,row,bitmap):
        for i in range(len(bitmap)):
            for j in range(len(bitmap[i])):
                if bitmap[i][j]:
                    c,r = col+i,row+j
                    if c>=0 and r>=0 and c<COLS and r<COLS:
                        self.plot(c,r)
    def rando(self):
        c=random.randint(0,COLS-1)
        r=random.randint(0,ROWS-1)
        flip=random.randint(0,1)
        self.plot(c,r) if flip else self.unplot(c,r)
        self.refresh()
    def reorder(self, buf):
        self.clear(False)
        for i in range(len(buf)):
            for j in range(len(buf[i])):
                if buf[i][j]:
                    self.plot(j,i)
    def rshift(self):
        #mem=self.mem
        mem=self.mem
        save18=mem[18] & 0x80
        save16=mem[16] & 0x80
        save14=mem[14] & 0x80
        save12=mem[12] & 0x80
        save10=mem[10] & 0x80 
        save8=mem[8]  & 0x80
        save6=mem[6] & 0x80
        save4=mem[4] & 0x80
        save2=mem[2] & 0x80
        save0=mem[0] & 0x80
        mem[18]=(mem[16]&0x7f) | save16
        mem[16]=(mem[14]&0x7f) | save14
        mem[14]=(mem[12]&0x7f) | save12
        mem[12]=(mem[10]&0x7f) | save10
        mem[10]=(mem[8]&0x7f)
        mem[8]=(mem[6]&0x7f) | save6
        mem[6]=(mem[4]&0x7f) | save4
        mem[4]=(mem[2]&0x7f) | save2
        mem[2]=(mem[0]&0x7f) | save0
        mem[0]=save18
        mem[9]=mem[7]
        mem[7]=mem[5]
        mem[5]=mem[3]
        mem[3]=mem[1]
        mem[1]=mem[19]
        mem[19]=mem[17]
        mem[17]=mem[15]
        mem[15]=mem[13]
        mem[13]=mem[11]
        mem[11]=0
    
    def lshift(self):
        #mem=self.mem
        prev = None
        for idx in range(len(self.mems)):
            mem=self.mems[idx]
            mem1 = self.mems[idx+1] if idx+1 < len(self.mems) else None
            save18=mem[18] & 0x80
            save16=mem[16] & 0x80
            save14=mem[14] & 0x80
            save12=mem[12] & 0x80
            save10=mem[10] & 0x80 
            save8=mem[8]  & 0x80
            save6=mem[6] & 0x80
            save4=mem[4] & 0x80
            save2=mem[2] & 0x80
            save0=mem[0] & 0x80
            mem[0]=(mem[2]&0x7f) | save2
            mem[2]=(mem[4]&0x7f) | save4
            mem[4]=(mem[6]&0x7f) | save6
            mem[6]=(mem[8]&0x7f) | save8
            mem[8]=(mem[10]&0x7f) | ((mem1[10] & 0x80) if mem1 else 0)
            mem[10]=(mem[12]&0x7f) | save12
            mem[12]=(mem[14]&0x7f) | save14
            mem[14]=(mem[16]&0x7f) | save16
            mem[16]=(mem[18]&0x7f) | save18
            if mem1:
                mem[18]=save0 | (mem1[0] & 0x7f)
            else:
                mem[18]=save0

            mem[11]=mem[13]
            mem[13]=mem[15]
            mem[15]=mem[17]
            mem[17]=mem[19]
            mem[19]=mem[1]
            mem[1] = mem[3]
            mem[3] = mem[5]
            mem[5] = mem[7]
            mem[7] = mem[9]
            if mem1:
                mem[9] = mem1[11]
            else:
                mem[9] = 0

        # mem[9]=mem[7]
        # mem[7]=mem[5]
        # mem[5]=mem[3]
        # mem[3]=mem[1]
        # mem[1]=mem[19]
        # mem[19]=mem[17]
        # mem[17]=mem[15]
        # mem[15]=mem[13]
        # mem[13]=mem[11]
        # mem[11]=0

class Life:
    def __init__(self):
        do_random = random.randint(0,1)==1
        self.buf0 = []
        self.buf1 = []
        for i in range(ROWS):
            line0 = []
            line1 = []
            for j in range(COLS):
                line0.append(random.randint(0,1) if do_random else 0)
                line1.append(0)
            self.buf0.append(line0)
            self.buf1.append(line1)
        if not do_random:
            self.buf0[3][0]=1
            self.buf0[4][1]=1
            self.buf0[4][2]=1
            self.buf0[5][0]=1
            self.buf0[5][1]=1
            self.buf0[7][5]=1
            self.buf0[8][4]=1
            self.buf0[8][3]=1
            self.buf0[9][5]=1
            self.buf0[9][4]=1
    def update(self):
        for row in range(ROWS):
            for col in range(COLS):
                ns = 0
                for drow in range(-1,2):
                    for dcol in range(-1,2):
                        if drow==0 and dcol==0:
                            continue
                        r = row + drow
                        c = col + dcol
                        if r>=ROWS: r -= ROWS
                        if c>=COLS: c -= COLS
                        if r<0: r+=ROWS
                        if c<0: c+=COLS
                        #if r>=0 and c>=0 and r<ROWS and c<COLS:
                        ns += self.buf0[r][c]
                if self.buf0[row][col] == 1:
                    self.buf1[row][col] = 1 if ns in [2,3] else 0
                else:
                    self.buf1[row][col] = 1 if ns == 3 else 0 
        self.buf0,self.buf1 = self.buf1,self.buf0

def demo(led):
        while 1:
            led.clear()
            for k in range(1024):
                led.rando()
                time.sleep(.01)
            led.clear()
            time.sleep(0.1)

            for k in range(3):
                life=Life()
                for i in range(50):
                    life.update()
                    led.reorder(life.buf0)
                    led.refresh()
                    time.sleep(.1)
            led.clear()
            time.sleep(0.1)

# led=LED()
# led.clear()
# led.clear()
# led.reorder(life.buf0)
# led.refresh()






# bitmap=[[1,1,1,1,0],
#         [1,0,0,0,1],
#         [1,0,0,0,1],
#         [1,1,1,1,0],
#         [1,0,0,0,1],
#         [1,0,0,0,1],   
#         [1,1,1,1,0]]    

# r=led.refresh

# led.draw(0,0,bitmap)
# #led.draw(4,0,bitmap)
# #l#d.draw(4,5,bitmap)
# led.draw(0,7,bitmap)
# led.refresh()



# import time
# led.clear()
# for c in range(14):
#    for r in range(0,10):
#       print(c,r)
#       led.plot(c,r)
#       led.refresh()
#       time.sleep(.01)
#       led.unplot(c,r)
#       led.refresh()
#       time.sleep(.01)

# #led.refresh()
