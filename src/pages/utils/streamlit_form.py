import streamlit as st
from typing import Dict, List, Union, Any
from operator import lt, le, gt, ge, eq, ne

from .interfaces.form import Form


class StreamlitForm(Form):
    COMPARISON_OPERATORS = {
        "lt": lt,
        "le": le,
        "gt": gt,
        "ge": ge,
        "eq": eq,
        "ne": ne,
    }

    def generate_form(
        self,
        form_config,
        form_values,
        name,
        submit_button,
    ) -> bool:
        with st.form(key=f"{name}"):
            widget_mapping = {
                "string": st.text_input,
                "number": st.number_input,
                "select": st.selectbox,
                "checkbox": st.checkbox,
                "multi_select": st.multiselect,
            }

            special_char_mapping = {
                "Double New Line (\\n\\n)": "\n\n",
                "New Line (\\n)": "\n",
                "Carriage Return (\\r)": "\r",
                'Space (" ")': " ",
                'Empty String ("")': "",
            }

            reverse_special_char_mapping = {
                v: k for k, v in special_char_mapping.items()
            }

            for param, details in form_config["params"].items():
                widget_func = widget_mapping.get(details["type"])
                if widget_func:
                    widget_args = {"label": details["label"], "key": f"{name}_{param}"}
                    if details["type"] == "number":
                        widget_args.update(
                            {
                                "min_value": details.get("min_value", 0),
                                "value": form_values.get(
                                    param, details.get("default", 0)
                                ),
                            }
                        )
                    elif details["type"] == "select":
                        options = [
                            reverse_special_char_mapping.get(option, option)
                            for option in details["options"]
                        ]
                        default_value = reverse_special_char_mapping.get(
                            form_values.get(param, details.get("default")),
                            details.get("default"),
                        )
                        widget_args.update(
                            {
                                "options": options,
                                "index": (
                                    options.index(default_value)
                                    if default_value in options
                                    else 0
                                ),
                            }
                        )
                    elif details["type"] == "multi_select":
                        options = [
                            reverse_special_char_mapping.get(option, option)
                            for option in details["options"]
                        ]
                        default_values = [
                            reverse_special_char_mapping.get(value, value)
                            for value in form_values.get(
                                param, details.get("default", [])
                            )
                        ]
                        widget_args.update(
                            {
                                "options": options,
                                "default": default_values,
                            }
                        )
                    elif details["type"] == "checkbox":
                        widget_args["value"] = form_values.get(
                            param, details.get("default", False)
                        )
                    else:
                        widget_args["value"] = form_values.get(
                            param, details.get("default", "")
                        )
                    form_values[param] = widget_func(**widget_args)
            submit_button = st.form_submit_button(label=submit_button)
            if submit_button:
                if "separators" in form_values:
                    form_values["separators"] = [
                        special_char_mapping.get(value, value)
                        for value in form_values["separators"]
                    ]
        return submit_button

    def validate_form_values(
        self,
        form_values: Dict[str, Any],
        validations: List[Dict[str, Any]],
        constants: Dict[str, Any],
    ) -> bool:
        for validation in validations:
            rule = validation["rule"]
            field1, operator, field2 = rule

            value1 = form_values.get(field1)
            value2 = constants.get(field2, form_values.get(field2, field2))

            if not self.evaluate_rule(value1, operator, value2):
                st.error(validation["message"])
                return False
        return True

    @staticmethod
    def evaluate_rule(value1: Any, operator: str, value2: Any) -> bool:
        try:
            comparison_func = StreamlitForm.COMPARISON_OPERATORS[operator]
        except KeyError:
            raise ValueError(f"Unrecognized comparison operator: {operator}")
        return comparison_func(value1, value2)
