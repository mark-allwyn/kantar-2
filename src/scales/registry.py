"""
Scale Registry

Manages and provides access to all defined scales.
"""

from typing import Dict, List, Optional
import json
from pathlib import Path
from .scale import Scale, ScaleType


class ScaleRegistry:
    """Registry for all measurement scales"""

    def __init__(self):
        self.scales: Dict[str, Scale] = {}

    def register_scale(self, scale: Scale):
        """Register a new scale"""
        if scale.id in self.scales:
            raise ValueError(f"Scale {scale.id} already registered")
        self.scales[scale.id] = scale

    def get_scale(self, scale_id: str) -> Optional[Scale]:
        """Get a scale by ID"""
        return self.scales.get(scale_id)

    def list_scales(self, include_deprecated: bool = False) -> List[Scale]:
        """List all registered scales"""
        if include_deprecated:
            return list(self.scales.values())
        return [s for s in self.scales.values() if not s.is_deprecated]

    def deprecate_scale(self, scale_id: str):
        """Mark a scale as deprecated"""
        if scale_id in self.scales:
            self.scales[scale_id].is_deprecated = True

    def save_to_json(self, filepath: str):
        """Save registry to JSON file"""
        data = {
            scale_id: {
                'id': scale.id,
                'name': scale.name,
                'scale_type': scale.scale_type.value,
                'num_levels': scale.num_levels,
                'level_values': scale.level_values,
                'level_labels': scale.level_labels,
                'anchor_texts': scale.anchor_texts,
                'description': scale.description,
                'language': scale.language,
                'version': scale.version,
                'is_deprecated': scale.is_deprecated,
                'metadata': scale.metadata
            }
            for scale_id, scale in self.scales.items()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_json(self, filepath: str):
        """Load registry from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for scale_id, scale_data in data.items():
            scale = Scale(
                id=scale_data['id'],
                name=scale_data['name'],
                scale_type=ScaleType(scale_data['scale_type']),
                num_levels=scale_data['num_levels'],
                level_values=scale_data['level_values'],
                level_labels=scale_data['level_labels'],
                anchor_texts=scale_data['anchor_texts'],
                description=scale_data['description'],
                language=scale_data.get('language', 'en'),
                version=scale_data.get('version', 'v1'),
                is_deprecated=scale_data.get('is_deprecated', False),
                metadata=scale_data.get('metadata', {})
            )
            self.register_scale(scale)


def create_default_scales() -> ScaleRegistry:
    """
    Create the default scale registry with all standard scales.

    These anchor statements are based on the SSR methodology paper and
    adapted for the Board Games questionnaire questions.
    """
    registry = ScaleRegistry()

    # ========== LIKERT-5 SCALES ==========

    # Purchase Intent (B2) - Primary metric
    registry.register_scale(Scale(
        id="likert5_purchase_intent_v1",
        name="5-Point Purchase Intent",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Definitely would not",
            "Probably would not",
            "Might or might not",
            "Probably would",
            "Definitely would"
        ],
        anchor_texts=[
            "I would definitely not buy this scratchcard. It doesn't interest me at all and I have no intention of purchasing it.",
            "I probably would not buy this scratchcard. It doesn't really appeal to me and I'd likely pass on it.",
            "I might or might not buy this scratchcard. I'm unsure and would need to think about it more before deciding.",
            "I would probably buy this scratchcard. It seems appealing and I'd likely purchase it if I saw it.",
            "I would absolutely buy this scratchcard! No question about it - I'm completely committed to purchasing this!"
        ],
        description="Measures purchase intent for scratchcard concepts",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct purchase intention (FIXED 2025-01-12: Reversed order to match GT)
            [
                "It's rather unlikely I'd buy it. I don't see myself purchasing this.",
                "I probably wouldn't buy it. It doesn't really appeal to me as a purchase.",
                "I might or might not buy it. I'm uncertain about purchasing this.",
                "I'd probably buy it. It seems like a good option that I'd likely purchase.",
                "I'd absolutely buy it! This is exactly what I want and I'm completely committed to purchasing it!"
            ],
            # Set 1: Formal purchase intent (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I would not purchase this product under any circumstances. It holds no appeal.",
                "I would be unlikely to purchase this product. It does not align with my interests.",
                "I am undecided about purchasing this product. More consideration is needed.",
                "I would likely purchase this product. It appears to be a suitable choice.",
                "I would absolutely purchase this product! It matches my preferences perfectly and I'm fully committed!"
            ],
            # Set 2: Casual purchase expression (FIXED 2025-01-12: Reversed order to match GT)
            [
                "No way I'd get this. Not interested at all.",
                "I'd probably skip this one. Not really for me.",
                "Not sure if I'd get this or not. Could go either way.",
                "I'd probably get this. Seems pretty good.",
                "Yeah, I'd absolutely get this! Looks perfect to me and I'm totally buying it!"
            ],
            # Set 3: Interest-based framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I have no interest in buying this whatsoever. It's not for me.",
                "I'm not very interested in buying this. It doesn't excite me.",
                "I'm somewhat on the fence about buying this. Need to think it over.",
                "I'm quite interested in buying this. It looks appealing.",
                "I'm incredibly interested in buying this! It's exactly what I want and I'm definitely going to buy it!"
            ],
            # Set 4: Action-oriented framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I will absolutely not make this purchase. Not worth my money.",
                "I will probably not make this purchase. Doesn't seem worth it.",
                "I may or may not make this purchase. Still deciding.",
                "I will probably make this purchase. Seems worth it.",
                "I will absolutely make this purchase! No hesitation whatsoever - I'm completely committed!"
            ],
            # Set 5: Likelihood-based framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "There's essentially no chance I'd buy this. Definitely not.",
                "There's a low chance I'd buy this. Probably not.",
                "There's about a 50-50 chance I'd buy this. Could see it going either way.",
                "There's a good chance I'd buy this. More likely than not.",
                "There's an absolutely certain chance I'd buy this! 100% - no doubt about it!"
            ]
        ]
    ))

    # Uniqueness (B3)
    registry.register_scale(Scale(
        id="likert5_uniqueness_v1",
        name="5-Point Uniqueness",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Not at all new and different",
            "Slightly new and different",
            "Somewhat new and different",
            "Very new and different",
            "Extremely new and different"
        ],
        anchor_texts=[
            "Level 5 - LOWEST uniqueness: This is not at all new and different. This feels like just another standard option. Nothing stands out.",
            "Level 4 - Low uniqueness: This is only slightly new and different. Just a small twist on something common. Mostly conventional.",
            "Level 3 - Moderate uniqueness: This is somewhat new and different. It adds some novelty, though parts are familiar. It's a fresh take on something known.",
            "Level 2 - High uniqueness: This is very new and different. The features are quite novel and this stands out significantly from what I usually see.",
            "Level 1 - HIGHEST uniqueness: This is incredibly new and different! I've genuinely never seen anything like this before - it's completely revolutionary and groundbreaking! Absolutely innovative!"
        ],
        description="Measures perceived uniqueness and novelty",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Moderate, contextual framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "This is not new at all. It's a standard concept I've seen many times before.",
                "This is only slightly new. It's similar to others with minor variations.",
                "This is somewhat new and different. It has a few unique touches but feels familiar overall.",
                "This is fairly new and different. It has some distinctive elements that make it stand out from typical options.",
                "This is incredibly new and different! It offers features I've genuinely never seen before - absolutely innovative!"
            ],
            # Set 1: Innovation framing with level guidance (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 5 - No innovation: This is not innovative at all. Completely conventional.",
                "Level 4: This is barely innovative. Just minor tweaks to the usual.",
                "Level 3: This is moderately innovative. Some creative elements present.",
                "Level 2: This is quite innovative. It brings new ideas to the table.",
                "Level 1 - Highest innovation: This is incredibly innovative! A truly groundbreaking concept that's absolutely revolutionary!"
            ],
            # Set 2: Distinctiveness framing with level guidance (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 5 - Not distinctive: This is not distinctive at all. Completely generic.",
                "Level 4: This is barely distinctive. Mostly blends in with others.",
                "Level 3: This is somewhat distinctive. Has some special features.",
                "Level 2: This is very distinctive. It has clear unique qualities.",
                "Level 1 - Most distinctive: This is incredibly distinctive! It stands out completely and is genuinely unique!"
            ],
            # Set 3: Originality framing with level guidance (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 5 - Not original: This is not original at all. It's a carbon copy.",
                "Level 4: This is slightly original. Mostly derivative with small changes.",
                "Level 3: This is moderately original. Has some unique aspects.",
                "Level 2: This is quite original. Brings something new to the mix.",
                "Level 1 - Highly original: This is incredibly original! A truly fresh take that's genuinely groundbreaking!"
            ],
            # Set 4: Uniqueness direct with level guidance (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 5 - Not unique: This is not unique at all. Identical to everything else.",
                "Level 4: This is barely unique. Quite similar to others.",
                "Level 3: This is somewhat unique. Has distinguishing features.",
                "Level 2: This is very unique. Clearly different from alternatives.",
                "Level 1 - Completely unique: This is absolutely unique! One of a kind and genuinely unlike anything else!"
            ],
            # Set 5: Familiarity (reverse framing) with level guidance (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 5 - Totally familiar: This is totally familiar. I've seen this countless times.",
                "Level 4: This is mostly familiar. Just slight variations from the norm.",
                "Level 3: This is moderately unfamiliar. Some new and some familiar.",
                "Level 2: This is quite unfamiliar. Much different than I'm used to.",
                "Level 1 - Most unfamiliar: This is completely unfamiliar! I've genuinely never seen this before - absolutely new!"
            ]
        ]
    ))

    # Value for Money (B4)
    registry.register_scale(Scale(
        id="likert5_value_v1",
        name="5-Point Value for Money",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Worth very much more",
            "Worth somewhat more",
            "Worth about the same",
            "Worth somewhat less",
            "Worth very much less"
        ],
        anchor_texts=[
            "This is worth very much more than the price. It's an excellent value and I'd pay significantly more for this.",
            "This is worth somewhat more than the price. The value seems pretty good and it feels like a fair deal.",
            "This is worth about the same as the price. The value matches the cost - neither a bargain nor overpriced.",
            "This is worth somewhat less than the price. It feels a bit expensive for what you get.",
            "This is worth very much less than the price. It's overpriced and definitely not worth the cost."
        ],
        description="Measures perceived value for money",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Worth-based framing
            [
                "This is worth far more than the price asked. Exceptional value.",
                "This is worth a bit more than the price asked. Good value overall.",
                "This is worth roughly what the price suggests. Fair value.",
                "This is worth a bit less than the price asked. Slightly overpriced.",
                "This is worth far less than the price asked. Very overpriced."
            ],
            # Set 1: Value proposition framing
            [
                "The value here is excellent. I'd gladly pay more.",
                "The value here is good. Seems like a fair deal.",
                "The value here is acceptable. Price matches what you get.",
                "The value here is poor. Feels somewhat expensive.",
                "The value here is terrible. Completely overpriced."
            ],
            # Set 2: Price-quality relationship
            [
                "The price is very low for this quality. Great bargain.",
                "The price is reasonable for this quality. Decent deal.",
                "The price matches this quality. Neither cheap nor expensive.",
                "The price is high for this quality. Not the best deal.",
                "The price is way too high for this quality. Bad deal."
            ],
            # Set 3: Money's worth framing
            [
                "I'm getting way more than my money's worth. Fantastic deal.",
                "I'm getting good money's worth. Reasonable investment.",
                "I'm getting fair money's worth. Balanced price-value.",
                "I'm not getting great money's worth. Bit of a stretch.",
                "I'm getting poor money's worth. Waste of money."
            ],
            # Set 4: Affordability perception
            [
                "This is a steal for the price. Incredibly affordable.",
                "This is fairly priced. Reasonably affordable.",
                "This is adequately priced. Neither cheap nor pricey.",
                "This is on the expensive side. Less affordable.",
                "This is way overpriced. Completely unaffordable."
            ],
            # Set 5: Cost-benefit assessment
            [
                "The benefits far outweigh the cost. Excellent investment.",
                "The benefits outweigh the cost. Worthwhile purchase.",
                "The benefits equal the cost. Balanced trade-off.",
                "The cost outweighs the benefits. Questionable purchase.",
                "The cost far outweighs the benefits. Poor investment."
            ]
        ]
    ))

    # Relevance (B11)
    registry.register_scale(Scale(
        id="likert5_relevance_v1",
        name="5-Point Relevance",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Not at all relevant",
            "Slightly relevant",
            "Somewhat relevant",
            "Very relevant",
            "Extremely relevant"
        ],
        anchor_texts=[
            "This is not at all relevant to me. It has nothing to do with my interests or needs.",
            "This is only slightly relevant to me. I can see some connection but it's pretty minimal.",
            "This is somewhat relevant to me. It relates to my interests to a reasonable degree.",
            "This is very relevant to me. It aligns well with my interests and preferences.",
            "This is extremely relevant to me. It's perfectly suited to my interests and exactly what I'd want."
        ],
        description="Measures personal relevance",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Personal relevance framing (FIXED 2025-01-12: Reversed order)
            [
                "This has total relevance to me. Perfectly matches my interests.",
                "This has strong relevance to me. Aligns well with my interests.",
                "This has some relevance to me. Relates to my interests reasonably.",
                "This has minimal relevance to me. A weak connection at best.",
                "This has no relevance to me. Completely disconnected from my interests."
            ],
            # Set 1: Applicability framing (FIXED 2025-01-12: Reversed order)
            [
                "This completely applies to me. Perfectly fits my situation.",
                "This strongly applies to me. Well-suited to my situation.",
                "This somewhat applies to me. Has reasonable applicability.",
                "This barely applies to me. Very limited applicability.",
                "This doesn't apply to me at all. Not suited for my situation."
            ],
            # Set 2: Fit and suitability (FIXED 2025-01-12: Reversed order)
            [
                "This fits me perfectly. Ideally suited to my preferences.",
                "This fits me very well. Highly suitable for my needs.",
                "This somewhat fits me. Reasonably suitable overall.",
                "This barely fits me. Mostly unsuitable with slight connections.",
                "This doesn't fit me at all. Totally unsuitable for me."
            ],
            # Set 3: Interest alignment (FIXED 2025-01-12: Reversed order)
            [
                "This completely interests me. Perfect alignment with my preferences.",
                "This strongly interests me. Good alignment with my preferences.",
                "This somewhat interests me. Decent alignment with my preferences.",
                "This barely interests me. Minimal alignment with my preferences.",
                "This doesn't interest me at all. No alignment with my preferences."
            ],
            # Set 4: Personal connection (FIXED 2025-01-12: Reversed order)
            [
                "I feel total connection to this. It's extremely relevant to me.",
                "I feel strong connection to this. It's quite relevant to me.",
                "I feel some connection to this. It's somewhat relevant to me.",
                "I feel little connection to this. It's mostly irrelevant to me.",
                "I feel no connection to this. It's completely irrelevant to me."
            ],
            # Set 5: Importance to me (FIXED 2025-01-12: Reversed order)
            [
                "This means everything to me. Critical importance for my needs.",
                "This means a lot to me. High importance for my needs.",
                "This means something to me. Some importance for my needs.",
                "This means very little to me. Minimal importance for my needs.",
                "This means nothing to me. Zero importance for my needs."
            ]
        ]
    ))

    # Playfulness (B11a)
    registry.register_scale(Scale(
        id="likert5_playfulness_v1",
        name="5-Point Playfulness",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Definitely wouldn't",
            "Probably wouldn't",
            "Might or might not",
            "Probably would",
            "Definitely would"
        ],
        anchor_texts=[
            "I definitely wouldn't play this with family or friends. It's not suitable for social situations at all.",
            "I probably wouldn't play this with family or friends. It doesn't really seem like something to share.",
            "I might or might not play this with family or friends. It could work in some social situations.",
            "I probably would play this with family or friends. It seems like it could be fun to share.",
            "I definitely would play this with family or friends. This is perfect for social enjoyment and sharing."
        ],
        description="Measures social playfulness intent",
        language="en",
        version="v1"
    ))

    # Gift Purchase Intent (B22)
    registry.register_scale(Scale(
        id="likert5_gift_v1",
        name="5-Point Gift Intent",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Definitely would",
            "Probably would",
            "Might or might not",
            "Probably would not",
            "Definitely would not"
        ],
        anchor_texts=[
            "I would definitely buy this as a gift. It would make a perfect present for someone.",
            "I would probably buy this as a gift. It seems like a nice gift option for the right person.",
            "I might or might not buy this as a gift. I'm unsure if it would work well as a present.",
            "I probably would not buy this as a gift. It doesn't really seem suitable as a present.",
            "I would definitely not buy this as a gift. This is not something I'd give to anyone."
        ],
        description="Measures gift purchase intent",
        language="en",
        version="v1"
    ))

    # Pleased with Gift (B24)
    registry.register_scale(Scale(
        id="likert5_pleased_v1",
        name="5-Point Gift Satisfaction",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=[
            "Extremely pleased",
            "Very pleased",
            "Moderately pleased",
            "Slightly pleased",
            "Not at all pleased"
        ],
        anchor_texts=[
            "I would be extremely pleased to receive this as a gift. It would make me very happy.",
            "I would be very pleased to receive this as a gift. I'd really appreciate getting this.",
            "I would be moderately pleased to receive this as a gift. It would be nice to get.",
            "I would be only slightly pleased to receive this as a gift. It's okay but not exciting.",
            "I would not be pleased at all to receive this as a gift. I wouldn't want this."
        ],
        description="Measures satisfaction with receiving as gift",
        language="en",
        version="v1"
    ))

    # ========== LIKERT-6 SCALE ==========

    # Likeability (B6)
    registry.register_scale(Scale(
        id="likert6_likeability_v1",
        name="6-Point Likeability",
        scale_type=ScaleType.LIKERT_6,
        num_levels=6,
        level_values=[1, 2, 3, 4, 5, 6],
        level_labels=[
            "Do not like at all",
            "Like slightly",
            "Like somewhat",
            "Like quite well",
            "Like very well",
            "Like extremely"
        ],
        anchor_texts=[
            "I do not like this at all. I have negative feelings - this doesn't appeal to me.",
            "I like this slightly. It's okay - I find it somewhat acceptable but nothing special.",
            "I like this somewhat. It's fairly good - I have a reasonably positive view of it.",
            "I like this quite well. It's very appealing and I'm impressed with it!",
            "I like this very well! It's very appealing and I'm really impressed with it! Very positive feelings!",
            "I like this extremely! This is outstanding and I absolutely love this scratchcard concept! Genuinely enthusiastic!"
        ],
        description="Measures overall likeability",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Semantically distinct framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I find this unappealing. It doesn't work for me and I have negative feelings about it.",
                "I find this just okay. It has mild appeal but nothing particularly stands out.",
                "I find this decent. It's reasonably appealing with some positive aspects.",
                "I like this quite well. It's definitely appealing and I'm fairly impressed with it - clearly positive!",
                "I find this very good! It appeals to me strongly and I have a clearly positive view of it!",
                "I find this absolutely excellent! It really stands out and I'm genuinely enthusiastic and excited about it!"
            ],
            # Set 1: Appeal framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "This is not appealing at all to me. Unappealing.",
                "This is slightly appealing to me. Mild appeal.",
                "This is moderately appealing to me. Decent appeal.",
                "This is quite appealing to me. Good solid appeal and I definitely like it.",
                "This is very appealing to me! Clear strong appeal and I really like it!",
                "This is incredibly appealing to me! Very high appeal and I absolutely love it!"
            ],
            # Set 2: Favorability framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I'm completely unfavorable toward this. Negative view.",
                "I'm slightly favorable toward this. Mildly positive.",
                "I'm moderately favorable toward this. Somewhat positive.",
                "I'm quite favorable toward this. Definitely positive view and I'm fairly impressed.",
                "I'm very favorable toward this! Clearly positive view and I really like it!",
                "I'm incredibly favorable toward this! Very positive view and genuinely excited!"
            ],
            # Set 3: Enjoyment framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I do not enjoy this at all. I find it unpleasant.",
                "I enjoy this slightly. Mildly enjoyable.",
                "I enjoy this moderately. It's reasonably enjoyable.",
                "I enjoy this quite well. It's definitely enjoyable and I'm fairly pleased with it.",
                "I enjoy this very much! I find it really great and I'm very positive about it!",
                "I enjoy this immensely! I absolutely love it and I'm genuinely enthusiastic!"
            ],
            # Set 4: Attraction framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I'm not attracted at all to this. Actually repelled by it.",
                "I'm slightly attracted to this. Mildly drawn to it.",
                "I'm moderately attracted to this. Somewhat drawn to it.",
                "I'm quite attracted to this. Definitely drawn to it with good positive feelings.",
                "I'm very attracted to this! Clearly drawn to it and really like it!",
                "I'm incredibly attracted to this! Very drawn to it and genuinely excited about it!"
            ],
            # Set 5: Positive sentiment (FIXED 2025-01-12: Reversed order to match GT)
            [
                "My feelings are very negative. It's poor.",
                "My feelings are slightly positive. It's okay.",
                "My feelings are moderately positive. It's decent.",
                "My feelings are quite positive. It's good and I'm fairly impressed with it.",
                "My feelings are very positive! It's really good and I'm very impressed!",
                "My feelings are incredibly positive! It's absolutely excellent and I love it!"
            ]
        ]
    ))

    # ========== LIKERT-4 SCALES ==========

    # Excitement (B12)
    registry.register_scale(Scale(
        id="likert4_excitement_v1",
        name="4-Point Excitement",
        scale_type=ScaleType.LIKERT_4,
        num_levels=4,
        level_values=[1, 2, 3, 4],
        level_labels=[
            "Not at all exciting",
            "Not very exciting",
            "Quite exciting",
            "Very exciting"
        ],
        anchor_texts=[
            "This is not at all exciting. It's completely boring and uninteresting.",
            "This is not very exciting. It doesn't generate much interest or enthusiasm.",
            "This is quite exciting. It has good appeal and generates genuine interest.",
            "This is absolutely thrilling and very exciting! I'm genuinely excited and energized by this!"
        ],
        description="Measures excitement level",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct excitement framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 1 (Not at all exciting): This is not at all exciting. Completely boring and uninteresting.",
                "Level 2 (Not very exciting): This is not very exciting. Limited appeal to me and doesn't generate much interest.",
                "Level 3 (Quite exciting): This is quite exciting. It has good appeal and generates genuine interest.",
                "Level 4 (Very exciting): This is absolutely thrilling! I'm genuinely excited and energized by this. It really grabs my attention and gets me fired up!"
            ],
            # Set 1: Enthusiasm framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 1 - LEAST EXCITING: I'm not at all enthusiastic about this. Zero interest, completely dull.",
                "Level 2: I'm not very enthusiastic about this. Minimal interest and weak appeal.",
                "Level 3: I'm quite enthusiastic about this. It interests me and has good appeal.",
                "Level 4 - MOST EXCITING: I'm incredibly enthusiastic about this! It energizes me and I'm genuinely pumped about it!"
            ],
            # Set 2: Thrill and stimulation (FIXED 2025-01-12: Reversed order to match GT)
            [
                "Level 1 = WORST: This is completely dull. Utterly unstimulating and boring.",
                "Level 2: This is rather dull. Not very stimulating or interesting.",
                "Level 3: This is quite interesting. Good stimulation with genuine appeal.",
                "Level 4 = BEST: This is absolutely thrilling! Highly stimulating, totally engaging, and I'm genuinely excited!"
            ],
            # Set 3: Captivation framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "1 = NOT AT ALL exciting: This doesn't captivate me at all. Completely unengaging and boring.",
                "2 = Not very exciting: This barely captivates me. Minimally engaging and limited appeal.",
                "3 = Quite exciting: This captivates me well. Engaging and interesting with good appeal.",
                "4 = VERY EXCITING: This absolutely captivates me! Totally engaging, fascinating, and I'm genuinely thrilled!"
            ],
            # Set 4: Interest generation (FIXED 2025-01-12: Reversed order to match GT)
            [
                "1 (Not at all exciting): This generates no interest. Not compelling at all, completely boring.",
                "2 (Not very exciting): This generates little interest. Barely compelling and weak appeal.",
                "3 (Quite exciting): This generates good interest. Quite compelling with genuine appeal.",
                "4 (Very exciting): This generates tremendous interest! Very compelling and I'm genuinely excited about it!"
            ],
            # Set 5: Appeal and attraction (FIXED 2025-01-12: Reversed order to match GT)
            [
                "1st level (Not at all exciting): This is not appealing at all. Completely unattractive and boring.",
                "2nd level (Not very exciting): This is barely appealing. Not very attractive or exciting.",
                "3rd level (Quite exciting): This is quite appealing. Attractive with genuine excitement.",
                "4th level (Very exciting): This is highly appealing and exciting! Very attractive and I'm genuinely enthusiastic!"
            ]
        ]
    ))

    # Believability (B14)
    registry.register_scale(Scale(
        id="likert4_believability_v1",
        name="4-Point Believability",
        scale_type=ScaleType.LIKERT_4,
        num_levels=4,
        level_values=[1, 2, 3, 4],
        level_labels=[
            "Not at all believable",
            "Not very believable",
            "Somewhat believable",
            "Very believable"
        ],
        anchor_texts=[
            "This is not at all believable. It's completely unrealistic and not credible.",
            "This is not very believable. It's questionable and raises some doubts.",
            "This is somewhat believable. It's mostly realistic with perhaps minor doubts.",
            "This is absolutely believable. It's completely realistic and credible - no doubts at all."
        ],
        description="Measures believability",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct believability assessment (FIXED 2025-01-12: Reversed order to match GT)
            [
                "This is not at all believable. It's completely unrealistic and false.",
                "This is not very believable. It's questionable and hard to accept.",
                "This is somewhat believable. It's mostly realistic with a few minor questions.",
                "This is absolutely believable. It's completely realistic and trustworthy - I believe it 100%."
            ],
            # Set 1: Credibility framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I find this completely non-credible. It's fabricated and fake.",
                "I find this poorly credible. It's suspicious and doubtful.",
                "I find this moderately credible. It's mostly authentic with minor concerns.",
                "I find this highly credible. It's authentic and legitimate - totally believable."
            ],
            # Set 2: Plausibility framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "This is totally implausible to me. It makes no sense whatsoever.",
                "This is rather implausible to me. It doesn't make much sense.",
                "This is fairly plausible to me. It makes reasonable sense overall.",
                "This is absolutely plausible to me. It makes perfect sense and I believe it completely."
            ],
            # Set 3: Trust-based framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I absolutely don't trust this to be true. Complete disbelief.",
                "I don't really trust this to be true. Significant doubts.",
                "I generally trust this to be true. Only minor doubts.",
                "I completely trust this to be true. Absolutely no doubts in my mind - it's totally believable."
            ],
            # Set 4: Realistic assessment (FIXED 2025-01-12: Reversed order to match GT)
            [
                "This is totally unrealistic. There's no way this is real.",
                "This is unrealistic. I have trouble seeing this being real.",
                "This is somewhat realistic. I can see this being real with some reservations.",
                "This is absolutely realistic. I can easily see this being real - it's completely believable."
            ],
            # Set 5: Convincing framing (FIXED 2025-01-12: Reversed order to match GT)
            [
                "I'm not at all convinced by this. It's completely unpersuasive.",
                "I'm not very convinced by this. It's barely persuasive.",
                "I'm moderately convinced by this. It's reasonably persuasive.",
                "I'm completely convinced by this. It's highly persuasive and absolutely believable."
            ]
        ]
    ))

    # ========== SLIDER SCALES ==========

    # Understanding (B13) - 9-point slider
    registry.register_scale(Scale(
        id="slider9_understanding_v1",
        name="9-Point Understanding",
        scale_type=ScaleType.SLIDER_9,
        num_levels=9,
        level_values=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        level_labels=[
            "Don't know what to expect at all",
            "Don't know what to expect",
            "Mostly don't know what to expect",
            "Somewhat don't know what to expect",
            "Neutral",
            "Somewhat know what to expect",
            "Mostly know what to expect",
            "Know what to expect",
            "Know exactly what to expect"
        ],
        anchor_texts=[
            "I don't know what to expect at all. This is completely unclear and confusing to me.",
            "I don't know what to expect. This is very unclear with little understanding.",
            "I mostly don't know what to expect. It's quite unclear with only minimal understanding.",
            "I somewhat don't know what to expect. It's more unclear than clear to me.",
            "I'm neutral about what to expect. I have some understanding but also some confusion.",
            "I somewhat know what to expect. It's more clear than unclear to me.",
            "I mostly know what to expect. It's quite clear with good understanding overall.",
            "I know what to expect. This is very clear with strong understanding.",
            "I know exactly what to expect. This is completely clear and I fully understand it."
        ],
        description="Measures understanding clarity (9-point slider)",
        language="en",
        version="v1"
    ))

    # Inertia (I1) - 7-point slider
    registry.register_scale(Scale(
        id="slider7_inertia_v1",
        name="7-Point Inertia",
        scale_type=ScaleType.SLIDER_7,
        num_levels=7,
        level_values=[1, 2, 3, 4, 5, 6, 7],
        level_labels=[
            "Always choose the same",
            "Usually choose the same",
            "Somewhat choose the same",
            "Neither",
            "Somewhat choose different",
            "Usually choose different",
            "Always choose different"
        ],
        anchor_texts=[
            "I always choose the same. I stick with what I know and never vary my choices.",
            "I usually choose the same. I tend to stick with familiar options most of the time.",
            "I somewhat tend to choose the same. I lean toward familiar options more often.",
            "I neither prefer the same nor different. I'm equally open to both familiar and new options.",
            "I somewhat tend to choose different. I lean toward trying new options more often.",
            "I usually choose different. I tend to try new options most of the time.",
            "I always choose different. I constantly seek variety and never stick with the same thing."
        ],
        description="Measures variety-seeking vs. habit (7-point slider)",
        language="en",
        version="v1"
    ))

    # ========== BINARY SCALES ==========

    # Increment (B7) - Buy different vs. wouldn't buy
    registry.register_scale(Scale(
        id="binary_increment_v1",
        name="Binary Increment",
        scale_type=ScaleType.BINARY,
        num_levels=2,
        level_values=[1, 2],
        level_labels=[
            "Would buy a different scratchcard",
            "Would not buy a scratchcard at all if this wasn't available"
        ],
        anchor_texts=[
            "If this wasn't available, I would buy a different scratchcard instead. I'd still purchase from the category.",
            "If this wasn't available, I wouldn't buy a scratchcard at all. I'd skip the purchase entirely."
        ],
        description="Measures purchase incrementality",
        language="en",
        version="v1"
    ))

    # ========== MULTI-SELECT SCALES ==========

    # Barriers (B21) - Why wouldn't you buy (conditional on low intent)
    registry.register_scale(Scale(
        id="multiselect_barriers_v1",
        name="Barriers to Purchase",
        scale_type=ScaleType.MULTI_SELECT,
        num_levels=7,
        level_values=[1, 2, 3, 4, 5, 6, 996],
        level_labels=[
            "I don't play board games",
            "The game mechanics didn't appeal to me",
            "The rules are too complicated",
            "The game's theme is not appealing to me",
            "The ticket price is too high",
            "The main prize is too low",
            "Other reason, please specify"
        ],
        anchor_texts=[
            "I have no interest in board games at all.",
            "The gameplay mechanics shown don't match my preferences.",
            "The rules seem overly complex for what I want.",
            "The theme or setting doesn't appeal to me.",
            "The price point is higher than I'm willing to pay.",
            "The potential prize value isn't attractive enough.",
            "There's a different reason I wouldn't buy this."
        ],
        description="Identifies barriers preventing purchase (shown when B2=4,5)",
        language="en",
        version="v1",
        metadata={"min_selections": 1, "random_order": True}
    ))

    # Occasions (B23) - Suitable occasions (conditional on would buy as gift)
    registry.register_scale(Scale(
        id="multiselect_occasions_v1",
        name="Gift Occasions",
        scale_type=ScaleType.MULTI_SELECT,
        num_levels=4,
        level_values=[1, 2, 3, 996],
        level_labels=[
            "To play at home with family or a partner",
            "For a party with friends",
            "For a cottage stay, weekend getaway, or vacation",
            "For another occasion, please specify"
        ],
        anchor_texts=[
            "This is perfect for casual play at home with loved ones.",
            "This would be great entertainment at a social gathering.",
            "This is ideal for leisure time away from home.",
            "I see this fitting a different type of occasion."
        ],
        description="Identifies suitable gift-giving occasions (shown when B22=1,2,3)",
        language="en",
        version="v1",
        metadata={"min_selections": 1, "random_order": True}
    ))

    return registry
