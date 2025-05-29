from web2app import Web2Exe


exe = Web2Exe(
  name="Google",
  url="https://www.google.com/",
  icon="assets/logo512.png",
)

exe2 = Web2Exe("https://www.google.com/")

assert exe2.name == "Google"

# exe.create(output_dir="output")
# print("EXE Created successfully.")