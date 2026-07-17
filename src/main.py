import boto3
from prompts import get_gabrielle_system_prompt, build_user_prompt

def main():
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    with open("bad_s3.tf", "r", encoding="utf-8") as f:
        tf_code = f.read()

    user_text = build_user_prompt("What is Terraform?")

    response = client.converse(
        modelId="us.anthropic.claude-sonnet-4-5-202050929-v1.0",
        system=[
            {
                "text": get_gabrielle_system_prompt()
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": user_text
                    }
                ]
            }
        ],
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 1400
        }
    )

    text = response["output"]["message"]["content"][0]["text"]
    print(text)

if __name__ == "__main__":
    main()