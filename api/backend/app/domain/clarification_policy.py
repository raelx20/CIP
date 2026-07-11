from dataclasses import dataclass


@dataclass
class ClarificationQuestion:
    topic: str
    question: str
    priority: int
    information_value: float
    already_answered: bool = False


class ClarificationPolicy:
    MAX_ROUNDS = 3
    MIN_INFORMATION_VALUE = 0.3

    ESSENTIAL_TOPICS = [
        "exact_problem",
        "precise_location",
        "duration",
        "severity",
        "people_affected",
    ]

    IMPORTANT_TOPICS = [
        "vulnerable_groups",
        "health_consequences",
        "safety_consequences",
        "alternatives_available",
        "supporting_evidence",
    ]

    OPTIONAL_TOPICS = [
        "frequency",
        "economic_impact",
        "environmental_impact",
        "service_disruption",
        "emergency_conditions",
    ]

    def should_clarify(
        self,
        missing_information: list[str],
        current_round: int,
        max_rounds: int,
        submission_status: str,
    ) -> bool:
        if current_round >= max_rounds:
            return False
        if submission_status in ["assessed", "completed", "rejected"]:
            return False
        if not missing_information:
            return False
        return True

    def generate_clarification_questions(
        self,
        missing_information: list[str],
        already_answered: list[str],
        current_round: int,
    ) -> list[ClarificationQuestion]:
        questions = []

        for topic in missing_information:
            if topic in already_answered:
                continue

            priority = self._get_topic_priority(topic)
            information_value = self._get_information_value(topic)

            if information_value < self.MIN_INFORMATION_VALUE:
                continue

            question_text = self._generate_question_text(topic)

            questions.append(
                ClarificationQuestion(
                    topic=topic,
                    question=question_text,
                    priority=priority,
                    information_value=information_value,
                )
            )

        questions.sort(key=lambda q: (-q.priority, -q.information_value))

        max_questions = max(1, 3 - current_round)
        return questions[:max_questions]

    def _get_topic_priority(self, topic: str) -> int:
        if topic in self.ESSENTIAL_TOPICS:
            return 3
        elif topic in self.IMPORTANT_TOPICS:
            return 2
        elif topic in self.OPTIONAL_TOPICS:
            return 1
        return 1

    def _get_information_value(self, topic: str) -> float:
        value_map = {
            "exact_problem": 0.95,
            "precise_location": 0.90,
            "duration": 0.85,
            "severity": 0.80,
            "people_affected": 0.75,
            "health_consequences": 0.70,
            "safety_consequences": 0.70,
            "vulnerable_groups": 0.65,
            "alternatives_available": 0.50,
            "supporting_evidence": 0.45,
            "frequency": 0.40,
            "economic_impact": 0.35,
            "environmental_impact": 0.35,
            "service_disruption": 0.30,
            "emergency_conditions": 0.60,
        }
        return value_map.get(topic, 0.3)

    def _generate_question_text(self, topic: str) -> str:
        questions = {
            "exact_problem": "Could you please describe the exact problem you are facing in more detail?",
            "precise_location": "Could you provide a more precise location for this issue? A landmark or nearby reference would help.",
            "duration": "How long has this problem been going on?",
            "severity": "How severe is this problem right now? Is it getting worse?",
            "people_affected": "Approximately how many people are affected by this issue?",
            "vulnerable_groups": "Are there any vulnerable groups (elderly, children, disabled persons) particularly affected?",
            "health_consequences": "Has this issue caused any health problems for anyone?",
            "safety_consequences": "Are there any safety concerns or risks to anyone?",
            "alternatives_available": "Are there any alternative solutions or workarounds currently being used?",
            "supporting_evidence": "Do you have any photos, documents, or other evidence you can share?",
            "frequency": "How often does this problem occur?",
            "economic_impact": "Has this issue caused any financial losses or economic hardship?",
            "environmental_impact": "Is there any environmental damage or concern related to this issue?",
            "service_disruption": "Is this issue disrupting any essential services?",
            "emergency_conditions": "Is this an emergency situation requiring immediate attention?",
        }
        return questions.get(topic, "Could you provide more information about this aspect?")
