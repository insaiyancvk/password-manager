import base64, sys, os, curses
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from ui_utils import pass_inp
from PIL import Image

def png_to_jpg(image):  

    with Image.open(image) as im:
        
        img_name, _ = os.path.splitext(os.path.basename(image))
        im.save(f'{img_name}.jpg',"JPEG")

    print(f'"{image}" saved as "{img_name}.jpg" !')
    return f'{img_name}.jpg'

def encrypt(key, source, encode=True): # Encrypt the str(dictionary) with a key and return utf-8 decoded string
    key = key.encode('utf-8') # encode the key to utf-8 (as bytes)
    source = source.encode('utf-8') # encode the string to utf-8 (as bytes)
    
    # STACKOVERFLOW STUFF
    key = SHA256.new(key).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True): # Decrypt the encrypted string data and return utf-8 decoded string
    key = key.encode('utf-8') # encode the key to utf-8 (as bytes)

    # STACKOVERFLOW STUFF
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding: # Check for the padding (idk what it is)
        print('Wrong key :(')
        return -1
    return data[:-padding].decode('utf-8') 

def write_enc_data(img_path, data, key):
    
    str_data = str(data) # Convert the dictionary to a string
    enc_data = encrypt(key, str_data) # encrypt str(dictionary)
    
    with open(img_path,'ab') as f: # open the file as append binary mode
        print('writing the encrypted data to image')
        f.write(enc_data.encode('utf-8')) # append the encrypted data

def read_enc_data(img_path, key):

    get_data = ''
    with open(img_path,'rb') as f: # open the file as read binary mode
        content = f.read()
        offset = content.index(bytes.fromhex('FFD9')) # get the index of FFD9
        f.seek(offset+2) # seek till the offset
        get_data = f.read().decode('utf-8') # read the data after the offset position and decode
        
    dec_data = eval(decrypt(key, get_data)) # decrypt the data and convert str(dictionary) to dictionary
    if dec_data == -1: # Check if the key is correct
        return -1
    return dec_data

def check_jpg(name):

    with open(name,'rb') as f: # open the file as read binary mode
        content = f.read()
    if bytes.fromhex('FFD9') in content: # Check if FFD9 exists in the file
        return True
    else:
        return False

def if_data(image):
    data = ''
    with open(image, 'rb') as f:
        content = f.read()
        offset = content.index(bytes.fromhex('FFD9'))
        f.seek(offset+2)
        data = f.read().decode('utf-8')
        
    if data == '':
        return False
    return True

def get_input():

    data_dict = {}
    
    print('\n\tJust hit enter when done with all the inputs\n\tAlso, don\'t worry about the password, it\'s hidden:)\n')
    print('Give your inputs ')

    while True:

        service = ''
        handle = ''
        passw = ''
        
        service = input('Enter name of the service (eg: Gmail, Facebook, instagram, etc): ')
        service = service.lower()
        if service=='':
            break
        
        handle = input(f'Enter the username/handle of your {service}: ')
        if handle=='':
            break
        
        # passw = getpass.getpass()
        outp = pass_inp(f'Enter the password of your {service}: ', 'passw')
        passw = outp['passw']
        if passw=='':
            break
        
        print()
        data_dict[service] = [handle, passw]
    
    return data_dict

def rem_data(img):

    with open(img,'rb') as f: # open the file as read binary mode
        content = f.read() 
        position = content.index(bytes.fromhex('FFD9'))+2 # Get the position of FFD9
        
    with open(img, 'r+') as f: # open the file as read update mode
        f.seek(position) # seek to FFD9 position
        f.truncate() # clear the data after FFD9

def clear_screen():
    if sys.platform=='win32' or os.name=='nt':
        os.system("cls")
    elif sys.platform=='linux' or os.name=='posix':
        os.system("clear")


KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = (curses.KEY_UP, ord('k'))
KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))

