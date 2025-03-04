import cmd
from PIL import Image

class GraphicalProcessorManager(cmd.Cmd):
    intro = 'Welcome to the Graphical Processor Manager (GPM). Type help or ? to list commands.\n'
    prompt = '>>> '

    def do_convert(self, path):
        if not path:
            print("Please provide a path to the image.")
            return
        
        try:
            ascii_art = self.image_to_ascii(path)
            print(ascii_art)
        except Exception as e:
            print(f"Error: {e}")

    def image_to_ascii(self, image_path, width=100):
        img = Image.open(image_path)
        img = img.convert("L")
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        ascii_chars = "@#S%?*+;:,. "
        ascii_art = ""
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                ascii_art += ascii_chars[pixel // 25]
            ascii_art += "\n"
        return ascii_art

    def do_exit(self, arg):
        print("Exiting GPM.")
        return True

if __name__ == "__main__":
    GraphicalProcessorManager().cmdloop()

