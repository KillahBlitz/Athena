import json
from pathlib import Path

from kinasis_library.events.extractor_event import ExtractorEvent, Objetives, RisecAnswer

from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.criteria import CriteriaRag


class ExtractorHandler:
    def __init__(self, qh=None, ch=None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()
        self._prompt = json.loads(Path("/Users/jmonroyc/Documents/MyProjects/Athena/Backend/src/prompts/jev_prompt.json").read_text(encoding="utf-8"))

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

    def generate_prompt_for_jev(self, prompt_info: dict):
        prompt = {}
        dimentions = []
        prompt["objetive_instruction"] = {
            "instruction": self._prompt.get("prompt_objetives"),
            "evalue_info": prompt_info.get("part_0")
        }
        for k, v in prompt_info.items():
            if k != "part_0":
                dimentions.append(v)
        prompt["dimension_instruction"] = {
            "instruction": self._prompt.get("prompt_criterias"),
            "evalue_info": dimentions
        }
        prompt["expected_output"] = self._prompt.get("expected_output")
        return prompt