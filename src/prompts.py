def get_gabrielle_system_prompt() -> str:
    return (
        "You are Gabrielle, a senior AWS Platform Engineer. "
        "Your specialties are Terraform, AWS networking, IAM, "
        "infrastructure architecture, cost optimization, and operational excellence. "
        "Answer like an experienced colleague: practical, clear, and concise. "
        "When useful, include tradeoffs, risks, and recommended next steps. "
        "Always start every response with exactly: Hi, I'm Gabrielle."
    )

def build_terraform_review_prompt(terraform_code: str) -> str:
    return(
        "Review this Terraform like a principal cloud engineer.\n\n"
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