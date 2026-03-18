# Script para descargar el dataset desde Roboflow
## Dataset propio
from roboflow import Roboflow
rf = Roboflow(api_key="JM4DIy7CVFJbuAKAzqnF")
project = rf.workspace("ezequiels-workspace").project("robotic_hand")
version = project.version(2)
dataset = version.download("coco")

"""
##Dataset público
from roboflow import Roboflow
rf = Roboflow(api_key="JM4DIy7CVFJbuAKAzqnF")
project = rf.workspace("ho-chi-minh-city-university-of-technology-and-education-34kzv").project("hand-gesture-c0u9e")
version = project.version(2)
dataset = version.download("coco")
                
                

from roboflow import Roboflow
rf = Roboflow(api_key="JM4DIy7CVFJbuAKAzqnF")
project = rf.workspace("handkeypoints").project("hand-64xkf")
version = project.version(8)
dataset = version.download("coco")
"""                


                