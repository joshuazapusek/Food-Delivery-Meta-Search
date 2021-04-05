# Version 1.0 of dodo
# Author: Joshua Zapusek
# Date Modified: 1/27/2021

import os.path
import time
import re
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from threading import Thread, Lock, current_thread

# Linked List for results list
class Node:
    def __init__(self, service, time, price):
        self.service = service
        self.time = time
        self.price = price
        self.next = None
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

# NOTE: Absolute hell uber puts me through here -> had to grab all spans and ps then filter
#####################################################################################################
def uberAuto(addr, roots, item, final):
    feeStr = 'Delivery Fee is'
    badWords = ['Picked for you (default)', 'Most popular', 'Rating', '-', 'Delivery time', 'Facebook', 'Twitter', 'Instagram', '']
    print("Uber Eats Automation")
    browser = webdriver.Chrome()
    browser.get(roots['ubereats'][0])
    time.sleep(3)
    # Fill relevant elements and click search
    input_elem = browser.find_element_by_css_selector(roots['ubereats'][1])
    input_elem.send_keys('{}'.format(addr))
    time.sleep(4)
    input_elem.send_keys(Keys.RETURN)
    #button_elem = browser.find_element_by_css_selector(roots['ubereats'][2])
    #button_elem.click()

    # Get key word to search
    if (item == None):
        word = input("Enter any Key Word :) \n")
    else:
        word = item
        time.sleep(3)
    input_elem = browser.find_element_by_css_selector('input[id="search-suggestions-typeahead-input"]')
    input_elem.send_keys('{}'.format(word))
    input_elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search for matching restaurant services
    #eatNow = float(input("Enter maximum time for delivery...\n"))
    eatNow = 60
    # Get names for servers
    time.sleep(2)
    #nameTags = browser.find_elements_by_xpath('.//p[@class = "cd ce cf i2 al aj i3 bo"]')
    #nameTags = browser.find_element_by_css_selector('p.cd ce cf i2 al aj i3 bo')
    #/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[1]/div/a/div/div[1]/p
    timeTags = browser.find_elements_by_tag_name('span')
    timeList = [e.text for e in timeTags]
    info = clean(timeList, badWords)
    # First elem is weird dont even know what char it is 
    info.pop(0)
    nameTags = browser.find_elements_by_tag_name('p')
    names = [e.text for e in nameTags]
    # Split delivery fees and times
    fees = []
    times = []
    for i in range(len(info)):
        if (feeStr in info[i]):
            fees.append(info[i])
        else:
            times.append(info[i])
    avs = []
    for e in times:
        newTime = re.sub("[^0-9]", " ", e)
        temp = newTime.split(" ")
        average = ((int(temp[0]) + int(temp[1])) / 2)
        avs.append(average)
    # Cut off closed places from names list
    del names[len(times):]
    resultWaits = sorted(zip(avs, times, names, fees))
    res = list(zip(*resultWaits))
    timeAvs = list(res[0])
    timeStrs = list(res[1])
    names = list(res[2])
    fees = list(res[3])

    # Display our findings
    found = 0
    for i in range(len(timeAvs)):
        if (timeAvs[i] <= eatNow):
            roots['ubereats'][3].append("Uber Eats: {} with expected time {} minutes and {}".format(names[i], timeStrs[i], fees[i]))
            found = 1
            print("Uber Eats: {} with expected time {} minutes and {}".format(names[i], timeStrs[i], fees[i]))
    if (found == 0):
        print("No restaurants in {} meeting required time".format(addr))

    # Call to organize
    data = []
    data.append(timeStrs)
    data.append(names)
    data.append(fees)

    organize(data, 'Uber Eats', final)

    # Check if we want to do another search
    if (input("Would you like to run another search? y/n ") == 'n'):
        browser.close()
        return 0
    else:
        browser.close()
        return 1

