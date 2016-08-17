from streetaddress.streetaddress import *

def clean_address (address_in):
    addr_parser = StreetAddressParser()

    addr = addr_parser.parse('1500 E. SECOND ST. #300, RENO, NV, 89502')
    print 'house: ' + str(addr['house']) #1600
    print 'street_full: ' + str(addr['street_full']) #Pennsylvania Ave
    print 'street_name: ' + str(addr['street_name']) #Pennsylvania
    print 'street_type: ' + str(addr['street_type']) #Ave
    print 'suite_type: ' + str(addr['suite_type']) #Apt


    addr_formatter = StreetAddressFormatter()
    street = '1500 E. 2nd Street'
    street = addr_formatter.append_TH_to_street(street) #West 23rd Street
    print 'append_TH_to_street: ' + str(street)

    street = addr_formatter.abbrev_direction(street) #W 23rd Street
    print 'abbrev_direction: ' + str(street)

    street = addr_formatter.abbrev_street_avenue_etc(street) #W 23rd St
    print 'abbrev_street_avenue_etc: ' + str(street)

    street = addr_formatter.st_nd_th_convert(street) #W 23rd St
    print 'st_nd_th_convert: ' + str(street)

    a = addr_formatter.st_nd_th_convert('1500 E 2 Street')
    print a


clean_address('1500 E. SECOND ST. #300, RENO, NV, 89502')