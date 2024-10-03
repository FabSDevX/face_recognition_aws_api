import boto3

s3 = boto3.resource('s3')

# Get list of objects for indexing
images=[('CarlosS1.jpg','Carlos Solis'),
      ('CarlosS2.jpg','Carlos Solis'),
      ('FabricioA1.jpeg','Fabricio Alvarado'),
      ('FabricioA2.png','Fabricio Alvarado'),
      ('FabricioP1.jpeg','Fabricio Porras'),
      ('FabricioP2.png','Fabricio Porras'),
      ('OlmanC1.jpg','Olman Castro'),
      ('OlmanC2.png','Olman Castro')
      ]

# Iterate through list to upload objects to S3   
for image in images:
    file = open(image[0],'rb')
    object = s3.Object('allowed-filter','index/'+ image[0])
    ret = object.put(Body=file,
                    Metadata={'FullName':image[1]})