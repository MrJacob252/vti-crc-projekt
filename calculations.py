# # result should be 1010011
# message_input = "1010"
# polynomial = "1011"

def xor_loop(remainder, len_remainder, len_poly, b_poly):
    '''
    XOR loop pro deleni generujicim polynomem
    '''
    # Dokud ma zbytek vetsi stupen nez gen pol
    while len_remainder >= len_poly:
        '''
        o kolik mist je potreba posunout gen pol aby spravne probehl xor
        default xor:
            1010000
               1011
        xor po posunuti:
            1010000
            1011000
        '''
        shift = len_remainder - len_poly
        # xor vypocet a posunuti gen polynomu
        remainder = (remainder ^ (b_poly << shift))
        # nova delka zbytku
        len_remainder = len(format(remainder, 'b'))
    
    return remainder

def crc_encode(message, poly):
    '''
    Zakodovani zpravy danym gen polynomem
    '''
    # zprava binarne
    b_message = int(message, 2)
    # polynom binarne
    b_poly = int(poly, 2)
    # delka polynomu
    len_poly = len(poly)
    
    # rozsireni zpravy o stupen polynomu
    b_message = (b_message << len_poly - 1)
    # inicializace zbytku
    remainder = b_message
    # delka zbytku
    len_remainder = len(format(remainder, 'b'))
    # vypocet zbytku
    remainder = xor_loop(remainder, len_remainder, len_poly, b_poly)
    # zapsani zbytku do zpravy
    # 1010000 zprava
    # 0000011 zbytek
    # 1010011 zabezpecena zprava
    encoded_message = b_message ^ remainder
    #formatovani zakodovane zpravy zpet do stringu '1010011'
    return format(encoded_message, 'b')

def crc_check(message, poly):
    '''
    Kontrola prijate zpravy zadanym polynomem
    Vraci None v pripada bezchybneho prenosu
    V pripade chyby vrati pozici chyby jako int
    '''
    # # stejne jako v crc encode
    b_message = int(message, 2)
    b_poly = int(poly, 2)
    len_poly = len(poly)
    
    remainder = b_message
    len_remainder = len(format(remainder, 'b'))
    
    remainder = xor_loop(remainder, len_remainder, len_poly, b_poly)
    # # konec stejneho
    # znytek jako string
    str_remainder = format(remainder, 'b')
    # seznam kombinaci jak vypada zbytek pokud je chyba v zabezpecovaci casti
    # aka: 1 = pozice x0, 10 = pozice x1, 100 pozice x2, atd...
    list_of_remainders = []
    # tvorba zbytku 
    for i in range(len(poly) - 1):
        temp = '1' + '0' * i
        list_of_remainders.append(temp)
    # # kontrola zbytku
    # bezchybny prenos
    if str_remainder == '0':
        return None
    # chyba v zabezpecovaci casti
    elif str_remainder in list_of_remainders:
        # vrati index listu podle daneho elementu (pokud je v listu)
        return list_of_remainders.index(str_remainder)
    # chyba v informacni casti
    else:
        # hledani zbytku v informacni casti
        position = error_search(message, b_poly, len_poly, remainder)
        return position
    
def error_search(message, bin_poly, len_poly, bin_remainder):
    '''
    Prohleda informacni cast crc zpravy a vrati pozici chyby jako int
    '''
    # vypocet n,k parametru kodu
    n = len(message)
    k = n - len_poly + 1
    # pro informacni cast
    for i in range(n - k, n):
        # momentalni pozice x na ktere se nachazime 
        x_position = i
        
        # testovaci polynom pro danou pozici
        # napr: x5 = 100000
        test = '1' + ('0' * i)
        # delka testovaciho polynomu
        len_test = len(test)
        # testovaci polynom binarne
        test = int(test, 2)
        # xor vypocet zbytku testovaciho polynomu
        test = xor_loop(test, len_test, len_poly, bin_poly)
        # pokud je vypozitany zbytek z test polynomu stejny jako zbytek z prijate zpravy nasli jsme chybu
        # pokud ne loop pokracuje
        if bin_remainder == test:
            # navrat pozice
            return x_position
    
