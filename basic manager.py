import getpass
from utils import check_jpg, get_input, if_data, write_enc_data, read_enc_data, Picker
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel

def access_data(image):
    data_dict = {}
    c = Console()
    key = getpass.getpass('Enter your key: ') # read the password with echo off
    print('Reading the data from image')
    # try:
    data_dict = read_enc_data(image, key) # read the data from image with the key
    # except:
    #     pass

    if data_dict == -1: # Exit if the padding doesn't match
        print('Wrong key :(')
        return
    else:
        print('\nData decrypted successfully.')

        options = ['Check the existing data','Update data','Delete data']
        picker = Picker(options, "Select your choice using the arrow keys or press q to quit", indicator= " => ")
        picker.register_custom_handler(ord('q'), lambda picker: exit())
        picker.register_custom_handler(ord('Q'), lambda picker: exit())
        _, op = picker.start()

        if op == 0:
            table = Table(header_style='bold cyan')
            table.add_column('Service')
            table.add_column('Handle')
            table.add_column('Password')
            for key, value in data_dict.items():
                print(key, value)
                table.add_row(key, value[0], value[1])
            c.print(table)
            return
        
        elif op == 1:
            pass

        elif op == 2:
            pass

if __name__ == '__main__':

    image = input('Enter the image path: ')
    data_dict = {}

    if check_jpg(image): # check if the input image has FFD9 in it

        if if_data(image):
            access_data(image)

        else: 

            key = input('Create a key (NEVER FORGET IT): ')
            ch1 = input('Would you like to add your data? (y/n): ')

            if ch1.lower() == 'y':

                data_dict = get_input() # get the service, handle, password dictionary
                write_enc_data(image, data_dict, key) # pass the dictionary, key to the function
                print(f"The encrypted data is written to {image} :)")
            
            else:
                print("\nSee you later!")

    elif not check_jpg(image):
        print("The image not in JPG format :(")
    

    #TODO: Complete dictionary part and fill some sample encrypted data and test the decryption ✅
    #TODO: Take a "proper" dictionary input. ✅
    #TODO: Take dictionary inputs and write/read to/from image ✅
    #TODO: Implement Create, Read, Update, Delete feature