#####################################################################################################
def seamAuto(addr, roots, item, final):
    badWords = ['Feature', 'Rating', 'Delivery time', '']
    print("SEAMLESS Automation")
    browser = webdriver.Chrome()
    browser.get(roots['seamless'][0])
    time.sleep(3)
    # Fill relevant elements and click search
    input_elem = browser.find_element_by_css_selector(roots['seamless'][1])
    input_elem.send_keys('{}'.format(addr))
    time.sleep(3)
    button_elem = browser.find_element_by_css_selector(roots['seamless'][2])
    button_elem.click()

    # Get key word to search
    if (item == None):
        word = input("Enter any Key Word :) \n")
    else:
        word = item
        time.sleep(3)
    input_elem = browser.find_element_by_css_selector('input[id="search-autocomplete-input"]')
    input_elem.send_keys('{}'.format(word))
    input_elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search for matching restaurant services
    #eatNow = float(input("Enter maximum time for delivery...\n"))
    eatNow = 60
    # Get names for servers
    nameTags = browser.find_elements_by_tag_name('h5')
    nameList = [e.text for e in nameTags]
    names = clean(nameList, badWords)
    # Get expected times
    timeTags = browser.find_elements_by_css_selector('span.value.h5.u-block')
    times = [e.text for e in timeTags]
    avs = []
    for e in times:
        newTime = re.sub("[^0-9]", " ", e)
        temp = newTime.split(" ")
        average = ((int(temp[0]) + int(temp[1])) / 2)
        avs.append(average)
    resultWaits = sorted(zip(avs, times, names))
    res = list(zip(*resultWaits))
    timeAvs = list(res[0])
    timeStrs = list(res[1])
    names = list(res[2])

    # Display our findings
    found = 0
    for i in range(len(timeAvs)):
        if (timeAvs[i] <= eatNow):
            roots['seamless'][3].append("Seamless: {} with expected time {} minutes".format(names[i], timeStrs[i]))
            found = 1
            print("Seamless: {} with expected time {} minutes".format(names[i], timeStrs[i]))
    if (found == 0):
        print("No restaurants in {} meeting required time".format(addr))

    # Call to organize
    data = []
    data.append(timeStrs)
    data.append(names)
    fees = [0] * len(names)
    data.append(fees)

    organize(data, 'Seamless', final)

    # Check if we want to do another search
    if (input("Would you like to run another search? y/n ") == 'n'):
        browser.close()
        return 0
    else:
        browser.close()
        return 1

#####################################################################################################
def hubAuto(addr, roots, item, final):
    badWords = ['Feature', 'Rating', 'Delivery time', '']
    print("GRUBHUB Automation")
    chrome_options = Options()
    chrome_options.add_experimental_option( "prefs", {'protocol_handler.excluded_schemes.tel': False})
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(roots['grubhub'][0])
    time.sleep(3)
    # Fill relevant elements and click search
    input_elem = browser.find_element_by_css_selector(roots['grubhub'][1])
    input_elem.send_keys('{}'.format(addr))
    time.sleep(2)
    #button_elem = browser.find_element_by_css_selector(roots['grubhub'][2])
    #button_elem.click()
    input_elem.send_keys(Keys.RETURN)
    # LESSON LEARNED: NEED TO SLEEP UNLESS DRIVER WILL NOT UPDATE IN TIME FOR NEXT SPIDER CRAWL - LOTS OF TIME WASTED HERE

    # Get key word to search
    if (item == None):
        word = input("Enter any Key Word :) \n")
    else:
        word = item
        time.sleep(3)
    
    input_elem = browser.find_element_by_css_selector('input[id="search-autocomplete-input"]')
    input_elem.send_keys('{}'.format(word))
    input_elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search for matching restaurant services
    #eatNow = float(input("Enter maximum time for delivery...\n"))
    eatNow = 60
    # Get names for servers
    nameTags = browser.find_elements_by_tag_name('h5')
    nameList = [e.text for e in nameTags]
    names = clean(nameList, badWords)
    # Get expected times
    timeTags = browser.find_elements_by_css_selector('span.value.h5.u-block')
    times = [e.text for e in timeTags]
    avs = []
    for e in times:
        newTime = re.sub("[^0-9]", " ", e)
        temp = newTime.split(" ")
        average = ((int(temp[0]) + int(temp[1])) / 2)
        avs.append(average)
    resultWaits = sorted(zip(avs, times, names))
    res = list(zip(*resultWaits))
    timeAvs = list(res[0])
    timeStrs = list(res[1])
    names = list(res[2])

    # Display our findings
    found = 0
    for i in range(len(timeAvs)):
        if (timeAvs[i] <= eatNow):
            roots['grubhub'][3].append("Grubhub: {} with expected time {} minutes".format(names[i], timeStrs[i]))
            found = 1
            print("Grubhub: {} with expected time {} minutes".format(names[i], timeStrs[i]))
    if (found == 0):
        print("No restaurants in {} meeting required time".format(addr))

    # Call to organize
    data = []
    data.append(timeStrs)
    data.append(names)
    fees = [0] * len(names)
    data.append(fees)

    organize(data, 'Grubhub', final)

    # Check if we want to do another search
    if (input("Would you like to run another search? y/n ") == 'n'):
        browser.close()
        return 0
    else:
        browser.close()
        return 1

