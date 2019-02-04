import os



for year in os.listdir("../../../../prosjekt/Histology/bladder_cancer_images"):
    if os.path.isdir("../../../../prosjekt/Histology/bladder_cancer_images/"+year):
        for filename in os.listdir("../../../../prosjekt/Histology/bladder_cancer_images/"+year):
            print(year+"/"+filename)