class Picker(object):
    """The :class:`Picker <Picker>` object
    :param options: a list of options to choose from
    :param title: (optional) a title above options list
    :param multiselect: (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
    :param indicator: (optional) custom the selection indicator
    :param default_index: (optional) set this if the default selected option is not the first one
    :param options_map_func: (optional) a mapping function to pass each option through before displaying
    """

    def __init__(self, options, title=None, indicator='*', default_index=0, multiselect=False, multi_select=False, min_selection_count=0, options_map_func=None):

        if len(options) == 0:
            raise ValueError('options should not be an empty list')

        self.options = options
        self.title = title
        self.indicator = indicator
        self.multiselect = multiselect or multi_select
        self.min_selection_count = min_selection_count
        self.options_map_func = options_map_func
        self.all_selected = []

        if default_index >= len(options):
            raise ValueError('default_index should be less than the length of options')

        if multiselect and min_selection_count > len(options):
            raise ValueError('min_selection_count is bigger than the available options, you will not be able to make any selection')

        if options_map_func is not None and not callable(options_map_func):
            raise ValueError('options_map_func must be a callable function')

        self.index = default_index
        self.custom_handlers = {}

    def register_custom_handler(self, key, func):
        self.custom_handlers[key] = func

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1

    def move_down(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0

    def mark_index(self):
        if self.multiselect:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)

    def get_selected(self):
        """return the current selected option as a tuple: (option, index)
           or as a list of tuples (in case multiselect==True)
        """
        if self.multiselect:
            return_tuples = []
            for selected in self.all_selected:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            return self.options[self.index], self.index

    def get_title_lines(self):
        if self.title:
            return self.title.split('\n') + ['']
        return []

    def get_option_lines(self):
        lines = []
        for index, option in enumerate(self.options):
            # pass the option through the options map of one was passed in
            if self.options_map_func:
                option = self.options_map_func(option)

            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * ' '

            if self.multiselect and index in self.all_selected:
                format = curses.color_pair(1)
                line = ('{0} {1}'.format(prefix, option), format)
            else:
                line = '{0} {1}'.format(prefix, option)
            lines.append(line)

        return lines

    def get_lines(self):
        title_lines = self.get_title_lines()
        option_lines = self.get_option_lines()
        lines = title_lines + option_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line

    def draw(self):
        """draw the curses ui on the screen, handle scroll if needed"""
        self.screen.clear()

        x, y = 1, 1  # start point
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y  # the max rows we can draw

        lines, current_line = self.get_lines()

        # calculate how many lines we should scroll, relative to the top
        scroll_top = getattr(self, 'scroll_top', 0)
        if current_line <= scroll_top:
            scroll_top = 0
        elif current_line - scroll_top > max_rows:
            scroll_top = current_line - max_rows
        self.scroll_top = scroll_top

        lines_to_draw = lines[scroll_top:scroll_top+max_rows]

        for line in lines_to_draw:
            if type(line) is tuple:
                self.screen.addnstr(y, x, line[0], max_x-2, line[1])
            else:
                self.screen.addnstr(y, x, line, max_x-2)
            y += 1

        self.screen.refresh()

    def run_loop(self):
        while True:
            self.draw()
            c = self.screen.getch()
            if c in KEYS_UP:
                self.move_up()
            elif c in KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                if self.multiselect and len(self.all_selected) < self.min_selection_count:
                    continue
                return self.get_selected()
            elif c in KEYS_SELECT and self.multiselect:
                self.mark_index()
            elif c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret

    def config_curses(self):
        try:
            # use the default colors of the terminal
            curses.use_default_colors()
            # hide the cursor
            curses.curs_set(0)
            # add some color for multi_select
            # @todo make colors configurable
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
        except:
            # Curses failed to initialize color support, eg. when TERM=vt100
            curses.initscr()

    def _start(self, screen):
        self.screen = screen
        self.config_curses()
        return self.run_loop()

    def start(self):
        return curses.wrapper(self._start)