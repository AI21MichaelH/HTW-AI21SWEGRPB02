import sys
sys.path.append('../.')

# config can be used by other python files
import config
config.TEST_MODE = True

from api import *

import unittest
import os
import base64

from distutils.dir_util import copy_tree

class TestData:
    pdfToken = 'yejvwomtiwsgubjlldjoddhtsrvdefakmkjnfrrwmqhlsfoswy'
    gifToken = 'pbjjgoojjnkaahstajumojutzyakdcbtaiopwrlknlryqjtcna'
    mp3Token = 'ylhzdajwnueqmkzdtpqbccjkczsnisdvkirbmdpfxqfxtzjmcf'
    excelToken = 'wssntykvewrcgsuekkcweigzhpzhruwmumyvtymyodaddvpdwi'

    def textBase64(): return 'VGVzdA=='
    def textContent(): return 'Test'
    
    def pdfBase64(): 
        with open("./_Testcases_data/yejvwomtiwsgubjlldjoddhtsrvdefakmkjnfrrwmqhlsfoswy", "rb") as file:
            return base64.b64encode(file.read())
    def pdfContent(): 
        with open("./_Testcases_data/yejvwomtiwsgubjlldjoddhtsrvdefakmkjnfrrwmqhlsfoswy", "rb") as file:
            return file.read()
    
    def gifBase64():
        with open("./_Testcases_data/pbjjgoojjnkaahstajumojutzyakdcbtaiopwrlknlryqjtcna", "rb") as file:
            return base64.b64encode(file.read())
    def gifContent():
        with open("./_Testcases_data/pbjjgoojjnkaahstajumojutzyakdcbtaiopwrlknlryqjtcna", "rb") as file:
            return file.read()
    
    def mp3Base64():
        with open("./_Testcases_data/ylhzdajwnueqmkzdtpqbccjkczsnisdvkirbmdpfxqfxtzjmcf", "rb") as file:
            return base64.b64encode(file.read())
    def mp3Content():
        with open("./_Testcases_data/ylhzdajwnueqmkzdtpqbccjkczsnisdvkirbmdpfxqfxtzjmcf", "rb") as file:
            return file.read()
    
    def excelBase64():
        with open("./_Testcases_data/wssntykvewrcgsuekkcweigzhpzhruwmumyvtymyodaddvpdwi", "rb") as file:
            return base64.b64encode(file.read())
    def excelContent():
        with open("./_Testcases_data/wssntykvewrcgsuekkcweigzhpzhruwmumyvtymyodaddvpdwi", "rb") as file:
            return file.read()

class Test(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        
        copy_tree('_Testcases_data', '../data')

    def tearDown(self):
        self.app_context.pop()
        path = '_Testcases_data'
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                os.remove(os.path.join('../data', f))

    # Test Upload
    def helper(self, videoName, base64String):
        upload(videoName, base64String)

        with open(os.path.join('./data', videoName, 'IMG1.jpg'), 'rb') as f:
            content = f.read()
        
        os.remove(os.path.join('./data', videoName, 'IMG1.jpg'))

        return content

    def test_Text_Upload(self):
        videoName = 'text-video'
        upload(videoName, TestData.textBase64())

        with open(os.path.join('./data', videoName, 'IMG1.jpg'), 'r') as f:
            content = f.read()
        
        os.remove(os.path.join('./data', videoName, 'IMG1.jpg'))

        self.assertEqual(content, TestData.textContent())

    def test_PDF_Upload(self):
        content = self.helper('pdf-video', TestData.pdfBase64())
        self.assertEqual(content, TestData.pdfContent())

    def test_GIF_Upload(self):
        content = self.helper('gif-video', TestData.gifBase64())
        self.assertEqual(content, TestData.gifContent())

    def test_MP3_Upload(self):
        content = self.helper('mp3-video', TestData.mp3Base64())
        self.assertEqual(content, TestData.mp3Content())
        
    def test_Excel_Upload(self):
        content = self.helper('excel-video', TestData.excelBase64())
        self.assertEqual(content, TestData.excelContent())

    #Test Download
    def test_PDF_Download(self):
        token = TestData.pdfToken
        
        result = self.client.get("/file/" + token)
        content = result.get_data()
        result.close()

        self.assertEqual(content, TestData.pdfContent())

    def test_GIF_Download(self):
        token = TestData.gifToken
        
        result = self.client.get("/file/" + token)
        content = result.get_data()
        result.close()

        self.assertEqual(content, TestData.gifContent())

    def test_MP3_Download(self):
        token = TestData.mp3Token
        
        result = self.client.get("/file/" + token)
        content = result.get_data()
        result.close()

        self.assertEqual(content, TestData.mp3Content())
        
    def test_Excel_Download(self):
        token = TestData.excelToken
        
        result = self.client.get("/file/" + token)
        content = result.get_data()
        result.close()

        self.assertEqual(content, TestData.excelContent())

if __name__ == '__main__':
    unittest.main()