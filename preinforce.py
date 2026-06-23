import os
import sys
import glob
import json
import uuid
import time
import re
import subprocess
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Reconfigure stdout/stderr to handle UTF-8 and ignore encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def clean_subproc_str(text):
    cleaned = []
    for c in text:
        o = ord(c)
        if (32 <= o <= 126) or (0xAC00 <= o <= 0xD7A3) or (0x3130 <= o <= 0x318F):
            cleaned.append(c)
        elif c in ['\n', '\r', '\t']:
            cleaned.append(c)
    return "".join(cleaned).strip()

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()

class LLMClient:
    def __init__(self, mock_mode=False):
        self.provider = DEFAULT_LLM_PROVIDER
        self.gemini_client = None
        self.openai_client = None
        self.mock_mode = mock_mode

        if self.mock_mode:
            print("LLMClient initialized in MOCK mode.")
            return

        # Determine active provider based on keys
        if self.provider == "gemini":
            if not GEMINI_API_KEY:
                if OPENAI_API_KEY:
                    self.provider = "openai"
                    print("Gemini API key missing, falling back to OpenAI.")
                else:
                    print("Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured in .env. Falling back to MOCK mode.")
                    self.mock_mode = True
                    return
            else:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                if GEMINI_API_KEY:
                    self.provider = "gemini"
                    from google import genai
                    self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                    print("OpenAI API key missing, falling back to Gemini.")
                else:
                    print("Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured in .env. Falling back to MOCK mode.")
                    self.mock_mode = True
                    return
            else:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_mock(self, prompt: str) -> str:
        # Simple rule-based mock response based on prompt contents
        if "Categorize and synthesize" in prompt:
            # Extract content from raw note
            title = "Mock Note"
            category = "10_Wiki/💡 Topics/General"
            parent = "10_Wiki/💡 Topics"
            related = []
            
            # Simple keyword matching for better mock category
            content_lower = prompt.lower()
            if "fogg" in content_lower or "fbm" in content_lower:
                mock_data = {
                    "category": "10_Wiki/💡 Topics/Psychology",
                    "similarity_score": 0.95,
                    "confidence_score": 0.98,
                    "tags": ["behavior-design", "persuasion", "psychology", "ux"],
                    "title": "Fogg Behavior Model",
                    "one_line_summary": "인간의 행동은 동기(Motivation), 능력(Ability), 계기(Trigger)가 동시에 작용할 때 발생하며, 행동 변화를 위해서는 동기 부여보다 행동을 더 쉽게 만드는 것이 효과적이다.",
                    "synthesized_patterns": "1. 동기 부여보다 복잡성을 낮추어 능력을 배려하는 것이 실질적 행동 유도에 유리하다.\n2. 계기(Trigger)는 대상의 현재 동기와 능력 상태에 맞춰 Spark, Facilitator, Signal로 매핑되어야 효과적이다.",
                    "synthesized_details": "- **행동의 3대 요소:** Motivation, Ability, Trigger가 같은 순간에 존재해야 함.\n- **단순함의 6요소:** 시간, 돈, 신체적 노력, 두뇌 사이클, 사회적 일탈, 비일상성.\n- **계기의 3유형:** Spark(동기 유도), Facilitator(과업 단순화), Signal(신호 알림).",
                    "parent": "10_Wiki/💡 Topics",
                    "related": ["Mindfulness Practice", "Policy"]
                }
                return json.dumps(mock_data, indent=2, ensure_ascii=False)
            elif "premium" in content_lower and "hero" in content_lower:
                mock_data = {
                    "category": "10_Wiki/🚀 Skills/E-commerce",
                    "similarity_score": 0.94,
                    "confidence_score": 0.96,
                    "tags": ["behavior-design", "e-commerce", "hero-section", "prompts"],
                    "title": "Premium Korean E-commerce Hero Section Prompt",
                    "one_line_summary": "국내 이커머스 상세페이지 상단 배치를 위한 '휴대용 냉각 선풍기' 프리미엄 히어로 섹션 이미지 생성용 상세 가이드 프롬프트.",
                    "synthesized_patterns": "1. 모바일 가독성을 극대화하기 위해 다중 섹션이 아닌 단일 세로형 히어로 비주얼(860px)을 채택한다.\n2. 제품 비율의 왜곡을 방지하고 화이트/아이스 블루 기반의 프리미엄 가전 톤앤매너를 일관되게 고수한다.",
                    "synthesized_details": "- **캔버스 사양:** 가로 860px, 세로 약 1900px, 롱페이지 콜라주나 다중 분할 배치 금지.\n- **비주얼 가이드:** 메탈릭 텍스처, 얼음 바람 및 블루 에너지 글로우 연출, 아이스 블루 그라데이션 배경.\n- **카피 레이아웃:** Pretendard 폰트 기반의 상단 카피, 하단 혜택 요약.",
                    "parent": "10_Wiki/🚀 Skills",
                    "related": ["Semiconductor Cooling Fan E-commerce 상세페이지 프롬프트 패키지", "Policy"]
                }
                return json.dumps(mock_data, indent=2, ensure_ascii=False)
            elif "semiconductor" in content_lower or "package" in content_lower:
                mock_data = {
                    "category": "10_Wiki/🚀 Skills/E-commerce",
                    "similarity_score": 0.96,
                    "confidence_score": 0.97,
                    "tags": ["behavior-design", "e-commerce", "detail-page", "prompts"],
                    "title": "Semiconductor Cooling Fan E-commerce 상세페이지 프롬프트 패키지",
                    "one_line_summary": "휴대용 반도체 냉각 선풍기의 국내 이커머스 최적화를 위한 12개 상세페이지 섹션별 종합 기획 및 비주얼 가이드라인 패키지.",
                    "synthesized_patterns": "1. 이커머스 전환율 향상과 반품율 방지를 위해 과장 광고 요소를 배제하고 모바일 최적화 여백과 프리미엄 가전 톤앤매너를 유지한다.\n2. 문제 제기(Problem)에서부터 기술적 증명(Tech), 다채로운 사용 씬(Usage), 최종 FAQ/CTA에 이르기까지 12단계 설득 논리 구조를 제공한다.",
                    "synthesized_details": "- **주요 섹션 구성:** Hero, Problem, Feature, Detail, Dark Tech, Wind, Foldable Stand, Portability, Usage Scene, Specs, Notice & FAQ, Final CTA.\n- **디자인 제약사항:** 중국식 난잡한 배치 지양, 가짜 인증마크 차단, 실제 제품 비율 및 라이프스타일 컷 유지.\n- **모바일 최적화:** 가독성 높은 국문 타이포그래피(Pretendard)와 그리드 형태의 사용처 카드가 핵심.",
                    "parent": "10_Wiki/🚀 Skills",
                    "related": ["Premium Korean E-commerce Hero Section Prompt", "Policy"]
                }
                return json.dumps(mock_data, indent=2, ensure_ascii=False)
            elif "mindfulness" in content_lower or "meditation" in content_lower:
                title = "Mindfulness Practice"
                category = "10_Wiki/💡 Topics/Mindfulness"
                related = ["Mindfulness Practice", "Policy"]
            elif "project" in content_lower or "action" in content_lower:
                title = "Project Alpha Sprint"
                category = "10_Wiki/🛠️ Projects/Alpha"
                parent = "10_Wiki/🛠️ Projects"
            elif "decision" in content_lower or "choose" in content_lower:
                title = "Architecture Decision Log"
                category = "10_Wiki/⚖️ Decisions/Architecture"
                parent = "10_Wiki/⚖️ Decisions"
            elif "prompt" in content_lower or "git" in content_lower:
                title = "Git Automation Guide"
                category = "10_Wiki/🚀 Skills/Git"
                parent = "10_Wiki/🚀 Skills"
                
            mock_data = {
                "category": category,
                "similarity_score": 0.88,
                "confidence_score": 0.92,
                "tags": ["reinforced", "mind-map", "mock"],
                "title": title,
                "one_line_summary": "This is a mock synthesized insight for testing the P-Reinforce pipeline.",
                "synthesized_patterns": "1. Iterative refinement is key to solid knowledge graphs.\n2. Standardized templates ensure consistency.",
                "synthesized_details": "- Checked input content and applied taxonomy rules.\n- Linked to related conceptual files to ensure connectivity.",
                "parent": parent,
                "related": related
            }
            return json.dumps(mock_data, indent=2, ensure_ascii=False)
            
        elif "manually moved the note" in prompt:
            return "Boundary Shift: User explicitly moved the file. Adjusted similarity bounds for this topic."
            
        elif "The user provided feedback" in prompt:
            if "완벽해" in prompt or "좋아" in prompt or "perfect" in prompt.lower():
                return json.dumps({
                    "w1_delta": 0.05,
                    "w3_delta": -0.01,
                    "rule_update": "User praised current folder organization. Strengthened classification accuracy weights."
                })
            else:
                return json.dumps({
                    "w1_delta": -0.05,
                    "w3_delta": 0.05,
                    "rule_update": "Adjusted classification boundary due to user correction request."
                })
        return "{}"

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        if self.mock_mode:
            return self.generate_mock(prompt)
            
        if self.provider == "gemini":
            try:
                from google.genai import types
                config = types.GenerateContentConfig()
                if system_instruction:
                    config.system_instruction = system_instruction
                
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                print(f"Gemini API error (gemini-2.5-flash): {e}. Trying gemini-1.5-flash...")
                try:
                    from google.genai import types
                    config = types.GenerateContentConfig()
                    if system_instruction:
                        config.system_instruction = system_instruction
                    response = self.gemini_client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt,
                        config=config
                    )
                    return response.text
                except Exception as e2:
                    print(f"Gemini API error (fallback): {e2}")
                    raise e2
        elif self.provider == "openai":
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API error: {e}")
                raise e

