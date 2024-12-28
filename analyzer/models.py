from django.db import models


# Create your models here.



class UploadedFile(models.Model):
    
    file = models.FileField()  
    # upload_to="uploads"

        
    #upload the user csv files to the uploads folder to store them temporarily for processing
    #make migrations and then migrate the changes to reflect to db

