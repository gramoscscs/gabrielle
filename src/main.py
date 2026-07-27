import boto3
from prompts import (
    get_gabrielle_system_prompt,
    build_terraform_action_prompt,
    build_terraform_review_prompt,
)
from tool_registry import build_tool_result_content, execute_tool, get_bedrock_tool_config


MAX_TOOL_ROUNDS = 6
DEMO_ACTION_MODE = True
TOOL_FALLBACK_NUDGE = (
    "You must execute terraform_cli now. "
    "Run exactly these calls in order with working_directory='.' : "
    "1) subcommand='fmt', args=['-check','recursive']; "
    "2) subcommand='init', args=['-backend=false']; "
    "3) subcommand='validate', args=[]. "
    "Then explain the results."
)

def main():
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    with open("samples/example_bad_code/bad_s3.tf", "r", encoding="utf-8") as f:
        tf_code = f.read()

    user_text = (
        build_terraform_action_prompt(tf_code)
        if DEMO_ACTION_MODE
        else build_terraform_review_prompt(tf_code)
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": user_text
                }
            ]
        }
    ]
    sent_no_tool_nudge = False

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.converse(
            modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system=[
                {
                    "text": get_gabrielle_system_prompt()
                }
            ],
            messages=messages,
            toolConfig=get_bedrock_tool_config(),
            inferenceConfig={
                "temperature": 0.2,
                "maxTokens": 1400
            }
        )

        output_message = response["output"]["message"]
        messages.append(output_message)

        tool_results = {}
        for content_block in output_message["content"]:
            tool_use = content_block.get("toolUse")
            if not tool_use:
                continue

            result = execute_tool(tool_use["name"], tool_use["input"])
            tool_results.append(
                {
                    "toolResult":{
                        "toolUseId": tool_use["toolUseId"],
                        "content": build_tool_result_content(result),
                        "status": "success" if result.get("ok") else "error",
                    }
                }
            )

        if not tool_results:
            if not sent_no_tool_nudge:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": TOOL_FALLBACK_NUDGE
                            }
                        ],
                    }
                )
                sent_no_tool_nudge = True
                continue

            final_text = "\n".join(
                content_block["text"]
                for content_block in output_message["content"]
                if "text" in content_block
            )
            print(final_text)
            return

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

    raise RuntimeError("Model exceeded the maximum number of tool rounds")

if __name__ == "__main__":
    main()