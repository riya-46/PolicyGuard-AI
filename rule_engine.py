import pandas as pd

def apply_rules_to_dataset(df, rules_list):

    df["Violated_Rule"] = ""
    df["Violation_Reason"] = ""

    # Replace spaces with underscore in column names
    df.columns = df.columns.str.replace(" ", "_")

    for rule in rules_list:

        rule_name = rule.get("name", "")
        explanation = rule.get("description", "")
        condition = rule.get("condition", "")

        try:
            mask = df.eval(condition)

            df.loc[mask, "Violated_Rule"] += rule_name + "; "
            df.loc[mask, "Violation_Reason"] += explanation + "; "

        except Exception as e:
            print(f"Error applying rule {rule_name}: {e}")

    return df