#####################################################################################################
def dashAuto(addr, roots, item, final):
    badWords = ['Closed']
    print("Door Dash Automation")
    browser = webdriver.Chrome()
    browser.get(roots['doordash'][0])
    time.sleep(5)
    # Fill relevant elements and click search
    input_elem = browser.find_element_by_css_selector(roots['doordash'][1])
    input_elem.send_keys('{}'.format(addr))
    time.sleep(5)
    button_elem = browser.find_element_by_css_selector(roots['doordash'][2])
    button_elem.send_keys(Keys.RETURN)
    # input_elem.send_keys(Keys.RETURN)
    # LESSON LEARNED: NEED TO SLEEP UNLESS DRIVER WILL NOT UPDATE IN TIME FOR NEXT SPIDER CRAWL - LOTS OF TIME WASTED HERE
    time.sleep(2)

    # Get key word to search
    if (item == None):
        word = input("Enter any Key Word :) \n")
    else:
        word = item
    input_elem = browser.find_element_by_css_selector('input[placeholder="Search"]')
    input_elem.send_keys('{}'.format(word))
    input_elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search for matching restaurant services
    #eatNow = float(input("Enter maximum time for delivery...\n"))
    eatNow = 60
    # Get names for servers
    nameTags = browser.find_elements_by_xpath('.//span[@class = "sc-bdVaJa bTYYIJ"]')
    nameList = [e.text for e in nameTags]
    print(nameList)
    names = clean(nameList, badWords)
    # Get expected times
    timeTags = browser.find_elements_by_xpath('.//span[@class = "sc-hdNmWC VlRbT sc-bdVaJa fjQPGh"]')
    times = [e.text for e in timeTags]
    times = clean(times, badWords)
    if (len(times) == 0):
        print("No available services")
        browser.close()
        return 0
    timeStrs = []
    for e in times:
        newTime = re.sub("[^0-9]", " ", e)
        temp = newTime.split(" ")
        timeStrs.append(temp[0])
    timeNums = [int(i) for i in timeStrs]
    resultWaits = sorted(zip(timeNums, timeStrs, names))
    res = list(zip(*resultWaits))
    timeNums = list(res[0])
    timeStrs = list(res[1])
    names = list(res[2])
    # Display our findings
    found = 0
    for i in range(len(timeNums)):
        if (timeNums[i] <= eatNow):
            roots['doordash'][3].append("Door Dash: {} with expected time {} minutes".format(names[i], timeStrs[i]))
            found = 1
            print("Door Dash: {} with expected time {} minutes".format(names[i], timeStrs[i]))
    if (found == 0):
        print("No restaurants in {} meeting required time".format(addr))

     # Call to organize
    data = []
    data.append(timeStrs)
    data.append(names)
    fees = [0] * len(names)
    data.append(fees)

    organize(data, 'Door Dash', final)

    # Check if we want to do another search
    if (input("Would you like to run another search? y/n ") == 'n'):
        browser.close()
        return 0
    else:
        browser.close()
        return 1