# --- Directories Initialization ---
def init_directories():
    directories = [
        "00_Raw",
        "10_Wiki/🛠️ Projects",
        "10_Wiki/💡 Topics",
        "10_Wiki/⚖️ Decisions",
        "10_Wiki/🚀 Skills",
        "20_Meta"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

def init_git():
    if not os.path.exists(".git"):
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            print("Git repository initialized.")
        except Exception as e:
            print(f"Warning: Failed to initialize Git repository: {e}")

# --- Policy Management ---
def read_policy():
    policy_path = Path("20_Meta/Policy.md")
    if not policy_path.exists():
        return {
            'w1': 0.4, 'w2': 0.3, 'w3': 0.3,
            'similarity_threshold': 0.85,
            'refactoring_threshold': 12,
            'base_confidence': 0.80
        }
    content = policy_path.read_text(encoding="utf-8")
    policy = {}
    
    w1_match = re.search(r"w1 \(Categorization Accuracy\)\*\*:\s*([\d\.]+)", content)
    w2_match = re.search(r"w2 \(Graph Connectivity\)\*\*:\s*([\d\.]+)", content)
    w3_match = re.search(r"w3 \(User Satisfaction\)\*\*:\s*([\d\.]+)", content)
    sim_match = re.search(r"Semantic Similarity Threshold\*\*:\s*([\d\.]+)", content)
    refac_match = re.search(r"Refactoring Threshold \(Files per folder\)\*\*:\s*(\d+)", content)
    conf_match = re.search(r"Default Base Confidence\*\*:\s*([\d\.]+)", content)
    
    policy['w1'] = float(w1_match.group(1)) if w1_match else 0.4
    policy['w2'] = float(w2_match.group(1)) if w2_match else 0.3
    policy['w3'] = float(w3_match.group(1)) if w3_match else 0.3
    policy['similarity_threshold'] = float(sim_match.group(1)) if sim_match else 0.85
    policy['refactoring_threshold'] = int(refac_match.group(1)) if refac_match else 12
    policy['base_confidence'] = float(conf_match.group(1)) if conf_match else 0.80
    return policy

def save_policy(w1, w2, w3, feedback_entry=None):
    policy_path = Path("20_Meta/Policy.md")
    if not policy_path.exists():
        return
    content = policy_path.read_text(encoding="utf-8")
    
    content = re.sub(r"(w1 \(Categorization Accuracy\)\*\*:\s*)[\d\.]+", f"\\g<1>{w1:.3f}", content)
    content = re.sub(r"(w2 \(Graph Connectivity\)\*\*:\s*)[\d\.]+", f"\\g<1>{w2:.3f}", content)
    content = re.sub(r"(w3 \(User Satisfaction\)\*\*:\s*)[\d\.]+", f"\\g<1>{w3:.3f}", content)
    
    if feedback_entry:
        feedback_section = "## 🔄 User Feedback History\n"
        if feedback_section in content:
            parts = content.split(feedback_section)
            history = parts[1].strip()
            if history == "*No feedback collected yet. Neural pathways are ready to learn.*" or not history:
                history = ""
            new_history = f"- {feedback_entry}\n{history}".strip()
            content = parts[0] + feedback_section + new_history + "\n"
            
    policy_path.write_text(content, encoding="utf-8")

# --- Wiki State Scanning ---
def get_summary(content):
    match = re.search(r"## 📌 한 줄 통찰 \(The Karpathy Summary\)\n>\s*(.*)", content)
    if match:
        return match.group(1).strip()
    return ""

def get_wiki_state():
    wiki_dir = Path("10_Wiki")
    files_info = []
    for path in wiki_dir.rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
            cat_match = re.search(r'category:\s*"\[\[(.*?)\]\]"', content)
            id_match = re.search(r'id:\s*([a-fA-F0-9\-]+)', content)
            title_match = re.search(r'^#\s*\[\[(.*?)\]\]', content, re.MULTILINE)
            if not title_match:
                title_match = re.search(r'^#\s*(.*)', content, re.MULTILINE)
            
            files_info.append({
                "path": Path(path).as_posix(),
                "category": cat_match.group(1) if cat_match else "",
                "id": id_match.group(1) if id_match else "",
                "title": title_match.group(1).replace("[[", "").replace("]]", "").strip() if title_match else path.stem,
                "summary": get_summary(content)
            })
        except Exception as e:
            print(f"Error reading state for {path}: {e}")
    return files_info

def is_raw_file_processed(raw_path_str):
    # Normalize path separators
    normalized_path = Path(raw_path_str).as_posix()
    wiki_state = get_wiki_state()
    for f in wiki_state:
        filepath = Path(f["path"])
        try:
            content = filepath.read_text(encoding="utf-8")
            if normalized_path in content or raw_path_str in content:
                return True
        except Exception:
            pass
    return False

# --- Git Sync operations ---
def git_sync(action_summary):
    try:
        # Check if git is initialized
        if not os.path.exists(".git"):
            return "local_dev"
        # Check if there are any changes (staged or unstaged)
        status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status_res.stdout.strip():
            return "clean"
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        # Clean action_summary for Windows ACP safety
        action_summary = clean_subproc_str(action_summary)
        commit_msg = f"[P-Reinforce] {action_summary}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
        print(f"Committed: {commit_msg}")
        
        # Get commit hash
        res = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
        commit_hash = res.stdout.strip()
        
        # Try pushing to origin main
        push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if push_res.returncode == 0:
            print("Pushed changes to origin main.")
        else:
            print("Push skipped or failed (local commit saved successfully).")
        return commit_hash
    except Exception as e:
        print(f"Git execution warning: {e}")
        return "local_commit"

# --- Graph and Index Rebuilding ---
def rebuild_index(files):
    categories = {
        "🛠️ Projects": [],
        "💡 Topics": [],
        "⚖️ Decisions": [],
        "🚀 Skills": []
    }
    
    for f in files:
        path_parts = Path(f["path"]).parts
        if len(path_parts) > 1:
            root_cat = path_parts[1]
            matched_cat = None
            for cat in categories.keys():
                if cat in root_cat or root_cat in cat:
                    matched_cat = cat
                    break
            if matched_cat:
                categories[matched_cat].append(f)
            else:
                categories["💡 Topics"].append(f)
                
    content = "# 🧠 External Brain - Wiki Index\n\nWelcome to your self-organizing knowledge base, curated by P-Reinforce.\n\n---\n\n"
    
    for cat, cat_files in categories.items():
        escaped_cat = cat.replace(" ", "%20")
        content += f"## [{cat}](file:///d:/Connect%20AI/2.%20위키에이전트/10_Wiki/{escaped_cat})\n"
        if not cat_files:
            content += "*No files synthesized yet.*\n\n"
        else:
            for cf in cat_files:
                abs_path = Path(cf["path"]).absolute().as_posix()
                summary_str = f" - *{cf['summary']}*" if cf['summary'] else ""
                content += f"- [{cf['title']}](file:///{abs_path}){summary_str}\n"
            content += "\n"
            
    content += "---\n"
    content += f"*Last index update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    Path("20_Meta/Index.md").write_text(content, encoding="utf-8")
    print("Index.md updated.")

def rebuild_graph_and_index():
    files = get_wiki_state()
    nodes = []
    edges = []
    
    for f in files:
        nodes.append({
            "id": f["id"],
            "label": f["title"],
            "path": f["path"],
            "category": f["category"]
        })

    for f in files:
        filepath = Path(f["path"])
        content = filepath.read_text(encoding="utf-8")
        
        related_links = []
        for line in content.splitlines():
            if "Related:" in line:
                links = re.findall(r'\[\[(.*?)\]\]', line)
                for l in links:
                    related_links.append(l.strip())
                    
        for rl in related_links:
            target_id = None
            for other in files:
                if other["title"] == rl or other["path"].endswith(rl) or Path(other["path"]).stem == rl or other["id"] == rl:
                    target_id = other["id"]
                    break
            if target_id and target_id != f["id"]:
                edge_exists = False
                for edge in edges:
                    if (edge["source"] == f["id"] and edge["target"] == target_id) or (edge["source"] == target_id and edge["target"] == f["id"]):
                        edge_exists = True
                        break
                if not edge_exists:
                    edges.append({
                        "source": f["id"],
                        "target": target_id
                    })
                    
        # Parent edge
        parent_match = re.search(r'Parent:\s*\[\[(.*?)\]\]', content)
        if parent_match:
            parent_label = parent_match.group(1).strip()
            for other in files:
                if other["title"] == parent_label or other["path"].endswith(parent_label) or Path(other["path"]).stem == parent_label:
                    edge_exists = False
                    for edge in edges:
                        if (edge["source"] == f["id"] and edge["target"] == other["id"]) or (edge["source"] == other["id"] and edge["target"] == f["id"]):
                            edge_exists = True
                            break
                    if not edge_exists:
                        edges.append({
                            "source": f["id"],
                            "target": other["id"]
                        })
                        
    graph_data = {"nodes": nodes, "edges": edges}
    Path("20_Meta/Graph.json").write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Graph.json updated. Nodes: {len(nodes)}, Edges: {len(edges)}")
    rebuild_index(files)

# --- Backlinking Logic ---
def ensure_bidirectional_links(target_filepath, related_titles):
    target_title = Path(target_filepath).stem
    files = get_wiki_state()
    for rel_title in related_titles:
        for other in files:
            if other["title"] == rel_title or Path(other["path"]).stem == rel_title:
                other_path = Path(other["path"])
                content = other_path.read_text(encoding="utf-8")
                
                # Check if it already has a link to this target
                if f"[[{target_title}]]" not in content:
                    # Inject link in Related section
                    # Search for Related line
                    lines = content.splitlines()
                    updated = False
                    for idx, line in enumerate(lines):
                        if "Related:" in line:
                            # Add backlink
                            if "[[" in line:
                                lines[idx] = line.rstrip() + f", [[{target_title}]]"
                            else:
                                lines[idx] = line.replace("Related:", f"Related: [[{target_title}]]")
                            updated = True
                            break
                    if not updated:
                        # Append Related line if not found
                        for idx, line in enumerate(lines):
                            if "## 🔗 지식 연결" in line or "## 🔗" in line:
                                lines.insert(idx + 2, f"- **Related:** [[{target_title}]]")
                                updated = True
                                break
                    if not updated:
                        lines.append(f"\n- **Related:** [[{target_title}]]")
                    
                    other_path.write_text("\n".join(lines), encoding="utf-8")
                    print(f"Added backlink from '{other['title']}' to '{target_title}'.")

# --- Refactoring Proposal ---
def check_for_refactoring(policy):
    wiki_dir = Path("10_Wiki")
    refac_threshold = policy.get('refactoring_threshold', 12)
    # Check immediate subfolders of 10_Wiki
    for root_cat in wiki_dir.iterdir():
        if root_cat.is_dir():
            # Count markdown files recursively
            files = list(root_cat.rglob("*.md"))
            if len(files) > refac_threshold:
                print(f"\n⚠️ [Policy Alert] Folder '{root_cat.name}' has {len(files)} files, which exceeds the threshold of {refac_threshold}!")
                print(f"💡 Suggestion: Consider running a refactoring/sub-categorization task on '{root_cat.name}'.\n")

# --- Processing Raw Ingestions ---
def process_raw_file(raw_filepath, llm_client, policy):
    raw_path = Path(raw_filepath)
    raw_content = raw_path.read_text(encoding="utf-8")
    wiki_state = get_wiki_state()
    
    print(f"Processing raw file: {raw_filepath}...")
    
    prompt = f"""
    You are P-Reinforce Architect. Categorize and synthesize the following raw note.
    
    --- RAW NOTE CONTENT ---
    {raw_content}
    ------------------------
    
    --- CURRENT WIKI STRUCTURE & POLICY ---
    Existing files in wiki: {json.dumps([{"title": f["title"], "category": f["category"], "path": f["path"]} for f in wiki_state], ensure_ascii=False)}
    Policy Guidelines: {json.dumps(policy, ensure_ascii=False)}
    ------------------------
    
    Choose the best target directory under '10_Wiki/' for this note.
    You can place it in one of the standard folders:
    - 10_Wiki/🛠️ Projects
    - 10_Wiki/💡 Topics
    - 10_Wiki/⚖️ Decisions
    - 10_Wiki/🚀 Skills
    Or create a subfolder under them if the content represents a new sub-theme (similarity score < similarity_threshold).
    
    Suggest a title, category, parent folder, related notes (at least 2, from existing wiki files list), tags, and confidence score.
    Also synthesize the content according to the Karpathy template details:
    - One-line summary
    - Extracted patterns (synthesized wisdom)
    - Detailed bullets
    
    Return a JSON object only. Do NOT include markdown tags around the JSON. The JSON must contain:
    1. "category": the target directory path, e.g. "10_Wiki/💡 Topics/Mindfulness"
    2. "similarity_score": similarity to existing categories (float 0.0 to 1.0)
    3. "confidence_score": confidence of this categorization (float 0.0 to 1.0)
    4. "tags": list of strings
    5. "title": string for document title
    6. "one_line_summary": one sentence summary
    7. "synthesized_patterns": bullet points or paragraph of patterns found
    8. "synthesized_details": detailed content in bullet points
    9. "parent": parent category link, e.g. "10_Wiki/💡 Topics"
    10. "related": list of related notes titles or paths (at least 2 related notes)
    """
    
    system_inst = "You are the P-Reinforce Architect. Return JSON only."
    res = llm_client.generate(prompt, system_inst)
    
    # Parse JSON
    try:
        json_match = re.search(r"\{.*\}", res, re.DOTALL)
        if not json_match:
            print(f"Error: Output was not JSON:\n{res}")
            return False
        
        data = json.loads(json_match.group(0))
        
        # Clean data fields
        category = data.get("category", "10_Wiki/💡 Topics").strip()
        title = data.get("title", raw_path.stem).strip()
        one_line_summary = data.get("one_line_summary", "").strip()
        synthesized_patterns = data.get("synthesized_patterns", "").strip()
        synthesized_details = data.get("synthesized_details", "").strip()
        parent = data.get("parent", "10_Wiki").strip()
        related = data.get("related", [])
        tags = data.get("tags", [])
        confidence = data.get("confidence_score", 0.8)
        similarity = data.get("similarity_score", 0.5)
        
        # Verify category exists or create it
        os.makedirs(category, exist_ok=True)
        
        # Create unique UUID
        doc_uuid = str(uuid.uuid4())
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Build target filename (safe title)
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' _-']).strip()
        target_path = Path(category) / f"{safe_title}.md"
        
        # Save placeholder first for git tracking
        target_path.write_text("Placeholder", encoding="utf-8")
        
        # Git synchronization stage
        action_sum = f"reinforce: \"{category.replace('10_Wiki/', '')}\" 폴더 생성 및 문서 연결 최적화"
        commit_hash = git_sync(action_sum)
        
        # Related notes formatting
        related_links_str = ", ".join([f"[[{r}]]" for r in related])
        if not related_links_str:
            related_links_str = "None"
            
        # Write actual content using standard template
        template = f"""---
id: {doc_uuid}
category: "[[{category}]]"
confidence_score: {confidence:.2f}
tags: {tags}
last_reinforced: {today_str}
github_commit: "{commit_hash}"
---

# [[{title}]]

## 📌 한 줄 통찰 (The Karpathy Summary)
> {one_line_summary}

## 📖 구조화된 지식 (Synthesized Content)
- **추출된 패턴:** {synthesized_patterns}
- **세부 내용:**
{synthesized_details}

## ⚠️ 모순 및 업데이트 (Contradictions & RL Update)
- **과거 데이터와의 충돌:** 없음 (신규 생성)
- **정책 변화:** {title} 주제를 {category}에 신규 매핑하여 분류 경계 확장.

## 🔗 지식 연결 (Graph)
- **Parent:** [[{parent}]]
- **Related:** {related_links_str}
- **Raw Source:** [[{raw_path.as_posix()}]]
"""
        target_path.write_text(template, encoding="utf-8")
        print(f"Synthesized wiki document created at: {target_path}")
        
        # Build back-links
        ensure_bidirectional_links(target_path, related)
        
        # Re-commit with finished document
        git_sync(f"finalize reinforce: {title} in {category}")
        
        return True
    except Exception as e:
        print(f"Failed to process raw note: {e}")
        return False

