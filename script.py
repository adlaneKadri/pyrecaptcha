from selenium import webdriver
from matplotlib import pyplot as plt
from urllib.request import Request, urlopen
import time
import shutil
import imagga_api
import sys
import urllib.request
import os
import numpy as np
import inflect


def loop(dafare = [], linkdownload = [], *args):
    
    #dafare = blocks that need to be checked - linkdownload = already downloaded links
    print(dafare)
    print(linkdownload)

    if not dafare:
        sys.exit("non riuscito") #exit if todo is empty 
    
    if "firsttime" in dafare: #if first time, download big image and cut it

        #remove old files
        for f in os.listdir('temp'):
            os.remove(os.path.join("temp", f)) 

        #get all images and download first (they are all the same)
        images = driver.find_elements_by_tag_name('img')
        urllib.request.urlretrieve(images[0].get_attribute('src'), "temp/temptetemp.jpg")

        #understand the grid
        tablerows = len(driver.find_elements_by_xpath("//*[@id=\"rc-imageselect-target\"]/table/tbody/tr"))
        tablecol = len(driver.find_elements_by_xpath("//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[1]/td"))
        print (str(tablecol) + "x" + str((tablerows)))

        #cut img using ImageMagick 
        os.system("convert temp/temptetemp.jpg -crop " + str(100/tablecol) + "%x" + str(100/tablerows) + "% +repage temp/image_%d.jpg")
    else:
        newitems = driver.find_elements_by_class_name('rc-image-tile-11') #rc-image-tile-11 = a single image tile/block

        print("new :")
        print(newitems)

        i = 0
        for item in newitems:
            img_src = item.get_attribute("src") #get src image attribute

            if img_src not in linkdownload: #if image not already downloaded, download it
                urllib.request.urlretrieve(img_src, "temp/image_" + dafare[i] + ".jpg") #download image and rename it properly
                i += 1
                linkdownload.append(img_src) #append download link to download links list

    okimg = [] #images to be clicked

    #get all cutted files
    for filename in os.listdir('temp'):

        if "image_" in filename: 
            print(filename)
            number = filename.replace("image_", "").replace(".jpg", "").replace(" ", "") #get tile number
            if number in dafare or "firsttime" in dafare:
                
                
                imagga_wrapper = imagga_api.ImaggaApi(api_key, api_secret)      #imagga api wrapper from https://github.com/meltwater/py-image-api-wrappers
                dictval = imagga_wrapper.get_tag_scores_and_time("temp/" + filename) #analyze from file

                for itm in dictval['tag_list']:
                    if itm[1] > 90:
                        print(itm[0])   #print most relevant tags
                    if itm[0] == testo: #check if tag == target 
                        if str(number) not in okimg: 
                            okimg.append(str(number)) #tiles need to be clicked
                            print("aggiungo " + str(itm[0]) + " per il blocco " + str(number) + "[" + str(itm[1]) + "]") #debug

    i = 0
    okimg.sort() #sort the array
    print(okimg)
    alltd = driver.find_elements_by_xpath("//*[@id=\"rc-imageselect-target\"]/table/tbody/tr/td") #get all table cells

    #check all the td and click the right one (hopefully)
    for td in alltd:
        if str(i) in okimg: 
            td.click()
        i += 1

    #click "verify"
    conf = driver.find_element_by_xpath("//*[contains(text(), 'Verify')]")
    conf.click()

    #check if we need to do this again
    again=driver.find_elements_by_xpath("//*[@id=\"rc-imageselect\"]/div[2]/div[4]")
    if not again:
        print("fatto :)") #done :)
        sys.exit("")
    else:
        print("ancora da fare, aspetto qualche secondo") #check new images
        time.sleep(10) #wait for images to load
        loop(okimg, linkdownload)

api_key = 'IMAGGA API KEY'
api_secret = 'IMAGGA API SECRET'

p = inflect.engine() #init inflect
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

#open driver & captcha page
driver = webdriver.Chrome()
driver.get('http://techplanetdemo.altervista.org/cap.html')

#wait to load frame
input("Press Enter to continue...")
driver.switch_to_frame(driver.find_element_by_xpath("/html/body/div[1]/div/div/iframe"))
content = driver.find_element_by_id('recaptcha-anchor')

#press captcha
content.click()
driver.switch_to_default_content()

#wait img frame then switch
input("ok")
iframe = driver.find_element_by_xpath("//*[@title=\"recaptcha challenge\"]")
driver.switch_to_frame(iframe)

#conf button and req text
bottoneok = driver.find_elements_by_id("recaptcha-verify-button")[0]
testo = p.singular_noun(driver.find_element_by_xpath("//strong").text) #plural word to singular
print(testo)


loop("[\"firsttime\"]")

