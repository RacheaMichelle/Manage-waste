def handler(request, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Health check: API is working!'
    }
