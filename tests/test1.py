import time
from web2app import Web2Exe

start = time.time()
exe = Web2Exe(
  name="Google",
  url="https://www.google.com/",
  icon="assets/logo512.png",
)
print(f"Object instance created in {time.time() - start:.2f}s")

exe2 = Web2Exe("https://www.google.com/")

assert exe2.name == "Google"

start = time.time()
exe.create(output_dir="output")
print(f"EXE created in {time.time() - start:.2f}s")