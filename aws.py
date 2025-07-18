import boto3

def detect_labels_local_file(photo):

    client = boto3.client('rekognition')
   
    with open(photo, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})
    
    result = []

    for label in response["Labels"]:
        name = label["Name"]
        confidence = label["Confidence"]

        result.append(f"{name} : {confidence:.2f}%")

    r = "<br/>".join(map(str, result))
    return r



# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)


def compare_faces(sourceFile, targetFile):

    # session = boto3.Session(profile_name='profile-name') >> 이건 뭔데
    client = boto3.client('rekognition')

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})

    for faceMatch in response['FaceMatches']:
        
        similarity = str(faceMatch['Similarity'])
        # print('The face at ' +
        #       str(position['Left']) + ' ' +
        #       str(position['Top']) +
        #       ' matches with ' + similarity + '% confidence')
        

    imageSource.close()
    imageTarget.close()
    # return len(response['FaceMatches']) 
    return f"두얼굴의 일치율은 {similarity}% 입니다."
    
