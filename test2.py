from multiprocessing import Manager

queue = Manager().Queue()

queue.put("sending prompt")

print("sending prompt" == queue)