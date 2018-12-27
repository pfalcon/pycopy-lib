import framebuf


fb = framebuf.FrameBuffer(None, 100, 100, framebuf.RGB888)
fb.fill(0x000000)
fb.line(0, 0, 99, 99, 0x00ff00)
fb.rect(10, 10, 80, 80, 0xff0000)
fb.fill_rect(25, 25, 50, 50, 0x0000ff)
fb.pixel(50, 50, 0xffffff)

fb.show()

input()
