import customtkinter as ctk
import calculations as clc

# GOOD LUCK (:
class Application():
    '''
    Hlavni gui
    '''
    def __init__(self, master):
        self.padding = {'pady': 5, 'padx': 5}
        
        self.widgets = {}
        
        # # # FRAMES # # #
        self.enc_in_frame = ctk.CTkFrame(master=master)
        self.enc_in_frame.grid(**self.padding, column=0, row=0,  sticky='nsew')

        self.dec_in_frame = ctk.CTkFrame(master=master)
        self.dec_in_frame.grid(**self.padding, column=0, row=1,  sticky='nsew')

        self.enc_out_frame = ctk.CTkFrame(master=master)
        self.enc_out_frame.grid(**self.padding, column=1, row=0, sticky='nsew')

        self.dec_out_frame = ctk.CTkFrame(master=master)
        self.dec_out_frame.grid(**self.padding, column=1, row=1, sticky='nsew')

        # # # ENCODER INPUT FRAME # # #
        self.enc_frame_title = ctk.CTkLabel(master=self.enc_in_frame, text="Encoder", font=ctk.CTkFont(size=20, weight='bold'))
        self.enc_frame_title.pack(**self.padding, anchor="n")

        self.mess_in_label = ctk.CTkLabel(master=self.enc_in_frame, text="Message")
        self.mess_in_label.pack(**self.padding, anchor="center")

        self.enc_mess_entry = ctk.CTkEntry(master=self.enc_in_frame, placeholder_text="Input binary message", width=300)
        self.enc_mess_entry.pack(**self.padding, anchor="center")

        self.nk_in_label = ctk.CTkLabel(master=self.enc_in_frame, text="Code (n,k)")
        self.nk_in_label.pack(**self.padding, anchor="center")

        self.nk_entry = ctk.CTkEntry(master=self.enc_in_frame, placeholder_text="Input (n,k) code as: n,k", width=300)
        self.nk_entry.pack(**self.padding, anchor="center")
        
        self.enc_button = ctk.CTkButton(master=self.enc_in_frame, text="ENCODE", font=ctk.CTkFont(weight="bold"), command=self.create_enc_out)
        self.enc_button.pack(**self.padding)

        # # # DECODER INPUT FRAME # # #
        self.dec_frame_title = ctk.CTkLabel(master=self.dec_in_frame, text="Decoder", font=ctk.CTkFont(size=20, weight='bold'))
        self.dec_frame_title.pack(**self.padding, anchor="n")

        self.mess_rec_label = ctk.CTkLabel(master=self.dec_in_frame, text="Message recieved")
        self.mess_rec_label.pack(**self.padding, anchor="center")

        self.dec_mess_entry = ctk.CTkEntry(master=self.dec_in_frame, placeholder_text="Input recieved binary message", width=300)
        self.dec_mess_entry.pack(**self.padding, anchor="center")

        self.poly_in_label = ctk.CTkLabel(master=self.dec_in_frame, text="Input generating polynomial")
        self.poly_in_label.pack(**self.padding, anchor="center")

        self.poly_entry = ctk.CTkEntry(master=self.dec_in_frame, placeholder_text="Input generating polynomial", width=300)
        self.poly_entry.pack(**self.padding, anchor="center")
        
        self.dec_button = ctk.CTkButton(master=self.dec_in_frame, text="DECODE", font=ctk.CTkFont(weight="bold"), command=self.create_dec_out)
        self.dec_button.pack(**self.padding)

        # # # ENCODER OUTPUT # # #
        self.enc_out_title = ctk.CTkLabel(master=self.enc_out_frame, text="Encoder Output", font=ctk.CTkFont(size=20, weight='bold'))
        self.enc_out_title.pack(**self.padding)

        # # # DECODER OUTPUT # # #
        self.dec_out_title = ctk.CTkLabel(master=self.dec_out_frame, text="Decoder Output", font=ctk.CTkFont(size=20, weight='bold'))
        self.dec_out_title.pack(**self.padding)
    
    def create_enc_out(self):
        '''
        Ziska data ze vstupu encoderu
        Zkontroluje na vyskyt moznych chyb
        Vytvori tabulku vystupu enkoderu
        '''
        mess = self.enc_mess_entry.get().strip()
        nk = self.nk_entry.get().strip()
        k = nk.split(',')
        k = k[1]
        
        # pokud jiz vystup encoderu existuje v slovniku widgetu, smaze se aby se nevytvoril duplikat
        if 'enc' in self.widgets:
            self.delete_enc_out()
        
        # kontrola vyjimek
        if len(mess) == 0 or len(nk) == 0:
            err = Error_popup('Not all encode parameters have been entered!')
            err.set_size(x=400)
            err.show()
            return
        elif nk[0] == '(' or nk[-1] == ')':
            err = Error_popup('Enter nk code without brackets and spaces!\nEnter code in format: n,k')
            err.set_size(x=400, y=50)
            err.show()
            return
        elif self.hamming_check(nk):
            err = Error_popup('Not a Hamming code!')
            err.show()
            return
        elif len(mess) != int(k):
            err = Error_popup('Given message is longer than given k')
            err.set_size(x=350)
            err.show()
            return

        # nalezeni polynomu a zakodovani dat polynomy
        data_in = clc.main_encode(mess, nk)
        
        # Vytvoreni vystupu enkoderu v gui
        enc_out_table = Encoder_output(master=self.enc_out_frame, daddy=self, data_in=data_in)
        self.widgets["enc"] = enc_out_table
        
    def delete_enc_out(self):
        '''
        Smaze vystup enkoderu
        '''
        self.widgets["enc"].destroy()
        self.widgets.pop("enc")
        
    def create_dec_out(self):
        '''
        vytvori vystup dekoderu a zkontroluje mozne chyby
        '''
        mess = self.dec_mess_entry.get().strip()
        poly = self.poly_entry.get().strip()
        
        # pokud jiz existuje vystup dekoderu, smaze ho aby se nevytvorily duplicity
        if 'dec' in self.widgets:
            self.delete_dec_out()
            
        # kontrola jestli jsou nejaka data ve vstupech dekoderu
        if len(mess) == 0 or len(poly) == 0:
            err = Error_popup('Not all decode parameters have been entered!')
            err.set_size(x=400)
            err.show()
            return 
        try:
            int(mess, 2)
        except:
            err = Error_popup('Wrong message input!\nInput message as a string of 1s and 0s\nExample: 1010011')
            err.set_size(x=400, y=75)
            err.show()
            return
        try:
            int(poly, 2)
        except:
            err = Error_popup('Wrong generating polynomial input!\nInput generating polynomial as a string of 1s and 0s\nExample: 1011')
            err.set_size(x=450, y=75)
            err.show()
            return
        
        # vytvoreni vystupu dekoderu
        data = [mess, poly]    
        dec_out_table = Decoder_output(master=self.dec_out_frame, data_in=data)
        self.widgets["dec"] = dec_out_table
        
    def delete_dec_out(self):
        '''
        Smaze vystup dekoderu
        '''
        self.widgets["dec"].destroy()
        self.widgets.pop("dec")
        
    def set_dec_data(self, mess, poly):
        '''
        Nastavi zadana data do vstupu dekoderu
        '''
        self.dec_mess_entry.delete(0,len(self.dec_mess_entry.get()))
        self.dec_mess_entry.insert(0, mess)
        self.poly_entry.delete(0,len(self.poly_entry.get()))
        self.poly_entry.insert(0, poly)
        
    def hamming_check(self, nk):
        '''
        zkontruje zda zadany kod je hamminguv kod
        pokud neni -> True
        '''
        code = nk.split(',')
        n = int(code[0])
        k = int(code[1])
        r = n - k
        
        n_test = (2**r) - 1
        k_test = (2**r) - 1 - r
        
        if n != n_test or k != k_test:
            return True
        
        return False
                
