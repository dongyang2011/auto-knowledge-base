"""
LLM-based information extractor.
"""
import json
from typing import Dict, Optional, List
from pathlib import Path

from src import ExtractedInfo, ExperimentalSetup
from src.llm import LLMBackend, OpenAIBackend


class LLMInformationExtractor:
    """Extract structured information from article text using LLM."""
    
    DEFAULT_SYSTEM_PROMPT = """
You are an academic article information extraction assistant. Extract the following key information 
from the provided article text and output it in valid JSON format.

Output schema:
{
  "title": "article title",
  "authors": ["author1", "author2"],
  "year": publication year (integer),
  "core_approach": "summary of the core method/proposed approach, keep under 200 words",
  "experimental_setup": {
    "datasets": ["list of datasets used"],
    "metrics": ["list of evaluation metrics"],
    "baselines": ["list of baseline methods compared against"]
  },
  "key_findings": ["list of main conclusions and findings, one sentence each"],
  "innovations": ["list of innovations compared to previous work, one sentence each"],
  "open_problems": ["list of open problems mentioned for future work, leave empty array if none"],
  "references": [
    {
      "title": "title of cited article",
      "authors": ["author1"],
      "year": "year"
    }
  ]
}

Requirements:
1. Output strictly valid JSON, no extra text before or after
2. If a field cannot be found, leave it as empty array or empty string
3. Extract accurately, do not make up information
"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.0, llm_backend: Optional[LLMBackend] = None):
        if llm_backend is not None:
            self.llm = llm_backend
        else:
            self.llm = OpenAIBackend(api_key=api_key, default_model=model)
        self.model = model
        self.temperature = temperature
        self.system_prompt = self.DEFAULT_SYSTEM_PROMPT.strip()
    
    def extract(self, text: str) -> Optional[ExtractedInfo]:
        """Extract structured information from article text."""
        try:
            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                model=self.model,
                temperature=self.temperature,
            )
            
            if not response.success or not response.content:
                print(f"Extraction error: {response.error_message}")
                return None
            
            data = json.loads(response.content)
            return self._parse_dict(data)
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def _parse_dict(self, data: Dict) -> ExtractedInfo:
        """Parse JSON dict into ExtractedInfo object."""
        exp_setup = ExperimentalSetup(
            datasets=data.get("experimental_setup", {}).get("datasets", []),
            metrics=data.get("experimental_setup", {}).get("metrics", []),
            baselines=data.get("experimental_setup", {}).get("baselines", [])
        )
        
        return ExtractedInfo(
            id="",  # Will be set by caller
            title=data.get("title", ""),
            authors=data.get("authors", []),
            year=data.get("year"),
            source="",  # Will be set by caller
            url=None,  # Will be set by caller
            original_path="",  # Will be set by caller
            domain=[],  # Will be set by caller
            core_approach=data.get("core_approach", ""),
            experimental_setup=exp_setup,
            key_findings=data.get("key_findings", []),
            innovations=data.get("innovations", []),
            open_problems=data.get("open_problems", []),
            references=data.get("references", [])
        )
    
    def save_extracted(self, extracted: ExtractedInfo, md_path: Path, json_path: Path):
        """Save extracted information to both Markdown and JSON."""
        # Save JSON
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": extracted.id,
                "title": extracted.title,
                "authors": extracted.authors,
                "year": extracted.year,
                "source": extracted.source,
                "url": extracted.url,
                "original_path": extracted.original_path,
                "domain": extracted.domain,
                "core_approach": extracted.core_approach,
                "experimental_setup": {
                    "datasets": extracted.experimental_setup.datasets,
                    "metrics": extracted.experimental_setup.metrics,
                    "baselines": extracted.experimental_setup.baselines
                },
                "key_findings": extracted.key_findings,
                "innovations": extracted.innovations,
                "open_problems": extracted.open_problems,
                "references": extracted.references,
                "created_at": extracted.created_at.isoformat(),
                "updated_at": extracted.updated_at.isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # Save Markdown
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {extracted.title}\n\n")
            f.write(f"## 基本信息\n")
            f.write(f"- **作者**: {', '.join(extracted.authors)}\n")
            f.write(f"- **年份**: {extracted.year}\n")
            f.write(f"- **来源**: {extracted.source}\n")
            if extracted.url:
                f.write(f"- **URL**: {extracted.url}\n")
            f.write(f"\n")
            
            f.write(f"## 核心方案\n{extracted.core_approach}\n\n")
            
            f.write(f"## 实验设置\n")
            if extracted.experimental_setup.datasets:
                f.write(f"### 数据集\n")
                for ds in extracted.experimental_setup.datasets:
                    f.write(f"- {ds}\n")
                f.write(f"\n")
            if extracted.experimental_setup.metrics:
                f.write(f"### 评估指标\n")
                for m in extracted.experimental_setup.metrics:
                    f.write(f"- {m}\n")
                f.write(f"\n")
            if extracted.experimental_setup.baselines:
                f.write(f"### 基线方法\n")
                for b in extracted.experimental_setup.baselines:
                    f.write(f"- {b}\n")
                f.write(f"\n")
            
            f.write(f"## 主要结论\n")
            for finding in extracted.key_findings:
                f.write(f"- {finding}\n")
            f.write(f"\n")
            
            f.write(f"## 创新点\n")
            for innovation in extracted.innovations:
                f.write(f"- {innovation}\n")
            f.write(f"\n")
            
            if extracted.open_problems:
                f.write(f"## 开放问题\n")
                for problem in extracted.open_problems:
                    f.write(f"- {problem}\n")
                f.write(f"\n")
            
            if extracted.references:
                f.write(f"## 参考文献\n")
                for ref in extracted.references:
                    title = ref.get("title", "")
                    year = ref.get("year", "")
                    authors = ref.get("authors", [])
                    author_str = ", ".join(authors)
                    f.write(f"- {title} ({year}) - {author_str}\n")