# --- Discrepancy Checker (State feedback) ---
def check_physical_discrepancies(llm_client):
    files = get_wiki_state()
    discrepancies = []
    policy = read_policy()
    
    for f in files:
        # Get parent directory relative to current path
        physical_dir = Path(f["path"]).parent.as_posix()
        declared_cat = f["category"].replace("[[", "").replace("]]", "").strip()
        
        if physical_dir != declared_cat and physical_dir.replace(" ", "") != declared_cat.replace(" ", ""):
            discrepancies.append({
                "file": f["path"],
                "title": f["title"],
                "physical": physical_dir,
                "declared": declared_cat
            })
            
    if discrepancies:
        print(f"Detected {len(discrepancies)} manual organization adjustments by user:")
        for d in discrepancies:
            print(f" - {d['title']} moved from '{d['declared']}' to '{d['physical']}'")
            
            # Read file and replace metadata category
            filepath = Path(d["file"])
            content = filepath.read_text(encoding="utf-8")
            content = re.sub(
                r'category:\s*"\[\[.*?\]\]"', 
                f'category: "[[{d["physical"]}]]"', 
                content
            )
            filepath.write_text(content, encoding="utf-8")
            
            # Policy update using LLM
            prompt = f"""
            The user manually moved the note "{d['title']}" from "{d['declared']}" to "{d['physical']}".
            Currently, our Policy.md contains classification guidelines.
            Please update the classification rules or boundary guidelines to align with this correction.
            Write a brief explanation of the boundary shift (e.g. why this note fits better in the new folder).
            """
            system_inst = "You are the P-Reinforce Architect. Update Policy rules based on user manual correction."
            explanation = llm_client.generate(prompt, system_inst)
            
            # Update weights: reduce w1 (accuracy), increase w3 (user satisfaction)
            w1 = max(0.1, policy['w1'] - 0.05)
            w3 = min(0.6, policy['w3'] + 0.05)
            w2 = 1.0 - w1 - w3
            
            feedback_entry = f"{datetime.date.today().strftime('%Y-%m-%d')}: Boundary Shift - User moved '{d['title']}' to '{d['physical']}'. Updated classification rules. Weight shift: w1={w1:.2f}, w2={w2:.2f}, w3={w3:.2f}. Details: {explanation.strip()}"
            save_policy(w1, w2, w3, feedback_entry)
            print(f"Policy weights and boundary updated for '{d['title']}'.")
            
            # Commit policy adjustments
            git_sync(f"reinforce feedback: shift boundary for {d['title']}")
    else:
        print("No physical organizational discrepancies detected.")