class Encoder_output():
    '''
    Vystup enkoderu
    '''
    def __init__(self, master, daddy, data_in):
        self.data = data_in
        # Class ktera vytvorila tuto class
        self.daddy = daddy
        
        self.radio_var = ctk.IntVar()
        
        self.main_frame = ctk.CTkFrame(master=master)
        self.main_frame.pack(pady=10, padx=10, fill='x', expand=True)
        
        self.main_frame.columnconfigure(index=0, weight=10)
        self.main_frame.columnconfigure(index=1, weight=10)
        self.main_frame.columnconfigure(index=2, weight=1)
        
        self.main_frame.rowconfigure(index=0, weight=1)
        
        self.gen_pol_title = ctk.CTkLabel(master=self.main_frame, text='Gen. polynomial', font=ctk.CTkFont(weight='bold'))
        self.gen_pol_title.grid(column=0, row=0, sticky="w")
        
        self.enc_mess_title = ctk.CTkLabel(master=self.main_frame, text='Encoded message', font=ctk.CTkFont(weight='bold'))
        self.enc_mess_title.grid(column=1, row=0, sticky="w")
        
        self.button_title = ctk.CTkLabel(master=self.main_frame, text='Use', font=ctk.CTkFont(weight='bold'))
        self.button_title.grid(column=2, row=0, sticky='w')
        
        self.create_lines()
        
        self.export = ctk.CTkButton(master=self.main_frame, text="Use in decoder", command=self.send_data_to_decoder)
        self.export.grid(column=0, row=len(self.data)+1, columnspan=3, sticky='nsew')
        
    
    def create_lines(self):
        '''
        Vytvori radek pro kazdou dvojici [zprava, polynom] a zapise do gui vystupu encoderu
        '''
        for i in range(len(self.data)):
            
            self.main_frame.rowconfigure(index=i+1, weight=1)
            
            temp_poly = ctk.CTkLabel(master=self.main_frame, text=f"{self.data[i][1]}")
            temp_poly.grid(column=0, row=i+1, sticky="w")
            
            temp_mess = ctk.CTkLabel(master=self.main_frame, text=f"{self.data[i][0]}")
            temp_mess.grid(column=1, row=i+1, sticky='w')

            
            temp_radio = ctk.CTkRadioButton(master=self.main_frame, text='', variable=self.radio_var, value=i)
            temp_radio.grid(column=2, row=i+1)

    def send_data_to_decoder(self):
        '''
        Zapise vybrana data do vstupu decoderu
        '''
        radio = self.radio_var.get()
        message = self.data[radio][0]
        poly = self.data[radio][1]
        
        self.daddy.set_dec_data(mess=message, poly=poly)
    
    def destroy(self):
        '''
        smaze hlavni ramecek
        '''
        self.main_frame.destroy()
        
