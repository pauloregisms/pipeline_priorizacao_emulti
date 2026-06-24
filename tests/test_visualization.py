"""Testes da tabela simplificada de classificação."""

from __future__ import annotations

import unittest

import pandas as pd

from emulti_pipeline.visualization import build_simplified_classification_table


class SimplifiedClassificationTableTests(unittest.TestCase):
    def test_sorts_urgent_before_other_priorities_and_formats_columns(self) -> None:
        profiles = pd.DataFrame(
            {
                "patient_id": ["SYN-1", "SYN-2", "SYN-3"],
                "age_years": [30, 45, 52],
                "gender_category": ["feminino", "masculino", "outro_ou_nao_informado"],
                "social_vulnerability": [0.2, 0.8, 0.5],
            }
        )
        psychometrics = pd.DataFrame(
            {
                "patient_id": ["SYN-1", "SYN-2", "SYN-3"],
                "phq9_total": [4, 22, 14],
                "gad7_total": [3, 17, 11],
                "idate_estado_total": [35, 70, 56],
            }
        )
        extracted = pd.DataFrame(
            {
                "patient_id": ["SYN-1", "SYN-2", "SYN-3"],
                "zhat_ideacao_suicida_present": [0, 1, 0],
                "zhat_planejamento_suicida_present": [0, 1, 0],
                "zhat_autoagressao_iminente_present": [0, 0, 0],
                "zhat_risco_violencia_present": [0, 0, 0],
                "zhat_sintomas_psicoticos_present": [0, 0, 0],
                "zhat_uso_problematico_substancias_present": [0, 1, 0],
                "zhat_internacao_previa_present": [0, 0, 0],
                "zhat_agravamento_recente_present": [0, 1, 1],
                "zhat_suporte_social_baixo_present": [0, 1, 0],
                "zhat_comprometimento_funcional_severity_code": [0, 3, 2],
            }
        )
        predictions = pd.DataFrame(
            {
                "patient_id": ["SYN-1", "SYN-2", "SYN-3"],
                "y_true": [0, 3, 2],
                "y_pred": [0, 3, 2],
                "true_priority": ["baixa", "urgente", "alta"],
                "predicted_priority": ["baixa", "urgente", "alta"],
                "proba_0": [0.8, 0.01, 0.02],
                "proba_1": [0.1, 0.01, 0.08],
                "proba_2": [0.08, 0.08, 0.75],
                "proba_3": [0.02, 0.90, 0.15],
            }
        )

        table = build_simplified_classification_table(
            profiles, psychometrics, extracted, predictions, include_reference=True
        )

        self.assertEqual(table.loc[0, "Prioridade prevista"], "Urgente")
        self.assertEqual(table.loc[0, "ID do perfil sintético"], "SYN-2")
        self.assertEqual(table.loc[0, "Concorda com a referência simulada?"], "Sim")
        self.assertIn("Ideação suicida", table.loc[0, "Sinais de atenção extraídos"])
        self.assertEqual(table.loc[0, "Probabilidade alta/urgente"], "98.0%")


if __name__ == "__main__":
    unittest.main()
