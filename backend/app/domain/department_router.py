from dataclasses import dataclass


DEPARTMENT_MAPPINGS: dict[str, list[str]] = {
    "water": ["Public Health Engineering", "Rural Water Supply", "Urban Water Supply"],
    "road": ["Public Works Department", "Rural Roads", "National Highways"],
    "electricity": ["Electricity Department", "Energy Corporation"],
    "education": ["Department of Education", "School Education", "Higher Education"],
    "health": ["Department of Health", "Public Health", "Medical Services"],
    "sanitation": ["Sanitation Department", "Swachh Bharat Mission"],
    "agriculture": ["Department of Agriculture", "Agricultural Marketing"],
    "housing": ["Housing Department", "Rural Housing", "Urban Housing"],
    "environment": ["Department of Environment", "Pollution Control Board"],
    "transport": ["Transport Department", "Road Transport"],
    "communication": ["Department of Telecommunications", "IT Department"],
    "social_welfare": ["Department of Social Welfare", "Tribal Welfare", "SC/ST Welfare"],
    "revenue": ["Revenue Department", "Land Records"],
    "police": ["Police Department", "Home Department"],
    "fire": ["Fire Services", "Emergency Services"],
}


class DepartmentRouter:
    def __init__(self, custom_mappings: dict[str, list[str]] | None = None):
        self.mappings = custom_mappings or DEPARTMENT_MAPPINGS

    def route(
        self,
        category: str,
        subcategory: str | None = None,
        location_context: dict | None = None,
    ) -> dict:
        category_lower = category.lower().strip()

        primary_candidates = self.mappings.get(category_lower, [])

        if not primary_candidates:
            for key, departments in self.mappings.items():
                if key in category_lower or category_lower in key:
                    primary_candidates = departments
                    break

        if not primary_candidates:
            primary_candidates = ["General Administration"]

        alternative_departments = []
        if subcategory:
            subcategory_lower = subcategory.lower().strip()
            for key, departments in self.mappings.items():
                if key != category_lower and (
                    key in subcategory_lower or subcategory_lower in key
                ):
                    alternative_departments.extend(departments)

        confidence = 0.8 if len(primary_candidates) > 0 else 0.3
        if subcategory and alternative_departments:
            confidence += 0.1

        return {
            "primary_department": primary_candidates[0] if primary_candidates else "General Administration",
            "alternative_departments": list(set(alternative_departments[:5])),
            "confidence": min(confidence, 1.0),
            "routing_reasons": [
                f"Category '{category}' maps to {primary_candidates[0]}",
            ],
            "jurisdiction_uncertainty": len(primary_candidates) > 2,
            "manual_review_required": confidence < 0.5,
        }
