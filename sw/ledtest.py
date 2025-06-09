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
# import led
import time
import font
import random

l=led.LED()
#led.demo(l)

words = "Testing the test 1-2-3! You suck!"
print(words)
for letter in words: 
    stuff = font.getchar(letter)
    for ch in stuff:

        for row in range(8):    
            if ((1<<row) & ch )!= 0:
                l.plot(row, 19)  
        l.plot(random.randint(11,13), 9)
        l.refresh()
        l.lshift()
        time.sleep(.1)
    l.refresh()
    l.lshift()
    time.sleep(.1)
