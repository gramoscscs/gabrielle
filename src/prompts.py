def get_gabrielle_system_prompt() -> str:
    return (
        "You are Gabrielle, a principal-level AWS Platform Engineer and Terraform reviewer. "
        "Your specialties are Terraform, AWS networking, IAM, infrastructure architecture, "
        "cost optimization, and operational excellence. "
        "When a local tool is available to inspect, validate, or verify Terraform behavior, "
        "use the tool instead of relying only on static reasoning. "
        "Revie infrastructure code rigorously and explain findings clearly. "
        "Always start every response with exactly: Hi, I'm Gabrielle."
    )

def build_terraform_review_prompt(terraform_code: str) -> str:
    return(
        "Review this Terraform like a principal cloud engineer.\n\n"
        "Use the Terraform CLI tool when it helps you verify formatting, initialization, validation, or plan behavior.\n\n"
        "Output format:\n"
        "1) Executive summary\n"
        "2) Findings by severity (Critical, High, Medium, Low)\n"
        "3) Concrete remediations with example snippets\n"
        "4) Production hardening checklist\n\n"
        "Terraform to review:\n"
        "--------------------\n"
        f"{terraform_code}\n"
        "--------------------"
    )


def build_terraform_action_prompt(terraform_code: str) -> str:
        return(
            "You must execute Terraform CLI checks before any review commentary.\n\n"
            "Required tool sequence (do not skip, reorder, or substitute):\n"
            "1) Call terraform_cli with this exact input object:\n"
            "   {\"subcommand\": \"fmt\", \"working_directory\": \".\", \"args\": [\"-check\", \"-recursive\"]}\n"
            "2) Call terraform_clie with this exact input object:\n"
            " {\"subcommand\": \"init\", \"working_directory\": \".\", \"args\": [\"-backend=false\"]}\n"
            "3) Call terraform_cli with this exact input object:\n"
            "   {\"subcommand\": \"validate\", \"working_directory\": \".\", \"args\": []}\n\n"
            "Execution rules:\n"
            "- Always run all three commands, even if one fails.\n"
            "- Use working_directory='.' unless explicitly told otherwise.\n"
            "- Do not provide final conclusions until all tool results are received.\n"
            "- Base your findings strictly on tool outputs plus the Terraform source below.\n\n"
            "Output format after all tools complete:\n"
            "1) Tool run summary table (command, pass/fail, key output)\n"
            "2) What failed and why\n"
            "3) Focused remediation steps\n"
            "4) Re-run checklist\n\n"
            "Terraform to assess:\n"
            "--------------------\n"
            f"{terraform_code}\n"
            "--------------------"
        )