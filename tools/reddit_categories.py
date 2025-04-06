from typing import Dict, List, TypedDict

class SubredditInfo(TypedDict):
    name: str
    description: str

class CategoryInfo(TypedDict):
    title: str
    description: str
    subreddits: List[SubredditInfo]

REDDIT_CATEGORIES: Dict[str, CategoryInfo] = {
    "relationships": {
        "title": "💔 충격적인 인간관계 & 감정적 갈등",
        "description": "인간관계와 감정적 갈등에 관한 다양한 이야기들",
        "subreddits": [
            {"name": "relationship_advice", "description": "연애, 가족, 인간관계에서 발생한 현실적인 조언이 필요한 사건들"},
            {"name": "AITA", "description": "도덕적 딜레마와 논쟁적인 상황"},
            {"name": "entitledparents", "description": "비상식적이고 무례한 부모들의 충격적인 이야기"},
            {"name": "JUSTNOMIL", "description": "시댁이나 처가 쪽과 갈등하는 극단적이고 불편한 가족 드라마"},
            {"name": "survivinginfidelity", "description": "충격적인 외도 및 바람피운 이야기와 그 후의 감정적 투쟁"}
        ]
    },
    "work": {
        "title": "🧑‍💼 이상하고 흥미로운 직장 이야기",
        "description": "직장에서 벌어지는 다양한 사건과 갈등",
        "subreddits": [
            {"name": "antiwork", "description": "부당한 업무환경, 퇴사 이야기, 상사와의 갈등 등"},
            {"name": "workreform", "description": "회사 내 부조리한 상황 및 직원 착취 사례 중심"},
            {"name": "TalesFromRetail", "description": "고객 서비스 분야에서 발생한 이상하고 웃픈 고객과의 사건"},
            {"name": "TalesFromTechSupport", "description": "IT 및 기술 지원직에서 벌어지는 웃기고 어이없는 상황"},
            {"name": "MaliciousCompliance", "description": "회사나 상사의 부당한 지시를 과도하게 충실히 따라 복수하는 이야기"}
        ]
    },
    "wedding": {
        "title": "🎩 충격적 결혼 & 행사 이야기",
        "description": "결혼식과 행사에서 벌어지는 다양한 사건들",
        "subreddits": [
            {"name": "weddingshaming", "description": "최악의 결혼식과 결혼 관련 사건들 (신부 측 vs 신랑 측 갈등 등)"},
            {"name": "bridezillas", "description": "결혼식 준비과정에서 미친 듯이 변한 신부들의 실제 사례"},
            {"name": "AmItheButtface", "description": "결혼식이나 가족 행사에서 발생한 이상하고 부끄러운 상황"},
            {"name": "TalesFromTheFrontDesk", "description": "호텔 및 이벤트 장소에서 벌어진 사건과 비하인드 이야기"},
            {"name": "TalesFromYourServer", "description": "웨딩이나 이벤트에서 서버가 겪은 기묘하고 놀라운 이야기"}
        ]
    }
} 