# --- Text Feedback handler ---
def handle_text_feedback(feedback_text, llm_client):
    policy = read_policy()
    prompt = f"""
    The user provided feedback: "{feedback_text}"
    
    Our current weights are:
    w1 (Categorization Accuracy): {policy['w1']}
    w2 (Graph Connectivity): {policy['w2']}
    w3 (User Satisfaction): {policy['w3']}
    
    How should we adjust these weights and our rules in Policy.md based on this feedback?
    - If it is praise (e.g., "이 폴더 분류 완벽해"), we increase w1 (Categorization Accuracy) to reward current policy, and slightly increase confidence rules.
    - If it is correction (e.g., "이건 '코딩'이 아니라 '비즈니스' 폴더로 옮겨줘"), we decrease w1 and increase w3 (User Satisfaction), and record the boundary rule shift.
    
    Please output a JSON response containing:
    1. "w1_delta": float value (e.g., +0.05 or -0.05)
    2. "w3_delta": float value (e.g., +0.05 or -0.05)
    3. "rule_update": string description of the new rule or adjustment to log in the policy file.
    
    Ensure it is valid JSON. Do NOT include markdown tags around the JSON.
    """
    system_inst = "You are the P-Reinforce Architect. Return JSON only."
    try:
        res_text = llm_client.generate(prompt, system_inst)
        json_match = re.search(r"\{.*\}", res_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            w1 = max(0.1, min(0.8, policy['w1'] + data.get("w1_delta", 0.0)))
            w3 = max(0.1, min(0.8, policy['w3'] + data.get("w3_delta", 0.0)))
            w2 = 1.0 - w1 - w3
            
            feedback_entry = f"{datetime.date.today().strftime('%Y-%m-%d')}: CLI Feedback: \"{feedback_text}\". {data.get('rule_update', '')}"
            save_policy(w1, w2, w3, feedback_entry)
            print(f"Feedback processed: w1={w1:.2f}, w2={w2:.2f}, w3={w3:.2f}")
            git_sync(f"reinforce feedback: text feedback processed")
        else:
            print(f"Could not parse LLM feedback response as JSON: {res_text}")
    except Exception as e:
        print(f"Failed to handle text feedback: {e}")

# --- Main CLI Flow ---
def main():
    import argparse
    parser = argparse.ArgumentParser(description="P-Reinforce Knowledge Automation Agent")
    parser.add_argument("--run", action="store_true", help="Process pending raw files once")
    parser.add_argument("--watch", type=int, metavar="N", help="Start polling watch loop every N seconds")
    parser.add_argument("--feedback", type=str, metavar="MSG", help="Record explicit user feedback or scan for discrepancies")
    parser.add_argument("--mock", action="store_true", help="Run with mock LLM responses for testing")
    
    args = parser.parse_args()
    
    init_directories()
    init_git()
    
    # Initialize LLM Client
    client = LLMClient(mock_mode=args.mock)
    policy = read_policy()
    
    if args.feedback:
        handle_text_feedback(args.feedback, client)
        check_physical_discrepancies(client)
        rebuild_graph_and_index()
        return
        
    if args.watch:
        print(f"Starting watch loop. Polling '00_Raw/' every {args.watch} seconds...")
        try:
            while True:
                # Scan for discrepancies
                check_physical_discrepancies(client)
                
                # Check for new raw files
                raw_files = list(Path("00_Raw").rglob("*.md"))
                processed_any = False
                for rf in raw_files:
                    if not is_raw_file_processed(rf):
                        success = process_raw_file(rf, client, policy)
                        if success:
                            processed_any = True
                
                if processed_any:
                    rebuild_graph_and_index()
                    check_for_refactoring(policy)
                    git_sync("update graph and index metadata")
                    
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("Watch loop stopped.")
        return

    # Default action: run once
    print("Running P-Reinforce once...")
    
    # Scan discrepancies
    check_physical_discrepancies(client)
    
    # Scan raw
    raw_files = list(Path("00_Raw").rglob("*.md"))
    print(f"Found {len(raw_files)} raw file(s) in '00_Raw/'.")
    processed_any = False
    for rf in raw_files:
        if not is_raw_file_processed(rf):
            success = process_raw_file(rf, client, policy)
            if success:
                processed_any = True
        else:
            print(f"Skipping already processed raw file: {rf}")
            
    if processed_any:
        rebuild_graph_and_index()
        check_for_refactoring(policy)
        git_sync("update graph and index metadata")
    else:
        # Rebuild graph anyway to ensure integrity
        rebuild_graph_and_index()
        git_sync("rebuild graph and index metadata")
        
    print("Run completed successfully.")

if __name__ == "__main__":
    main()
