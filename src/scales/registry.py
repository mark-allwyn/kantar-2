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
            "Definitely would",
            "Probably would",
            "Might or might not",
            "Probably would not",
            "Definitely would not"
        ],
        anchor_texts=[
            "I would definitely buy this scratchcard. It looks perfect for me and I'm very interested in purchasing it.",
            "I would probably buy this scratchcard. It seems appealing and I'd likely purchase it if I saw it.",
            "I might or might not buy this scratchcard. I'm unsure and would need to think about it more before deciding.",
            "I probably would not buy this scratchcard. It doesn't really appeal to me and I'd likely pass on it.",
            "I would definitely not buy this scratchcard. It doesn't interest me at all and I have no intention of purchasing it."
        ],
        description="Measures purchase intent for scratchcard concepts",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct purchase intention
            [
                "It's very likely I'd buy it. This looks like something I'd definitely purchase.",
                "I'd probably buy it. It seems like a good option that I'd likely purchase.",
                "I might or might not buy it. I'm uncertain about purchasing this.",
                "I probably wouldn't buy it. It doesn't really appeal to me as a purchase.",
                "It's rather unlikely I'd buy it. I don't see myself purchasing this."
            ],
            # Set 1: Formal purchase intent
            [
                "I would certainly purchase this product. It matches my preferences perfectly.",
                "I would likely purchase this product. It appears to be a suitable choice.",
                "I am undecided about purchasing this product. More consideration is needed.",
                "I would be unlikely to purchase this product. It does not align with my interests.",
                "I would not purchase this product under any circumstances. It holds no appeal."
            ],
            # Set 2: Casual purchase expression
            [
                "Yeah, I'd definitely get this. Looks great to me.",
                "I'd probably get this. Seems pretty good.",
                "Not sure if I'd get this or not. Could go either way.",
                "I'd probably skip this one. Not really for me.",
                "No way I'd get this. Not interested at all."
            ],
            # Set 3: Interest-based framing
            [
                "I'm very interested in buying this. It's exactly what I want.",
                "I'm quite interested in buying this. It looks appealing.",
                "I'm somewhat on the fence about buying this. Need to think it over.",
                "I'm not very interested in buying this. It doesn't excite me.",
                "I have no interest in buying this whatsoever. It's not for me."
            ],
            # Set 4: Action-oriented framing
            [
                "I will definitely make this purchase. No hesitation.",
                "I will probably make this purchase. Seems worth it.",
                "I may or may not make this purchase. Still deciding.",
                "I will probably not make this purchase. Doesn't seem worth it.",
                "I will absolutely not make this purchase. Not worth my money."
            ],
            # Set 5: Likelihood-based framing
            [
                "There's a very high chance I'd buy this. Almost certainly.",
                "There's a good chance I'd buy this. More likely than not.",
                "There's about a 50-50 chance I'd buy this. Could see it going either way.",
                "There's a low chance I'd buy this. Probably not.",
                "There's essentially no chance I'd buy this. Definitely not."
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
            "Extremely new and different",
            "Very new and different",
            "Somewhat new and different",
            "Slightly new and different",
            "Not at all new and different"
        ],
        anchor_texts=[
            "Level 1 - HIGHEST uniqueness (most positive): This concept is extremely new and different - I've never seen anything like this before. It's completely revolutionary and groundbreaking. The AR and personalization features are incredibly innovative.",
            "Level 2 - High uniqueness: This concept is very new and different. The combination of physical scratchcard with digital AR features is quite novel and stands out significantly.",
            "Level 3 - Moderate uniqueness: This concept is somewhat new and different. The AR element adds novelty, though scratchcards themselves are familiar. It's a fresh take on something known.",
            "Level 4 - Low uniqueness: This concept is only slightly new and different. The digital addition is a small twist, but scratchcards are common. Mostly conventional.",
            "Level 5 - LOWEST uniqueness (least positive): This concept is not at all new and different. Scratchcards are everywhere and this feels like just another one. Nothing stands out."
        ],
        description="Measures perceived uniqueness and novelty",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Moderate, contextual framing (FIXED 2025-12-17)
            [
                "This is quite new and different for a scratchcard. It offers features I haven't seen before in this category.",
                "This is fairly new and different. It has some distinctive elements that make it stand out from typical scratchcards.",
                "This is somewhat new and different. It has a few unique touches but feels familiar overall.",
                "This is only slightly new. It's similar to other scratchcards with minor variations.",
                "This is not new at all. It's a standard scratchcard concept I've seen many times before."
            ],
            # Set 1: Innovation framing with level guidance
            [
                "Level 1 - Highest innovation: This is highly innovative. A truly groundbreaking concept.",
                "Level 2: This is quite innovative. It brings new ideas to the table.",
                "Level 3: This is moderately innovative. Some creative elements present.",
                "Level 4: This is barely innovative. Just minor tweaks to the usual.",
                "Level 5 - No innovation: This is not innovative at all. Completely conventional."
            ],
            # Set 2: Distinctiveness framing with level guidance
            [
                "Level 1 - Most distinctive: This is extremely distinctive. It stands out completely.",
                "Level 2: This is very distinctive. It has clear unique qualities.",
                "Level 3: This is somewhat distinctive. Has some special features.",
                "Level 4: This is barely distinctive. Mostly blends in with others.",
                "Level 5 - Not distinctive: This is not distinctive at all. Completely generic."
            ],
            # Set 3: Originality framing with level guidance
            [
                "Level 1 - Highly original: This is highly original. A truly fresh take.",
                "Level 2: This is quite original. Brings something new to the mix.",
                "Level 3: This is moderately original. Has some unique aspects.",
                "Level 4: This is slightly original. Mostly derivative with small changes.",
                "Level 5 - Not original: This is not original at all. It's a carbon copy."
            ],
            # Set 4: Uniqueness direct with level guidance
            [
                "Level 1 - Completely unique: This is completely unique. One of a kind.",
                "Level 2: This is very unique. Clearly different from alternatives.",
                "Level 3: This is somewhat unique. Has distinguishing features.",
                "Level 4: This is barely unique. Quite similar to others.",
                "Level 5 - Not unique: This is not unique at all. Identical to everything else."
            ],
            # Set 5: Familiarity (reverse framing) with level guidance
            [
                "Level 1 - Most unfamiliar: This is completely unfamiliar. I've never seen this before.",
                "Level 2: This is quite unfamiliar. Much different than I'm used to.",
                "Level 3: This is moderately unfamiliar. Some new and some familiar.",
                "Level 4: This is mostly familiar. Just slight variations from the norm.",
                "Level 5 - Totally familiar: This is totally familiar. I've seen this countless times."
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
            "Moderately relevant",
            "Very relevant",
            "Extremely relevant"
        ],
        anchor_texts=[
            "This is not at all relevant to me. It has nothing to do with my interests or needs.",
            "This is only slightly relevant to me. I can see some connection but it's pretty minimal.",
            "This is moderately relevant to me. It relates to my interests to a reasonable degree.",
            "This is very relevant to me. It aligns well with my interests and preferences.",
            "This is extremely relevant to me. It's perfectly suited to my interests and exactly what I'd want."
        ],
        description="Measures personal relevance",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Personal relevance framing
            [
                "This has no relevance to me. Completely disconnected from my interests.",
                "This has minimal relevance to me. A weak connection at best.",
                "This has moderate relevance to me. Relates to my interests reasonably.",
                "This has strong relevance to me. Aligns well with my interests.",
                "This has total relevance to me. Perfectly matches my interests."
            ],
            # Set 1: Applicability framing
            [
                "This doesn't apply to me at all. Not suited for my situation.",
                "This barely applies to me. Very limited applicability.",
                "This somewhat applies to me. Has reasonable applicability.",
                "This strongly applies to me. Well-suited to my situation.",
                "This completely applies to me. Perfectly fits my situation."
            ],
            # Set 2: Fit and suitability
            [
                "This doesn't fit me at all. Totally unsuitable for me.",
                "This barely fits me. Mostly unsuitable with slight connections.",
                "This moderately fits me. Reasonably suitable overall.",
                "This fits me very well. Highly suitable for my needs.",
                "This fits me perfectly. Ideally suited to my preferences."
            ],
            # Set 3: Interest alignment
            [
                "This doesn't interest me at all. No alignment with my preferences.",
                "This barely interests me. Minimal alignment with my preferences.",
                "This moderately interests me. Decent alignment with my preferences.",
                "This strongly interests me. Good alignment with my preferences.",
                "This completely interests me. Perfect alignment with my preferences."
            ],
            # Set 4: Personal connection
            [
                "I feel no connection to this. It's completely irrelevant to me.",
                "I feel little connection to this. It's mostly irrelevant to me.",
                "I feel some connection to this. It's somewhat relevant to me.",
                "I feel strong connection to this. It's quite relevant to me.",
                "I feel total connection to this. It's extremely relevant to me."
            ],
            # Set 5: Importance to me
            [
                "This means nothing to me. Zero importance for my needs.",
                "This means very little to me. Minimal importance for my needs.",
                "This means something to me. Moderate importance for my needs.",
                "This means a lot to me. High importance for my needs.",
                "This means everything to me. Critical importance for my needs."
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
            "Like extremely",
            "Like very much",
            "Like moderately",
            "Like slightly",
            "Neither like nor dislike",
            "Do not like at all"
        ],
        anchor_texts=[
            "I like this extremely. This is truly exceptional - I absolutely love this scratchcard concept.",
            "I like this very much. It's very appealing and I find it really attractive overall.",
            "I like this moderately. It's fairly good - I have a reasonably positive view of it.",
            "I like this slightly. It's okay - I find it somewhat acceptable but nothing special.",
            "I neither like nor dislike this. I'm neutral - it doesn't particularly appeal or not appeal to me.",
            "I do not like this at all. I have negative feelings - this doesn't appeal to me."
        ],
        description="Measures overall likeability",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Semantically distinct framing (FIXED 2025-12-17)
            [
                "I find this excellent. It really stands out and I'm genuinely enthusiastic about it.",
                "I find this quite good. It appeals to me and I have a clearly positive view of it.",
                "I find this decent. It's reasonably appealing with some positive aspects.",
                "I find this just okay. It has mild appeal but nothing particularly stands out.",
                "I feel neutral about this. It neither appeals nor fails to appeal - I have no strong opinion either way.",
                "I find this unappealing. It doesn't work for me and I have negative feelings about it."
            ],
            # Set 1: Appeal framing - less superlative
            [
                "This is extremely appealing to me. Very high appeal.",
                "This is very appealing to me. Clear appeal.",
                "This is moderately appealing to me. Decent appeal.",
                "This is slightly appealing to me. Mild appeal.",
                "This is neither appealing nor unappealing. Neutral - no opinion.",
                "This is not appealing at all to me. Unappealing."
            ],
            # Set 2: Favorability framing - more measured
            [
                "I'm extremely favorable toward this. Very positive view.",
                "I'm very favorable toward this. Clearly positive view.",
                "I'm moderately favorable toward this. Somewhat positive.",
                "I'm slightly favorable toward this. Mildly positive.",
                "I'm neither favorable nor unfavorable. Neutral stance with no opinion.",
                "I'm completely unfavorable toward this. Negative view."
            ],
            # Set 3: Enjoyment framing - reduced enthusiasm
            [
                "I enjoy this extremely. I really like it.",
                "I enjoy this very much. I find it quite pleasant.",
                "I enjoy this moderately. It's reasonably enjoyable.",
                "I enjoy this slightly. Mildly enjoyable.",
                "I neither enjoy nor disenjoy this. Indifferent with no feelings.",
                "I do not enjoy this at all. I find it unpleasant."
            ],
            # Set 4: Attraction framing - balanced
            [
                "I'm extremely attracted to this. Very drawn to it.",
                "I'm very attracted to this. Clearly drawn to it.",
                "I'm moderately attracted to this. Somewhat drawn to it.",
                "I'm slightly attracted to this. Mildly drawn to it.",
                "I'm neither attracted nor repelled. No feelings in either direction.",
                "I'm not attracted at all to this. Actually repelled by it."
            ],
            # Set 5: Positive sentiment - moderate tone
            [
                "My feelings are extremely positive. It's excellent.",
                "My feelings are very positive. It's quite good.",
                "My feelings are moderately positive. It's decent.",
                "My feelings are slightly positive. It's okay.",
                "My feelings are neutral. Neither positive nor negative at all.",
                "My feelings are very negative. It's poor."
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
            "Very exciting",
            "Somewhat exciting",
            "Not very exciting",
            "Not at all exciting"
        ],
        anchor_texts=[
            "This is very exciting. It really grabs my attention and generates enthusiasm.",
            "This is somewhat exciting. It has some appeal and interest but isn't thrilling.",
            "This is not very exciting. It doesn't generate much interest or enthusiasm.",
            "This is not at all exciting. It's completely boring and uninteresting."
        ],
        description="Measures excitement level",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct excitement framing
            [
                "This is very exciting. It really grabs my attention.",
                "This is somewhat exciting. It has decent appeal.",
                "This is not very exciting. Limited appeal to me.",
                "This is not at all exciting. Completely boring."
            ],
            # Set 1: Enthusiasm framing
            [
                "I'm very enthusiastic about this. It energizes me.",
                "I'm moderately enthusiastic about this. It interests me.",
                "I'm not very enthusiastic about this. Minimal interest.",
                "I'm not at all enthusiastic about this. Zero interest."
            ],
            # Set 2: Thrill and stimulation
            [
                "This is thrilling. Highly stimulating and engaging.",
                "This is fairly interesting. Moderately stimulating.",
                "This is rather dull. Not very stimulating.",
                "This is completely dull. Utterly unstimulating."
            ],
            # Set 3: Captivation framing
            [
                "This captivates me. Totally engaging and fascinating.",
                "This somewhat captivates me. Reasonably engaging.",
                "This barely captivates me. Minimally engaging.",
                "This doesn't captivate me at all. Completely unengaging."
            ],
            # Set 4: Interest generation
            [
                "This generates strong interest. Very compelling.",
                "This generates some interest. Moderately compelling.",
                "This generates little interest. Barely compelling.",
                "This generates no interest. Not compelling at all."
            ],
            # Set 5: Appeal and attraction
            [
                "This is highly appealing. Very attractive to me.",
                "This is moderately appealing. Somewhat attractive.",
                "This is barely appealing. Not very attractive.",
                "This is not appealing at all. Completely unattractive."
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
            "Very believable",
            "Somewhat believable",
            "Not very believable",
            "Not at all believable"
        ],
        anchor_texts=[
            "This is very believable. It seems completely realistic and credible.",
            "This is somewhat believable. It seems mostly realistic with perhaps minor doubts.",
            "This is not very believable. It seems questionable and raises some doubts.",
            "This is not at all believable. It seems completely unrealistic and not credible."
        ],
        description="Measures believability",
        language="en",
        version="v1",
        num_reference_sets=6,
        anchor_text_sets=[
            # Set 0: Direct believability assessment
            [
                "This is very believable. It sounds completely realistic and trustworthy.",
                "This is somewhat believable. It sounds mostly realistic with a few questions.",
                "This is not very believable. It sounds questionable and hard to accept.",
                "This is not at all believable. It sounds completely unrealistic and false."
            ],
            # Set 1: Credibility framing
            [
                "I find this highly credible. It appears authentic and legitimate.",
                "I find this moderately credible. It appears mostly authentic with minor concerns.",
                "I find this poorly credible. It appears suspicious and doubtful.",
                "I find this completely non-credible. It appears fabricated and fake."
            ],
            # Set 2: Plausibility framing
            [
                "This seems very plausible to me. It makes perfect sense.",
                "This seems fairly plausible to me. It makes reasonable sense overall.",
                "This seems rather implausible to me. It doesn't make much sense.",
                "This seems totally implausible to me. It makes no sense whatsoever."
            ],
            # Set 3: Trust-based framing
            [
                "I fully trust this to be true. No doubts in my mind.",
                "I generally trust this to be true. Only minor doubts.",
                "I don't really trust this to be true. Significant doubts.",
                "I absolutely don't trust this to be true. Complete disbelief."
            ],
            # Set 4: Realistic assessment
            [
                "This feels very realistic. I can easily see this being real.",
                "This feels somewhat realistic. I can see this being real with reservations.",
                "This feels unrealistic. I have trouble seeing this being real.",
                "This feels totally unrealistic. There's no way this is real."
            ],
            # Set 5: Convincing framing
            [
                "I'm very convinced by this. It's highly persuasive.",
                "I'm moderately convinced by this. It's reasonably persuasive.",
                "I'm not very convinced by this. It's barely persuasive.",
                "I'm not at all convinced by this. It's completely unpersuasive."
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