def poly_search(code):
    '''
    Hledani polynomu ktere dokazi delit x^n + 1 bez zbytku
    Vrati list polynomu
    '''
    # Rozdeli zadany kod  na n a k
    code = code.split(',')
    n = int(code[0])
    k = int(code[1])
    
    # nejvetsi mozny generujici polynom
    # napr 1111
    maximum = '1' * (n-k+1)
    maximum = int(maximum, 2)
    # nejmensi mozny generujici polynom
    # napr 1000
    minimum = '1' + ('0' * (n - k))
    minimum = int(minimum, 2)
    # deleny polynom x^n + 1
    search_poly = '1' + '0' * (n - 1) + '1'
    search_poly = int(search_poly, 2)
    # seznam nalezenych polynomy
    found = []
    # projde vsechny polynomy od napr 1000 do 1111
    for i in range(minimum, maximum + 1):
        
        remainder = search_poly
        len_remainder = len(format(remainder, 'b'))
        # delka testovaneho 'generujiciho' polynomu
        len_i = len(format(i, 'b'))
        # vypocet zbytku
        remainder = xor_loop(remainder, len_remainder, len_i, i)
        # pokud je zbytek 0, pridame polynom do seznamu jako string
        if remainder == 0:
            found.append(format(i, 'b'))
    # navrat seznamu nalezenych polynomu
    return found

def format_message_to_x(message):
    '''
    formatuje danou zpravy ve formatu '10101'
    do formatu x^4 + x^2 + x^0
    '''
    # finalni vystup
    output = ''
    # seznam pozic na kterych se nachaizi '1'
    positions = []
    # projde zadanou zpravu a najde vsechny pozice kde je '1' a zapise do listu
    for i in range(len(message)):
        if message[i] == "1":
            # musime odecist i - 1 od delky zpravy protoze prochazime zpravu z leva, ale
            # polynom zacina s 0 v pravo
            # [0,1,2,3,4] mame
            # [4,3,2,1,0] chceme
            positions.append(len(message) - i - 1)
    
    # zapis vystupu
    for i in range(len(positions)):    
        #prvni zkontrolujeme jestli jsme na konci seznamu pozic a jestli je dana pozice 0, pokud ano piseme pouze 1
        if positions[i] == 0:
            output += '1'
        # pokud jsme na konci seznamu pozic a dana pozice neni 0, piseme pouze 'x^n'
        elif i == len(positions) - 1:
            output += f'x^{positions[i]}'
        # v ostatnich pripadech piseme 'x^n +' 
        else:
            output += f'x^{positions[i]} + '
    # vratime formatovany vystup
    return output
          
def repair_message(str_message, position):
    '''
    Prehodi bit zpravy na zadane pozici
    '''
    # pozice ve formatu -x, protoze chceme jit z druhe strany listu
    position = -position - 1
    # rozdeli string zpravy na list
    rep_mess = [*str_message]
    # prevede bit na dane pozici na int
    # provede (x + 1) % 2 diky cemu se prehodi 1 na 0 nebo 0 na 1
    # prevede pozici opet na str
    rep_mess[position] = str((int(rep_mess[position]) + 1) % 2)
    # spoji list zpet na string a vrati
    return ''.join(rep_mess)

def main_encode(message, code):
    '''
    provede nalezeni generucich polynomu a zakodovani zpravy pro kazdy polynom
    vrati polynomy a zakodovane zpravy ve formatu:
    [[zprava, polynom], [zprava, polynom]]
    '''
    # najde vsechny gen polynomy pro kod
    polys = poly_search(code)
    # vystupni list
    output = []
    # pro kazdy nalezeny polynom zakoduje zpravy a zapise do vystupniho listu jako [zprava, polynom]
    for i in polys:
        encoded = crc_encode(message, i)
        output.append([encoded, i])
        
    return output

# if __name__ == "__main__":
#     mess = '1010'
#     poly = '1011'
#     code = '7,4'
    
#     print('ENCODE --- ---')
#     print(crc_encode(mess, poly))
    
#     print('CRC CHECK --- ---')
#     print(crc_check('1110011', poly))
#     print(crc_check('1010010', poly))
    
#     print('POLY SEARCH --- ---')
#     print(poly_search(code))
    