#####################################################################################################
def cavAuto(addr, roots, item, final):
    badWords = ['Closed']
    print("Try Caviar Automation")
    browser = webdriver.Chrome()
    browser.get(roots['caviar'][0])
    time.sleep(8)
    # Fill relevant elements and click search
    input_elem = browser.find_element_by_css_selector(roots['caviar'][1])
    input_elem.send_keys('{}'.format(addr))
    time.sleep(4)
    button_elem = browser.find_element_by_css_selector(roots['caviar'][2])
    button_elem.send_keys(Keys.RETURN)
    # input_elem.send_keys(Keys.RETURN)
    # LESSON LEARNED: NEED TO SLEEP UNLESS DRIVER WILL NOT UPDATE IN TIME FOR NEXT SPIDER CRAWL - LOTS OF TIME WASTED HERE
    time.sleep(2)

    # Get key word to search
    if (item == None):
        word = input("Enter any Key Word :) \n")
    else:
        word = item
        time.sleep(3)
    input_elem = browser.find_element_by_css_selector('input[placeholder="Search"]')
    input_elem.send_keys('{}'.format(word))
    input_elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search for matching restaurant services
    #eatNow = float(input("Enter maximum time for delivery...\n"))
    eatNow = 60
    # Get names for servers
    nameTags = browser.find_elements_by_xpath('.//span[@class="sc-bdVaJa cCeeKZ"]')
    nameList = [e.text for e in nameTags]
    names = clean(nameList, badWords)
    # Get expected times
    timeTags = browser.find_elements_by_xpath('.//span[@class="sc-hdNmWC VlRbT sc-bdVaJa ipgJLW"]')
    times = [e.text for e in timeTags]
    times = clean(times, badWords)
    if (len(times) == 0):
        print("No available services")
        browser.close()
        return 0
    timeStrs = []
    for e in times:
        newTime = re.sub("[^0-9]", " ", e)
        temp = newTime.split(" ")
        timeStrs.append(temp[0])
    timeNums = [int(i) for i in timeStrs]
    resultWaits = sorted(zip(timeNums, timeStrs, names))
    res = list(zip(*resultWaits))
    timeNums = list(res[0])
    timeStrs = list(res[1])
    names = list(res[2])
    # Display our findings
    found = 0
    for i in range(len(timeNums)):
        if (timeNums[i] <= eatNow):
            roots['caviar'][3].append("Caviar: {} with expected time {} minutes".format(names[i], timeStrs[i]))
            found = 1
            print("Caviar: {} with expected time {} minutes".format(names[i], timeStrs[i]))
    if (found == 0):
        print("No restaurants in {} meeting required time".format(addr))

    # Call to organize
    data = []
    data.append(timeStrs)
    data.append(names)
    fees = [0] * len(names)
    data.append(fees)

    organize(data, 'Caviar', final)

    # Check if we want to do another search
    if (input("Would you like to run another search? y/n ") == 'n'):
        browser.close()
        return 0
    else:
        browser.close()
        return 1

#####################################################################################################
def clean(arr, words):
    arr1 = []
    for elem in arr:
        if (elem not in words):
            arr1.append(elem)
    return arr1 

# Eventually this can be made into a hash table for large numbers of restaurants. Right now the space complexity doesnt make sense to do
#####################################################################################################
def organize(findings, service, res):
    # function to create a list of linked lists for each restaurant. The linked list consists of nodes with 
        # fields of service, time, price 
    print(findings)
    print(service)
    print(type(res))
    # findings is a zipped list containing up to three elems: time, name, price
    for i in range(len(findings)):
        key = findings[i][1]
        if (key not in res):
            serveList = LinkedList()
            res[key] = serveList
            serveList.head = Node(service, findings[0], findings[2])
            serveList.tail = serveList.head
        else:
            serveList = res[key]
            newNode = Node(service, findings[0], findings[2])
            serveList.tail.next = newNode
            serveList.tail = newNode

