import os
import shutil
import re

repo_dir = r"scratch\Auto-Empirical-Research-Skills"
dest_skills_dir = r"C:\Users\New\.gemini\config\skills"

# 1. Flagship skills to install directly
flagships = {
    "empirical-python": os.path.join(repo_dir, "skills", "00.1-Full-empirical-analysis-skill_Python"),
    "empirical-stata": os.path.join(repo_dir, "skills", "00.2-Full-empirical-analysis-skill_Stata"),
    "empirical-r": os.path.join(repo_dir, "skills", "00.3-Full-empirical-analysis-skill_R"),
    "statspai-analysis": os.path.join(repo_dir, "skills", "00-Full-empirical-analysis-skill_StatsPAI"),
    "paper-workflow": os.path.join(repo_dir, "skills", "69-Paper-WorkFlow"),
    "aer-workflow": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-workflow"),
    "aer-identification": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-identification"),
    "aer-robustness": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-robustness"),
    "aer-tables-figures": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-tables-figures"),
    "aer-rebuttal": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-rebuttal"),
    "aer-submission": os.path.join(repo_dir, "skills", "50-brycewang-aer-skills", "skills", "aer-submission"),
    "academic-paper-composer": os.path.join(repo_dir, "skills", "01-lishix520-academic-paper-skills", "composer"),
    "academic-paper-strategist": os.path.join(repo_dir, "skills", "01-lishix520-academic-paper-skills", "strategist"),
    "causal-inference-mixtape": os.path.join(repo_dir, "skills", "10-Jill0099-causal-inference-mixtape"),
    "lit-review-agent-tools": os.path.join(repo_dir, "skills", "71-brycewang-lit-review-agent-tools", "literature-review-tools"),
    "kaggle-research": os.path.join(repo_dir, "skills", "72-kaggle-research", "kaggle-research"),
    "p-hacking-audit": os.path.join(repo_dir, "skills", "73-brycewang-p-hacking-skills", "skills", "00-phack-router"),
    "spss-amos-sem": os.path.join(repo_dir, "skills", "74-brycewang-spss-amos-sem", "spss-amos-sem"),
    "citation-checker": os.path.join(repo_dir, "skills", "62-PHY041-claude-skill-citation-checker"),
    "econfin-proposal": os.path.join(repo_dir, "skills", "67-econfin-workflow-toolkit", "econfin-proposal"),
    "did-analysis": os.path.join(repo_dir, "skills", "67-econfin-workflow-toolkit", "did-analysis"),
    "synthetic-control": os.path.join(repo_dir, "skills", "67-econfin-workflow-toolkit", "synthetic-control"),
    "de-aigc-skills": os.path.join(repo_dir, "skills", "48-de-AIGC-skills"),
    "academic-proofreader": os.path.join(repo_dir, "skills", "38-peternka-academic-proofreader"),
}

def ignore_patterns(path, names):
    ignored = set()
    for name in names:
        if name in [".git", "__pycache__", ".pytest_cache", ".DS_Store", "node_modules"]:
            ignored.add(name)
        elif name.endswith(".pyc"):
            ignored.add(name)
    return ignored

print("1. Installing auto-empirical-research-skills (master router repo)...")
router_dst = os.path.join(dest_skills_dir, "auto-empirical-research-skills")
if os.path.exists(router_dst):
    shutil.rmtree(router_dst)
shutil.copytree(repo_dir, router_dst, ignore=ignore_patterns)
print(f"Installed router to {router_dst}")

print("\n2. Installing flagship standalone skills...")
for skill_name, src_path in flagships.items():
    dst_path = os.path.join(dest_skills_dir, skill_name)
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path, ignore=ignore_patterns)
    
    # Ensure SKILL.md has matching name frontmatter
    skill_md = os.path.join(dst_path, "SKILL.md")
    if os.path.exists(skill_md):
        with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # If frontmatter name doesn't match folder name, update it for clarity
        if not re.search(r"^name:\s*" + re.escape(skill_name) + r"\s*$", content, re.MULTILINE):
            content = re.sub(r"^name:\s*.*$", f"name: {skill_name}", content, count=1, flags=re.MULTILINE)
            with open(skill_md, "w", encoding="utf-8") as f:
                f.write(content)
    print(f"Installed flagship skill: {skill_name}")

print("\nInstallation complete!")