class Decoder_output():
    '''
    Vystup dekderu
    '''
    def __init__(self, master, data_in):
        self.data = data_in
        
        self.title_padding = {"padx":5, "pady":0}
        self.text_padding = {"padx":20, "pady":0}
        
        self.main_frame = ctk.CTkFrame(master=master)
        self.main_frame.pack(pady=10, padx=10, fill='x', expand=True)
        
        # zkontroluje vstupni data jestli se ma do hlavniho ramecku vytvorit bezchybny vystup nebo vystup s chybou 
        self.input_check()
        
    def clear_offsprings(self):
        '''
        Vycisti vsechny potomky hlavniho ramecku (aka smaze vse uvnitr)
        '''
        for child in self.main_frame.winfo_children():
            child.destroy()
         
    def destroy(self):
        '''
        Smaze hlavni ramecek
        '''
        self.main_frame.destroy()
        
    def error_out(self, err_pos):
        '''
        Vystup s chybou
        '''
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='ERROR FOUND!' ,font=ctk.CTkFont(weight='bold', size=20))
        self.dec_mess_title.pack(**self.title_padding, anchor="center")
        
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='Recieved message:' ,font=ctk.CTkFont(weight='bold'))
        self.dec_mess_title.pack(**self.title_padding, anchor="w")
        
        self.dec_mess = ctk.CTkLabel(master=self.main_frame, text=f'{self.data[0]}')
        self.dec_mess.pack(**self.text_padding, anchor="w")
        
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='Recieved message as a polynomial:' ,font=ctk.CTkFont(weight='bold'))
        self.dec_mess_title.pack(**self.title_padding, anchor="w")
        
        self.dec_mess = ctk.CTkLabel(master=self.main_frame, text=f'{clc.format_message_to_x(self.data[0])}')
        self.dec_mess.pack(**self.text_padding, anchor="w")
        
        self.syndrome_title = ctk.CTkLabel(master=self.main_frame, text='Error detection:' ,font=ctk.CTkFont(weight='bold'))
        self.syndrome_title.pack(**self.title_padding, anchor="w")
        
        self.syndrome_text = ctk.CTkLabel(master=self.main_frame, text=f'Error detected on position x^{err_pos}!')
        self.syndrome_text.pack(**self.text_padding, anchor="w")
        
        self.repaired_mess_title = ctk.CTkLabel(master=self.main_frame, text='Repaired message:' ,font=ctk.CTkFont(weight='bold'))
        self.repaired_mess_title.pack(**self.title_padding, anchor="w")
        
        self.repaired_mess = ctk.CTkLabel(master=self.main_frame, text=f'{clc.repair_message(self.data[0], err_pos)}')
        self.repaired_mess.pack(**self.text_padding, anchor="w")
        
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='Repaired message as a polynomial:' ,font=ctk.CTkFont(weight='bold'))
        self.dec_mess_title.pack(**self.title_padding, anchor="w")
        
        self.dec_mess = ctk.CTkLabel(master=self.main_frame, text=f'{clc.format_message_to_x(clc.repair_message(self.data[0], err_pos))}')
        self.dec_mess.pack(**self.text_padding, anchor="w")
        
    def no_issues_out(self):
        '''
        Vystup bez chyby
        '''
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='Recieved message:' ,font=ctk.CTkFont(weight='bold'))
        self.dec_mess_title.pack(**self.title_padding, anchor="w")
        
        self.dec_mess = ctk.CTkLabel(master=self.main_frame, text=f'{self.data[0]}')
        self.dec_mess.pack(**self.text_padding, anchor="w")
        
        self.dec_mess_title = ctk.CTkLabel(master=self.main_frame, text='Recieved message as a polynomial:' ,font=ctk.CTkFont(weight='bold'))
        self.dec_mess_title.pack(**self.title_padding, anchor="w")
        
        self.dec_mess = ctk.CTkLabel(master=self.main_frame, text=f'{clc.format_message_to_x(self.data[0])}')
        self.dec_mess.pack(**self.text_padding, anchor="w")
        
        self.syndrome_title = ctk.CTkLabel(master=self.main_frame, text='Errors:' ,font=ctk.CTkFont(weight='bold'))
        self.syndrome_title.pack(**self.title_padding, anchor="w")
        
        self.syndrome_text = ctk.CTkLabel(master=self.main_frame, text='No errors')
        self.syndrome_text.pack(**self.text_padding, anchor="w")
    
    def input_check(self):
        '''
        Zkontroluje vstupni data a vytvori bezchybny vystup neboo vstup s chybou
        '''
        # zkontroluje vstupni data a pokud najde chyby vrati pozici chyby
        check = clc.crc_check(self.data[0], self.data[1])
        
        # smaze vse uvnitr hlavniho ramecku a vytvori bezchybny vystup
        if check == None:
            self.clear_offsprings()
            self.no_issues_out()
        # smaze vse uvnitr hlavniho ramecku a vytvori vystup s chybou
        else:
            self.clear_offsprings()
            self.error_out(check)