#####################################################################################################
def threadDatBitch(addr, roots, item):
    # Need to have all user inputs before threading
    thread_grub = Thread(target=hubAuto, args=(addr, roots, item))
    thread_seam = Thread(target=seamAuto, args=(addr, roots, item))
    thread_uber = Thread(target=uberAuto, args=(addr, roots, item))
    thread_dash = Thread(target=dashAuto, args=(addr, roots, item))
    thread_cav = Thread(target=cavAuto, args=(addr, roots, item))

    thread_grub.daemon = True 
    thread_seam.daemon = True
    thread_uber.daemon = True
    thread_dash.daemon = True
    thread_cav.daemon = True

    thread_grub.start()
    thread_seam.start()
    thread_uber.start()
    thread_dash.start()
    thread_cav.start()

    thread_grub.join()
    thread_seam.join()
    thread_uber.join()
    thread_dash.join()
    thread_cav.join()

#####################################################################################################
def control():
    start = time.time()
    roots = {
        'grubhub': ['https://www.grubhub.com/', 'input[placeholder="Enter street address or zip code"]', 'button[class="s-btn s-btn-primary s-btn--block addressInput-submitBtn s-btn--large"]', []], 
        'ubereats': ['https://www.ubereats.com/', 'input[placeholder="Enter delivery address"]', 'button[class="cj cx bp ei ej cd ce cf bp cg db ag bd ci ba cj ck cl cm cn co cp"]', []], 
        'doordash': ['https://www.doordash.com/en-US', 'input[placeholder="Enter delivery address"]', 'button[kind="BUTTON/PLAIN"]', []],
        'seamless': ['https://www.seamless.com/', 'input[placeholder="Enter street address or zip code"]', 'button[class="s-btn s-btn-primary s-btn--block addressInput-submitBtn s-btn--large"]', []],
        'postmates': ['https://postmates.com/', 'input[placeholder="Enter your address..."]', 'css-um3ari eol9noh5', []],
        'caviar': ['https://www.trycaviar.com/en-US', 'input[placeholder="Enter delivery address"]', 'button[kind="BUTTON/PLAIN"]', []]
        }
    # map storing restaurant as key and linked list of services as values
    res = dict()

    addr = None
    contHub = 1
    contDash = 1
    contEats = 1
    contPosty = 1
    contSeam = 1
    contCav = 1

    print("Welcome to dodo!!!")

    if (input("To mutithread, enter Y...") != 'Y'):
        while (1):
            addr = input("Enter your Address: ")
            correct = input("Please confirm your address: {}, y/n ".format(addr))
            if (correct == 'y'):
                print("Searching your location...")
                break
        item = input("Enter your desired item ")
        dashAuto(addr, roots, item, res)
        '''
        while (1):
            if (contEats != 0):
                contEats = uberAuto(addr, roots, item, res)
            if (contHub != 0):
                contHub = hubAuto(addr, roots, item, res)
            if (contDash != 0):
                contDash = dashAuto(addr, roots, item, res)
            if (contSeam != 0):
                contSeam = seamAuto(addr, roots, item, res)
            if (contCav != 0):
                contCav = cavAuto(addr, roots, item, res)
            if (contDash == 0 and contHub == 0 and contSeam == 0 and contCav == 0 and contEats == 0):
                break
        '''

        print("Thank you!")
    else:
        addr = input("Enter your Address: ")
        item = input("Enter what you would like ")
        threadDatBitch(addr, roots, item)

    # write to file
    
    for key in res:
        nodes = res[key]
        if (nodes.head == nodes.tail):
            print('{}\t {}\t {}\t {}'.format(key, nodes.head.service, nodes.head.time, nodes.head.price if nodes.head.price != 0 else ''))
        else :
            current = nodes.head
            print('{}\t '.format(current.service), end = " ")
            while (current.next != None):
                if (current == nodes.tail):
                     print('{}\t {}\t {}'.format(current.service, current.time, current.price if current.price != 0 else ''))
                else:
                    print('{}\t {}\t {}'.format(current.service, current.time, current.price if current.price != 0 else ''), end = " ")
                current = current.next
    print("--- %s seconds ---" % (time.time() - start))

if __name__ == "__main__":
    control()