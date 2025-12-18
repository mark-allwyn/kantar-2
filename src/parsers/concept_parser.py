"""
Concept Parser Module

Extracts product concepts from PowerPoint presentations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pptx import Presentation


@dataclass
class Concept:
    """A product concept to be tested"""
    id: str  # e.g., "Concept 1"
    name: str
    description: str
    price: Optional[str] = None
    features: List[str] = field(default_factory=list)
    occasion: Optional[str] = None
    full_text: str = ""  # Complete concept description for LLM
    image_description: Optional[str] = None


class ConceptParser:
    """Parser for PowerPoint concept presentations"""

    def __init__(self, pptx_path: str):
        self.pptx_path = pptx_path
        self.prs = None

    def parse(self) -> List[Concept]:
        """Extract all concepts from the PPTX file"""
        self.prs = Presentation(self.pptx_path)
        concepts = []

        for slide_idx, slide in enumerate(self.prs.slides):
            # Extract all text from the slide
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text = shape.text.strip()
                    if text:
                        slide_text.append(text)

            if not slide_text:
                continue

            # Try to identify this as a concept slide
            full_text = "\n".join(slide_text)

            # Look for concept indicators
            is_concept = any(keyword in full_text.lower()
                           for keyword in ['concept', 'christmas', 'birthday', 'valentine', 'czk', 'qr'])

            if is_concept:
                concept = self._parse_concept_slide(slide_idx + 1, slide_text, full_text)
                if concept:
                    concepts.append(concept)

        return concepts

    def _parse_concept_slide(self, slide_num: int, text_lines: List[str], full_text: str) -> Optional[Concept]:
        """Parse a single concept from slide text"""

        # Initialize concept
        concept_id = f"Concept {slide_num}"
        name = text_lines[0] if text_lines else f"Concept {slide_num}"

        # Extract price (look for CZK)
        price = None
        for line in text_lines:
            if 'czk' in line.lower():
                price = line.strip()
                break

        # Extract features (bullet points, numbered items)
        features = []
        for line in text_lines:
            # Skip the title and price lines
            if line == name or (price and line == price):
                continue

            # Look for feature indicators
            if any(indicator in line.lower() for indicator in
                   ['qr', 'ar', 'video', 'message', 'photo', 'upload', 'game', 'available']):
                features.append(line.strip())

        # Determine occasion
        occasion = None
        if 'christmas' in full_text.lower():
            occasion = 'Christmas'
        elif 'birthday' in full_text.lower():
            occasion = 'Birthday'
        elif 'valentine' in full_text.lower():
            occasion = 'Valentine'

        # Create concept description for LLM
        description_parts = [name]
        if price:
            description_parts.append(f"Price: {price}")
        if occasion:
            description_parts.append(f"Occasion: {occasion}")
        if features:
            description_parts.append("Features:")
            description_parts.extend([f"- {f}" for f in features])

        description = "\n".join(description_parts)

        return Concept(
            id=concept_id,
            name=name,
            description=description,
            price=price,
            features=features,
            occasion=occasion,
            full_text=full_text
        )

    def to_dict(self, concepts: List[Concept]) -> List[Dict]:
        """Convert concepts to dictionary for JSON serialization"""
        return [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'price': c.price,
                'features': c.features,
                'occasion': c.occasion,
                'full_text': c.full_text
            }
            for c in concepts
        ]
