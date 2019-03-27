from tasks import *

w = {}
w["health"] = ["health", "research"]
w["science"] = ["research", "science", "study"]
w["industry"] = ["market", "industry", "business", "profit", "corporation", "marketing"]
print(word_family_graph_task("dummy", w))