import streamlit as st
from typing import Dict, Any
from operator import lt, le, gt, ge, eq, ne


class StreamlitForm:
    COMPARISON_OPERATORS = {"lt": lt, "le": le, "gt": gt, "ge": ge, "eq": eq, "ne": ne}

    def __init__(self, form_config: Dict[str, Any]):
        self.form_config = form_config

    def generate_form(
        self, form_values: Dict[str, Any], name: str, submit_button_label: str
    ) -> bool:
        with st.form(key=name):
            widget_mapping = self._get_widget_mapping()
            special_char_mapping = self._get_special_char_mapping()
            reverse_special_char_mapping = {
                v: k for k, v in special_char_mapping.items()
            }

            for param, details in self.form_config["params"].items():
                widget_func = widget_mapping.get(details["type"])
                if widget_func:
                    widget_args = {"label": details["label"], "key": f"{name}_{param}"}
                    if details["type"] == "number":
                        widget_args["min_value"] = details.get("min_value", 0)
                        widget_args["value"] = form_values.get(
                            param, details.get("default", 0)
                        )
                    elif details["type"] in ["select", "multi_select"]:
                        options = [
                            reverse_special_char_mapping.get(option, option)
                            for option in details["options"]
                        ]
                        if details["type"] == "select":
                            default_value = reverse_special_char_mapping.get(
                                form_values.get(param, details.get("default")),
                                details.get("default"),
                            )
                            widget_args["options"] = options
                            widget_args["index"] = (
                                options.index(default_value)
                                if default_value in options
                                else 0
                            )
                        else:
                            default_values = [
                                reverse_special_char_mapping.get(value, value)
                                for value in form_values.get(
                                    param, details.get("default", [])
                                )
                            ]
                            widget_args["options"] = options
                            widget_args["default"] = default_values
                    elif details["type"] == "checkbox":
                        widget_args["value"] = form_values.get(
                            param, details.get("default", False)
                        )
                    else:
                        widget_args["value"] = form_values.get(
                            param, details.get("default", "")
                        )
                    form_values[param] = widget_func(**widget_args)
            submit_button_clicked = st.form_submit_button(label=submit_button_label)
            if submit_button_clicked and "separators" in form_values:
                form_values["separators"] = [
                    special_char_mapping.get(value, value)
                    for value in form_values["separators"]
                ]
            return submit_button_clicked

    def validate_form_values(self, form_values: Dict[str, Any]) -> bool:
        validations = self.form_config.get("validations", [])
        constants = self.form_config.get("constants", {})
        for validation in validations:
            rule = validation["rule"]
            field1, operator, field2 = rule
            value1 = form_values.get(field1)
            value2 = constants.get(field2, form_values.get(field2, field2))
            if not self._evaluate_rule(value1, operator, value2):
                st.error(validation["message"])
                return False
        return True

    def _get_special_char_mapping(self):
        special_char_mapping = {
            "Double New Line (\\n\\n)": "\n\n",
            "New Line (\\n)": "\n",
            "Carriage Return (\\r)": "\r",
            'Space (" ")': " ",
            'Empty String ("")': "",
        }

        return special_char_mapping

    def _get_widget_mapping(self):
        widget_mapping = {
            "string": st.text_input,
            "number": st.number_input,
            "select": st.selectbox,
            "checkbox": st.checkbox,
            "multi_select": st.multiselect,
        }

        return widget_mapping

    @staticmethod
    def _evaluate_rule(value1: Any, operator: str, value2: Any) -> bool:
        comparison_func = StreamlitForm.COMPARISON_OPERATORS.get(operator)
        if not comparison_func:
            raise ValueError(f"Unrecognized comparison operator: {operator}")
        return comparison_func(value1, value2)
