import boto3
import botocore.config
import json
import datetime



def blog_generate_using_bedrock(blogtopic:str)->str:
    
    model_id = "meta.llama3-8b-instruct-v1:0"

    
    prompt=f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """
    
    
    body={
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.95,
    }
    
    try:
        bedrock=boto3.client('bedrock-runtime',region_name='us-east-1',config=botocore.config.Config(
            read_timeout=300,retries={'max_attempts': 3}
            ))
        
        response=bedrock.invoke_model(body=json.dumps(body),modelId=model_id)
        
        response_content=response['body'].read()
        response_data=json.loads(response_content)
        print(response_data)
        
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print("Error generating blog using Bedrock:", str(e))
        return "Error generating blog."
    
def save_blog_to_s3(blog_content:str,s3_bucket:str,s3_key:str)->bool:
    try:
        s3=boto3.client('s3')
        s3.put_object(Bucket=s3_bucket,Key=s3_key,Body=blog_content)
        print(f"Blog saved to S3 bucket {s3_bucket} with key {s3_key}")
        return True
    except Exception as e:
        print("Error saving blog to S3:", str(e))
        return False
        
def lambda_handler(event, context):
    event=json.loads(event['body'])
    blogtopic=event['blogtopic']
    blog_content=blog_generate_using_bedrock(blogtopic)
    
    if blog_content:
        current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key=f"blogs/{blogtopic.replace(' ','_')}_{current_time}.txt"
        s3_bucket='<bucket name>'
        save_blog_to_s3(blog_content,s3_bucket,s3_key)
        
    else:
        print("No blog content generated.")       
    
       
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Blog generation process completed.'})
    }   