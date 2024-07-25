import re
import json
import uuid
import urllib.parse
import boto3

'''
Folder structure:

covenants-deeds-images
    -raw
        -mn-ramsey-county
        -wi-milwaukee-county
    -ocr
        -txt
            -mn-ramsey-county
            -wi-milwaukee-county
        -json
            -mn-ramsey-county
            -wi-milwaukee-county
        -stats
            -mn-ramsey-county
            -wi-milwaukee-county
        -hits
            -mn-ramsey-county
            -wi-milwaukee-county
    -web
        -mn-ramsey-county
        -wi-milwaukee-county
'''

s3 = boto3.client('s3')

def load_json(bucket, key):
    content_object = s3.get_object(Bucket=bucket, Key=key)
    file_content = content_object['Body'].read().decode('utf-8')
    return json.loads(file_content)

def save_page_ocr_json(textract_response, bucket, key_parts):
    """In this version, this function just re-writes the key parts into the correct output syntax and returns the result rather than saving a new OCR json file"""
    out_key = f"ocr/json/{key_parts['workflow']}/{key_parts['remainder']}.json"
    return out_key

def save_page_text(lines, bucket, key_parts):
    """In this version, this function just re-writes the key parts into the correct output syntax and returns the result rather than saving a new TXT file"""
    text_blob = ''

    out_key = f"ocr/txt/{key_parts['workflow']}/{key_parts['remainder']}.txt"
    return out_key

def save_doc_stats(lines, bucket, key_parts, public_uuid):
    """ This is the only part of the lambda that actually saves a new object to S3, mainly due to the new UUID being generated."""
    num_lines = len(lines)
    num_chars = sum([len(line['Text']) for line in lines])

    stats = {
        'workflow': key_parts['workflow'],
        'remainder': key_parts['remainder'],
        'public_uuid': public_uuid,
        'num_lines': num_lines,
        'num_chars': num_chars
    }

    out_key = f"ocr/stats/{key_parts['workflow']}/{key_parts['remainder']}__{public_uuid}.json"

    s3.put_object(
        Body=json.dumps(stats),
        Bucket=bucket,
        Key=out_key,
        StorageClass='GLACIER_IR',
        ContentType='application/json'
    )
    return out_key


def lambda_handler(event, context):
    """Designed to mimic actions of OCR step, but skip OCR, to avoid needing to re-OCR files that have already been OCRed. The function opens a previously created OCR JSON saved to s3 and passes data about it on to the next step. This lambda is only used for DeedPageProcessorFAKEOCR, which is run to correct errors in post-OCR stages of the main DeedPageProcessor Step Function."""

    if 'Records' in event:
        # Get the object from a more standard put event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(
            event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    else:
        # Get the object from an EventBridge event
        bucket = event['detail']['bucket']['name']
        key = event['detail']['object']['key']

    print(f'FAKING OCR STEP FOR {bucket} {key}')

    # Read from pre-existing json result, Get the text blocks
    # key = key.replace('test/milwaukee', 'raw/wi-milwaukee-county')  # Temp for testing
    key_parts = re.search('(?P<status>[a-z]+)/(?P<workflow>[A-z\-]+)/(?P<remainder>.+)\.(?P<extension>[a-z]+)', key).groupdict()
    textract_json_file = save_page_ocr_json({}, bucket, key_parts)

    print(textract_json_file)
    response = load_json(bucket, textract_json_file)
    blocks=response['Blocks']

    page_info = [block for block in blocks if block['BlockType'] == 'PAGE']
    lines = [block for block in blocks if block['BlockType'] == 'LINE']
    words = [block for block in blocks if block['BlockType'] == 'WORD']

    # Generate a new UUID because you can't easily derive the old one, if it was created. This can lead to duplicate S3 objects (same file, different randomized suffix), but generally only one copy will be processed by the ingestion process since only one will have made it all the way through the process.
    public_uuid = uuid.uuid4().hex

    page_txt_file = save_page_text(lines, bucket, key_parts)
    page_stats_file = save_doc_stats(lines, bucket, key_parts, public_uuid)

    return {
        "statusCode": 200,
        "body": {
            "message": "hello world",
            "bucket": bucket,
            "orig": key,
            "json": textract_json_file,
            "txt": page_txt_file,
            "stats": page_stats_file,
            "uuid": public_uuid
        },
    }
