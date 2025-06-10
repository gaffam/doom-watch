import json
import doom_watch as dw

current_data = dw.get_live_data()
score, scenarios = dw.calculate_risk_score(current_data)

output = {
    "score": score,
    "scenarios": scenarios,
}
print(json.dumps(output))