class Error_popup():
    '''
    Vyskakovaci okno s chybou
    '''
    def __init__(self, error_text):
        # text chyby
        self.error_text = error_text
        self.root = self.set_root()
        
        self.padding = {'padx': 5, 'pady': 5}
        
        self.err_label = ctk.CTkLabel(master=self.root, text=self.error_text, font=ctk.CTkFont(weight='bold', size=16))
        self.err_label.pack(**self.padding)
        
        # self.ok_button = ctk.CTkButton(master=self.root, text="OK", command=lambda: self.root.destroy())
        # self.ok_button.pack()
        
    def set_root(self):
        '''
        nastaveni korenu popup okna
        '''
        root = ctk.CTk()
        size = {'width': 200, 'height': 30}
        root.minsize(**size)
        root.maxsize(**size)
        root.resizable(0,0)
        
        root.columnconfigure(index=0, weight=1)
        root.columnconfigure(index=1, weight=5)
        root.rowconfigure(index=0, weight=1)
        root.rowconfigure(index=1, weight=1)
        
        return root
        
    def set_size(self, x=200, y=30):
        '''
        nastaveni velikosti pop-up okna
        '''
        size = {'width': x, 'height': y}
        self.root.minsize(**size)
        self.root.maxsize(**size)
        
    def show(self):
        '''
        zobrazeni pop-up okna
        '''
        self.root.mainloop()
        
def set_root():
    '''
    nastaveni korenu hlavniho GUI okna
    '''
    root = ctk.CTk()
    root.geometry("1200x625")
    root.minsize(width=300, height=625)
    
    root.columnconfigure(index=0, weight=1)
    root.columnconfigure(index=1, weight=5)
    root.rowconfigure(index=0, weight=1)
    root.rowconfigure(index=1, weight=1)
    
    return root

def main():
    '''
    Spusti program
    '''
    # nastaveni vzhledu gui
    ctk.set_appearance_mode("system")
    # nastaveni barevneho profilu
    ctk.set_default_color_theme("dark-blue")
    # nastaveni korenu
    root = set_root()
    # samotne gui
    Application(root)
    # spusteni gui
    root.mainloop()
      
# if __name__ == "__main__":
#     main()
    