import json
import math
from pathlib import Path

from kinasis_library.events.extractor_event import ExtractorEvent, Objetives, RisecAnswer

from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.criteria import CriteriaRag
from models.prompt_response import PromptResponse

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "jev_prompt.json"
SCORE_LEVELS = ["0", "20", "40", "60", "80", "100"]
MAX_SCORE_INDEX = len(SCORE_LEVELS) - 1
CRITERIA_THRESHOLD = 60


class ExtractorHandler:
    def __init__(self, qh=None, ch=None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()
        self._prompt = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))

    @staticmethod
    def _score_to_pct(answer: dict) -> int:
        if answer.get("type") != "score":
            raise ValueError(f"Respuesta inválida para {answer.get('name')!r}: se esperaba 'score', "
                              f"se obtuvo {answer.get('type')!r}")
        score = answer.get("score")
        if score is None or not isinstance(score, (int, float)) or math.isnan(score):
            raise ValueError(f"Score inválido para {answer.get('name')!r}: {score!r}")
        if not (0 <= score <= MAX_SCORE_INDEX):
            raise ValueError(f"Score fuera de rango para {answer.get('name')!r}: {score!r} "
                              f"(rango válido 0-{MAX_SCORE_INDEX})")
        return round(score / MAX_SCORE_INDEX * 100)

    @staticmethod
    def _choice_to_bool(answer: dict) -> bool:
        if answer.get("type") != "choice":
            raise ValueError(f"Respuesta inválida para {answer.get('name')!r}: se esperaba 'choice', "
                              f"se obtuvo {answer.get('type')!r}")
        choice = answer.get("choice")
        if choice not in ("true", "false"):
            raise ValueError(f"Choice inválido para {answer.get('name')!r}: {choice!r}")
        return choice == "true"

    def _merge_criteria_objectives(self, criteria: list[CriteriaRag], objectives: list[Objetives]) -> list[dict]:
        objetives_prompt_list = []
        for o in objectives:
            for c in criteria:
                if c.carrera_id == o.id_carrera and o.description != "":
                    objetives_prompt_list.append({
                        "criteria_id": c.criteria_id,
                        "criteria": c.criteria,
                        "description": o.description
                    })
        return objetives_prompt_list

    def _obtain_context_dimention(self, key: int, criteria: list[CriteriaRag], questions: RisecAnswer):
        priority_criteria = questions.criteria_list
        save = {}
        priority_save = {}
        for pc in priority_criteria:
            priority_save.update(pc)
        for c in criteria:
            save[c.criteria_id] = c.criteria
        match key:
            case 1:
                name_dimension = "Realistic"
            case 2:
                name_dimension = "Investigative"
            case 4:
                name_dimension = "Social"
            case 5:
                name_dimension = "Enterprising"
            case 6:
                name_dimension = "Conventional"
        dimension_prompt = {
            "dimension": name_dimension,
            "criteria": save,
            "priority_criteria": priority_save,
            "open_question": questions.open_question
        }
        return dimension_prompt

    def _match_criteria_with_event(self, criteria: list[dict], event: ExtractorEvent) -> dict[int, list[CriteriaRag]]:
        criteria_por_riasec: dict[int, list[CriteriaRag]] = {tipo: [] for tipo in range(7)}
        prompt_info = {}

        for c in criteria:
            criterio = CriteriaRag(
                criteria_id=c["criterio_id"],
                carrera_id=c["carrera_id"],
                criteria=c["resumen_criterio"],
                criteria_type=c["riasec_id"])
            criteria_por_riasec[criterio.criteria_type].append(criterio)
        list_criteria_0 = criteria_por_riasec[0]
        part_0 = self._merge_criteria_objectives(list_criteria_0, event.objetives)
        for k, v in criteria_por_riasec.items():
            if k == 0:
                prompt_info["part_0"] = part_0
            elif k == 3:
                pass
            else:
                prompt_info[f"part_{k}"] = self._obtain_context_dimention(k, criteria_por_riasec[k], event.questions[k])
        return prompt_info

    def get_info_prompt(self, event: ExtractorEvent):
        criteria_rag = self._qh.get_criteria_order_by_id_riasec(event.area_id)
        prompt_parameters = self._match_criteria_with_event(criteria_rag, event)
        return prompt_parameters

    def generate_prompt_for_jev(self, prompt_info: dict) -> dict:
        objetivo_template = self._prompt["prompt_objetivo_coincidence"]
        dimension_coincidence_template = self._prompt["prompt_dimension_coincidence"]
        dimension_repeat_template = self._prompt["prompt_dimension_repeat"]

        questions = []
        for idx, item in enumerate(prompt_info.get("part_0", [])):
            questions.append({
                "name": f"part_0:{item['criteria_id']}:coincidence",
                "type": "score",
                "instructions": objetivo_template.format(idx=idx),
                "levels": [{"label": label} for label in SCORE_LEVELS],
            })

        for part_key, part in prompt_info.items():
            if part_key == "part_0":
                continue
            for criteria_id in part["criteria"]:
                questions.append({
                    "name": f"{part_key}:{criteria_id}:coincidence",
                    "type": "score",
                    "instructions": dimension_coincidence_template.format(
                        part_key=part_key, criterio_id=criteria_id),
                    "levels": [{"label": label} for label in SCORE_LEVELS],
                })
            for criteria_id in part["priority_criteria"]:
                questions.append({
                    "name": f"{part_key}:{criteria_id}:repeat",
                    "type": "choice",
                    "instructions": dimension_repeat_template.format(
                        part_key=part_key, criterio_id=criteria_id),
                    "choices": [{"value": "true", "label": "true"},
                                {"value": "false", "label": "false"}],
                })

        return {
            "input": json.dumps(prompt_info, ensure_ascii=False),
            "questions": questions,
        }

    def format_jev_response(self, prompt_info: dict, response: dict) -> dict:
        answers = {answer["name"]: answer for answer in response["answers"]}

        objetives_criteria = []
        for item in prompt_info.get("part_0", []):
            name = f"part_0:{item['criteria_id']}:coincidence"
            objetives_criteria.append({
                "criteria_id": item["criteria_id"],
                "coincidence": self._score_to_pct(answers[name]),
            })

        priority_criteria = []
        criterias = []
        for part_key, part in prompt_info.items():
            if part_key == "part_0":
                continue
            pct_by_criteria = {
                criteria_id: self._score_to_pct(answers[f"{part_key}:{criteria_id}:coincidence"])
                for criteria_id in part["criteria"]
            }
            for criteria_id in part["priority_criteria"]:
                priority_criteria.append({
                    "criteria_id": int(criteria_id),
                    "coincidence": pct_by_criteria[int(criteria_id)],
                    "repeat": self._choice_to_bool(answers[f"{part_key}:{criteria_id}:repeat"]),
                })
            for criteria_id, pct in pct_by_criteria.items():
                if pct >= CRITERIA_THRESHOLD:
                    criterias.append({"criteria_id": criteria_id, "coincidence": pct})

        return {
            "objetives_criteria": objetives_criteria,
            "priority_criteria": priority_criteria,
            "criterias": criterias,
        }

    def save_result_to_db(self, result: dict, event: ExtractorEvent) -> None:
        priority_ids = {crit["criteria_id"] for crit in result["priority_criteria"]}
        prompt_result = PromptResponse(**result)

        main_criteria_by_career = {row["carrera_id"]: row["criterio_id"] for row in self._qh.get_main_criteria_by_area(event.area_id)}
        coincidence_by_criteria = { crit["criteria_id"]: crit["coincidence"] / 100 for crit in prompt_result.objetives_criteria}

        for obj in event.objetives:
            self._ch.save_objetive_user(
                score=obj.porc_evaluation,
                user_id=event.user_id,
                career_id=obj.id_carrera)

            criteria_id = main_criteria_by_career.get(obj.id_carrera)
            if criteria_id is None:
                continue
            self._ch.save_objetive_criteria(
                user_id=event.user_id,
                criteria_id=criteria_id,
                coincidence=coincidence_by_criteria.get(criteria_id, 0.0))

        for crit in prompt_result.priority_criteria:
            count = 1
            if crit["repeat"]:
                count = count + 1
            self._ch.save_user_criteria(
                user_id=event.user_id,
                criteria_id=crit["criteria_id"],
                coincidence=1.0,
                repeat_count=count)

        for crit in prompt_result.criterias:
            if crit["criteria_id"] in priority_ids:
                continue
            self._ch.save_user_criteria(
                user_id=event.user_id,
                criteria_id=crit["criteria_id"],
                coincidence=crit["coincidence"] / 100,
                repeat_count=1)

        self._ch.update_user_status(event.uuid_user, 2)
